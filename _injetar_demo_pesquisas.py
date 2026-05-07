"""
Injeta 8 pesquisas DEMO no outputs_pesquisas/pesquisas_df.json — 4 institutos
(Veritá, Igape, Cepphor, Phoenix) × 2 rodadas, foco Deputado Federal DF 2026.

Espelha o que está no relatorio_pesquisas_demo.html. Inclui um bloco extra
`consolidacao_demo` no JSON com regressão linear pré-calculada e findings
editoriais — consumido pelo painel "Análise Consolidada" do dashboard.

Idempotente: substitui qualquer entrada is_demo existente por essas 8.
"""
import json
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent
JSON_PATH = ROOT / "outputs_pesquisas" / "pesquisas_df.json"

INSTITUTO_COR = {
    "Veritá":   "#1f77b4",
    "Igape":    "#ff7f0e",
    "Cepphor":  "#2ca02c",
    "Phoenix":  "#d62728",
}

CANDIDATOS = [
    # (chave, nome, partido, cor própria do candidato)
    ("kicis", "Bia Kicis",            "PL",          "#A32D2D"),
    ("fred",  "Fred Linhares",        "Republicanos","#854F0B"),
    ("erika", "Erika Kokay",          "PT",          "#534AB7"),
    ("jcr",   "Julio Cesar Ribeiro",  "Republicanos","#D85A30"),
    ("veras", "Reginaldo Veras",      "PV",          "#0F6E56"),
    ("nemer", "Roney Nemer",          "PP",          "#6B7280"),
]

# 8 pesquisas — campo Federal · candidatos REAIS · % SINTÉTICOS
PESQUISAS = [
    # data, instituto, n, kicis fred erika jcr veras nemer | bln ns_nr
    ("2026-02-15", "Igape",   1000, 14, 13, 13, 11, 5, 5,  8, 31),
    ("2026-02-20", "Veritá",  1220, 15, 14, 12, 11, 5, 4,  8, 31),
    ("2026-03-10", "Cepphor", 1500, 16, 14, 12, 10, 5, 5,  8, 30),
    ("2026-03-25", "Phoenix", 1203, 17, 15, 13, 10, 6, 5,  7, 27),
    ("2026-04-15", "Veritá",  1220, 18, 15, 12,  9, 6, 5,  7, 28),
    ("2026-04-22", "Igape",   3000, 17, 14, 13,  9, 7, 5,  7, 28),
    ("2026-05-05", "Cepphor",  400, 19, 16, 13,  8, 7, 5,  7, 25),
    ("2026-05-15", "Phoenix", 1500, 20, 17, 14,  8, 7, 5,  6, 23),
]

CARGO_FOCAL = "Deputado Federal"
DATA_BASE = date(2026, 2, 15)


def dia(s: str) -> int:
    return (date.fromisoformat(s) - DATA_BASE).days


def regressao(xs, ys):
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    cov = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    var = sum((x - mx) ** 2 for x in xs)
    slope = cov / var if var else 0
    return my - slope * mx, slope


def montar_entry(idx: int, p: tuple) -> dict:
    data_div, instituto, n, *pcts, bln, ns = p
    cands = [
        {"nome": nome, "partido": part, "pct": float(pcts[i])}
        for i, (_, nome, part, _) in enumerate(CANDIDATOS)
    ]
    proto = f"DEMO{(idx+1):03d}2026"
    return {
        "protocolo":             proto,
        "instituto":             instituto + " · DEMO",
        "instituto_razao_social": "Pesquisa de demonstração — " + instituto,
        "instituto_cnpj":        "—",
        "pesquisa_propria":      False,
        "cargo":                 [CARGO_FOCAL],
        "data_registro":         data_div,
        "data_campo_inicio":     data_div,
        "data_campo_fim":        data_div,
        "data_divulgacao":       data_div,
        "n_entrevistados":       n,
        "metodologia":           "Pesquisa quantitativa demonstrativa, face-a-face em ponto de fluxo. Amostra representativa do eleitorado DF (16+).",
        "plano_amostral":        f"Universo: 2,2M eleitores DF (TSE 2026). Margem de erro: ±2,5pp · IC 95%. Cotas: sexo, idade, escolaridade, renda.",
        "estatistico":           "Demonstração",
        "conre":                 "—",
        "valor":                 None,
        "uf":                    "DF",
        "url_tse_pesqele":       None,
        "pdf_arquivo":           None,
        "is_demo":               True,
        "extracao": {
            "status":      "extraido",
            "extraido_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "modelo":      "demo (dados sintéticos)",
            "erro":        None,
            "cargos":              [CARGO_FOCAL],
            "filtros_demograficos": ["sexo", "idade", "escolaridade", "renda"],
            "cenarios": [
                {
                    "cargo":           CARGO_FOCAL,
                    "tipo":            "estimulada",
                    "questao":         "—",
                    "candidatos":      cands,
                    "tem_branco_nulo": True,
                    "tem_ns_nr":       True,
                    "branco_nulo_pct": float(bln),
                    "ns_nr_pct":       float(ns),
                    "ic_pp":           2.5,
                },
            ],
        },
    }


def montar_consolidacao() -> dict:
    """Pré-calcula regressão linear por candidato + findings editoriais
    para o painel consolidado do dashboard."""
    serie_por_cand = {}
    cand_idx = {k: 3+i for i, (k, *_ ) in enumerate(CANDIDATOS)}

    for k, nome, partido, cor in CANDIDATOS:
        serie = []
        for p in PESQUISAS:
            data, instituto, n = p[0], p[1], p[2]
            pct = p[cand_idx[k]]
            serie.append({
                "data":      data,
                "dia":       dia(data),
                "instituto": instituto,
                "n":         n,
                "pct":       float(pct),
            })
        xs = [s["dia"] for s in serie]
        ys = [s["pct"] for s in serie]
        intercept, slope = regressao(xs, ys)
        delta = slope * (max(xs) - min(xs))
        serie_por_cand[k] = {
            "key":        k,
            "nome":       nome,
            "partido":    partido,
            "cor":        cor,
            "serie":      serie,
            "intercept":  round(intercept, 3),
            "slope":      round(slope, 5),
            "delta":      round(delta, 1),
            "y_inicio":   ys[0],
            "y_fim":      ys[-1],
        }

    # Findings editoriais (textos cravados — espelham o relatório)
    findings = [
        {
            "titulo": "Bia Kicis consolida liderança do PL no DF",
            "body": (
                f'Líder isolada do campo liberal-conservador, <strong>Bia Kicis (PL)</strong> avança de '
                f'<strong>14% para 20%</strong> em três meses (<span class="up">+{serie_por_cand["kicis"]["delta"]:.1f}pp</span>). '
                f'Os <strong>4 institutos</strong> avaliados confirmam a tendência de alta — sinal de movimento estrutural, '
                f'não de oscilação amostral. A magnitude (~6pp) supera a margem de erro consolidada (±2,5pp).'
            ),
        },
        {
            "titulo": "Bancada evangélica fragmenta-se",
            "body": (
                f'<strong>Julio Cesar Ribeiro (Republicanos)</strong>, pastor evangélico eleito em 2022, '
                f'recua de <strong>11% para 8%</strong> (<span class="dn">{serie_por_cand["jcr"]["delta"]:.1f}pp</span>) — '
                f'queda confirmada por todos os 4 institutos. Já <strong>Fred Linhares</strong>, do mesmo partido '
                f'mas com perfil mais técnico, sobe <span class="up">+{serie_por_cand["fred"]["delta"]:.1f}pp</span>. '
                f'Movimento sugere realocação intra-bancada, não saída de eleitores do campo conservador.'
            ),
        },
        {
            "titulo": "Reginaldo Veras emerge como segundo nome do PT-aliados",
            "body": (
                f'Erika Kokay segue dominando o voto progressista (~13%, estável). Mas <strong>Reginaldo Veras (PV)</strong> '
                f'avança discretamente de 5% para 7% (<span class="up">+{serie_por_cand["veras"]["delta"]:.1f}pp</span>), '
                f'criando uma <em>segunda opção</em> consistente para o eleitor de centro-esquerda — útil em '
                f'cenário onde o quociente eleitoral exigir distribuição de votos.'
            ),
        },
    ]

    return {
        "cargo":      CARGO_FOCAL,
        "periodo":    {"inicio": "2026-02-15", "fim": "2026-05-15"},
        "n_pesquisas": len(PESQUISAS),
        "institutos": [{"nome": k, "cor": v} for k, v in INSTITUTO_COR.items()],
        "candidatos": list(serie_por_cand.values()),
        "findings":   findings,
    }


def main():
    if not JSON_PATH.exists():
        raise SystemExit(f"{JSON_PATH} não existe — rode coletor_pesquisas.py primeiro")

    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))

    # Remove entries DEMO existentes (idempotência)
    pesquisas = [p for p in data["pesquisas"] if not p.get("is_demo")]

    # Adiciona as 8 novas
    for i, p in enumerate(PESQUISAS):
        pesquisas.append(montar_entry(i, p))

    # Re-ordena por data_divulgacao desc
    pesquisas.sort(key=lambda p: p.get("data_divulgacao") or "", reverse=True)

    data["pesquisas"]   = pesquisas
    data["n_pesquisas"] = len(pesquisas)
    data["consolidacao_demo"] = montar_consolidacao()
    data["atualizado_em"] = datetime.now(timezone.utc).isoformat(timespec="seconds")

    JSON_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    n_demo = sum(1 for p in pesquisas if p.get("is_demo"))
    print(f"OK: {len(pesquisas)} pesquisas no JSON ({n_demo} demo · {len(pesquisas)-n_demo} reais)")
    print(f"    consolidacao_demo: {len(data['consolidacao_demo']['candidatos'])} candidatos · {data['consolidacao_demo']['n_pesquisas']} pesquisas")


if __name__ == "__main__":
    main()
