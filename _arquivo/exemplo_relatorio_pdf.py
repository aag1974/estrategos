"""
Exemplo standalone do relatório PDF de um candidato.
Gera relatorio_<NOME>.html — abrir no browser e Cmd+P → Salvar como PDF.

Layout: A4 retrato, uma página, com header/KPIs/zonas/listas/diagnóstico/tabela.
Cores e separadores seguindo o painel do dashboard.
"""
import re, base64, json, math, sys
from pathlib import Path
from datetime import date

DASHBOARD = Path("dashboard_com_candidato.html")
TARGET = sys.argv[1] if len(sys.argv) > 1 else "DAMARES"

# ── Carrega dados ────────────────────────────────────────────────────────────
html_src = DASHBOARD.read_text(encoding="utf-8")
m = re.search(r'const GC_DATA = JSON\.parse\(atob\("([^"]+)"\)\)', html_src)
GC_DATA = json.loads(base64.b64decode(m.group(1)).decode("utf-8"))
m = re.search(r'var D=JSON\.parse\(atob\("([^"]+)"\)\)', html_src)
D = json.loads(base64.b64decode(m.group(1)).decode("utf-8"))

ELEITOS = {
    "GOVERNADOR": ["IBANEIS"],
    "SENADOR": ["DAMARES"],
    "DEPUTADO_FEDERAL": ["BEATRIZ KICIS","DAVYS FREDERICO","ERIKA JUCÁ","RAFAEL CAVALCANTI",
                          "JULIO CESAR RIBEIRO","REGINALDO VERAS","JOÃO ALBERTO FRAGA","GILVAM"],
    "DEPUTADO_DISTRITAL": ["FÁBIO FELIX","FRANCISCO DOMINGOS","MAX MACIEL","DANIEL XAVIER DONIZET",
        "MARTINS MACHADO","ROBÉRIO BANDEIRA","JORGE VIANA DE SOUSA","JAQUELINE ANGELA",
        "THIAGO DE ARAÚJO","EDUARDO WEYNE","JOAQUIM DOMINGOS RORIZ","IOLANDO ALMEIDA",
        "DANIEL DE CASTRO","JOÃO HERMETO","ROOSEVELT VILELA","JANE KLEBIA",
        "BERNARDO ROGÉRIO","GABRIEL MAGNO","JOAO ALVES CARDOSO","PAULA MORENO PARO",
        "RICARDO VALE DA SILVA","WELLINGTON LUIZ","PEDRO PAULO DE OLIVEIRA","DAYSE AMARILIO"]
}
CN = {"progressista":"Progressista","moderado":"Moderado","liberal_conservador":"Liberal/Cons.","outros":"Outros"}
COR_CAMPO = {"progressista":"#A32D2D","moderado":"#0F6E56","liberal_conservador":"#854F0B","outros":"#6B7280"}
BG_CAMPO = {"progressista":"#FCEBEB","moderado":"#E1F5EE","liberal_conservador":"#FAEEDA","outros":"#F1EFE8"}
CARGO_LBL = {"GOVERNADOR":"Governador","SENADOR":"Senador","DEPUTADO_FEDERAL":"Dep. Federal","DEPUTADO_DISTRITAL":"Dep. Distrital"}

# ── Encontra candidato ──────────────────────────────────────────────────────
c = next((c for c in GC_DATA if TARGET.upper() in c["nm"].upper()), None)
if not c:
    print(f"Candidato '{TARGET}' não encontrado.")
    sys.exit(1)

# ── Cálculos ────────────────────────────────────────────────────────────────
def is_eleito(nome, cargo):
    nm = nome.upper()
    return any(i in nm for i in ELEITOS.get(cargo, []))

def tipologia(c):
    deltas = []
    for r in c["ras"]:
        if r.get("idx") is not None:
            deltas.append((r["idx"]-1)*100)
    if len(deltas) < 2: return None
    media = sum(deltas)/len(deltas)
    sigma = math.sqrt(sum((d-media)**2 for d in deltas)/len(deltas))
    if sigma < 30: return ("Distribuído", "background:#E0F2FE;color:#075985")
    if sigma < 60: return ("Híbrido", "background:#FEF3C7;color:#92400E")
    return ("Concentrado", "background:#FCE7F3;color:#9D174D")

def zona_cat(idxC, idxK):
    if idxC is None or idxK is None: return None
    if idxC >= 1.15 and idxK >= 1.15: return "compartilhado"
    if idxC >= 1.15: return "pessoal"
    if idxC < 0.85 and idxK >= 1.15: return "conquistar"
    if idxC < 0.85: return "sem_espaco"
    return "esperado"

ZONA_DEF = {
    "compartilhado": ("Reduto consolidado", "#A7F3C8", "#0B5A2E"),
    "pessoal":       ("Voto pessoal",        "#E0F2FE", "#075985"),
    "esperado":      ("Esperado",            "#FEF3C7", "#B45309"),
    "conquistar":    ("Espaço a conquistar", "#FFE4D6", "#9A3412"),
    "sem_espaco":    ("Sem espaço pelo campo","#FCA5A5", "#5A1010"),
}
ZONA_ORD = ["compartilhado","pessoal","esperado","conquistar","sem_espaco"]

# Augmenta RAs com idxCampo, aptos, zona, e dados PDAD da RA
PDAD_KEYS = ["renda_pc","pct_ab","pct_de","pct_super","pct_sem_fund",
             "pct_serv_fed","pct_privado","el_jov","el_ido","el_fem","el_super"]
ras_z = []
for r in c["ras"]:
    d = D.get(r["ra"], {})
    idx_campo = d.get("votos",{}).get(c["cargo"],{}).get(c["campo"],{}).get("idx")
    aptos = d.get("el_aptos") or 0
    cat = zona_cat(r.get("idx"), idx_campo)
    pdad = {k: d.get(k) for k in PDAD_KEYS}
    ras_z.append({**r, "idxCampo": idx_campo, "aptos": aptos, "zona": cat, "pdad": pdad})

zona_cnt = {k: 0 for k in ZONA_ORD}
for r in ras_z:
    if r["zona"]: zona_cnt[r["zona"]] += 1
zona_total = sum(zona_cnt.values()) or 1

# Ranking
same_cargo = sorted([x for x in GC_DATA if x["cargo"]==c["cargo"]], key=lambda x: -(x.get("total") or 0))
rank = next((i+1 for i,x in enumerate(same_cargo) if x["nm"]==c["nm"]), 0)
eleito = is_eleito(c["nm"], c["cargo"])
tip = tipologia(c)

# Listas
fortes = sorted([r for r in ras_z if r["status"] in ("REDUTO","BASE FORTE")],
                key=lambda r: -(r["votos"] or 0))[:3]
conquistar = sorted([r for r in ras_z if r["zona"]=="conquistar"],
                    key=lambda r: -(r["aptos"] or 0))[:3]

# Canibal
same_cc = [x for x in GC_DATA if x["nm"]!=c["nm"] and x["cargo"]==c["cargo"] and x["campo"]==c["campo"]]
canibal = []
for r in ras_z:
    if r["status"] not in ("REDUTO","BASE FORTE"): continue
    min_v = (r["votos"] or 0) * 0.3
    concs = []
    for o in same_cc:
        ora = next((x for x in o["ras"] if x["ra"]==r["ra"]), None)
        if ora and ora["status"] in ("REDUTO","BASE FORTE") and (ora["votos"] or 0) >= min_v:
            concs.append({"nm": o["nm"], "votos": ora["votos"]})
    if concs:
        concs.sort(key=lambda x: -x["votos"])
        canibal.append({"ra": r["ra"], "votos": r["votos"], "concs": concs})
canibal.sort(key=lambda r: (-len(r["concs"]), -r["votos"]))
canibal = canibal[:3]

# Diagnóstico (mesma lógica do painel)
nC, nP, nQ, nS = zona_cnt["compartilhado"], zona_cnt["pessoal"], zona_cnt["conquistar"], zona_cnt["sem_espaco"]
campo_lbl = CN[c["campo"]]
tip_lbl = tip[0] if tip else None
if tip_lbl and nC >= 5:
    f1 = f"Voto <strong>{tip_lbl}</strong> com base sólida no campo <strong>{campo_lbl}</strong> — {nC} RAs em Reduto consolidado."
elif tip_lbl and nC >= 1:
    f1 = f"Voto <strong>{tip_lbl}</strong> com base modesta no campo <strong>{campo_lbl}</strong> ({nC} RA{'s' if nC>1 else ''} em Reduto consolidado)."
elif tip_lbl:
    f1 = f"Voto <strong>{tip_lbl}</strong> sem RAs de Reduto consolidado — base ainda não consolidada no campo."
else:
    f1 = f"Base com {nC} RAs em Reduto consolidado." if nC>0 else "Sem RAs de Reduto consolidado."
f2 = ""
if nP >= 3:
    f2 = f" Tem {nP} RAs de <strong>voto pessoal</strong> (forte ali sem o campo) — ativo independente da legenda."
elif nP >= 1:
    f2 = f" Tem {nP} RA{'s' if nP>1 else ''} de voto pessoal — voto que segue ele, não o campo."
if nQ >= 3:
    f3 = f" <strong>{nQ} RAs em espaço a conquistar</strong>: campo é forte mas o candidato fica abaixo do esperado — território natural pra crescer numa próxima campanha."
elif nQ >= 1:
    f3 = f" {nQ} RA{'s' if nQ>1 else ''} em espaço a conquistar (campo forte, ele fraco) — janela limitada pra crescer dentro do mesmo campo."
else:
    f3 = " Sem RAs em espaço a conquistar — o candidato já capturou o que existe de força do campo, crescer agora exige ir além da base ideológica."
f4 = f" Em {nS} RAs nem o candidato nem o campo são fortes — terreno improdutivo, fora do mapa de prioridade." if nS >= zona_total*0.4 else ""
diag = f1 + f2 + f3 + f4

# ── Helpers de render ────────────────────────────────────────────────────────
def fmt(v): return f"{v:,}".replace(",", ".")
def fmtK(v):
    if v >= 1000: return f"{v/1000:.1f}".replace(".",",") + "k"
    return fmt(v)
def idx_pct(idx):
    if idx is None: return "—"
    d = round((idx-1)*100)
    return ("+" if d>=0 else "") + str(d) + "%"
def idx_col(idx):
    if idx is None: return "var(--muted)"
    return "#085041" if idx >= 1 else "#791F1F"
def first2(s): return " ".join(s.split()[:2])

# Status badge
ST_BADGE = {
    "REDUTO":     ("Reduto",    "#A7F3C8", "#0B5A2E"),
    "BASE FORTE": ("Base forte", "#DCFCE7", "#15803D"),
    "CAMPO MEDIO":("Esperado",   "#FEF3C7", "#B45309"),
    "CAMPO MÉDIO":("Esperado",   "#FEF3C7", "#B45309"),
    "BASE FRACA": ("Base fraca", "#FEE2E2", "#991B1B"),
    "AUSENCIA":   ("Ausência",  "#FCA5A5", "#5A1010"),
}

# Linha da tabela — Status agora é Zona estratégica (consistência com Mapa estratégico)
def render_tabela_row(r):
    z = r.get("zona")
    if z:
        z_lbl, z_bg, z_col = ZONA_DEF[z]
    else:
        z_lbl, z_bg, z_col = "—", "#F1EFE8", "#6B7280"
    return f"""<tr>
      <td class="ra">{r['ra']}</td>
      <td class="num">{fmt(r['votos'])}</td>
      <td class="num">{r['pct_cargo']:.1f}%</td>
      <td class="num">{r['pct_campo']:.1f}%</td>
      <td class="num" style="color:{idx_col(r.get('idx'))};font-weight:500">{idx_pct(r.get('idx'))}</td>
      <td><span class="st-badge" style="background:{z_bg};color:{z_col}">{z_lbl}</span></td>
    </tr>"""

# Linha da tabela compacta (paisagem) — RA · Votos · Performance · Campo · Zona
def render_tabela_row_full(r):
    z = r.get("zona")
    if z:
        z_lbl, z_bg, z_col = ZONA_DEF[z]
    else:
        z_lbl, z_bg, z_col = "—", "#F1EFE8", "#6B7280"
    return f"""<tr>
      <td class="ra">{r['ra']}</td>
      <td class="num">{fmt(r['votos'])}</td>
      <td class="num" style="color:{idx_col(r.get('idx'))};font-weight:500">{idx_pct(r.get('idx'))}</td>
      <td class="num" style="color:{idx_col(r.get('idxCampo'))};font-weight:500">{idx_pct(r.get('idxCampo'))}</td>
      <td><span class="st-badge" style="background:{z_bg};color:{z_col}">{z_lbl}</span></td>
    </tr>"""

tabela_rows = "\n".join(render_tabela_row_full(r) for r in sorted(ras_z, key=lambda r: -(r["idx"] or 0)))

# ── Perfil do eleitor (PDAD ponderado por votos × média DF ponderada por aptos) ──
def media_ponderada(ras, valor_key, peso_key):
    soma_peso, soma_val = 0, 0
    for r in ras:
        peso = r.get(peso_key) or 0
        v = (r.get("pdad") or {}).get(valor_key) if "pdad" in r else r.get(valor_key)
        if v is not None and peso > 0:
            soma_peso += peso
            soma_val += peso * v
    return soma_val/soma_peso if soma_peso else None

# DF: ponderado pelos aptos de todas as RAs (representa o eleitor médio do DF)
df_baseline = []
for ra_nome, d in D.items():
    if d.get("el_aptos") and not d.get("sem_zona"):
        pdad = {k: d.get(k) for k in PDAD_KEYS}
        df_baseline.append({**pdad, "el_aptos": d["el_aptos"], "ra": ra_nome,
                             "abstencao": d.get("abstencao")})

cand_perfil = {k: media_ponderada(ras_z, k, "votos") for k in PDAD_KEYS}
df_perfil   = {k: media_ponderada(df_baseline, k, "el_aptos") for k in PDAD_KEYS}

# ── DADOS DA PÁGINA 1 (PADRÃO PRA TODOS) ─────────────────────────────────────
def df_wavg(key, weight_key="el_aptos"):
    s, w = 0, 0
    for d in df_baseline:
        v, p = d.get(key), d.get(weight_key)
        if v is not None and p:
            s += v*p; w += p
    return s/w if w else None

# DF KPIs (PDAD)
df_kpis = {
    "renda": df_wavg("renda_pc"),
    "classe_ab": df_wavg("pct_ab"),
    "classe_de": df_wavg("pct_de"),
    "ens_super": df_wavg("pct_super"),
}
# RAs extremas por renda (incluindo sem_zona pra contexto demográfico, mas filtra null)
ras_renda = sorted(
    [(r, D[r].get("renda_pc"), D[r].get("el_aptos")) for r in D if D[r].get("renda_pc") is not None],
    key=lambda x: x[1]
)
ras_mais_ricas = list(reversed(ras_renda))[:3]
ras_mais_pobres = ras_renda[:3]

# Eleitorado KPIs (TSE)
df_aptos_total = sum(d.get("el_aptos") or 0 for d in df_baseline)
df_eleitorado = {
    "aptos_total": df_aptos_total,
    "abstencao": df_wavg("abstencao"),
    "el_fem": df_wavg("el_fem"),
    "el_super": df_wavg("el_super"),
    "el_jov": df_wavg("el_jov"),
    "el_ido": df_wavg("el_ido"),
}
ras_top_aptos = sorted(
    [(r, D[r].get("el_aptos") or 0) for r in D if not D[r].get("sem_zona") and D[r].get("el_aptos")],
    key=lambda x: -x[1]
)[:5]

# Campo político: matriz cargos × campos (% do voto, ponderado por aptos)
CARGOS_ORD = ["GOVERNADOR","SENADOR","DEPUTADO_FEDERAL","DEPUTADO_DISTRITAL"]
CAMPOS_ORD = ["progressista","moderado","liberal_conservador","outros"]
def matriz_campo():
    out = {}
    for cargo in CARGOS_ORD:
        out[cargo] = {}
        for campo in CAMPOS_ORD:
            s, w = 0, 0
            for d in df_baseline:
                ra_nome = d.get("ra")
                pct = D.get(ra_nome,{}).get("votos",{}).get(cargo,{}).get(campo,{}).get("pct")
                ap = d.get("el_aptos")
                if pct is not None and ap:
                    s += pct*ap; w += ap
            out[cargo][campo] = s/w if w else 0
    return out
campo_matrix = matriz_campo()

PERFIL_LBL = {
    "renda_pc":     ("Renda p/capita",          "R$ {:,.0f}"),
    "pct_ab":       ("Classe A/B",              "{:.1f}%"),
    "pct_de":       ("Classe D/E",              "{:.1f}%"),
    "pct_super":    ("Ensino superior",         "{:.1f}%"),
    "pct_sem_fund": ("Sem fundamental",         "{:.1f}%"),
    "pct_serv_fed": ("Serv. federal",           "{:.1f}%"),
    "el_super":     ("Eleitor superior",        "{:.1f}%"),
    "el_jov":       ("Jovens (16-24)",          "{:.1f}%"),
    "el_ido":       ("Idosos (60+)",            "{:.1f}%"),
    "el_fem":       ("Eleitor feminino",        "{:.1f}%"),
}

def fmt_pdad_val(key, v):
    if v is None: return "—"
    fmt_str = PERFIL_LBL[key][1]
    if "{:,.0f}" in fmt_str:
        return ("R$ " + f"{v:,.0f}").replace(",", ".")
    # Percentual: vírgula como separador decimal
    return fmt_str.format(v).replace(".", ",")

# 6 KPIs do perfil pro PDF (escolha curada)
PERFIL_KEYS = ["renda_pc", "pct_ab", "pct_super", "pct_serv_fed", "el_jov", "el_ido"]

def render_perfil_card(key):
    lbl, _ = PERFIL_LBL[key]
    cv, dv = cand_perfil.get(key), df_perfil.get(key)
    cand_str = fmt_pdad_val(key, cv)
    df_str = fmt_pdad_val(key, dv)
    # Cor do valor: verde se maior que DF, vermelho se menor, neutro se ≈
    if cv is None or dv is None:
        val_color = "var(--txt)"
    else:
        d = cv - dv
        if abs(d) < (dv * 0.02 if dv else 0.5):
            val_color = "var(--txt)"
        elif d > 0:
            val_color = "#085041"  # verde
        else:
            val_color = "#791F1F"  # vermelho
    return f"""<div class="perfil-card">
      <div class="perfil-lbl">{lbl}</div>
      <div class="perfil-val" style="color:{val_color}">{cand_str}</div>
      <div class="perfil-ref">DF: {df_str}</div>
    </div>"""

perfil_html = "".join(render_perfil_card(k) for k in PERFIL_KEYS)

# ── Distribuição em faixas de Performance (5 status boxes) ────────────────────
status_cnt = c.get("status_cnt", {})
nReduto = status_cnt.get("REDUTO", 0)
nForte  = status_cnt.get("BASE FORTE", 0)
nMedio  = (status_cnt.get("CAMPO MEDIO", 0)) + (status_cnt.get("CAMPO MÉDIO", 0))
nFraca  = status_cnt.get("BASE FRACA", 0)
nAusen  = status_cnt.get("AUSENCIA", 0)
total_status = nReduto + nForte + nMedio + nFraca + nAusen or 1

faixas = [
    ("Reduto",      nReduto, "#A7F3C8", "#0B5A2E"),
    ("Base forte",  nForte,  "#DCFCE7", "#15803D"),
    ("Esperado",    nMedio,  "#FEF3C7", "#B45309"),
    ("Base fraca",  nFraca,  "#FEE2E2", "#991B1B"),
    ("Ausência",    nAusen,  "#FCA5A5", "#5A1010"),
]
faixas_html = "".join(
    f"""<div class="zona-card" style="background:{bg};color:{col}">
      <div class="zona-num">{n}</div>
      <div class="zona-lbl">{lbl}</div>
      <div class="zona-pct">{round(n/total_status*100)}%</div>
    </div>"""
    for lbl, n, bg, col in faixas
)

# Zonas
zonas_html = ""
for k in ZONA_ORD:
    lbl, bg, col = ZONA_DEF[k]
    n = zona_cnt[k]
    pct = round(n/zona_total*100)
    zonas_html += f"""<div class="zona-card" style="background:{bg};color:{col}">
      <div class="zona-num">{n}</div>
      <div class="zona-lbl">{lbl}</div>
      <div class="zona-pct">{pct}%</div>
    </div>"""

# Listas em 3 cards horizontais (uma linha por categoria)
def card_forte(r):
    z = r.get("zona")
    if z:
        z_lbl, z_bg, z_col = ZONA_DEF[z]
    else:
        z_lbl, z_bg, z_col = "—", "#F1EFE8", "#6B7280"
    return (f"<div class='card-mini'>"
            f"<div class='card-head'>"
              f"<div class='card-ra'>{r['ra']}</div>"
              f"<div class='card-tag' style='background:{z_bg};color:{z_col}'>{z_lbl}</div>"
            f"</div>"
            f"<div class='card-meta'>"
              f"<span style='color:#B45309;font-weight:600'>{fmtK(r['votos'])}</span> votos"
              f" · <span style='color:{idx_col(r.get('idx'))};font-weight:600'>{idx_pct(r.get('idx'))}</span>"
            f"</div>"
            f"</div>")

def card_conquistar(r):
    return (f"<div class='card-mini'>"
            f"<div class='card-head'>"
              f"<div class='card-ra'>{r['ra']}</div>"
              f"<div class='card-tag' style='background:#FFE4D6;color:#9A3412'>A conquistar</div>"
            f"</div>"
            f"<div class='card-meta'>"
              f"<strong>{fmtK(r['aptos'])}</strong> eleitores"
              f" · campo <span style='color:#085041;font-weight:600'>{idx_pct(r.get('idxCampo'))}</span>"
              f" · você <span style='color:#791F1F;font-weight:600'>{idx_pct(r.get('idx'))}</span>"
            f"</div>"
            f"</div>")

# Padding com cards vazios (placeholders) se houver menos de 3 itens
def _padded(items, render_fn, n=3):
    cards = [render_fn(r) for r in items[:n]]
    while len(cards) < n:
        cards.append("<div class='card-mini card-empty'>—</div>")
    return "".join(cards)

fortes_html = (
    _padded(fortes, card_forte) if fortes
    else '<div class="empty-row">Nenhuma RA em Reduto ou Base forte.</div>'
)
conquistar_html = (
    _padded(conquistar, card_conquistar) if conquistar
    else '<div class="empty-row">Sem RAs em "espaço a conquistar" — base do campo já capturada.</div>'
)

# Status badge no topo
st_label_top = "Eleito" if eleito else "Não eleito"
st_bg_top = "#DCFCE7" if eleito else "#FEE2E2"
st_col_top = "#15803D" if eleito else "#991B1B"
campo_cor = COR_CAMPO[c["campo"]]
campo_bg = BG_CAMPO[c["campo"]]
voto_html = f'<span class="hd-tag" style="{tip[1]}">{tip[0]}</span>' if tip else ""

today = date.today().strftime("%d/%m/%Y")

# ── HTML helpers da PÁGINA 1 (padrão) ─────────────────────────────────────────
def _kpi_card(num, lbl, sub=""):
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    return f'<div class="kpi"><div class="kpi-num">{num}</div><div class="kpi-lbl">{lbl}</div>{sub_html}</div>'

# População KPIs
def _fmt_pt2(v): return f"{int(v):,}".replace(",", ".")
def _fmt_pct2(v): return f"{v:.1f}".replace(".", ",") + "%"
pop_kpis = (
    _kpi_card(f"R$ {_fmt_pt2(df_kpis['renda'])}", "Renda média per capita", "(PDAD 2021)") +
    _kpi_card(_fmt_pct2(df_kpis["classe_ab"]), "Classe A/B", "% pop. nas faixas mais altas") +
    _kpi_card(_fmt_pct2(df_kpis["classe_de"]), "Classe D/E", "% pop. nas faixas mais baixas") +
    _kpi_card(_fmt_pct2(df_kpis["ens_super"]), "Ensino superior", "% pop. com graduação")
)

# Mini-tabela renda RAs extremas
def _row_renda(ra, renda, lbl):
    return f"<tr><td class='ra'>{ra}</td><td class='num'>R$ {renda:,.0f}</td><td><span class='st-badge' style='background:{lbl[1]};color:{lbl[2]}'>{lbl[0]}</span></td></tr>".replace(",", ".")
extremas_html = "".join(
    _row_renda(r, v, ("Mais alta", "#DCFCE7", "#15803D"))
    for r, v, _ in ras_mais_ricas[:3]
) + "".join(
    _row_renda(r, v, ("Mais baixa", "#FEE2E2", "#991B1B"))
    for r, v, _ in ras_mais_pobres[:3]
)

# Eleitorado KPIs
def _fmt_pt(v): return f"{int(v):,}".replace(",", ".")
def _fmt_pct(v): return f"{v:.1f}".replace(".", ",") + "%"
elei_kpis = (
    _kpi_card(_fmt_pt(df_eleitorado["aptos_total"]), "Eleitores aptos", "Total no DF (TSE 2022)") +
    _kpi_card(_fmt_pct(df_eleitorado["abstencao"]), "Abstenção média", "(TSE 2022)") +
    _kpi_card(_fmt_pct(df_eleitorado["el_fem"]), "Eleitor feminino", "(TSE 2022)") +
    _kpi_card(_fmt_pct(df_eleitorado["el_super"]), "Com ensino superior", "do eleitorado (TSE 2022)")
)

# Top RAs por aptos
top_aptos_html = "".join(
    f"<tr><td class='ra'>{ra}</td><td class='num'>{fmt(int(ap))}</td><td class='num'>{ap/df_aptos_total*100:.1f}%</td></tr>"
    for ra, ap in ras_top_aptos
)

# Campo político: matriz cargo×campo
CARGOS_LBL = {"GOVERNADOR":"Governador","SENADOR":"Senador","DEPUTADO_FEDERAL":"Dep. Federal","DEPUTADO_DISTRITAL":"Dep. Distrital"}
CAMPO_BG_MAP = {"progressista":"#FCEBEB","moderado":"#E1F5EE","liberal_conservador":"#FAEEDA","outros":"#F1EFE8"}
CAMPO_COR_MAP = {"progressista":"#A32D2D","moderado":"#0F6E56","liberal_conservador":"#854F0B","outros":"#6B7280"}

def _campo_cell(campo, val):
    bg = CAMPO_BG_MAP[campo]
    col = CAMPO_COR_MAP[campo]
    # Maior força = cor mais forte; usar opacidade pela magnitude
    intensity = min(val/60, 1)  # cap em 60% (alta dominância)
    return f"<td class='num campo-cell' style='background:{bg};color:{col};font-weight:{'600' if val>=40 else '500'}'>{val:.0f}%</td>"

matriz_html = "<table class='tbl-matriz'><thead><tr><th></th>"
for campo in CAMPOS_ORD:
    matriz_html += f"<th style='color:{CAMPO_COR_MAP[campo]};text-align:right'>{CN[campo]}</th>"
matriz_html += "</tr></thead><tbody>"
for cargo in CARGOS_ORD:
    matriz_html += f"<tr><td class='cargo-lbl'>{CARGOS_LBL[cargo]}</td>"
    for campo in CAMPOS_ORD:
        matriz_html += _campo_cell(campo, campo_matrix[cargo][campo])
    matriz_html += "</tr>"
matriz_html += "</tbody></table>"

# Narrativa do campo político (composta de fatos)
def dominante(cargo):
    items = sorted(campo_matrix[cargo].items(), key=lambda x: -x[1])
    return items[0]
campo_narr_lines = []
for cargo in CARGOS_ORD:
    domc, domv = dominante(cargo)
    campo_narr_lines.append(f"<strong>{CARGOS_LBL[cargo]}</strong>: <span style='color:{CAMPO_COR_MAP[domc]};font-weight:500'>{CN[domc]}</span> dominante ({domv:.0f}% dos votos válidos)")
campo_narr = " · ".join(campo_narr_lines)

# ── HTML final ───────────────────────────────────────────────────────────────
HTML = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Relatório · {c['nm']} · Estrategos</title>
<style>
@page {{ size: A4 landscape; margin: 8mm 10mm; }}
:root {{
  --bg:#F5F2EC; --s1:#FFFFFF; --s2:#F0EDE6; --bd:rgba(0,0,0,.08); --bd2:rgba(0,0,0,.18);
  --txt:#1A1A1A; --muted:#6B7280; --amber:#B45309;
}}
* {{ box-sizing: border-box; }}
body {{
  font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif;
  font-size: 10pt; color: var(--txt); margin: 0; background: white;
}}
.report {{ width: 100%; max-width: 277mm; margin: 0 auto; }}

/* Header */
.hd {{
  display:flex; align-items:flex-start; gap:14px; padding-bottom:8pt; border-bottom:2pt solid var(--amber);
}}
.hd-logo {{
  flex-shrink:0; width:48pt; height:48pt; background:var(--s2); border-radius:6pt;
  display:flex; align-items:center; justify-content:center; font-size:8pt; color:var(--muted);
}}
.hd-info {{ flex:1; min-width:0 }}
.hd-nome {{ font-size:14pt; font-weight:600; line-height:1.15; margin-bottom:4pt }}
.hd-line {{ display:flex; gap:6pt; flex-wrap:wrap; align-items:center; margin-bottom:3pt; font-size:9pt }}
.hd-tag {{ font-size:8pt; padding:1.5pt 6pt; border-radius:8pt; font-weight:500 }}
.hd-data {{ font-size:8pt; color:var(--muted); white-space:nowrap }}

/* KPIs */
.kpis {{ display:grid; grid-template-columns: repeat(4, 1fr); gap:6pt; margin-top:6pt }}
.kpi {{
  background:var(--s2); border-radius:5pt; padding:6pt 8pt; border-left:2pt solid var(--amber);
}}
.kpi-num {{ font-size:14pt; font-weight:600; color:var(--amber); line-height:1 }}
.kpi-lbl {{ font-size:7.5pt; color:var(--muted); text-transform:uppercase; letter-spacing:.4pt; margin-top:2pt }}
.kpi-sub {{ font-size:6.5pt; color:var(--muted); margin-top:1pt; line-height:1.2 }}

/* Matriz campo político */
.tbl-matriz {{ width:100%; border-collapse:collapse; font-size:9pt }}
.tbl-matriz th {{ padding:4pt 6pt; font-size:7.5pt; font-weight:600; color:var(--muted); text-transform:uppercase; letter-spacing:.4pt }}
.tbl-matriz td {{ padding:5pt 6pt; border-bottom:0.5pt solid var(--bd) }}
.tbl-matriz td.cargo-lbl {{ font-weight:500; font-size:9pt; color:var(--txt) }}
.tbl-matriz td.campo-cell {{ text-align:center; font-family:"SF Mono",Menlo,monospace; min-width:40pt }}

/* Mini tabelas RAs extremas */
.tbl-mini {{ width:100%; border-collapse:collapse; font-size:8.5pt; margin-top:3pt }}
.tbl-mini th {{ background:var(--s2); padding:3pt 6pt; text-align:left; font-size:7pt; color:var(--muted); text-transform:uppercase; letter-spacing:.4pt; font-weight:600 }}
.tbl-mini td {{ padding:3pt 6pt; border-bottom:0.5pt solid var(--bd) }}
.tbl-mini td.ra {{ font-weight:500 }}
.tbl-mini td.num {{ font-family:"SF Mono",Menlo,monospace; text-align:right; font-size:8pt }}

/* Header simples da pg 1 (sem ser do candidato) */
.hd-simple {{
  display:flex; align-items:center; justify-content:space-between; gap:14px;
  padding-bottom:8pt; border-bottom:2pt solid var(--amber); margin-bottom:6pt;
}}
.hd-simple .hd-title {{ font-size:13pt; font-weight:600; color:var(--txt) }}
.hd-simple .hd-sub {{ font-size:9pt; color:var(--muted); margin-top:2pt }}

/* Narrativa de seção (frase contextual) */
.sec-narr {{ font-size:9pt; color:var(--muted); line-height:1.55; margin-bottom:5pt }}
.sec-narr strong {{ color:var(--txt) }}

/* Side-by-side em pg 1 */
.cols-2-eq {{ display:grid; grid-template-columns:1fr 1fr; gap:10pt; align-items:start }}

/* Sec title */
.sec {{ margin-top:7pt }}
.sec-title {{
  font-size:8pt; letter-spacing:1.2pt; text-transform:uppercase; color:var(--amber);
  margin-bottom:3pt; padding-bottom:2pt; border-bottom:0.5pt solid var(--bd2); font-weight:600
}}

/* Mapa estratégico (5 zonas) */
.zonas {{ display:grid; grid-template-columns:repeat(5,1fr); gap:3pt }}
.zona-card {{ border-radius:5pt; padding:5pt 4pt; text-align:center }}
.zona-num {{ font-size:14pt; font-weight:700; line-height:1 }}
.zona-lbl {{ font-size:6.5pt; font-weight:500; line-height:1.2; margin-top:2pt }}
.zona-pct {{ font-size:6.5pt; opacity:.75; margin-top:1pt }}

/* Cards mini — 3 cards horizontais por categoria */
.cards-row {{ display:grid; grid-template-columns:1fr 1fr 1fr; gap:5pt; margin-top:3pt }}
.card-mini {{
  background:var(--s2); border-radius:5pt; padding:5pt 7pt;
  display:flex; flex-direction:column; gap:3pt; min-width:0;
}}
.card-head {{
  display:flex; align-items:center; gap:5pt; min-width:0;
}}
.card-ra {{ font-size:8.5pt; font-weight:500; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; color:var(--txt); flex:1; min-width:0 }}
.card-meta {{ font-size:7.5pt; color:var(--muted); line-height:1.35 }}
.card-tag {{ font-size:6.5pt; padding:1pt 5pt; border-radius:5pt; font-weight:500; white-space:nowrap; flex-shrink:0 }}
.card-empty {{ color:var(--bd2); justify-content:center; align-items:center; text-align:center }}
.empty-row {{ background:var(--s2); border-radius:5pt; padding:7pt 9pt; font-style:italic; color:var(--muted); font-size:8.5pt; margin-top:3pt }}

/* Listas (legado, ainda usado em outras seções) */
.cols-2 {{ display:grid; grid-template-columns:1fr 1fr; gap:8pt }}
.cols-3 {{ display:grid; grid-template-columns:1fr 1fr 1fr; gap:6pt }}
.list-item {{
  background:var(--s2); border-radius:4pt; padding:4pt 6pt;
  display:flex; flex-direction:column; gap:2pt; margin-bottom:3pt;
}}
.list-item .li-ra {{ font-size:8.5pt; font-weight:500; white-space:nowrap; overflow:hidden; text-overflow:ellipsis }}
.list-item .li-meta {{ font-size:7pt; color:var(--muted); line-height:1.3 }}
.list-item .li-tag {{ font-size:6.5pt; padding:1pt 5pt; border-radius:6pt; font-weight:500; white-space:nowrap; align-self:flex-start; margin-top:1pt }}
.empty {{ font-size:8pt; color:var(--muted); font-style:italic; padding:5pt 8pt; background:var(--s2); border-radius:5pt }}

/* Diagnóstico */
.diag {{
  background:var(--s2); padding:6pt 9pt; border-radius:5pt; border-left:2pt solid var(--amber);
  font-size:8.5pt; line-height:1.5; color:#1A1A1A;
}}
.diag strong {{ color:var(--txt) }}

/* Tabela */
.tbl-wrap {{ border:0.5pt solid var(--bd2); border-radius:4pt; overflow:hidden; margin-top:3pt }}
.tbl {{ width:100%; border-collapse:collapse; font-size:7.5pt }}
.tbl th {{
  background:var(--s2); text-align:left; padding:2.5pt 5pt; font-size:6.5pt;
  letter-spacing:.5pt; text-transform:uppercase; color:var(--muted); font-weight:600; border-bottom:0.5pt solid var(--bd2)
}}
.tbl td {{ padding:1.8pt 5pt; border-bottom:0.5pt solid var(--bd) }}
.tbl tr:last-child td {{ border-bottom:none }}
.tbl td.ra {{ font-weight:500; max-width:50mm; white-space:nowrap; overflow:hidden; text-overflow:ellipsis }}
.tbl td.num {{ font-family:"SF Mono",Menlo,monospace; text-align:right; font-size:7pt }}
.st-badge {{ font-size:6.5pt; padding:.5pt 4pt; border-radius:5pt; font-weight:500; white-space:nowrap }}

/* Footer */
.foot {{
  margin-top:8pt; padding-top:5pt; border-top:0.5pt solid var(--bd2);
  font-size:7pt; color:var(--muted); text-align:center; line-height:1.5
}}
.foot strong {{ color:#1A1A1A; font-weight:600 }}

/* Page break entre página 1 e 2 */
.page-2 {{ page-break-before: always; break-before: page; padding-top:0 }}
.page-2 .hd {{ padding-bottom:5pt; gap:10px }}
.page-2 .hd-logo {{ width:36pt; height:36pt }}
.page-2 .hd-nome {{ font-size:12pt; margin-bottom:2pt }}
.page-2 .hd-line {{ margin-bottom:2pt }}

/* Layout paisagem: 2 colunas (análise esquerda, tabela direita) */
.layout-2col {{ display:grid; grid-template-columns:1.15fr 1fr; gap:14pt; margin-top:6pt }}
.layout-left {{ min-width:0 }}
.layout-right {{ min-width:0 }}

/* Perfil cards (paisagem: 3 colunas, 2 linhas — coluna esquerda é estreita) */
.perfil-grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:4pt }}
.perfil-card {{
  background:var(--s2); border-radius:5pt; padding:6pt 7pt; border-left:2pt solid var(--amber);
  display:flex; flex-direction:column; gap:3pt;
}}
.perfil-lbl {{
  font-size:6.5pt; color:var(--muted); text-transform:uppercase; letter-spacing:.3pt;
  line-height:1.2; font-weight:600; white-space:nowrap;
}}
.perfil-val {{
  font-size:12pt; font-weight:700; line-height:1;
}}
.perfil-ref {{ font-size:6.5pt; color:var(--muted); line-height:1.2 }}

@media print {{
  body {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
  .page-2 {{ page-break-before: always; }}
}}

/* Visual screen: separa as duas páginas pra ver no browser */
@media screen {{
  .page-2 {{ margin-top:20mm; padding-top:20mm; border-top:1pt dashed var(--bd2) }}
}}
</style>
</head>
<body>
<div class="report">

  <!-- ═══════════════════════ PAPER ÚNICO — CANDIDATO ═══════════════════════ -->
  <div class="page-2" style="page-break-before:auto;break-before:auto">

    <!-- HEADER DO CANDIDATO -->
    <div class="hd">
      <div class="hd-logo">opinião</div>
      <div class="hd-info">
        <div class="hd-nome">{c['nm']}</div>
        <div class="hd-line">
          <span class="hd-tag" style="background:{st_bg_top};color:{st_col_top};font-weight:600">{st_label_top}</span>
          <span style="font-size:9pt;color:var(--muted)">· {rank}º mais votado · {CARGO_LBL[c['cargo']]} · <strong style="color:#B45309">{fmt(c['total'])}</strong> votos</span>
        </div>
        <div class="hd-line">
          <span class="hd-tag" style="background:{campo_bg};color:{campo_cor}">{campo_lbl}</span>
          {voto_html}
          <span style="font-size:9pt;color:var(--muted)">· {c['partido']}</span>
        </div>
      </div>
      <div class="hd-data">Diagnóstico estratégico</div>
    </div>

    <!-- LAYOUT 2 COLUNAS: análise (esq) + tabela (dir) -->
    <div class="layout-2col">
      <div class="layout-left">
        <!-- ONDE JÁ É FORTE -->
        <div class="sec">
          <div class="sec-title">Onde já é forte</div>
          <div class="cards-row">{fortes_html}</div>
        </div>

        <!-- ONDE DÁ PRA CRESCER -->
        <div class="sec">
          <div class="sec-title">Onde dá pra crescer</div>
          <div class="cards-row">{conquistar_html}</div>
        </div>

        <!-- DIAGNÓSTICO -->
        <div class="sec">
          <div class="sec-title">Diagnóstico</div>
          <div class="diag">{diag}</div>
        </div>

        <!-- PERFIL DO ELEITOR -->
        <div class="sec">
          <div class="sec-title">Perfil Médio do Eleitor do Candidato (Estimado)</div>
          <div class="perfil-grid">{perfil_html}</div>
        </div>
      </div>

      <div class="layout-right">
        <!-- TABELA COMPLETA POR RA -->
        <div class="sec" style="margin-top:0">
          <div class="sec-title">Desempenho por RA</div>
          <div class="tbl-wrap"><table class="tbl">
            <thead><tr>
              <th>RA</th>
              <th style="text-align:right">Votos</th>
              <th style="text-align:right">Perf.</th>
              <th style="text-align:right">Campo</th>
              <th>Zona</th>
            </tr></thead>
            <tbody>{tabela_rows}</tbody>
          </table></div>
        </div>
      </div>
    </div>

    <!-- FOOTER FINAL -->
    <div class="foot">
      Página 2 de 2 — Diagnóstico do candidato · <strong>Estrategos</strong> — Inteligência Política da <strong>Opinião Informação Estratégica</strong>
    </div>

  </div>

</div>
</body>
</html>"""

out = Path(f"relatorio_{TARGET.upper().replace(' ','_')}.html")
out.write_text(HTML, encoding="utf-8")
print(f"✅ Gerado: {out}")
print(f"   Abra no browser e Cmd+P → Salvar como PDF")
