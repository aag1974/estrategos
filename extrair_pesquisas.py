"""
extrair_pesquisas.py — extrai estrutura de cenários dos questionários PDF
das pesquisas eleitorais TSE, usando Claude Haiku (Anthropic API).

Os PDFs no TSE são questionários (perguntas + candidatos testados), NÃO
relatórios de resultado. Por isso o extrator captura:
  - Cargos pesquisados
  - Cenários (estimulada · espontânea · rejeição · 2º turno) por cargo
  - Candidatos testados em cada cenário
  - Filtros demográficos aplicados

Os percentuais de cada candidato ficam em fontes separadas (relatórios dos
institutos, divulgações na imprensa) — fora do escopo do MVP.

Uso:
    export ANTHROPIC_API_KEY=sk-ant-...
    python3 extrair_pesquisas.py [--uf DF] [--limite N] [--reprocessar]

Idempotente: por padrão só processa pesquisas com status "pendente".
Use --reprocessar para refazer todas.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent
DIR_OUT = ROOT / "outputs_pesquisas"
DIR_QUEST = ROOT / "dados_tse_pesquisas" / "questionarios"

API_URL = "https://api.anthropic.com/v1/messages"
MODELO = "claude-haiku-4-5-20251001"
MAX_TOKENS = 4096

PROMPT_SISTEMA = """Você está extraindo a estrutura de um questionário de pesquisa eleitoral registrado no TSE (Tribunal Superior Eleitoral) brasileiro.

O QUE ESTE PDF É:
- Documento que descreve as perguntas que serão feitas aos eleitores numa pesquisa.
- Lista os candidatos testados em cada cenário (mas NÃO os percentuais — eles ficam em outra fonte).
- Contém filtros demográficos (sexo, idade, escolaridade, renda, etc).

O QUE EXTRAIR:
1. Cenários por cargo (Governador, Senador, Deputado Federal, Deputado Distrital).
2. Para cada cenário: tipo, número da questão, candidatos com partido se mencionado, e flags de branco/nulo e NS/NR.
3. Filtros demográficos aplicados (apenas tipos, não valores).

TIPOS DE CENÁRIO (use exatamente estas chaves):
- "estimulada": apresenta lista de candidatos ao entrevistado
- "espontanea": pergunta aberta, sem lista
- "rejeicao": "em quem NÃO votaria de jeito nenhum"
- "2o_turno": cenários de segundo turno (par a par)

Formato de saída: JSON puro, sem texto fora do JSON, sem markdown.

Schema:
{
  "cargos": ["Governador", "Senador", ...],
  "cenarios": [
    {
      "cargo": "Governador",
      "tipo": "estimulada",
      "questao": "Q. 06",
      "candidatos": [
        {"nome": "Celina Leão", "partido": "PP"},
        ...
      ],
      "tem_branco_nulo": true,
      "tem_ns_nr": true
    }
  ],
  "filtros_demograficos": ["sexo", "idade", "escolaridade", "renda"]
}

REGRAS:
- Use exatamente as chaves do schema. Sem acentos em chaves.
- Nomes de candidatos: capitalize normalmente ("Celina Leão", "Ibaneis Rocha").
- Partido: sigla curta ("PT", "MDB", "PL", "União" etc). Se não mencionado, omita o campo.
- Se o cenário lista os mesmos candidatos da estimulada anterior, ainda assim repita a lista.
- Em "2o_turno", use 2 candidatos no array.
- Não invente candidatos que não estão no PDF. Se houver dúvida, omita.
- Se o PDF não tiver cenário claro pra um cargo (ex: só pergunta espontânea), ainda registre o cenário com o tipo certo.
"""


def carregar_json(uf: str) -> dict:
    path = DIR_OUT / f"pesquisas_{uf.lower()}.json"
    if not path.exists():
        sys.exit(f"ERRO: {path} não existe. Rode coletor_pesquisas.py primeiro.")
    return json.loads(path.read_text(encoding="utf-8"))


def salvar_json(uf: str, data: dict):
    path = DIR_OUT / f"pesquisas_{uf.lower()}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def extrair_texto_pdf(pdf_path: Path) -> str:
    """Usa pdftotext (poppler) pra extrair texto. Mais barato em tokens que PDF b64."""
    try:
        r = subprocess.run(
            ["pdftotext", str(pdf_path), "-"],
            capture_output=True, text=True, check=True, timeout=30,
        )
        return r.stdout
    except FileNotFoundError:
        sys.exit("ERRO: pdftotext não encontrado. Instale 'poppler' (brew install poppler).")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"pdftotext falhou: {e.stderr}")


def chamar_claude(texto_pdf: str, api_key: str) -> dict:
    """Chama Claude Haiku via REST. Retorna JSON parseado da extração."""
    body = json.dumps({
        "model": MODELO,
        "max_tokens": MAX_TOKENS,
        "system": PROMPT_SISTEMA,
        "messages": [{
            "role": "user",
            "content": f"Extraia a estrutura do questionário abaixo no formato JSON especificado:\n\n---\n{texto_pdf}\n---",
        }],
    }).encode("utf-8")

    req = urllib.request.Request(
        API_URL, data=body,
        headers={
            "x-api-key":         api_key,
            "anthropic-version": "2023-06-01",
            "content-type":      "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8", errors="replace") if e.fp else str(e)
        raise RuntimeError(f"HTTP {e.code}: {msg[:300]}")

    text = data["content"][0]["text"].strip()
    # Tolera markdown wrap eventual
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.MULTILINE).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"JSON inválido na resposta: {e}\nResposta: {text[:400]}")


def validar_extracao(extr: dict) -> tuple[bool, str]:
    """Sanity checks no JSON extraído."""
    if not isinstance(extr, dict):
        return False, "extração não é um dict"
    if "cenarios" not in extr or not isinstance(extr["cenarios"], list):
        return False, "campo 'cenarios' ausente ou não é lista"
    if "cargos" not in extr or not isinstance(extr["cargos"], list):
        return False, "campo 'cargos' ausente ou não é lista"
    for c in extr["cenarios"]:
        if c.get("tipo") not in ("estimulada", "espontanea", "rejeicao", "2o_turno"):
            return False, f"tipo de cenário inválido: {c.get('tipo')}"
        if not isinstance(c.get("candidatos", []), list):
            return False, "candidatos de cenário não é lista"
    return True, ""


def extrair_uma(p: dict, api_key: str) -> dict:
    """Atualiza p["extracao"] in-place. Retorna o entry."""
    pdf_arquivo = p.get("pdf_arquivo")
    if not pdf_arquivo:
        p["extracao"] = {
            "status": "sem_pdf", "extraido_em": None, "modelo": None,
            "erro": "PDF não encontrado em dados_tse_pesquisas/questionarios/",
            "cenarios": [],
        }
        return p

    pdf_path = DIR_QUEST / pdf_arquivo
    if not pdf_path.exists():
        p["extracao"] = {
            "status": "sem_pdf", "extraido_em": None, "modelo": None,
            "erro": f"arquivo {pdf_arquivo} não existe",
            "cenarios": [],
        }
        return p

    print(f"  · {p['protocolo']} ({p['instituto'][:30]})... ", end="", flush=True)
    try:
        texto = extrair_texto_pdf(pdf_path)
        if len(texto.strip()) < 100:
            raise RuntimeError(f"texto extraído vazio ({len(texto)} chars)")
        extr = chamar_claude(texto, api_key)
        ok, msg = validar_extracao(extr)
        if not ok:
            raise RuntimeError(f"validação falhou: {msg}")
        p["extracao"] = {
            "status":      "extraido",
            "extraido_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "modelo":      MODELO,
            "erro":        None,
            "cargos":              extr.get("cargos", []),
            "cenarios":            extr.get("cenarios", []),
            "filtros_demograficos": extr.get("filtros_demograficos", []),
        }
        print(f"OK ({len(extr.get('cenarios', []))} cenários)")
    except Exception as e:
        p["extracao"] = {
            "status":      "falhou",
            "extraido_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "modelo":      MODELO,
            "erro":        str(e)[:300],
            "cenarios":    [],
        }
        print(f"FALHOU: {str(e)[:80]}")
    return p


def main():
    ap = argparse.ArgumentParser(description="Extrator IA de pesquisas TSE")
    ap.add_argument("--uf", default="DF")
    ap.add_argument("--limite", type=int, default=None,
                    help="Processar no máximo N pesquisas pendentes")
    ap.add_argument("--reprocessar", action="store_true",
                    help="Reprocessa todas (não só pendentes)")
    args = ap.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        env_path = ROOT / ".env"
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                line = line.strip()
                if line.startswith("ANTHROPIC_API_KEY"):
                    api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break
    if not api_key:
        sys.exit("ERRO: ANTHROPIC_API_KEY não definida.\n"
                 "Defina via: export ANTHROPIC_API_KEY=sk-ant-...\n"
                 "Ou crie um arquivo .env na raiz com a linha: ANTHROPIC_API_KEY=sk-ant-...")

    data = carregar_json(args.uf)
    pesquisas = data["pesquisas"]

    alvo = [p for p in pesquisas
            if args.reprocessar or p["extracao"]["status"] == "pendente"]
    if args.limite:
        alvo = alvo[:args.limite]

    print()
    print(f"  Extrator de pesquisas (Claude Haiku) — UF={args.uf}")
    print("  " + "─" * 38)
    print(f"  {len(pesquisas)} pesquisas no JSON · {len(alvo)} para processar")
    print()

    if not alvo:
        print("  Nada a fazer.")
        return

    for p in alvo:
        extrair_uma(p, api_key)

    salvar_json(args.uf, data)
    n_ok = sum(1 for p in pesquisas if p["extracao"]["status"] == "extraido")
    n_falhou = sum(1 for p in pesquisas if p["extracao"]["status"] == "falhou")
    n_pend = sum(1 for p in pesquisas if p["extracao"]["status"] == "pendente")
    print()
    print(f"  ✅ Salvo. Extraídas: {n_ok} · Falharam: {n_falhou} · Pendentes: {n_pend}")
    print()


if __name__ == "__main__":
    main()
