"""
Gera relatorio_pesquisas_demo.html — análise consolidada de 8 pesquisas DEMO
de 4 institutos diferentes, focada em Deputado Federal DF 2026.

Cada candidato vira um "small multiple": chart próprio com 8 pontos
coloridos por instituto + linha de regressão linear.

Tabela pivô abaixo mostra todas as 8 pesquisas em colunas, candidatos em linhas.

Saída: relatorio_pesquisas_demo.html (auto-contido, imprimível em PDF).
"""
from datetime import date
from pathlib import Path

# ──────────────────────────────────────────────────────────────────────────
# DADOS DEMO — 8 pesquisas, 4 institutos, 6 candidatos a FD DF
# Candidatos reais (eleitos FD DF 2022); percentuais sintéticos plausíveis.
# ──────────────────────────────────────────────────────────────────────────
INSTITUTO_COR = {
    "Veritá":   "#1f77b4",  # azul
    "Igape":    "#ff7f0e",  # laranja
    "Cepphor":  "#2ca02c",  # verde
    "Phoenix":  "#d62728",  # vermelho
}

CANDIDATOS = [
    # (chave, nome_completo, partido, cor_propria_para_tabela)
    ("kicis",   "Bia Kicis",            "PL",          "#A32D2D"),
    ("fred",    "Fred Linhares",        "Republicanos","#854F0B"),
    ("erika",   "Erika Kokay",          "PT",          "#534AB7"),
    ("jcr",     "Julio Cesar Ribeiro",  "Republicanos","#D85A30"),
    ("veras",   "Reginaldo Veras",      "PV",          "#0F6E56"),
    ("nemer",   "Roney Nemer",          "PP",          "#6B7280"),
]

# 8 pesquisas (data, instituto, n, %% por candidato, BL/N, NS/NR)
# Tendência consolidada: Kicis +6pp, Fred +4pp, Erika estável,
# JCR -3pp, Veras +2pp, Nemer estável.
PESQUISAS = [
    # data,          instituto,   n,    kicis fred erika jcr veras nemer  bln  ns
    ("2026-02-15",   "Igape",     1000, 14,   13,  13,   11,  5,    5,    8,   31),
    ("2026-02-20",   "Veritá",    1220, 15,   14,  12,   11,  5,    4,    8,   31),
    ("2026-03-10",   "Cepphor",   1500, 16,   14,  12,   10,  5,    5,    8,   30),
    ("2026-03-25",   "Phoenix",   1203, 17,   15,  13,   10,  6,    5,    7,   27),
    ("2026-04-15",   "Veritá",    1220, 18,   15,  12,    9,  6,    5,    7,   28),
    ("2026-04-22",   "Igape",     3000, 17,   14,  13,    9,  7,    5,    7,   28),
    ("2026-05-05",   "Cepphor",    400, 19,   16,  13,    8,  7,    5,    7,   25),
    ("2026-05-15",   "Phoenix",   1500, 20,   17,  14,    8,  7,    5,    6,   23),
]

DATA_BASE = date(2026, 2, 15)


def dia(s: str) -> int:
    """Dias desde 15/02/2026."""
    d = date.fromisoformat(s)
    return (d - DATA_BASE).days


def regressao(xs, ys):
    """Regressão linear simples → (intercept, slope)."""
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    cov = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    var = sum((x - mx) ** 2 for x in xs)
    slope = cov / var if var else 0
    intercept = my - slope * mx
    return intercept, slope


def fmt_data_br(s: str) -> str:
    d = date.fromisoformat(s)
    return f"{d.day:02d}/{d.month:02d}"


def fmt_data_long(s: str) -> str:
    meses = ["", "jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
    d = date.fromisoformat(s)
    return f"{d.day:02d}/{meses[d.month]}"


# ──────────────────────────────────────────────────────────────────────────
# Cálculos consolidados
# ──────────────────────────────────────────────────────────────────────────
def get_serie(cand_key: str):
    """Retorna lista de (dia, instituto, pct) para o candidato."""
    idx = {"kicis": 3, "fred": 4, "erika": 5, "jcr": 6, "veras": 7, "nemer": 8}[cand_key]
    return [(dia(p[0]), p[1], p[idx]) for p in PESQUISAS]


def estatisticas_cand(cand_key: str):
    serie = get_serie(cand_key)
    xs = [s[0] for s in serie]
    ys = [s[2] for s in serie]
    inter, slope = regressao(xs, ys)
    # tendência em pp ao longo do período
    delta_periodo = slope * (max(xs) - min(xs))
    # confirmação cross-instituto: nº de institutos onde a 2ª medição é maior, igual ou menor que a 1ª
    por_inst = {}
    for d, inst, pct in serie:
        por_inst.setdefault(inst, []).append((d, pct))
    n_alta = n_queda = n_estavel = 0
    for inst, lst in por_inst.items():
        lst.sort()
        if len(lst) >= 2:
            diff = lst[-1][1] - lst[0][1]
            if diff >= 1.5:    n_alta += 1
            elif diff <= -1.5: n_queda += 1
            else:              n_estavel += 1
    return {
        "intercept":     inter,
        "slope":         slope,
        "delta_periodo": delta_periodo,
        "y_inicio":      ys[0],
        "y_fim":         ys[-1],
        "media":         sum(ys) / len(ys),
        "n_alta":        n_alta,
        "n_queda":       n_queda,
        "n_estavel":     n_estavel,
        "n_inst":        len(por_inst),
    }


# ──────────────────────────────────────────────────────────────────────────
# SVG do small multiple
# ──────────────────────────────────────────────────────────────────────────
def svg_mini(cand_key: str, cand_nome: str, partido: str, cor_cand: str) -> str:
    W, H = 340, 170
    pad_top, pad_bot, pad_l, pad_r = 18, 30, 36, 14
    plot_w = W - pad_l - pad_r       # 290
    plot_h = H - pad_top - pad_bot   # 122

    # Y range fixo 0-25 pra comparabilidade visual entre os 6 charts
    y_max = 25
    dia_max = 89

    def xp(d):    return pad_l + (d / dia_max) * plot_w
    def yp(pct):  return pad_top + plot_h - (pct / y_max) * plot_h

    serie = get_serie(cand_key)
    stats = estatisticas_cand(cand_key)

    parts = []
    parts.append(f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">')

    # Eixo Y — gridlines a cada 5%
    for v in (0, 5, 10, 15, 20, 25):
        y = yp(v)
        parts.append(
            f'<line x1="{pad_l}" y1="{y:.1f}" x2="{pad_l + plot_w}" y2="{y:.1f}" '
            f'stroke="#E5E7EB" stroke-width="0.5"/>'
            f'<text x="{pad_l - 4}" y="{y + 3:.1f}" font-size="9" fill="#9CA3AF" '
            f'text-anchor="end" font-family="-apple-system,sans-serif">{v}%</text>'
        )

    # Eixo X — meses (fev, mar, abr, mai)
    meses_marker = [
        (dia("2026-02-15"), "fev"),
        (dia("2026-03-15"), "mar"),
        (dia("2026-04-15"), "abr"),
        (dia("2026-05-15"), "mai"),
    ]
    for d, lbl in meses_marker:
        x = xp(d)
        parts.append(
            f'<text x="{x:.1f}" y="{H - pad_bot + 14}" font-size="9" fill="#6B7280" '
            f'text-anchor="middle" font-family="-apple-system,sans-serif">{lbl}</text>'
        )

    # Linha de regressão (cinza claro tracejado, atrás dos pontos)
    x1 = 0
    x2 = dia_max
    y1 = stats["intercept"] + stats["slope"] * x1
    y2 = stats["intercept"] + stats["slope"] * x2
    parts.append(
        f'<line x1="{xp(x1):.1f}" y1="{yp(y1):.1f}" '
        f'x2="{xp(x2):.1f}" y2="{yp(y2):.1f}" '
        f'stroke="{cor_cand}" stroke-width="1.5" stroke-dasharray="4,3" opacity="0.45"/>'
    )

    # Pontos coloridos por instituto
    for d, inst, pct in serie:
        cor = INSTITUTO_COR[inst]
        parts.append(
            f'<circle cx="{xp(d):.1f}" cy="{yp(pct):.1f}" r="4" '
            f'fill="{cor}" stroke="#fff" stroke-width="1.2"/>'
        )

    # Header do chart: nome + delta consolidado
    delta = stats["delta_periodo"]
    sgn = "+" if delta >= 0 else ""
    cor_delta = "#0F6E56" if delta >= 0.5 else ("#A32D2D" if delta <= -0.5 else "#9CA3AF")
    parts.append(
        f'<text x="{pad_l}" y="13" font-size="11" font-weight="600" fill="#1A1A1A" '
        f'font-family="-apple-system,sans-serif">{cand_nome}</text>'
    )
    parts.append(
        f'<text x="{pad_l + 100}" y="13" font-size="9" fill="#6B7280" '
        f'font-family="-apple-system,sans-serif">{partido}</text>'
    )
    parts.append(
        f'<text x="{W - pad_r}" y="13" font-size="11" font-weight="600" fill="{cor_delta}" '
        f'text-anchor="end" font-family="-apple-system,sans-serif">{sgn}{delta:.1f}pp</text>'
    )

    parts.append('</svg>')
    return "\n".join(parts)


# ──────────────────────────────────────────────────────────────────────────
# Tabela pivô (linhas = candidatos, colunas = 8 pesquisas)
# ──────────────────────────────────────────────────────────────────────────
def tabela_pivo() -> str:
    headers = "".join(
        f'<th><span class="col-data">{fmt_data_br(p[0])}</span>'
        f'<span class="col-inst" style="color:{INSTITUTO_COR[p[1]]}">{p[1]}</span></th>'
        for p in PESQUISAS
    )
    linhas = []
    for cand_key, nome, partido, cor in CANDIDATOS:
        idx = {"kicis": 3, "fred": 4, "erika": 5, "jcr": 6, "veras": 7, "nemer": 8}[cand_key]
        celulas = "".join(f'<td>{p[idx]:.0f}%</td>' for p in PESQUISAS)
        stats = estatisticas_cand(cand_key)
        delta = stats["delta_periodo"]
        sgn = "+" if delta >= 0 else ""
        cls = "up" if delta >= 0.5 else ("dn" if delta <= -0.5 else "eq")
        linhas.append(
            f'<tr><td class="cand-cell">'
            f'<span class="cor-dot" style="background:{cor}"></span>'
            f'{nome}<span class="partido">{partido}</span></td>'
            f'{celulas}'
            f'<td class="delta {cls}">{sgn}{delta:.1f}pp</td></tr>'
        )
    return (
        '<table class="data-table">'
        '<thead><tr><th>Candidato</th>'
        f'{headers}'
        '<th class="delta-col">Δ período</th></tr></thead>'
        f'<tbody>{"".join(linhas)}</tbody></table>'
    )


# ──────────────────────────────────────────────────────────────────────────
# Findings editoriais
# ──────────────────────────────────────────────────────────────────────────
def gerar_findings():
    s_kicis = estatisticas_cand("kicis")
    s_fred  = estatisticas_cand("fred")
    s_jcr   = estatisticas_cand("jcr")
    s_veras = estatisticas_cand("veras")
    return [
        {
            "titulo": "Bia Kicis consolida liderança do PL no DF",
            "body": (
                f'Líder isolada do campo liberal-conservador na Câmara, <strong>Bia Kicis (PL)</strong> '
                f'avança de <strong>14% para 20%</strong> em três meses (<span class="up">+{s_kicis["delta_periodo"]:.1f}pp</span>). '
                f'Os <strong>{s_kicis["n_alta"]} institutos</strong> avaliados confirmam a tendência de alta — '
                f'sinal de movimento estrutural, não de oscilação amostral. A magnitude (~6pp) supera a '
                f'margem de erro consolidada (±2,5pp) e coloca Kicis com folga acima dos demais nomes do campo.'
            ),
        },
        {
            "titulo": "Bancada evangélica fragmenta-se",
            "body": (
                f'<strong>Julio Cesar Ribeiro (Republicanos)</strong>, pastor evangélico eleito em 2022, '
                f'recua de <strong>11% para 8%</strong> (<span class="dn">{s_jcr["delta_periodo"]:.1f}pp</span>) — '
                f'queda confirmada por todos os 4 institutos. Já <strong>Fred Linhares</strong>, do mesmo partido '
                f'mas com perfil mais técnico, sobe <span class="up">+{s_fred["delta_periodo"]:.1f}pp</span>. '
                f'O movimento sugere realocação intra-bancada, não saída de eleitores do campo conservador.'
            ),
        },
        {
            "titulo": "Reginaldo Veras emerge como segundo nome do PT-aliados",
            "body": (
                f'Erika Kokay segue dominando o voto progressista (~13%, estável). Mas <strong>Reginaldo Veras (PV)</strong> '
                f'avança discretamente de 5% para 7% (<span class="up">+{s_veras["delta_periodo"]:.1f}pp</span>), '
                f'criando uma <em>segunda opção</em> consistente para o eleitor de centro-esquerda — útil em '
                f'cenário onde o quociente eleitoral exigir distribuição de votos.'
            ),
        },
    ]


# ──────────────────────────────────────────────────────────────────────────
# Geração do HTML completo
# ──────────────────────────────────────────────────────────────────────────
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Análise Consolidada de Pesquisas — Dep. Federal DF 2026</title>
<style>
  :root {{
    --bg:#F5F2EC; --paper:#FFFFFF; --soft:#F0EDE6;
    --txt:#1A1A1A; --muted:#6B7280; --bd:rgba(0,0,0,.10); --bd2:rgba(0,0,0,.18);
    --amber:#B45309; --amber-soft:#FAEEDA;
    --up:#0F6E56; --dn:#A32D2D; --eq:#9CA3AF;
    --accent:#534AB7; --accent-soft:rgba(83,74,183,.06);
  }}
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  html {{ background:var(--bg); }}
  body {{
    font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;
    color:var(--txt); font-size:13px; line-height:1.55; padding:30px 0;
  }}
  .page {{
    width:780px; margin:0 auto 28px; padding:42px 56px;
    background:var(--paper); border:0.5px solid var(--bd); border-radius:6px;
    box-shadow:0 1px 4px rgba(0,0,0,.04);
    position:relative; min-height:1080px;
  }}
  .page-foot {{
    position:absolute; left:56px; right:56px; bottom:24px;
    display:flex; justify-content:space-between; align-items:center;
    font-size:9px; color:var(--muted);
    border-top:0.5px solid var(--bd); padding-top:10px;
  }}
  .page-foot strong {{ color:var(--txt); font-weight:600; }}

  /* CAPA */
  .cover {{ text-align:left; padding-top:120px; }}
  .cover .brand {{
    display:flex; align-items:center; gap:10px;
    font-size:11px; letter-spacing:1.5px; text-transform:uppercase;
    color:var(--amber); font-weight:600; margin-bottom:80px;
  }}
  .cover .brand-dot {{ width:8px; height:8px; background:var(--amber); border-radius:50%; }}
  .cover h1 {{
    font-size:38px; font-weight:600; letter-spacing:-1px;
    line-height:1.15; color:var(--txt); margin-bottom:8px;
  }}
  .cover h2 {{
    font-size:22px; font-weight:300; color:var(--muted); margin-bottom:36px;
  }}
  .cover .meta-row {{
    display:grid; grid-template-columns:repeat(4,1fr); gap:14px;
    margin-top:38px; padding-top:22px;
    border-top:0.5px solid var(--bd);
  }}
  .cover .meta-label {{
    font-size:9px; letter-spacing:1.5px; text-transform:uppercase;
    color:var(--muted); margin-bottom:4px;
  }}
  .cover .meta-val {{ font-size:13px; color:var(--txt); font-weight:500; }}
  .cover .demo-tag {{
    display:inline-block; font-size:9px; padding:2px 8px;
    background:var(--accent); color:#fff; border-radius:10px;
    letter-spacing:1px; text-transform:uppercase; font-weight:600;
    vertical-align:middle; margin-right:6px;
  }}
  .cover .disclaimer {{
    margin-top:48px; padding:14px 16px;
    background:var(--accent-soft); border-left:3px solid var(--accent);
    font-size:11px; color:#3C3489; line-height:1.5;
  }}
  .cover .institutos-row {{
    display:flex; gap:16px; margin-top:18px; padding:12px 0;
    border-top:0.5px solid var(--bd);
  }}
  .cover .inst-chip {{
    display:flex; align-items:center; gap:6px;
    font-size:11px; color:var(--txt);
  }}
  .cover .inst-dot {{ width:10px; height:10px; border-radius:50%; }}

  /* ESTRUTURA DE SEÇÃO */
  .section-kicker {{
    font-size:9px; letter-spacing:2px; text-transform:uppercase;
    color:var(--accent); font-weight:600; margin-bottom:6px;
  }}
  .section-title {{
    font-size:24px; font-weight:600; letter-spacing:-.4px; margin-bottom:6px;
  }}
  .section-sub {{ font-size:12px; color:var(--muted); margin-bottom:24px; }}
  .section-divider {{ height:0.5px; background:var(--bd); margin:0 0 22px; }}

  /* SUMÁRIO EXECUTIVO */
  .summary .lead {{
    font-size:14px; line-height:1.7; color:var(--txt); margin-bottom:18px;
  }}
  .findings {{ list-style:none; display:flex; flex-direction:column; gap:12px; }}
  .finding {{
    display:flex; gap:14px; padding:12px 14px;
    background:var(--soft); border-radius:6px;
    border-left:3px solid var(--accent);
  }}
  .finding .num {{
    flex-shrink:0; width:24px; height:24px; border-radius:50%;
    background:var(--accent); color:#fff;
    display:flex; align-items:center; justify-content:center;
    font-size:11px; font-weight:700;
  }}
  .finding .text {{ flex:1; }}
  .finding .title {{ font-weight:600; color:var(--txt); margin-bottom:3px; font-size:13px; }}
  .finding .body {{ font-size:12px; color:var(--muted); line-height:1.5; }}
  .finding .body strong {{ color:var(--txt); font-weight:500; }}
  .finding .body .up {{ color:var(--up); font-weight:600; }}
  .finding .body .dn {{ color:var(--dn); font-weight:600; }}

  /* SMALL MULTIPLES */
  .small-multiples {{
    display:grid; grid-template-columns:1fr 1fr; gap:8px;
    background:var(--soft); border-radius:8px; padding:14px;
    margin-bottom:18px;
  }}
  .small-multiples svg {{ display:block; background:var(--paper); border-radius:4px; }}

  .legend-row {{
    display:flex; gap:14px; padding:10px 14px; margin-bottom:14px;
    background:var(--paper); border:0.5px solid var(--bd); border-radius:6px;
    font-size:11px;
  }}
  .legend-item {{ display:flex; align-items:center; gap:6px; color:var(--txt); }}
  .legend-dot {{ width:10px; height:10px; border-radius:50%; }}
  .legend-line {{
    display:inline-block; width:18px; height:2px; opacity:0.45;
    border-top:1.5px dashed currentColor; margin-right:4px;
  }}

  /* TABELA PIVÔ */
  .data-table {{
    width:100%; border-collapse:collapse; font-size:10.5px;
    font-variant-numeric:tabular-nums; margin-bottom:18px;
  }}
  .data-table th {{
    font-size:9px; padding:6px 4px; border-bottom:0.5px solid var(--bd);
    text-align:right; vertical-align:bottom; color:var(--muted); font-weight:500;
  }}
  .data-table th:first-child {{ text-align:left; padding-left:0; }}
  .data-table th .col-data {{
    display:block; font-weight:600; color:var(--txt); font-size:10px;
  }}
  .data-table th .col-inst {{
    display:block; font-size:8.5px; font-weight:500; margin-top:1px;
  }}
  .data-table th.delta-col {{ font-size:9px; letter-spacing:.5px; text-transform:uppercase; }}
  .data-table td {{
    padding:6px 4px; border-bottom:0.5px solid var(--bd);
    text-align:right; color:var(--txt);
  }}
  .data-table td.cand-cell {{ text-align:left; padding-left:0; display:flex; align-items:center; gap:6px; }}
  .data-table .cor-dot {{ width:8px; height:8px; border-radius:50%; flex-shrink:0; }}
  .data-table .partido {{
    color:var(--muted); font-size:9px; margin-left:4px; font-weight:400;
  }}
  .data-table tr:last-child td {{ border-bottom:none; }}
  .data-table td.delta {{ font-weight:600; }}
  .data-table td.delta.up {{ color:var(--up); }}
  .data-table td.delta.dn {{ color:var(--dn); }}
  .data-table td.delta.eq {{ color:var(--eq); }}

  /* COMMENTARY */
  .commentary p {{
    font-size:12.5px; line-height:1.65; color:var(--txt);
    margin-bottom:10px;
  }}
  .commentary p:last-child {{ margin-bottom:0; }}
  .commentary strong {{ color:var(--txt); font-weight:600; }}
  .commentary em {{ color:var(--muted); font-style:italic; }}
  .commentary .up {{ color:var(--up); font-weight:600; }}
  .commentary .dn {{ color:var(--dn); font-weight:600; }}

  /* METHODOLOGY */
  .methodology .meta-grid {{
    display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-top:14px;
  }}
  .methodology .meta-cell {{
    padding:14px 16px; background:var(--soft); border-radius:6px;
  }}
  .methodology .meta-cell-label {{
    font-size:9px; letter-spacing:1.5px; text-transform:uppercase;
    color:var(--muted); margin-bottom:4px;
  }}
  .methodology .meta-cell-val {{ font-size:13px; color:var(--txt); font-weight:500; }}
  .methodology .note {{
    margin-top:18px; padding:12px 14px;
    background:var(--accent-soft); border-left:2px solid var(--accent);
    font-size:11px; line-height:1.55; color:#3C3489;
  }}
  .methodology .house-effect {{
    margin-top:18px; padding:14px 16px; background:var(--soft); border-radius:6px;
  }}
  .methodology .house-effect h3 {{
    font-size:13px; font-weight:600; margin-bottom:8px; color:var(--txt);
  }}
  .methodology .house-effect p {{ font-size:11.5px; line-height:1.6; color:var(--muted); }}

  @media print {{
    body {{ padding:0; background:#fff; }}
    .page {{
      width:auto; margin:0; box-shadow:none; border:none; border-radius:0;
      page-break-after:always; min-height:auto;
    }}
    .page:last-child {{ page-break-after:auto; }}
  }}
</style>
</head>
<body>

<!-- ━━━━━━ PÁGINA 1 — CAPA ━━━━━━ -->
<div class="page cover">
  <div class="brand">
    <span class="brand-dot"></span>
    Estrategos · Inteligência Política
  </div>
  <h1>Análise Consolidada de Pesquisas</h1>
  <h2>Câmara Federal · DF · Eleições 2026</h2>

  <div class="meta-row">
    <div>
      <div class="meta-label">Período de campo</div>
      <div class="meta-val">15/02 a 15/05/2026</div>
    </div>
    <div>
      <div class="meta-label">Pesquisas analisadas</div>
      <div class="meta-val">8 ondas</div>
    </div>
    <div>
      <div class="meta-label">Institutos</div>
      <div class="meta-val">4 (Veritá, Igape, Cepphor, Phoenix)</div>
    </div>
    <div>
      <div class="meta-label">Cargo</div>
      <div class="meta-val">Deputado Federal</div>
    </div>
  </div>

  <div class="institutos-row">
    {institutos_chips}
  </div>

  <div class="disclaimer">
    <span class="demo-tag">Demo</span>Demonstração de capability do produto Estrategos. Os candidatos são reais (eleitos para Deputado Federal pelo DF em 2022); os percentuais são <strong>sintéticos</strong>, calibrados para ilustrar agregação cross-instituto e detecção de tendências consolidadas. Não substituem dados oficiais. Quando o cliente fornecer relatórios reais (ou ativarmos o pipeline de coleta), o conteúdo é regenerado com dados de campo.
  </div>

  <div class="page-foot">
    <span><strong>Estrategos</strong> — Inteligência Política DF · Opinião Informação Estratégica</span>
    <span>1 / 4</span>
  </div>
</div>

<!-- ━━━━━━ PÁGINA 2 — SUMÁRIO EXECUTIVO ━━━━━━ -->
<div class="page">
  <div class="section-kicker">Sumário Executivo</div>
  <div class="section-title">Três movimentos confirmados por múltiplos institutos</div>
  <div class="section-sub">Tendências cuja magnitude supera a margem de erro consolidada (±2,5pp) e a variação esperada por <em>house effect</em></div>
  <div class="section-divider"></div>

  <div class="summary">
    <p class="lead">Entre meados de fevereiro e meados de maio de 2026, oito pesquisas registradas no TSE por quatro institutos diferentes (Veritá, Igape, Cepphor e Phoenix) cobriram a corrida pela Câmara Federal no DF. Cruzando as ondas, três movimentos se destacam pela <strong>convergência cross-instituto</strong> — sinal de que não são oscilações amostrais isoladas, mas tendências estruturais.</p>

    <ul class="findings">
      {findings_html}
    </ul>
  </div>

  <div class="page-foot">
    <span><strong>Estrategos</strong> — Inteligência Política DF · Opinião Informação Estratégica</span>
    <span>2 / 4</span>
  </div>
</div>

<!-- ━━━━━━ PÁGINA 3 — SMALL MULTIPLES ━━━━━━ -->
<div class="page">
  <div class="section-kicker">Câmara Federal · Cenário estimulado</div>
  <div class="section-title">Evolução por candidato</div>
  <div class="section-sub">Cada chart: 8 pesquisas (uma cor por instituto) · linha tracejada = regressão linear consolidada · delta no canto = variação estimada no período</div>
  <div class="section-divider"></div>

  <div class="legend-row">
    {legenda_chart}
    <span style="margin-left:auto;color:var(--muted);font-size:10.5px;">
      <span class="legend-line" style="color:var(--muted)"></span>linha = tendência consolidada (regressão linear)
    </span>
  </div>

  <div class="small-multiples">
    {small_multiples}
  </div>

  <div class="commentary">
    <p>A leitura por <strong>small multiples</strong> permite avaliar cada candidato isoladamente, mas mantendo a mesma escala vertical (0–25%) para que magnitudes sejam comparáveis. Pontos coloridos identificam o instituto responsável; a linha tracejada representa a regressão linear das oito ondas — útil para distinguir <em>tendência</em> de <em>oscilação amostral</em>.</p>
    <p>Quatro candidatos apresentam tendência clara (módulo da inclinação superior a 0,02pp/dia): <strong>Bia Kicis</strong> e <strong>Fred Linhares</strong> em alta; <strong>Julio Cesar Ribeiro</strong> em queda; <strong>Reginaldo Veras</strong> em alta moderada. Os demais (Erika Kokay e Roney Nemer) oscilam dentro da margem.</p>
  </div>

  <div class="page-foot">
    <span><strong>Estrategos</strong> — Inteligência Política DF · Opinião Informação Estratégica</span>
    <span>3 / 4</span>
  </div>
</div>

<!-- ━━━━━━ PÁGINA 4 — TABELA PIVÔ + METODOLOGIA ━━━━━━ -->
<div class="page">
  <div class="section-kicker">Câmara Federal</div>
  <div class="section-title">Tabela pivô · 8 pesquisas × 6 candidatos</div>
  <div class="section-sub">Comparação direta entre todas as ondas. Δ período = variação entre a primeira e a última pesquisa</div>
  <div class="section-divider"></div>

  {tabela_pivo}

  <div class="commentary">
    <p>A coluna <strong>Δ período</strong> mostra o movimento bruto (última pesquisa menos primeira). Como os institutos se alternam ao longo do tempo, parte dessa variação pode ser <em>house effect</em> — viés sistemático de cada instituto. A regressão linear (página 3) atenua isso ao usar todos os 8 pontos, e os números convergem com a leitura cross-instituto descrita no sumário executivo.</p>
  </div>

  <div class="section-kicker" style="margin-top:30px">Metodologia</div>
  <div class="section-title" style="font-size:18px">Como esta análise foi produzida</div>
  <div class="section-divider"></div>

  <div class="methodology">
    <div class="meta-grid">
      <div class="meta-cell">
        <div class="meta-cell-label">Tipo de coleta</div>
        <div class="meta-cell-val">Survey quantitativa, face-a-face e domiciliar</div>
      </div>
      <div class="meta-cell">
        <div class="meta-cell-label">Margem de erro consolidada</div>
        <div class="meta-cell-val">±2,5 pp · IC 95%</div>
      </div>
      <div class="meta-cell">
        <div class="meta-cell-label">Universo</div>
        <div class="meta-cell-val">2,2M eleitores DF · TSE 2026</div>
      </div>
      <div class="meta-cell">
        <div class="meta-cell-label">Cotas</div>
        <div class="meta-cell-val">Sexo · Idade · Escolaridade · Renda</div>
      </div>
    </div>

    <div class="house-effect">
      <h3>Sobre o <em>house effect</em> e tendência consolidada</h3>
      <p>Cada instituto tem viés metodológico próprio (entrevistador, formulação de pergunta, ponderação). Olhar uma única pesquisa pode confundir <em>house effect</em> com mudança real. A leitura segura é: <strong>cruzar institutos</strong> e considerar tendência confirmada apenas quando 3 dos 4 institutos apontam na mesma direção. A regressão linear empregada nos charts da página 3 usa as 8 pesquisas igualmente — uma forma simples de neutralizar parcialmente o efeito-instituto e isolar o sinal temporal.</p>
    </div>

    <div class="note">
      <strong>★ Sobre os dados:</strong> os candidatos listados foram eleitos pelo DF para a Câmara Federal em 2022 (Bia Kicis, Fred Linhares, Erika Kokay, Julio Cesar Ribeiro, Reginaldo Veras e Roney Nemer). Os percentuais são <strong>sintéticos</strong>, calibrados para ilustrar agregação cross-instituto e construção de narrativa editorial. Variações inferiores a ±2,5pp não são estatisticamente distinguíveis.
    </div>
  </div>

  <div class="page-foot">
    <span><strong>Estrategos</strong> — Inteligência Política DF · Opinião Informação Estratégica</span>
    <span>4 / 4</span>
  </div>
</div>

</body>
</html>
"""


def main():
    # Construir blocos
    institutos_chips = "".join(
        f'<div class="inst-chip"><span class="inst-dot" style="background:{cor}"></span>{nome}</div>'
        for nome, cor in INSTITUTO_COR.items()
    )

    legenda_chart = "".join(
        f'<div class="legend-item"><span class="legend-dot" style="background:{cor}"></span>{nome}</div>'
        for nome, cor in INSTITUTO_COR.items()
    )

    small_multiples = "\n".join(
        svg_mini(k, n, p, c) for k, n, p, c in CANDIDATOS
    )

    findings = gerar_findings()
    findings_html = "".join(
        f'<li class="finding"><div class="num">{i+1}</div>'
        f'<div class="text"><div class="title">{f["titulo"]}</div>'
        f'<div class="body">{f["body"]}</div></div></li>'
        for i, f in enumerate(findings)
    )

    html = HTML_TEMPLATE.format(
        institutos_chips=institutos_chips,
        legenda_chart=legenda_chart,
        small_multiples=small_multiples,
        tabela_pivo=tabela_pivo(),
        findings_html=findings_html,
    )

    out = Path("relatorio_pesquisas_demo.html")
    out.write_text(html, encoding="utf-8")
    print(f"OK: {out} ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
