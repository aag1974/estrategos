"""Cruza despesas (TSE 2022) × votos (outputs_fase0) por candidato no DF.
Exploração inicial: distribuição de gasto por cargo, custo/voto, percentis.
"""
import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DESP = ROOT / "outputs_tse_2022_DF" / "despesas_contratadas_DF.csv"
CAND = ROOT / "outputs_fase0" / "candidatos_2022.csv"

# ── 1. Agrega despesa por candidato (SQ_CANDIDATO é ID estável) ──
gasto_por_sq = defaultdict(float)
meta_por_sq = {}
with DESP.open(encoding="latin-1") as f:
    reader = csv.reader(f, delimiter=";")
    header = next(reader)
    idx = {col.strip('"'): i for i, col in enumerate(header)}
    for row in reader:
        sq = row[idx["SQ_CANDIDATO"]].strip('"')
        nome = row[idx["NM_CANDIDATO"]].strip('"')
        cargo = row[idx["DS_CARGO"]].strip('"')
        partido = row[idx["SG_PARTIDO"]].strip('"')
        nr_cand = row[idx["NR_CANDIDATO"]].strip('"')
        vr = row[idx["VR_DESPESA_CONTRATADA"]].strip('"').replace(",", ".")
        try:
            gasto_por_sq[sq] += float(vr)
        except ValueError:
            continue
        if sq not in meta_por_sq:
            meta_por_sq[sq] = {"nome": nome, "cargo": cargo, "partido": partido, "nr": nr_cand}

print(f"Despesas: {len(gasto_por_sq)} candidatos com prestação no DF (2022)\n")

# ── 2. Soma votos por candidato (matching por NR_VOTAVEL + DS_CARGO) ──
votos_por_chave = defaultdict(int)
with CAND.open(encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row["ANO"] != "2022":
            continue
        chave = (row["NR_VOTAVEL"], row["DS_CARGO"])
        votos_por_chave[chave] += int(row["QT_VOTOS"])

# ── 3. Cruza por NR_CANDIDATO + cargo (DS_CARGO normalizado pra maiúscula) ──
linhas = []
for sq, gasto in gasto_por_sq.items():
    m = meta_por_sq[sq]
    cargo_up = m["cargo"].upper()
    chave = (m["nr"], cargo_up)
    votos = votos_por_chave.get(chave, 0)
    linhas.append({
        "sq": sq, "nome": m["nome"], "cargo": cargo_up, "partido": m["partido"],
        "nr": m["nr"], "gasto": gasto, "votos": votos,
        "custo_voto": (gasto / votos) if votos > 0 else None
    })

# ── 4. Identifica ELEITOS (top N por votos no cargo) ──
# Senado: ciclo alterna 1/3 e 2/3. 2018 elegeu 2 vagas; 2022 elegeu 1; 2026 elegerá 2.
N_VAGAS = {"GOVERNADOR": 1, "SENADOR": 1, "DEPUTADO FEDERAL": 8, "DEPUTADO DISTRITAL": 24}
votos_por_cargo = defaultdict(list)
for l in linhas:
    votos_por_cargo[l["cargo"]].append((l["sq"], l["votos"]))
eleitos_sq = set()
for cargo, lst in votos_por_cargo.items():
    lst.sort(key=lambda x: -x[1])
    n = N_VAGAS.get(cargo, 0)
    eleitos_sq.update(sq for sq, _ in lst[:n])
for l in linhas:
    l["eleito"] = l["sq"] in eleitos_sq

# ── 5. Distribuição por cargo — TODOS vs SÓ ELEITOS ──
import statistics
def stats(sub, label):
    if not sub:
        return None
    gastos = sorted([l["gasto"] for l in sub])
    cv = sorted([l["custo_voto"] for l in sub if l["custo_voto"] is not None])
    p10 = gastos[int(len(gastos)*0.1)] if len(gastos) >= 10 else gastos[0]
    p90 = gastos[int(len(gastos)*0.9)] if len(gastos) >= 10 else gastos[-1]
    return {
        "n": len(sub),
        "min": gastos[0], "p10": p10,
        "med": statistics.median(gastos),
        "media": statistics.mean(gastos),
        "p90": p90, "max": gastos[-1],
        "med_cv": statistics.median(cv) if cv else 0,
    }

print("=" * 130)
print("DISTRIBUIÇÃO DE GASTO POR CARGO — SÓ ELEITOS (régua realista)")
print("=" * 130)
print(f"{'CARGO':<22} {'N':>3} {'mín':>11} {'p10':>11} {'mediana':>11} {'média':>11} {'p90':>11} {'máx':>11} {'R$/voto':>10}")
for cargo in ["GOVERNADOR", "SENADOR", "DEPUTADO FEDERAL", "DEPUTADO DISTRITAL"]:
    sub = [l for l in linhas if l["cargo"] == cargo and l["eleito"]]
    s = stats(sub, "")
    if not s: continue
    print(f"{cargo:<22} {s['n']:>3} R$ {s['min']:>8,.0f} R$ {s['p10']:>8,.0f} R$ {s['med']:>8,.0f} "
          f"R$ {s['media']:>8,.0f} R$ {s['p90']:>8,.0f} R$ {s['max']:>8,.0f} R$ {s['med_cv']:>7,.2f}")

print("\n" + "=" * 130)
print("COMPARATIVO — TODOS vs SÓ ELEITOS (mediana de gasto e R$/voto)")
print("=" * 130)
print(f"{'CARGO':<22} {'N tot':>6} {'med tot':>12} {'R$/v tot':>10} {'N elt':>6} {'med elt':>12} {'R$/v elt':>10} {'gap mediana':>14}")
for cargo in ["GOVERNADOR", "SENADOR", "DEPUTADO FEDERAL", "DEPUTADO DISTRITAL"]:
    todos = [l for l in linhas if l["cargo"] == cargo]
    eleitos = [l for l in linhas if l["cargo"] == cargo and l["eleito"]]
    st = stats(todos, ""); se = stats(eleitos, "")
    if not st or not se: continue
    gap = (se["med"] / st["med"]) if st["med"] else 0
    print(f"{cargo:<22} {st['n']:>6} R$ {st['med']:>8,.0f} R$ {st['med_cv']:>7,.2f} "
          f"{se['n']:>6} R$ {se['med']:>8,.0f} R$ {se['med_cv']:>7,.2f} {gap:>12,.1f}x")

# ── 5. Top 10 maiores gastadores DF ──
print("\n" + "=" * 110)
print("TOP 10 MAIORES GASTOS DECLARADOS — DF 2022")
print("=" * 110)
print(f"{'CARGO':<22} {'CANDIDATO':<35} {'PARTIDO':<6} {'GASTO':>15} {'VOTOS':>9} {'R$/voto':>10}")
for l in sorted(linhas, key=lambda x: -x["gasto"])[:10]:
    cv = f"R$ {l['custo_voto']:>7,.2f}" if l["custo_voto"] else "—"
    print(f"{l['cargo']:<22} {l['nome'][:34]:<35} {l['partido'][:5]:<6} "
          f"R$ {l['gasto']:>11,.0f} {l['votos']:>9,} {cv:>10}")

# ── 6. Batch atual — agora posicionado entre ELEITOS ──
nomes_batch = ["FÁBIO FELIX", "MANZONI", "PAULA MORENO", "ROGÉRIO EDUARDO", "KICIS",
               "RITA DE CÁSSIA FERNANDES", "YARA MARISTELA", "DAMARES", "IBANEIS"]
print("\n" + "=" * 130)
print("BATCH ATUAL — gasto, votos e PERCENTIL ENTRE ELEITOS DO MESMO CARGO")
print("=" * 130)
print(f"{'CARGO':<22} {'CANDIDATO':<32} {'eleito?':>8} {'GASTO':>14} {'VOTOS':>9} {'R$/voto':>10} {'p elt':>8}")
for batch_nome in nomes_batch:
    matches = [l for l in linhas if batch_nome in l["nome"].upper()]
    for l in matches[:1]:
        sub_elt = sorted([x["gasto"] for x in linhas if x["cargo"] == l["cargo"] and x["eleito"]])
        if l["eleito"]:
            rank = sum(1 for g in sub_elt if g <= l["gasto"])
            pct = f"p{rank/len(sub_elt)*100:.0f}"
        else:
            menores = sum(1 for g in sub_elt if g >= l["gasto"])
            pct = f"<elt({menores}/{len(sub_elt)} elt acima)"
        cv = f"R$ {l['custo_voto']:>7,.2f}" if l["custo_voto"] else "—"
        elt = "✓" if l["eleito"] else "—"
        print(f"{l['cargo']:<22} {l['nome'][:31]:<32} {elt:>8} R$ {l['gasto']:>10,.0f} {l['votos']:>9,} {cv:>10} {pct:>8}")
