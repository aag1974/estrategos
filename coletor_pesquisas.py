"""
coletor_pesquisas.py — coleta pesquisas eleitorais 2026 do TSE Dados Abertos
e produz JSON canônico para o dashboard Estrategos (filtrado por UF=DF).

Fontes:
- Catálogo CSV via CKAN: pesquisa_eleitoral_2026.zip (com 1 CSV por UF + BRASIL)
- PDFs dos questionários: questionario_pesquisa_2026.zip

O JSON gerado é consumido por:
- gerar_estrategos.py (embarca como __PESQUISAS_B64__ no index.html)
- extrair_pesquisas.py (preenche `extracao` com cenários extraídos por IA)

Uso:
    python3 coletor_pesquisas.py [--uf DF] [--baixar-pdfs]

Sem --baixar-pdfs, só atualiza o JSON com a lista de pesquisas; assume que
PDFs já estão em dados_tse_pesquisas/questionarios/. Com a flag, baixa o ZIP
de questionários (~377 MB), extrai só os da UF, depois apaga o ZIP.
"""
import argparse
import csv
import json
import re
import sys
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent
DIR_DADOS = ROOT / "dados_tse_pesquisas"
DIR_QUEST = DIR_DADOS / "questionarios"
DIR_OUT = ROOT / "outputs_pesquisas"

URL_PESQUISAS = "https://cdn.tse.jus.br/estatistica/sead/odsele/pesquisa_eleitoral/pesquisa_eleitoral_2026.zip"
URL_QUESTIONARIOS = "https://cdn.tse.jus.br/estatistica/sead/odsele/pesquisa_eleitoral/questionario_pesquisa_2026.zip"
URL_PESQELE = "https://pesqele-divulgacao.tse.jus.br/divulgacaopesqele/divulgacao/index.html"

CARGOS_VALIDOS = {
    "Governador", "Senador",
    "Deputado Federal", "Deputado Distrital", "Deputado Estadual",
    "Presidente da República",
}


def baixar(url: str, destino: Path, label: str = ""):
    print(f"  Baixando {label or url}...", end="", flush=True)
    destino.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, str(destino))
    kb = destino.stat().st_size // 1024
    print(f" {kb:,} KB")


def baixar_csv_pesquisas(uf: str) -> Path:
    """Baixa o ZIP de pesquisas (~1 MB), extrai o CSV BRASIL e devolve o caminho."""
    DIR_DADOS.mkdir(parents=True, exist_ok=True)
    zip_path = DIR_DADOS / "pesquisa_eleitoral_2026.zip"
    csv_local = DIR_DADOS / "pesquisa_eleitoral_2026_BRASIL.csv"
    baixar(URL_PESQUISAS, zip_path, "catálogo pesquisas")
    with zipfile.ZipFile(zip_path) as z:
        z.extract("pesquisa_eleitoral_2026_BRASIL.csv", DIR_DADOS)
    return csv_local


def baixar_pdfs_uf(uf: str):
    """Baixa o ZIP grande de questionários, extrai só os da UF, apaga o ZIP."""
    DIR_QUEST.mkdir(parents=True, exist_ok=True)
    zip_path = DIR_DADOS / "questionario_pesquisa_2026.zip"
    baixar(URL_QUESTIONARIOS, zip_path, f"questionários (~377 MB)")
    print(f"  Extraindo PDFs de {uf}...", end="", flush=True)
    n = 0
    with zipfile.ZipFile(zip_path) as z:
        for name in z.namelist():
            if name.startswith(f"{uf}") and name.lower().endswith(".pdf"):
                z.extract(name, DIR_QUEST)
                n += 1
    print(f" {n} PDFs")
    zip_path.unlink()


def normalizar_data(s: str) -> str | None:
    """Aceita 'YYYY-MM-DD HH:MM:SS' ou 'YYYY-MM-DD' e devolve 'YYYY-MM-DD' ou None."""
    if not s or s == "#NULO#":
        return None
    s = s.strip()
    m = re.match(r"^(\d{4}-\d{2}-\d{2})", s)
    return m.group(1) if m else None


def normalizar_cargos(s: str) -> list[str]:
    """Cargos vêm separados por vírgula no CSV. Filtra valores válidos."""
    if not s or s == "#NULO#":
        return []
    return [c.strip() for c in s.split(",") if c.strip() in CARGOS_VALIDOS]


def normalizar_valor(s: str) -> float | None:
    if not s or s == "#NULO#":
        return None
    try:
        return float(s.replace(".", "").replace(",", "."))
    except ValueError:
        return None


def normalizar_cnpj(s: str) -> str:
    s = (s or "").strip()
    if len(s) != 14 or not s.isdigit():
        return s
    return f"{s[:2]}.{s[2:5]}.{s[5:8]}/{s[8:12]}-{s[12:]}"


def truncar(s: str, n: int = 400) -> str:
    if not s or s == "#NULO#":
        return ""
    s = s.strip()
    return s if len(s) <= n else s[:n].rstrip() + "…"


def encontrar_pdf_local(protocolo: str) -> Path | None:
    """Procura PDF cujo nome começa com o protocolo. Os PDFs do TSE têm
    formato <PROTOCOLO>_<ID>_questionario_pesquisa.pdf."""
    if not DIR_QUEST.exists():
        return None
    for p in DIR_QUEST.iterdir():
        if p.name.startswith(protocolo) and p.suffix.lower() == ".pdf":
            return p
    return None


def construir_url_pesqele(uf: str) -> str:
    """Link genérico para o PesqEle (TSE não oferece deep-link por protocolo)."""
    return f"{URL_PESQELE}#/divulgacao/2026/UF/{uf}"


def carregar_existente(json_path: Path) -> dict[str, dict]:
    """Para preservar `extracao` de pesquisas já processadas, indexa por protocolo."""
    if not json_path.exists():
        return {}
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
        return {p["protocolo"]: p for p in data.get("pesquisas", [])}
    except Exception:
        return {}


def coletar(uf: str, baixar_zip: bool = True, baixar_pdfs: bool = False) -> dict:
    DIR_OUT.mkdir(parents=True, exist_ok=True)
    out_path = DIR_OUT / f"pesquisas_{uf.lower()}.json"

    # 1. Baixar/garantir CSV
    if baixar_zip:
        csv_path = baixar_csv_pesquisas(uf)
    else:
        csv_path = DIR_DADOS / "pesquisa_eleitoral_2026_BRASIL.csv"
        if not csv_path.exists():
            csv_path = baixar_csv_pesquisas(uf)

    if baixar_pdfs:
        baixar_pdfs_uf(uf)

    # 2. Pré-carregar extrações existentes (idempotência) e preservar DEMO
    existentes = carregar_existente(out_path)
    demo_entries = [p for p in existentes.values() if p.get("is_demo")]

    # 3. Filtrar e estruturar
    print(f"  Filtrando UF={uf} no CSV...", end="", flush=True)
    pesquisas = []
    with csv_path.open(encoding="latin-1", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            if row.get("SG_UF", "").strip() != uf:
                continue
            protocolo = row["NR_PROTOCOLO_REGISTRO"].strip()
            pdf = encontrar_pdf_local(protocolo)
            entry = {
                "protocolo":             protocolo,
                "instituto":             (row.get("NM_EMPRESA_FANTASIA") or row.get("NM_EMPRESA") or "").strip()
                                          if row.get("NM_EMPRESA_FANTASIA") not in (None, "", "#NULO#")
                                          else row.get("NM_EMPRESA", "").strip(),
                "instituto_razao_social": row.get("NM_EMPRESA", "").strip(),
                "instituto_cnpj":        normalizar_cnpj(row.get("NR_CNPJ_EMPRESA", "")),
                "pesquisa_propria":      row.get("ST_PESQUISA_PROPRIA", "").strip() == "S",
                "cargo":                 normalizar_cargos(row.get("DS_CARGO", "")),
                "data_registro":         normalizar_data(row.get("DT_REGISTRO", "")),
                "data_campo_inicio":     normalizar_data(row.get("DT_INICIO_PESQUISA", "")),
                "data_campo_fim":        normalizar_data(row.get("DT_FIM_PESQUISA", "")),
                "data_divulgacao":       normalizar_data(row.get("DT_DIVULGACAO", "")),
                "n_entrevistados":       int(row["QT_ENTREVISTADO"]) if row.get("QT_ENTREVISTADO", "").strip().isdigit() else None,
                "metodologia":           truncar(row.get("DS_METODOLOGIA_PESQUISA", ""), 600),
                "plano_amostral":        truncar(row.get("DS_PLANO_AMOSTRAL", ""), 600),
                "estatistico":           (row.get("NM_ESTATISTICO_RESP") or "").strip().title(),
                "conre":                 row.get("CD_CONRE", "").strip(),
                "valor":                 normalizar_valor(row.get("VR_PESQUISA", "")),
                "uf":                    uf,
                "url_tse_pesqele":       construir_url_pesqele(uf),
                "pdf_arquivo":           pdf.name if pdf else None,
                "extracao": existentes.get(protocolo, {}).get("extracao") or {
                    "status":      "pendente" if pdf else "sem_pdf",
                    "extraido_em": None,
                    "modelo":      None,
                    "erro":        None,
                    "cenarios":    [],
                },
            }
            pesquisas.append(entry)

    # Re-injeta entries DEMO (preservadas)
    pesquisas.extend(demo_entries)

    # Ordena: divulgação mais recente primeiro
    pesquisas.sort(key=lambda p: p.get("data_divulgacao") or "", reverse=True)
    print(f" {len(pesquisas)} pesquisas")

    n_pendente = sum(1 for p in pesquisas if p["extracao"]["status"] == "pendente")
    n_extraido = sum(1 for p in pesquisas if p["extracao"]["status"] == "extraido")
    n_sem_pdf  = sum(1 for p in pesquisas if p["extracao"]["status"] == "sem_pdf")
    print(f"    extraídas: {n_extraido} · pendentes: {n_pendente} · sem PDF: {n_sem_pdf}")

    saida = {
        "atualizado_em":  datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "fonte":          "TSE Dados Abertos · " + URL_PESQUISAS,
        "uf":             uf,
        "n_pesquisas":    len(pesquisas),
        "pesquisas":      pesquisas,
    }
    out_path.write_text(json.dumps(saida, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  ✅ {out_path} ({out_path.stat().st_size // 1024:,} KB)")
    return saida


def main():
    ap = argparse.ArgumentParser(description="Coletor TSE de pesquisas eleitorais")
    ap.add_argument("--uf", default="DF", help="UF para filtrar (default: DF)")
    ap.add_argument("--baixar-pdfs", action="store_true",
                    help="Baixa o ZIP de questionários (377 MB) e extrai PDFs da UF")
    ap.add_argument("--cache", action="store_true",
                    help="Usa CSV em cache se já existir, em vez de re-baixar")
    args = ap.parse_args()

    print()
    print(f"  Coletor de pesquisas TSE — UF={args.uf}")
    print("  " + "─" * 38)
    coletar(args.uf, baixar_zip=not args.cache, baixar_pdfs=args.baixar_pdfs)
    print()


if __name__ == "__main__":
    main()
