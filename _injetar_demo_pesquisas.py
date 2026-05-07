"""
Injeta 3 rodadas DEMO no outputs_pesquisas/pesquisas_df.json para servir
como case de demonstração do Clipping de Pesquisas (com percentuais e
tendência cross-rodada).

Os candidatos usados são REAIS (extraídos do questionário Veritá DF003202026),
mas os percentuais são SINTÉTICOS e claramente marcados (is_demo=true).

Idempotente: se entries DEMO existirem, são substituídas. Reais são preservadas.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent
JSON_PATH = ROOT / "outputs_pesquisas" / "pesquisas_df.json"

CANDS_GOV = [
    ("Celina Leão",          "PP"),
    ("José Roberto Arruda",  "PSD"),
    ("Leandro Grass",        "PT"),
    ("Paula Belmonte",       "PSDB"),
    ("Ricardo Cappelli",     "PSB"),
    ("Kiko Caputo",          "Novo"),
]

CANDS_SEN = [
    ("Ibaneis Rocha",        "MDB"),
    ("José Reguffe",         "União"),
    ("Bia Kicis",            "PL"),
    ("Erika Kokay",          "PT"),
    ("Michelle Bolsonaro",   "PL"),
    ("Leila Barros",         "PDT"),
    ("Sebastião Coelho",     "Novo"),
]

# 3 rodadas (índices: pct_gov[i], pct_sen[i], com soma + brancos/NS/NR fechando 100)
RODADAS = [
    {
        "protocolo":         "DEMO0012026",
        "data_registro":     "2026-03-12",
        "data_campo_inicio": "2026-03-10",
        "data_campo_fim":    "2026-03-13",
        "data_divulgacao":   "2026-03-15",
        "n_entrevistados":   1500,
        "ic_pp":             2.5,
        "pct_gov":           [22, 18, 16, 12, 4, 4],   # Σ = 76 (BL/N 12, NS/NR 12)
        "pct_sen":           [28, 19, 15, 14, 11, 5, 3],  # Σ = 95 (BL/N 3, NS/NR 2)
        "bln_gov": 12, "ns_gov": 12,
        "bln_sen":  3, "ns_sen":  2,
    },
    {
        "protocolo":         "DEMO0022026",
        "data_registro":     "2026-04-08",
        "data_campo_inicio": "2026-04-05",
        "data_campo_fim":    "2026-04-09",
        "data_divulgacao":   "2026-04-10",
        "n_entrevistados":   1500,
        "ic_pp":             2.5,
        "pct_gov":           [24, 17, 15, 13, 5, 3],   # Σ = 77 (BL/N 11, NS/NR 12)
        "pct_sen":           [30, 17, 16, 15, 10, 5, 3],  # Σ = 96
        "bln_gov": 11, "ns_gov": 12,
        "bln_sen":  2, "ns_sen":  2,
    },
    {
        "protocolo":         "DEMO0032026",
        "data_registro":     "2026-05-03",
        "data_campo_inicio": "2026-05-01",
        "data_campo_fim":    "2026-05-04",
        "data_divulgacao":   "2026-05-05",
        "n_entrevistados":   1500,
        "ic_pp":             2.5,
        "pct_gov":           [26, 16, 17, 13, 5, 3],   # Σ = 80 (BL/N 10, NS/NR 10)
        "pct_sen":           [31, 14, 18, 16, 9, 5, 3],   # Σ = 96
        "bln_gov": 10, "ns_gov": 10,
        "bln_sen":  2, "ns_sen":  2,
    },
]


def montar_entry(r: dict) -> dict:
    cands_gov = [
        {"nome": n, "partido": p, "pct": float(r["pct_gov"][i])}
        for i, (n, p) in enumerate(CANDS_GOV)
    ]
    cands_sen = [
        {"nome": n, "partido": p, "pct": float(r["pct_sen"][i])}
        for i, (n, p) in enumerate(CANDS_SEN)
    ]
    return {
        "protocolo":             r["protocolo"],
        "instituto":             "Estrategos · DEMO POLL",
        "instituto_razao_social": "Pesquisa de demonstração — Estrategos",
        "instituto_cnpj":        "—",
        "pesquisa_propria":      True,
        "cargo":                 ["Governador", "Senador"],
        "data_registro":         r["data_registro"],
        "data_campo_inicio":     r["data_campo_inicio"],
        "data_campo_fim":        r["data_campo_fim"],
        "data_divulgacao":       r["data_divulgacao"],
        "n_entrevistados":       r["n_entrevistados"],
        "metodologia":           "Pesquisa quantitativa demonstrativa, face a face em ponto de fluxo. Amostra representativa do eleitorado DF, estratificada por sexo, idade, escolaridade e renda.",
        "plano_amostral":        f"Universo: 2,2M eleitores DF (TSE 2026). Margem de erro: ±{r['ic_pp']}pp · IC 95%. Cotas: sexo, idade, escolaridade, renda.",
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
            "cargos":              ["Governador", "Senador"],
            "filtros_demograficos": ["sexo", "idade", "escolaridade", "renda"],
            "cenarios": [
                {
                    "cargo":           "Governador",
                    "tipo":            "estimulada",
                    "questao":         "Q. 06",
                    "candidatos":      cands_gov,
                    "tem_branco_nulo": True,
                    "tem_ns_nr":       True,
                    "branco_nulo_pct": float(r["bln_gov"]),
                    "ns_nr_pct":       float(r["ns_gov"]),
                    "ic_pp":           float(r["ic_pp"]),
                },
                {
                    "cargo":           "Senador",
                    "tipo":            "estimulada",
                    "questao":         "Q. 11",
                    "candidatos":      cands_sen,
                    "tem_branco_nulo": True,
                    "tem_ns_nr":       True,
                    "branco_nulo_pct": float(r["bln_sen"]),
                    "ns_nr_pct":       float(r["ns_sen"]),
                    "ic_pp":           float(r["ic_pp"]),
                },
            ],
        },
    }


def main():
    if not JSON_PATH.exists():
        raise SystemExit(f"{JSON_PATH} não existe — rode coletor_pesquisas.py primeiro")

    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))

    # Remove entries DEMO existentes (idempotência)
    pesquisas = [p for p in data["pesquisas"] if not p.get("is_demo")]

    # Adiciona as 3 demo
    for r in RODADAS:
        pesquisas.append(montar_entry(r))

    # Re-ordena por data_divulgacao desc
    pesquisas.sort(key=lambda p: p.get("data_divulgacao") or "", reverse=True)

    data["pesquisas"]   = pesquisas
    data["n_pesquisas"] = len(pesquisas)
    data["atualizado_em"] = datetime.now(timezone.utc).isoformat(timespec="seconds")

    JSON_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK: {len(pesquisas)} pesquisas no JSON ({sum(1 for p in pesquisas if p.get('is_demo'))} demo)")


if __name__ == "__main__":
    main()
