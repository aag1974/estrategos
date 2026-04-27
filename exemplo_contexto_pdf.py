"""
Paper de Contexto Territorial do DF — A4 paisagem, página única.
Padrão pra qualquer candidato: É o panorama do DF (PDAD 2021 + TSE 2022).

Uso: python3 exemplo_contexto_pdf.py
Saída: relatorio_contexto_DF.html
Abrir no browser, Cmd+P → Salvar como PDF (paisagem).
"""
import re, base64, json
from pathlib import Path
from datetime import date

DASHBOARD = Path("dashboard_com_candidato.html")

# ── Carrega dados ────────────────────────────────────────────────────────────
html_src = DASHBOARD.read_text(encoding="utf-8")
m = re.search(r'var D=JSON\.parse\(atob\("([^"]+)"\)\)', html_src)
D = json.loads(base64.b64decode(m.group(1)).decode("utf-8"))

CN = {"progressista":"Progressista","moderado":"Moderado","liberal_conservador":"Liberal/Cons.","outros":"Outros"}
CARGOS_ORD = ["GOVERNADOR","SENADOR","DEPUTADO_FEDERAL","DEPUTADO_DISTRITAL"]
CAMPOS_ORD = ["progressista","moderado","liberal_conservador","outros"]
CARGOS_LBL = {"GOVERNADOR":"Governador","SENADOR":"Senador","DEPUTADO_FEDERAL":"Dep. Federal","DEPUTADO_DISTRITAL":"Dep. Distrital"}
CAMPO_BG_MAP = {"progressista":"#FCEBEB","moderado":"#E1F5EE","liberal_conservador":"#FAEEDA","outros":"#F1EFE8"}
CAMPO_COR_MAP = {"progressista":"#A32D2D","moderado":"#0F6E56","liberal_conservador":"#854F0B","outros":"#6B7280"}

# ── Cálculos DF ──────────────────────────────────────────────────────────────
PDAD_KEYS = ["renda_pc","pct_ab","pct_de","pct_super","pct_sem_fund","pct_serv_fed","el_jov","el_ido","el_fem","el_super","abstencao"]

df_baseline = []
for ra_nome, d in D.items():
    if d.get("el_aptos") and not d.get("sem_zona"):
        pdad = {k: d.get(k) for k in PDAD_KEYS}
        df_baseline.append({**pdad, "el_aptos": d["el_aptos"], "ra": ra_nome})

def df_wavg(key, weight_key="el_aptos"):
    s, w = 0, 0
    for d in df_baseline:
        v, p = d.get(key), d.get(weight_key)
        if v is not None and p:
            s += v*p; w += p
    return s/w if w else None

df_kpis = {
    "renda": df_wavg("renda_pc"),
    "classe_ab": df_wavg("pct_ab"),
    "classe_de": df_wavg("pct_de"),
    "ens_super": df_wavg("pct_super"),
}
ras_renda = sorted(
    [(r, D[r].get("renda_pc"), D[r].get("el_aptos")) for r in D if D[r].get("renda_pc") is not None],
    key=lambda x: x[1]
)
ras_mais_ricas = list(reversed(ras_renda))[:3]
ras_mais_pobres = ras_renda[:3]

df_aptos_total = sum(d.get("el_aptos") or 0 for d in df_baseline)
df_eleitorado = {
    "aptos_total": df_aptos_total,
    "abstencao": df_wavg("abstencao"),
    "el_fem": df_wavg("el_fem"),
    "el_super": df_wavg("el_super"),
}
ras_top_aptos = sorted(
    [(r, D[r].get("el_aptos") or 0) for r in D if not D[r].get("sem_zona") and D[r].get("el_aptos")],
    key=lambda x: -x[1]
)[:5]

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

# ── Helpers de formatação ────────────────────────────────────────────────────
def fmt(v): return f"{int(v):,}".replace(",", ".")
def fmt_pct(v): return f"{v:.1f}".replace(".", ",") + "%"

def _kpi_card(num, lbl, sub=""):
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    return f'<div class="kpi"><div class="kpi-num">{num}</div><div class="kpi-lbl">{lbl}</div>{sub_html}</div>'

# Pop KPIs
pop_kpis = (
    _kpi_card(f"R$ {fmt(df_kpis['renda'])}", "Renda p/capita", "(PDAD 2021)") +
    _kpi_card(fmt_pct(df_kpis["classe_ab"]), "Classe A/B", "% pop. faixas mais altas") +
    _kpi_card(fmt_pct(df_kpis["classe_de"]), "Classe D/E", "% pop. faixas mais baixas") +
    _kpi_card(fmt_pct(df_kpis["ens_super"]), "Ensino superior", "% pop. com graduação")
)

# Eleitorado KPIs
elei_kpis = (
    _kpi_card(fmt(df_eleitorado["aptos_total"]), "Eleitores aptos", "Total no DF (TSE 2022)") +
    _kpi_card(fmt_pct(df_eleitorado["abstencao"]), "Abstenção média", "(TSE 2022)") +
    _kpi_card(fmt_pct(df_eleitorado["el_fem"]), "Eleitor feminino", "(TSE 2022)") +
    _kpi_card(fmt_pct(df_eleitorado["el_super"]), "Com ensino superior", "do eleitorado")
)

# Mini-tabelas
def _row_renda(ra, renda, lbl):
    return f"<tr><td class='ra'>{ra}</td><td class='num'>R$ {fmt(renda)}</td><td><span class='st-badge' style='background:{lbl[1]};color:{lbl[2]}'>{lbl[0]}</span></td></tr>"
extremas_html = "".join(
    _row_renda(r, v, ("Mais alta", "#DCFCE7", "#15803D"))
    for r, v, _ in ras_mais_ricas[:3]
) + "".join(
    _row_renda(r, v, ("Mais baixa", "#FEE2E2", "#991B1B"))
    for r, v, _ in ras_mais_pobres[:3]
)

top_aptos_html = "".join(
    f"<tr><td class='ra'>{ra}</td><td class='num'>{fmt(int(ap))}</td><td class='num'>{ap/df_aptos_total*100:.1f}%</td></tr>".replace(".", ",")
    for ra, ap in ras_top_aptos
)

# Matriz campo político
def _campo_cell(campo, val):
    bg = CAMPO_BG_MAP[campo]
    col = CAMPO_COR_MAP[campo]
    return f"<td class='num campo-cell' style='background:{bg};color:{col};font-weight:{'600' if val>=40 else '500'}'>{val:.0f}%</td>"

matriz_html = "<table class='tbl-matriz'><thead><tr><th></th>"
for campo in CAMPOS_ORD:
    matriz_html += f"<th style='color:{CAMPO_COR_MAP[campo]};text-align:center'>{CN[campo]}</th>"
matriz_html += "</tr></thead><tbody>"
for cargo in CARGOS_ORD:
    matriz_html += f"<tr><td class='cargo-lbl'>{CARGOS_LBL[cargo]}</td>"
    for campo in CAMPOS_ORD:
        matriz_html += _campo_cell(campo, campo_matrix[cargo][campo])
    matriz_html += "</tr>"
matriz_html += "</tbody></table>"

def dominante(cargo):
    items = sorted(campo_matrix[cargo].items(), key=lambda x: -x[1])
    return items[0]
campo_narr_lines = []
for cargo in CARGOS_ORD:
    domc, domv = dominante(cargo)
    campo_narr_lines.append(f"<strong>{CARGOS_LBL[cargo]}</strong>: <span style='color:{CAMPO_COR_MAP[domc]};font-weight:500'>{CN[domc]}</span> dominante ({domv:.0f}%)")
campo_narr = " · ".join(campo_narr_lines)

today = date.today().strftime("%d/%m/%Y")

# ── HTML ─────────────────────────────────────────────────────────────────────
HTML = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Contexto territorial · Distrito Federal · Estrategos</title>
<style>
@page {{ size: A4 landscape; margin: 8mm 10mm; }}
:root {{
  --bg:#F5F2EC; --s1:#FFFFFF; --s2:#F0EDE6; --bd:rgba(0,0,0,.08); --bd2:rgba(0,0,0,.18);
  --txt:#1A1A1A; --muted:#6B7280; --amber:#B45309;
}}
* {{ box-sizing:border-box }}
body {{
  font-family:-apple-system,BlinkMacSystemFont,"Helvetica Neue",Arial,sans-serif;
  font-size:10pt; color:var(--txt); margin:0; background:white;
}}
.report {{ width:100%; max-width:277mm; margin:0 auto }}

/* Header */
.hd {{ display:flex; align-items:flex-start; gap:14px; padding-bottom:8pt; border-bottom:2pt solid var(--amber); margin-bottom:8pt }}
.hd-logo {{ flex-shrink:0; width:40pt; height:40pt; background:var(--s2); border-radius:6pt; display:flex; align-items:center; justify-content:center; font-size:8pt; color:var(--muted) }}
.hd-info {{ flex:1; min-width:0 }}
.hd-title {{ font-size:14pt; font-weight:600; line-height:1.15; margin-bottom:3pt }}
.hd-sub {{ font-size:9pt; color:var(--muted) }}
.hd-data {{ font-size:8pt; color:var(--muted); white-space:nowrap }}

/* Layout 2 cols + 1 full */
.row-2 {{ display:grid; grid-template-columns:1fr 1fr; gap:14pt; margin-bottom:7pt }}
.col {{ min-width:0 }}

.sec-title {{
  font-size:8pt; letter-spacing:1.2pt; text-transform:uppercase; color:var(--amber);
  margin-bottom:3pt; padding-bottom:2pt; border-bottom:0.5pt solid var(--bd2); font-weight:600;
}}
.sec-narr {{ font-size:8.5pt; color:var(--muted); line-height:1.55; margin-bottom:5pt }}
.sec-narr strong {{ color:var(--txt) }}

/* KPIs */
.kpis {{ display:grid; grid-template-columns:repeat(4,1fr); gap:5pt; margin-bottom:5pt }}
.kpi {{ background:var(--s2); border-radius:5pt; padding:6pt 7pt; border-left:2pt solid var(--amber) }}
.kpi-num {{ font-size:13pt; font-weight:600; color:var(--amber); line-height:1 }}
.kpi-lbl {{ font-size:7pt; color:var(--muted); text-transform:uppercase; letter-spacing:.4pt; margin-top:2pt; font-weight:600 }}
.kpi-sub {{ font-size:6.5pt; color:var(--muted); margin-top:1pt; line-height:1.2 }}

/* Mini tabelas */
.tbl-mini {{ width:100%; border-collapse:collapse; font-size:8.5pt; margin-top:3pt }}
.tbl-mini th {{ background:var(--s2); padding:3pt 6pt; text-align:left; font-size:7pt; color:var(--muted); text-transform:uppercase; letter-spacing:.4pt; font-weight:600 }}
.tbl-mini td {{ padding:3pt 6pt; border-bottom:0.5pt solid var(--bd) }}
.tbl-mini td.ra {{ font-weight:500 }}
.tbl-mini td.num {{ font-family:"SF Mono",Menlo,monospace; text-align:right; font-size:8pt }}
.st-badge {{ font-size:7pt; padding:1pt 5pt; border-radius:6pt; font-weight:500; white-space:nowrap }}

/* Matriz campo político */
.tbl-matriz {{ width:100%; border-collapse:collapse; font-size:9.5pt }}
.tbl-matriz th {{ padding:4pt 6pt; font-size:7.5pt; font-weight:600; color:var(--muted); text-transform:uppercase; letter-spacing:.4pt }}
.tbl-matriz td {{ padding:5pt 6pt; border-bottom:0.5pt solid var(--bd) }}
.tbl-matriz td.cargo-lbl {{ font-weight:500; font-size:9pt; color:var(--txt) }}
.tbl-matriz td.campo-cell {{ text-align:center; font-family:"SF Mono",Menlo,monospace; min-width:40pt }}

/* Footer */
.foot {{
  margin-top:8pt; padding-top:5pt; border-top:0.5pt solid var(--bd2);
  font-size:7pt; color:var(--muted); text-align:center; line-height:1.5
}}
.foot strong {{ color:#1A1A1A; font-weight:600 }}

@media print {{
  body {{ -webkit-print-color-adjust:exact; print-color-adjust:exact }}
}}
</style>
</head>
<body>
<div class="report">

  <!-- HEADER -->
  <div class="hd">
    <div class="hd-logo">opinião</div>
    <div class="hd-info">
      <div class="hd-title">Distrito Federal · Panorama territorial</div>
      <div class="hd-sub">Contexto demográfico, eleitoral e político — base PDAD 2021 e TSE 2022</div>
    </div>
    <div class="hd-data">{today}</div>
  </div>

  <!-- LINHA 1: POPULAÇÃO + ELEITORADO LADO A LADO -->
  <div class="row-2">
    <div class="col">
      <div class="sec-title">População (PDAD 2021)</div>
      <div class="sec-narr">DF tem <strong>33 regiões administrativas</strong> com altíssima desigualdade interna — renda per capita varia em ordem de grandeza entre RAs ricas (Plano Piloto, Lago Sul) e periferias.</div>
      <div class="kpis">{pop_kpis}</div>
      <table class="tbl-mini">
        <thead><tr><th>RA</th><th style="text-align:right">Renda p/capita</th><th>Faixa</th></tr></thead>
        <tbody>{extremas_html}</tbody>
      </table>
    </div>
    <div class="col">
      <div class="sec-title">Eleitorado (TSE 2022)</div>
      <div class="sec-narr"><strong>{fmt(int(df_eleitorado['aptos_total']))}</strong> eleitores aptos distribuídos entre as RAs com zona TSE. Volume eleitoral concentrado nas RAs populosas — Ceilândia sozinha vale mais de 200 mil eleitores.</div>
      <div class="kpis">{elei_kpis}</div>
      <table class="tbl-mini">
        <thead><tr><th>Top 5 RAs por eleitorado</th><th style="text-align:right">Aptos</th><th style="text-align:right">% do DF</th></tr></thead>
        <tbody>{top_aptos_html}</tbody>
      </table>
    </div>
  </div>

  <!-- LINHA 2: CAMPO POLÍTICO FULL-WIDTH -->
  <div>
    <div class="sec-title">Campo político (TSE 2022)</div>
    <div class="sec-narr">% do voto válido por campo em cada cargo, ponderado pelo eleitorado das RAs. {campo_narr}.</div>
    {matriz_html}
  </div>

  <!-- FOOTER -->
  <div class="foot">
    Fontes: <strong>PDAD 2021</strong> (IPEDF) · <strong>TSE 2022</strong>.
    Instrumento gerado pelo painel <strong>Estrategos</strong> — solução de Inteligência Política da <strong>Opinião Informação Estratégica</strong>.
  </div>

</div>
</body>
</html>"""

out = Path("relatorio_contexto_DF.html")
out.write_text(HTML, encoding="utf-8")
print(f"✅ Gerado: {out}")
print(f"   Abra no browser e Cmd+P → Salvar como PDF (paisagem)")
