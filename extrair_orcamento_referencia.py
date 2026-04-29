"""Pré-extrai estatísticas de orçamento de campanha do TSE 2022 (DF).

Output: outputs_tse_2022_DF/orcamento_referencia.json
Contém:
- Por cargo: mediana, mínimo eleito, p10, p90 de gasto entre os ELEITOS
- Por candidato (NOME normalizado + cargo): gasto declarado total
- Limites legais 2022 (tabela TSE)
"""
import csv
import json
import unicodedata
from collections import defaultdict
from pathlib import Path
import statistics

def _norm(s):
    s = unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode()
    return s.upper().strip()

ROOT = Path(__file__).resolve().parent
DESP = ROOT / "outputs_tse_2022_DF" / "despesas_contratadas_DF.csv"
CAND = ROOT / "outputs_fase0" / "candidatos_2022.csv"
OUT = ROOT / "outputs_tse_2022_DF" / "orcamento_referencia.json"

# Senado 2022 = ciclo 1/3 → 1 vaga por estado
N_VAGAS_2022 = {"GOVERNADOR": 1, "SENADOR": 1, "DEPUTADO FEDERAL": 8, "DEPUTADO DISTRITAL": 24}

# Limites legais TSE 2022 (DF, 1º turno)
LIMITE_LEGAL_2022 = {
    "GOVERNADOR": 7_000_000,
    "SENADOR": 3_780_000,
    "DEPUTADO FEDERAL": 3_176_573,
    "DEPUTADO DISTRITAL": 1_260_000,
}

# 1. Despesa por candidato
gasto_por_sq = defaultdict(float)
meta_por_sq = {}
with DESP.open(encoding="latin-1") as f:
    reader = csv.reader(f, delimiter=";")
    header = [c.strip('"') for c in next(reader)]
    idx = {c: i for i, c in enumerate(header)}
    for row in reader:
        sq = row[idx["SQ_CANDIDATO"]].strip('"')
        cargo = row[idx["DS_CARGO"]].strip('"').upper()
        nome = row[idx["NM_CANDIDATO"]].strip('"')
        nr = row[idx["NR_CANDIDATO"]].strip('"')
        try:
            v = float(row[idx["VR_DESPESA_CONTRATADA"]].strip('"').replace(",", "."))
        except ValueError:
            continue
        if v <= 0:
            continue
        gasto_por_sq[sq] += v
        if sq not in meta_por_sq:
            meta_por_sq[sq] = {"nome": nome, "cargo": cargo, "nr": nr}

# 2. Votos por candidato
votos_chave = defaultdict(int)
with CAND.open(encoding="utf-8") as f:
    for row in csv.DictReader(f):
        if row["ANO"] != "2022":
            continue
        votos_chave[(row["NR_VOTAVEL"], row["DS_CARGO"])] += int(row["QT_VOTOS"])

# 3. Identifica eleitos (top N por votos por cargo)
por_cargo = defaultdict(list)
for sq, m in meta_por_sq.items():
    v = votos_chave.get((m["nr"], m["cargo"]), 0)
    por_cargo[m["cargo"]].append({"sq": sq, "nr": m["nr"], "nome": m["nome"],
                                   "votos": v, "gasto": gasto_por_sq[sq]})
eleitos_sq = set()
for cargo, lst in por_cargo.items():
    lst.sort(key=lambda x: -x["votos"])
    n = N_VAGAS_2022.get(cargo, 0)
    eleitos_sq.update(c["sq"] for c in lst[:n])

# 4. Stats por cargo (entre eleitos): GASTO + VOTOS
def stats_cargo(cargo):
    eleitos_cargo = [sq for sq in eleitos_sq if meta_por_sq[sq]["cargo"] == cargo]
    if not eleitos_cargo:
        return None
    gastos = sorted([gasto_por_sq[sq] for sq in eleitos_cargo])
    votos = sorted([votos_chave.get((meta_por_sq[sq]["nr"], cargo), 0) for sq in eleitos_cargo])
    n = len(eleitos_cargo)
    return {
        "n_eleitos": n,
        # GASTO
        "min": gastos[0],
        "p10": gastos[max(0, int(n * 0.1) - 1)] if n >= 10 else gastos[0],
        "mediana": statistics.median(gastos),
        "p90": gastos[min(n - 1, int(n * 0.9))] if n >= 10 else gastos[-1],
        "max": gastos[-1],
        "valores": gastos,
        # VOTOS — referências para projeção de cenários simulados
        "votos_min": votos[0],
        "votos_mediana": int(statistics.median(votos)),
        "votos_lider": votos[-1],
    }

referencia = {
    "ano_base": 2022,
    "uf": "DF",
    "limite_legal": LIMITE_LEGAL_2022,
    "stats_eleitos": {c: stats_cargo(c) for c in N_VAGAS_2022},
    "gasto_por_candidato": {},  # chave: NR + "|" + cargo
}

# 5. Gasto histórico por candidato (chave: NOME normalizado | cargo)
for sq, m in meta_por_sq.items():
    chave = f"{_norm(m['nome'])}|{m['cargo']}"
    referencia["gasto_por_candidato"][chave] = referencia["gasto_por_candidato"].get(chave, 0) + gasto_por_sq[sq]

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(referencia, indent=2, ensure_ascii=False))
print(f"OK → {OUT}")
print(f"   Cargos: {list(N_VAGAS_2022.keys())}")
for c in N_VAGAS_2022:
    s = referencia["stats_eleitos"][c]
    print(f"   {c}: {s['n_eleitos']} eleitos · mediana R$ {s['mediana']:,.0f} · "
          f"p10 R$ {s['p10']:,.0f} · p90 R$ {s['p90']:,.0f}")
print(f"   Total candidatos: {len(referencia['gasto_por_candidato'])}")
