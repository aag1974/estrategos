"""Perfil de despesas dos ELEITOS DF 2022 — agregado por rubrica.

Agrupa as 40+ categorias finas do TSE (DS_ORIGEM_DESPESA) em ~8 rubricas grandes
e mostra a distribuição % entre os eleitos de cada cargo.
"""
import csv
from collections import defaultdict
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parent
DESP = ROOT / "outputs_tse_2022_DF" / "despesas_contratadas_DF.csv"
CAND = ROOT / "outputs_fase0" / "candidatos_2022.csv"

# ── Mapeamento de categoria fina → rubrica ──
RUBRICAS = {
    # MOBILIZAÇÃO (boca de urna, panfletagem, eventos de rua)
    "Atividades de militância e mobilização de rua": "Mobilização",
    "Comícios": "Mobilização",
    "Eventos de promoção da candidatura": "Mobilização",
    # PESSOAL
    "Despesas com pessoal": "Pessoal",
    "Encargos sociais": "Pessoal",
    # MÍDIA TRADICIONAL (impressos, adesivos, AV)
    "Publicidade por materiais impressos": "Mídia tradicional",
    "Publicidade por adesivos": "Mídia tradicional",
    "Publicidade por jornais e revistas": "Mídia tradicional",
    "Publicidade por carros de som": "Mídia tradicional",
    "Produção de programas de rádio, televisão ou vídeo": "Mídia tradicional",
    "Produção de jingles, vinhetas e slogans": "Mídia tradicional",
    # MÍDIA DIGITAL
    "Despesa com Impulsionamento de Conteúdos": "Mídia digital",
    "Criação e inclusão de páginas na internet": "Mídia digital",
    # OPERACIONAL (logística, deslocamento, alimentação)
    "Alimentação": "Operacional",
    "Combustíveis e lubrificantes": "Operacional",
    "Cessão ou locação de veículos": "Operacional",
    "Despesas com transporte ou deslocamento": "Operacional",
    "Despesas com Hospedagem": "Operacional",
    "Materiais de expediente": "Operacional",
    "Locação/cessão de bens móveis (exceto veículos)": "Operacional",
    "Aquisição/Doação de bens móveis ou imóveis": "Operacional",
    "Correspondências e despesas postais": "Operacional",
    # ESTRUTURA (sede, comitê, contas)
    "Locação/cessão de bens imóveis": "Estrutura",
    "Pré-instalação física de comitê de campanha": "Estrutura",
    "Água": "Estrutura",
    "Energia elétrica": "Estrutura",
    "Telefone": "Estrutura",
    "Despesa com geradores de energia": "Estrutura",
    # SERVIÇOS PROFISSIONAIS
    "Serviços prestados por terceiros": "Serviços profissionais",
    "Serviços próprios prestados por terceiros": "Serviços profissionais",
    "Serviços contábeis": "Serviços profissionais",
    "Serviços advocatícios": "Serviços profissionais",
    # PESQUISA
    "Pesquisas ou testes eleitorais": "Pesquisa",
    # ENCARGOS / OUTROS
    "Encargos financeiros, taxas bancárias e/ou op. cartão de crédito": "Encargos/Outros",
    "Taxa de Administração de Financiamento Coletivo": "Encargos/Outros",
    "Impostos, contribuições e taxas": "Encargos/Outros",
    "Multas eleitorais": "Encargos/Outros",
    "Doações financeiras a outros candidatos/partidos": "Encargos/Outros",
    "Reembolsos de gastos realizados por eleitores": "Encargos/Outros",
    "Diversas a especificar": "Encargos/Outros",
    "#NULO": "Encargos/Outros",
}

ORDEM_RUBRICAS = ["Mobilização", "Pessoal", "Mídia tradicional", "Mídia digital",
                  "Operacional", "Estrutura", "Serviços profissionais", "Pesquisa",
                  "Encargos/Outros"]

N_VAGAS_2022 = {"GOVERNADOR": 1, "SENADOR": 1, "DEPUTADO FEDERAL": 8, "DEPUTADO DISTRITAL": 24}

# ── 1. Lê despesas, agrega por candidato × rubrica ──
gasto_total_sq = defaultdict(float)
gasto_rub_sq = defaultdict(lambda: defaultdict(float))
meta_sq = {}
with DESP.open(encoding="latin-1") as f:
    reader = csv.reader(f, delimiter=";")
    header = next(reader)
    idx = {col.strip('"'): i for i, col in enumerate(header)}
    for row in reader:
        sq = row[idx["SQ_CANDIDATO"]].strip('"')
        cargo = row[idx["DS_CARGO"]].strip('"').upper()
        nome = row[idx["NM_CANDIDATO"]].strip('"')
        nr = row[idx["NR_CANDIDATO"]].strip('"')
        cat = row[idx["DS_ORIGEM_DESPESA"]].strip('"')
        vr = row[idx["VR_DESPESA_CONTRATADA"]].strip('"').replace(",", ".")
        try:
            v = float(vr)
        except ValueError:
            continue
        if v <= 0:
            continue
        rub = RUBRICAS.get(cat, "Encargos/Outros")
        gasto_total_sq[sq] += v
        gasto_rub_sq[sq][rub] += v
        if sq not in meta_sq:
            meta_sq[sq] = {"nome": nome, "cargo": cargo, "nr": nr}

# ── 2. Cruza com votos pra identificar eleitos ──
votos_chave = defaultdict(int)
with CAND.open(encoding="utf-8") as f:
    for row in csv.DictReader(f):
        if row["ANO"] != "2022":
            continue
        votos_chave[(row["NR_VOTAVEL"], row["DS_CARGO"])] += int(row["QT_VOTOS"])

por_cargo = defaultdict(list)
for sq, m in meta_sq.items():
    v = votos_chave.get((m["nr"], m["cargo"]), 0)
    por_cargo[m["cargo"]].append({"sq": sq, "nome": m["nome"], "votos": v,
                                   "gasto": gasto_total_sq[sq]})

eleitos_sq = set()
for cargo, lst in por_cargo.items():
    lst.sort(key=lambda x: -x["votos"])
    n = N_VAGAS_2022.get(cargo, 0)
    eleitos_sq.update(c["sq"] for c in lst[:n])

# ── 3. % por rubrica entre eleitos (mediana e média) ──
print("=" * 110)
print("PERFIL DE DESPESA — % DO TOTAL GASTO ENTRE ELEITOS (DF 2022)")
print("=" * 110)
print(f"{'RUBRICA':<26} {'GOV (n=1)':>11} {'SEN (n=1)':>11} {'FED (n=8)':>22} {'DIS (n=24)':>22}")
print(f"{'':<26} {'':>11} {'':>11} {'med':>10} {'média':>11} {'med':>10} {'média':>11}")
print("-" * 110)

dados_rub = {}
for cargo in ["GOVERNADOR", "SENADOR", "DEPUTADO FEDERAL", "DEPUTADO DISTRITAL"]:
    eleitos_cargo = [sq for sq in eleitos_sq if meta_sq[sq]["cargo"] == cargo]
    pcts_por_rub = defaultdict(list)
    for sq in eleitos_cargo:
        total = gasto_total_sq[sq]
        if total <= 0:
            continue
        for rub in ORDEM_RUBRICAS:
            pct = gasto_rub_sq[sq].get(rub, 0) / total * 100
            pcts_por_rub[rub].append(pct)
    dados_rub[cargo] = pcts_por_rub

for rub in ORDEM_RUBRICAS:
    linha = [rub]
    for cargo, n in [("GOVERNADOR", 1), ("SENADOR", 1)]:
        vals = dados_rub[cargo].get(rub, [])
        v = vals[0] if vals else 0
        linha.append(f"{v:>9.1f}%")
    for cargo, n in [("DEPUTADO FEDERAL", 8), ("DEPUTADO DISTRITAL", 24)]:
        vals = dados_rub[cargo].get(rub, [])
        med = statistics.median(vals) if vals else 0
        media = statistics.mean(vals) if vals else 0
        linha.append(f"{med:>8.1f}%")
        linha.append(f"{media:>9.1f}%")
    print(f"{linha[0]:<26} {linha[1]:>11} {linha[2]:>11} {linha[3]:>10} {linha[4]:>11} {linha[5]:>10} {linha[6]:>11}")

# ── 4. Comparativo eleitos × não-eleitos (Federal e Distrital) ──
print("\n" + "=" * 110)
print("COMPARATIVO ELEITOS × NÃO-ELEITOS — % do gasto por rubrica (mediana)")
print("=" * 110)
print(f"{'RUBRICA':<26} {'FED elt':>10} {'FED ñ-elt':>12} {'Δ FED':>8} {'DIS elt':>10} {'DIS ñ-elt':>12} {'Δ DIS':>8}")
print("-" * 110)

# Recalcula mediana % por rubrica para não-eleitos (com gasto > R$ 1k pra evitar zeros)
def stats_rub(cargo, eleito_filter):
    pcts = defaultdict(list)
    for sq, m in meta_sq.items():
        if m["cargo"] != cargo:
            continue
        if (sq in eleitos_sq) != eleito_filter:
            continue
        if gasto_total_sq[sq] < 1000:  # filtra ruído
            continue
        for rub in ORDEM_RUBRICAS:
            p = gasto_rub_sq[sq].get(rub, 0) / gasto_total_sq[sq] * 100
            pcts[rub].append(p)
    return {r: statistics.median(v) if v else 0 for r, v in pcts.items()}

med_fed_e = stats_rub("DEPUTADO FEDERAL", True)
med_fed_n = stats_rub("DEPUTADO FEDERAL", False)
med_dis_e = stats_rub("DEPUTADO DISTRITAL", True)
med_dis_n = stats_rub("DEPUTADO DISTRITAL", False)

for rub in ORDEM_RUBRICAS:
    fe = med_fed_e[rub]; fn = med_fed_n[rub]
    de = med_dis_e[rub]; dn = med_dis_n[rub]
    delta_f = fe - fn
    delta_d = de - dn
    print(f"{rub:<26} {fe:>9.1f}% {fn:>10.1f}% {delta_f:>+7.1f} {de:>9.1f}% {dn:>10.1f}% {delta_d:>+7.1f}")
