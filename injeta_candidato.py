"""
injeta_candidato.py — visão Candidato da Geopolítica
=====================================================
Roda DEPOIS de injeta_geopolitica.py. Os items de nav
'ni-geo-territorio' e 'ni-geo-candidato' já são criados pelo
fase4_v2.py; este script apenas DEFINE a função irGeoCandidato()
e injeta a seção #geo-cand-section.

Layout: lista de candidatos (25%) | mapa de calor (50%) | relatório (25%)

Entrada:
  dashboard_com_geo.html           (saída do injeta_geopolitica.py)
  outputs_fase3c/votos_candidato_ra.csv

Saída:
  dashboard_com_candidato.html

Uso:
  python3 injeta_candidato.py
"""

import json, base64, csv
from pathlib import Path
from collections import defaultdict

DASHBOARD_IN = Path("dashboard_com_geo.html")
CSV_IN       = Path("outputs_fase3c/votos_candidato_ra.csv")
OUTPUT       = Path("index.html")

MIN_VOTOS = 50


def carregar_dados():
    por_cand = defaultdict(lambda: {"meta": None, "ras": []})
    with open(CSV_IN, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            nm = row["NM_CANDIDATO"]
            if por_cand[nm]["meta"] is None:
                por_cand[nm]["meta"] = {
                    "cargo":   row["DS_CARGO"],
                    "campo":   row["CAMPO"],
                    "partido": row["SG_PARTIDO"],
                    "total":   int(row["TOTAL_CAND"]),
                }
            idx_raw = row.get("INDICE_SOBRE", "")
            try:
                idx_val = float(idx_raw) if idx_raw not in (None, "", "nan") else None
            except (TypeError, ValueError):
                idx_val = None
            por_cand[nm]["ras"].append({
                "ra":        row["RA_NOME"],
                "votos":     int(row["QT_VOTOS_RA"]),
                "pct_cargo": float(row["PCT_DO_CARGO"]),
                "pct_campo": float(row["PCT_DO_CAMPO"]),
                "idx":       idx_val,
                "status":    row["STATUS_BASE"],
            })
    candidatos = []
    for nm, info in por_cand.items():
        if info["meta"]["total"] < MIN_VOTOS:
            continue
        status_cnt = defaultdict(int)
        for ra in info["ras"]:
            status_cnt[ra["status"]] += 1
        candidatos.append({
            "nm":         nm,
            "cargo":      info["meta"]["cargo"],
            "campo":      info["meta"]["campo"],
            "partido":    info["meta"]["partido"],
            "total":      info["meta"]["total"],
            "ras":        info["ras"],
            "status_cnt": dict(status_cnt),
        })
    candidatos.sort(key=lambda x: -x["total"])
    return candidatos


CSS_CAND = """
#geo-cand-section{display:none;flex:1;flex-direction:column;overflow:hidden;background:var(--bg)}
#geo-cand-section.gc-vis{display:flex}
#gc-toolbar{height:40px;display:flex;align-items:center;background:var(--s1);border-bottom:0.5px solid var(--bd);flex-shrink:0}
.gc-tb-group{display:flex;align-items:center;gap:8px;padding:0 14px;height:100%}
.gc-tb-sep{width:0.5px;background:var(--bd);height:100%;flex-shrink:0}
.gc-tb-lbl{font-size:9px;letter-spacing:1.5px;text-transform:uppercase;color:var(--muted);white-space:nowrap}
select.gc-sel{background:var(--s1);border:0.5px solid var(--bd2);border-radius:6px;color:var(--txt);font-size:12px;padding:4px 8px;cursor:pointer;outline:none;font-family:inherit}
select.gc-sel:hover{border-color:var(--amber)}
#gc-body{display:grid;grid-template-columns:25% 50% 25%;flex:1;overflow:hidden;min-height:0}
#gc-left{background:var(--s1);border-right:0.5px solid var(--bd);display:flex;flex-direction:column;overflow:hidden}
.gc-col-head{padding:8px 14px;border-bottom:0.5px solid var(--bd);background:var(--s2);flex-shrink:0;font-size:9px;letter-spacing:2px;text-transform:uppercase;color:var(--muted)}
#gc-filters{padding:8px 12px;border-bottom:0.5px solid var(--bd);flex-shrink:0;display:flex;flex-direction:column;gap:6px}
#gc-cargo-pills{display:flex;gap:3px;flex-wrap:wrap}
.gc-cargo-pill{font-size:10px;padding:2px 8px;border-radius:20px;cursor:pointer;border:0.5px solid var(--bd2);background:var(--s1);color:var(--muted);font-family:inherit;transition:all .12s}
.gc-cargo-pill:hover{color:var(--txt)}
.gc-cargo-pill.gc-active{background:#1D9E751A;border-color:#1D9E75;color:#0F6E56;font-weight:500}
#gc-search{background:var(--s2);border:0.5px solid var(--bd);border-radius:6px;color:var(--txt);font-size:11px;padding:4px 8px;outline:none;font-family:inherit;width:100%}
#gc-search:focus{border-color:var(--amber)}
#gc-list{flex:1;overflow-y:auto;padding:3px 0}
#gc-list::-webkit-scrollbar{width:3px}
#gc-list::-webkit-scrollbar-thumb{background:var(--bd2)}
.gc-item{display:flex;align-items:center;gap:6px;padding:7px 12px;cursor:pointer;transition:background .12s;border-left:2px solid transparent}
.gc-item:hover{background:var(--s2)}
.gc-item.gc-sel{background:var(--s2);border-left-color:var(--amber)}
.gc-item-dot{width:6px;height:6px;border-radius:50%;flex-shrink:0}
.gc-item-body{flex:1;min-width:0}
.gc-item-nome{font-size:11px;font-weight:500;color:var(--txt);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.gc-item-meta{font-size:10px;color:var(--muted);margin-top:1px}
.gc-item-votos{font-size:11px;font-family:var(--mono,monospace);color:var(--amber);flex-shrink:0;font-weight:500}
.gc-empty-list{padding:18px 14px;font-size:11px;color:var(--muted);text-align:center;font-style:italic}
.gc-dot-prog{background:#534AB7}
.gc-dot-mod{background:#0F6E56}
.gc-dot-lib{background:#854F0B}
.gc-dot-out{background:#9CA3AF}
#gc-map-wrap{position:relative;overflow:hidden}
#gc-map{width:100%;height:100%}
#gc-map .leaflet-interactive{outline:none!important}
#gc-map .leaflet-interactive:focus{outline:none!important}
#gc-map-legend{position:absolute;bottom:28px;left:12px;z-index:500;background:var(--s1);border:0.5px solid var(--bd2);border-radius:8px;padding:8px 12px;box-shadow:0 2px 8px rgba(0,0,0,.08);min-width:155px}
.gcml-title{font-size:9px;letter-spacing:1.5px;text-transform:uppercase;color:var(--muted);margin-bottom:5px}
.gcml-grad-wrap{display:flex;align-items:center;gap:5px}
.gcml-grad{flex:1;height:5px;border-radius:3px}
.gcml-val{font-size:10px;color:var(--muted);white-space:nowrap}
#gc-map-empty{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;color:var(--muted);pointer-events:none;z-index:400}
.gcme-icon{font-size:32px;opacity:.2}
.gcme-txt{font-size:12px;line-height:1.6;max-width:260px;text-align:center}
#gc-right{background:var(--s1);border-left:0.5px solid var(--bd);display:flex;flex-direction:column;overflow:hidden}
#gc-right-empty{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px;color:var(--muted);padding:20px;text-align:center}
.gc-empty-icon{font-size:28px;opacity:.25}
#gc-panel-body{flex:1;overflow-y:auto;padding:12px 14px}
#gc-panel-body::-webkit-scrollbar{width:3px}
#gc-panel-body::-webkit-scrollbar-thumb{background:var(--bd2)}
.gcp-id{margin-bottom:14px;padding-bottom:12px;border-bottom:0.5px solid var(--bd)}
.gcp-nome{font-size:15px;font-weight:500;color:var(--txt);line-height:1.3;margin-bottom:6px}
.gcp-tags{display:flex;gap:4px;flex-wrap:wrap;margin-bottom:10px}
.gcp-tag{font-size:10px;padding:2px 8px;border-radius:10px;font-weight:500}
.gcp-tag-prog{background:#EEEDFE;color:#3C3489}
.gcp-tag-mod{background:#E1F5EE;color:#085041}
.gcp-tag-lib{background:#FAEEDA;color:#633806}
.gcp-tag-out{background:#F3F4F6;color:#4B5563}
.gcp-tag-cargo{background:#E0F2FE;color:#075985}
.gcp-total-row{display:flex;align-items:baseline;gap:8px}
.gcp-total{font-size:24px;font-weight:500;color:var(--amber);font-family:var(--mono,inherit)}
.gcp-total-lbl{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.5px}
.gcp-partido{font-size:11px;color:var(--muted);margin-top:2px}
.gcp-section{margin-bottom:14px}
.gcp-sec-title{font-size:9px;letter-spacing:1.5px;text-transform:uppercase;color:var(--amber);margin-bottom:7px;padding-bottom:4px;border-bottom:0.5px solid var(--bd)}
.gcp-status-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:4px}
.gcp-status-box{background:var(--s2);border-radius:7px;padding:8px 4px;text-align:center;cursor:pointer;transition:background .12s;border:0.5px solid transparent}
.gcp-status-box:hover{background:var(--s3)}
.gcp-status-box.gcp-sb-active{border-color:var(--amber);background:var(--s3)}
.gcp-status-val{font-size:15px;font-weight:500;font-family:var(--mono,inherit)}
.gcp-status-lbl{font-size:8px;color:var(--muted);margin-top:2px;text-transform:uppercase;letter-spacing:.3px;line-height:1.1}
.gcp-sb-reduto   .gcp-status-val{color:#0B5A2E}
.gcp-sb-forte    .gcp-status-val{color:#15803D}
.gcp-sb-medio    .gcp-status-val{color:#B45309}
.gcp-sb-fraca    .gcp-status-val{color:#991B1B}
.gcp-sb-ausencia .gcp-status-val{color:#5A1010}
.gcp-tbl-wrap{border:0.5px solid var(--bd);border-radius:7px;overflow:hidden;background:var(--s2)}
.gcp-tbl{width:100%;border-collapse:collapse;font-size:11px}
.gcp-tbl th{background:var(--s1);padding:6px 6px;font-size:9px;letter-spacing:.5px;text-transform:uppercase;color:var(--muted);font-weight:500;text-align:left;cursor:pointer;user-select:none;border-bottom:0.5px solid var(--bd);white-space:nowrap}
.gcp-tbl th:hover{color:var(--txt)}
.gcp-tbl th.gcp-sorted{color:var(--amber)}
.gcp-tbl td{padding:5px 6px;border-bottom:0.5px solid var(--bd);color:var(--txt)}
.gcp-tbl tr:last-child td{border-bottom:none}
.gcp-tbl td.gcp-num{font-family:var(--mono,monospace);text-align:right}
.gcp-tbl td.gcp-ra{max-width:160px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-weight:500}
.gcp-status-tag{display:inline-block;font-size:9px;padding:1px 6px;border-radius:8px;font-weight:500;white-space:nowrap}
.gcp-st-reduto{background:#A7F3C8;color:#0B5A2E}
.gcp-st-forte{background:#DCFCE7;color:#15803D}
.gcp-st-medio{background:#FEF3C7;color:#B45309}
.gcp-st-fraca{background:#FEE2E2;color:#991B1B}
.gcp-st-ausencia{background:#FCA5A5;color:#5A1010}
.gcp-diag-group{background:var(--s2);border-radius:7px;margin-bottom:6px;overflow:hidden}
.gcp-diag-head{padding:7px 10px;cursor:pointer;display:flex;align-items:center;justify-content:space-between;user-select:none}
.gcp-diag-head:hover{background:var(--s3)}
.gcp-diag-nome{font-size:11px;font-weight:500;display:flex;align-items:center;gap:6px}
.gcp-diag-count{font-size:10px;color:var(--muted);font-family:var(--mono,inherit)}
.gcp-diag-chev{font-size:9px;color:var(--muted);transition:transform .15s}
.gcp-diag-group.gcp-open .gcp-diag-chev{transform:rotate(90deg)}
.gcp-diag-body{display:none;padding:0 10px 8px;border-top:0.5px solid var(--bd)}
.gcp-diag-group.gcp-open .gcp-diag-body{display:block}
.gcp-diag-row{display:flex;justify-content:space-between;align-items:center;padding:4px 0;border-bottom:0.5px dashed var(--bd);font-size:11px}
.gcp-diag-row:last-child{border-bottom:none}
.gcp-diag-ra{color:var(--txt);flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.gcp-diag-nums{color:var(--muted);font-family:var(--mono,monospace);font-size:10px;flex-shrink:0}
.gcp-diag-dot{width:8px;height:8px;border-radius:2px;flex-shrink:0}
.gcd-base{background:#15803D}
.gcd-sub{background:#D97706}
.gcd-forca{background:#534AB7}
.gcd-nao{background:#9CA3AF}
.gcp-empty-diag{font-size:11px;color:var(--muted);font-style:italic;padding:8px 0}

/* ── PAPER ANALÍTICO DO CANDIDATO (visível só na impressão) ───────────────── */
.paper-wrap{display:none}
@media print {
  .paper-wrap{
    display:block !important;
    order:-1 !important;
    page-break-after:always !important;
    break-after:page !important;
    page-break-before:auto !important;
    break-before:auto !important;
    width:100% !important;
    background:white !important;
    color:#1A1A1A !important;
    padding:0 !important;
    margin:0 !important;
    font-family:-apple-system,BlinkMacSystemFont,"Helvetica Neue",Arial,sans-serif !important;
  }
  .paper-report{ width:100%; max-width:277mm; margin:0 auto; font-size:10pt; color:#1A1A1A }
  .paper-hd{ display:flex; align-items:flex-start; gap:14px; padding-bottom:8pt; border-bottom:2pt solid #B45309; margin-bottom:6pt }
  .paper-logo{ flex-shrink:0; width:36pt; height:36pt; background:#F0EDE6; border-radius:6pt; display:flex; align-items:center; justify-content:center; font-size:8pt; color:#6B7280 }
  .paper-logo-img{ flex-shrink:0; height:32pt; width:auto; max-width:90pt; object-fit:contain; filter:sepia(1) saturate(1.2) hue-rotate(5deg) brightness(0.7) }
  .paper-info{ flex:1; min-width:0 }
  .paper-nome{ font-size:13pt; font-weight:600; line-height:1.15; margin-bottom:3pt }
  .paper-line{ display:flex; gap:6pt; flex-wrap:wrap; align-items:center; margin-bottom:2pt; font-size:9pt }
  .paper-tag{ font-size:8pt; padding:1.5pt 6pt; border-radius:8pt; font-weight:500 }
  .paper-data{ font-size:8pt; color:#6B7280; white-space:nowrap }

  .paper-2col{ display:grid; grid-template-columns:1.15fr 1fr; gap:14pt; margin-top:6pt }
  .paper-left, .paper-right{ min-width:0 }

  .paper-sec{ margin-top:7pt }
  .paper-sec-title{ font-size:8pt; letter-spacing:1.2pt; text-transform:uppercase; color:#B45309; margin-bottom:3pt; padding-bottom:2pt; border-bottom:0.5pt solid rgba(0,0,0,.18); font-weight:600 }

  .paper-cards-row{ display:grid; grid-template-columns:1fr 1fr 1fr; gap:5pt; margin-top:3pt }
  .paper-card{ background:#F0EDE6; border-radius:5pt; padding:5pt 7pt; display:flex; flex-direction:column; gap:3pt; min-width:0 }
  .paper-card-head{ display:flex; align-items:center; gap:5pt; min-width:0 }
  .paper-card-ra{ font-size:8.5pt; font-weight:500; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; flex:1; min-width:0 }
  .paper-card-tag{ font-size:6.5pt; padding:1pt 5pt; border-radius:5pt; font-weight:500; white-space:nowrap; flex-shrink:0 }
  .paper-card-meta{ font-size:7.5pt; color:#6B7280; line-height:1.35 }
  .paper-card-empty{ color:rgba(0,0,0,.18); justify-content:center; align-items:center; text-align:center }
  .paper-empty{ background:#F0EDE6; border-radius:5pt; padding:7pt 9pt; font-style:italic; color:#6B7280; font-size:8.5pt; margin-top:3pt }

  .paper-diag{ background:#F0EDE6; padding:6pt 9pt; border-radius:5pt; border-left:2pt solid #B45309; font-size:8.5pt; line-height:1.5; color:#1A1A1A }
  .paper-diag strong{ color:#1A1A1A }

  .paper-perfil-grid{ display:grid; grid-template-columns:repeat(3,1fr); gap:4pt; margin-top:3pt }
  .paper-perfil-card{ background:#F0EDE6; border-radius:5pt; padding:6pt 7pt; border-left:2pt solid #B45309; display:flex; flex-direction:column; gap:3pt }
  .paper-perfil-lbl{ font-size:6.5pt; color:#6B7280; text-transform:uppercase; letter-spacing:.3pt; line-height:1.2; font-weight:600; white-space:nowrap }
  .paper-perfil-val{ font-size:12pt; font-weight:700; line-height:1 }
  .paper-perfil-ref{ font-size:6.5pt; color:#6B7280; line-height:1.2 }

  .paper-tbl-wrap{ border:0.5pt solid rgba(0,0,0,.18); border-radius:4pt; overflow:hidden; margin-top:3pt }
  .paper-tbl{ width:100%; border-collapse:collapse; font-size:7.5pt }
  .paper-tbl th{ background:#F0EDE6; text-align:left; padding:2.5pt 5pt; font-size:6.5pt; letter-spacing:.5pt; text-transform:uppercase; color:#6B7280; font-weight:600; border-bottom:0.5pt solid rgba(0,0,0,.18) }
  .paper-tbl td{ padding:1.8pt 5pt; border-bottom:0.5pt solid rgba(0,0,0,.08) }
  .paper-tbl tr:last-child td{ border-bottom:none }
  .paper-tbl td.ra{ font-weight:500; max-width:50mm; white-space:nowrap; overflow:hidden; text-overflow:ellipsis }
  .paper-tbl td.num{ font-family:"SF Mono",Menlo,monospace; text-align:right; font-size:7pt }
  .paper-st-badge{ font-size:6.5pt; padding:.5pt 4pt; border-radius:5pt; font-weight:500; white-space:nowrap }

  .paper-foot{ margin-top:8pt; padding-top:5pt; border-top:0.5pt solid rgba(0,0,0,.18); font-size:7pt; color:#6B7280; text-align:center; line-height:1.5 }
  .paper-foot strong{ color:#1A1A1A; font-weight:600 }

  /* Paper de contexto DF — layout 2 cols + matriz */
  .paper-row-2{ display:grid; grid-template-columns:1fr 1fr; gap:14pt; margin-bottom:7pt }
  .paper-col{ min-width:0 }
  .paper-sec-narr{ font-size:8.5pt; color:#6B7280; line-height:1.55; margin-bottom:5pt }
  .paper-sec-narr strong{ color:#1A1A1A }
  .paper-kpis{ display:grid; grid-template-columns:repeat(4,1fr); gap:5pt; margin-bottom:5pt }
  .paper-kpi{ background:#F0EDE6; border-radius:5pt; padding:6pt 7pt; border-left:2pt solid #B45309 }
  .paper-kpi-num{ font-size:13pt; font-weight:600; color:#B45309; line-height:1 }
  .paper-kpi-lbl{ font-size:7pt; color:#6B7280; text-transform:uppercase; letter-spacing:.4pt; margin-top:2pt; font-weight:600 }
  .paper-kpi-sub{ font-size:6.5pt; color:#6B7280; margin-top:1pt; line-height:1.2 }
  .paper-tbl-mini{ width:100%; border-collapse:collapse; font-size:8.5pt; margin-top:3pt }
  .paper-tbl-mini th{ background:#F0EDE6; padding:3pt 6pt; text-align:left; font-size:7pt; color:#6B7280; text-transform:uppercase; letter-spacing:.4pt; font-weight:600 }
  .paper-tbl-mini td{ padding:3pt 6pt; border-bottom:0.5pt solid rgba(0,0,0,.08) }
  .paper-tbl-mini td.ra{ font-weight:500 }
  .paper-tbl-mini td.num{ font-family:"SF Mono",Menlo,monospace; text-align:right; font-size:8pt }
  .paper-tbl-matriz{ width:100%; border-collapse:collapse; font-size:9.5pt }
  .paper-tbl-matriz th{ padding:4pt 6pt; font-size:7.5pt; font-weight:600; color:#6B7280; text-transform:uppercase; letter-spacing:.4pt }
  .paper-tbl-matriz td{ padding:5pt 6pt; border-bottom:0.5pt solid rgba(0,0,0,.08) }
  .paper-tbl-matriz td.cargo-lbl{ font-weight:500; font-size:9pt; color:#1A1A1A }
  .paper-tbl-matriz td.campo-cell{ text-align:center; font-family:"SF Mono",Menlo,monospace; min-width:40pt }

  /* Modo "só relatório" — disparado por body.print-iso (Candidatos > Imprimir relatório) */
  body.print-iso #app,
  body.print-iso .met-modal,
  body.print-iso #cmp-overlay { display:none !important; }
  body.print-iso #rel-paper-iso {
    display:block !important;
    width:100% !important;
    background:white !important;
    color:#1A1A1A !important;
    padding:0 !important;
    margin:0 !important;
    font-family:-apple-system,BlinkMacSystemFont,"Helvetica Neue",Arial,sans-serif !important;
    page-break-before:auto !important;
    page-break-after:auto !important;
    order:0 !important;
  }
}
"""


CAND_SECTION_HTML = """
  <!-- GEOPOLITICA CANDIDATO -->
  <div id="geo-cand-section">
    <div id="gc-toolbar">
      <div class="gc-tb-group">
        <span class="gc-tb-lbl">Colorir mapa por</span>
        <select class="gc-sel" id="gc-var-sel" onchange="gcRecolor()">
          <option value="votos">Votos absolutos</option>
          <option value="pct_cargo">% do cargo</option>
          <option value="pct_campo">% do campo</option>
          <option value="idx">Performance</option>
        </select>
      </div>
      <div class="gc-tb-sep"></div>
      <div class="gc-tb-group">
        <span class="gc-tb-lbl" id="gc-candidato-ativo">Selecione um candidato à esquerda</span>
      </div>
      <div class="gc-tb-group" style="margin-left:auto;padding-right:14px">
        <button class="geo-pill-print" onclick="imprimirCand()" title="Imprimir consulta atual"><span style="font-size:13px">\U0001F5A8</span> Imprimir</button>
      </div>
    </div>

    <!-- Cabeçalho de impressão (oculto na tela, visível só no @media print) -->
    <div class="print-header" id="gc-print-header">
      <div class="print-header-row">
        <div class="print-header-left">
          <img class="print-logo" src="__LOGO_SRC__" alt="Opinião"/>
          <div>
            <div class="print-kicker">Opinião · Informação Estratégica</div>
            <div class="print-titulo">Geopolítica · Candidato</div>
          </div>
        </div>
        <div class="print-data" id="gc-print-data"></div>
      </div>
      <div class="print-filtros" id="gc-print-filtros"></div>
    </div>

    <div id="gc-body">
      <div id="gc-left">
        <div class="gc-col-head">Candidatos 2022</div>
        <div id="gc-filters">
          <div id="gc-cargo-pills">
            <button class="gc-cargo-pill gc-active" onclick="gcSetCargo('TODOS',this)">Todos</button>
            <button class="gc-cargo-pill" onclick="gcSetCargo('DEPUTADO_DISTRITAL',this)">Distrital</button>
            <button class="gc-cargo-pill" onclick="gcSetCargo('DEPUTADO_FEDERAL',this)">Federal</button>
            <button class="gc-cargo-pill" onclick="gcSetCargo('SENADOR',this)">Senador</button>
            <button class="gc-cargo-pill" onclick="gcSetCargo('GOVERNADOR',this)">Governador</button>
          </div>
          <input id="gc-search" placeholder="Buscar por nome ou partido..." oninput="gcFiltrarLista()">
        </div>
        <div id="gc-list"></div>
      </div>
      <div id="gc-map-wrap">
        <div id="gc-map"></div>
        <div id="gc-map-empty">
          <div class="gcme-icon">\U0001F5FA</div>
          <div class="gcme-txt">O mapa mostra a distribuição territorial dos votos do candidato selecionado</div>
        </div>
        <div id="gc-map-legend" style="display:none">
          <div class="gcml-title" id="gcml-title">Votos</div>
          <div class="gcml-grad-wrap">
            <span class="gcml-val" id="gcml-min">-</span>
            <div class="gcml-grad" id="gcml-grad"></div>
            <span class="gcml-val" id="gcml-max">-</span>
          </div>
        </div>
      </div>
      <div id="gc-right">
        <div class="gc-col-head">Relatório</div>
        <div id="gc-right-empty">
          <div class="gc-empty-icon">\U0001F4CA</div>
          <div class="gc-empty-txt">Selecione um candidato para ver o relatório completo</div>
        </div>
        <div id="gc-panel-body" style="display:none"></div>
      </div>
    </div>

    <!-- Tabela de top RAs (visível só no print) -->
    <div class="print-tabela-wrap" id="gc-print-tabela-wrap">
      <div class="print-tabela-titulo" id="gc-print-tabela-titulo">Ranking das regiões</div>
      <table class="print-tabela" id="gc-print-tabela"></table>
    </div>

    <!-- Rodapé de impressão -->
    <div class="print-rodape print-only">
      Fontes: TSE 2022 (votos por seção, cadastro eleitoral) · PDAD 2021 (perfil socioeconômico).
      Instrumento gerado pelo painel <strong>Estrategos</strong> — solução de Inteligência Política da <strong>Opinião Informação Estratégica</strong>.
    </div>

    <!-- Paper analítico do candidato (preenchido por imprimirCand, visível só no print) -->
    <div class="paper-wrap" id="gc-paper-wrap"></div>
  </div>
"""


CAND_JS = r"""
// GEOPOLITICA > CANDIDATO ================================================

const GC_DATA = JSON.parse(atob("__CAND_B64__"));

// Marcar eleitos com base na LISTA OFICIAL TSE/CLDF 2022
// Fonte: Câmara dos Deputados + CLDF. Sistema proporcional brasileiro
// (quociente eleitoral + sobras + federações) — não usar ranking simples.
var ELEITOS_2022 = {
  GOVERNADOR: ["IBANEIS"],
  SENADOR:    ["DAMARES"],
  DEPUTADO_FEDERAL: [
    "BEATRIZ KICIS","DAVYS FREDERICO","ERIKA JUCÁ","RAFAEL CAVALCANTI",
    "JULIO CESAR RIBEIRO","REGINALDO VERAS","JOÃO ALBERTO FRAGA","GILVAM"
  ],
  DEPUTADO_DISTRITAL: [
    "FÁBIO FELIX","FRANCISCO DOMINGOS","MAX MACIEL","DANIEL XAVIER DONIZET",
    "MARTINS MACHADO","ROBÉRIO BANDEIRA","JORGE VIANA DE SOUSA","JAQUELINE ANGELA",
    "THIAGO DE ARAÚJO","EDUARDO WEYNE","JOAQUIM DOMINGOS RORIZ","IOLANDO ALMEIDA",
    "DANIEL DE CASTRO","JOÃO HERMETO","ROOSEVELT VILELA","JANE KLEBIA",
    "BERNARDO ROGÉRIO","GABRIEL MAGNO","JOAO ALVES CARDOSO","PAULA MORENO PARO",
    "RICARDO VALE DA SILVA","WELLINGTON LUIZ","PEDRO PAULO DE OLIVEIRA","DAYSE AMARILIO"
  ]
};
(function(){
  Object.keys(ELEITOS_2022).forEach(function(cargo){
    var idents = ELEITOS_2022[cargo].map(function(s){return s.toUpperCase();});
    GC_DATA.filter(function(c){return c.cargo===cargo;}).forEach(function(c){
      var nm = (c.nm||"").toUpperCase();
      c.eleito = idents.some(function(id){ return nm.indexOf(id)>=0; });
    });
  });
})();

// Tipologia do candidato baseada em σ dos deltas (sobre-índice − 1) entre RAs.
// Distribuído (σ<30) · Híbrido (30..60) · Concentrado (≥60).
function gcTipologia(c){
  var deltas=[];
  c.ras.forEach(function(r){ if(r.idx!=null) deltas.push((r.idx-1)*100); });
  if(deltas.length<2) return null;
  var media = deltas.reduce(function(a,b){return a+b;},0)/deltas.length;
  var sigma = Math.sqrt(deltas.reduce(function(a,b){return a+(b-media)*(b-media);},0)/deltas.length);
  var lbl, css, desc;
  if(sigma<30){ lbl='Distribuído'; css='background:#E0F2FE;color:#075985';
    desc='Voto espalhado quase igualmente entre as 28 regiões. Esse candidato não tem reduto chamativo nem ausência preocupante — tem voto razoavelmente parecido em todo lugar.'; }
  else if(sigma<60){ lbl='Híbrido'; css='background:#FEF3C7;color:#92400E';
    desc='Voto com reduto claro, mas que ainda alcança o resto. Tem regiões onde o candidato se destaca bem mais, e também presença razoável fora dessas regiões.'; }
  else { lbl='Concentrado'; css='background:#FCE7F3;color:#9D174D';
    desc='Voto preso a poucas regiões. O candidato tem desempenho expressivo em alguns territórios e quase desaparece em outros.'; }
  return {lbl:lbl, css:css, sigma:sigma, desc:desc};
}

var gcCargoFiltro = 'TODOS';
var gcBusca       = '';
var gcCandSel     = null;
var gcVarSel      = 'votos';
var gcStatusFiltro = null;
var gcSortCol     = 'pct_campo';
var gcSortDir     = 'desc';
var gcMap         = null;
var gcMapInit     = false;
var gcLayer       = null;

var GC_CAMPO_LBL = {progressista:'Progressista',moderado:'Moderado',liberal_conservador:'Liberal/Cons.',outros:'Outros'};
var GC_CAMPO_DOT = {progressista:'gc-dot-prog',moderado:'gc-dot-mod',liberal_conservador:'gc-dot-lib',outros:'gc-dot-out'};
var GC_CAMPO_TAG = {progressista:'gcp-tag-prog',moderado:'gcp-tag-mod',liberal_conservador:'gcp-tag-lib',outros:'gcp-tag-out'};
var GC_CARGO_LBL = {DEPUTADO_DISTRITAL:'Dep. Distrital',DEPUTADO_FEDERAL:'Dep. Federal',SENADOR:'Senador',GOVERNADOR:'Governador'};
var GC_VAR_LBL   = {votos:'Votos absolutos',pct_cargo:'% do cargo',pct_campo:'% do campo',idx:'Performance'};

function gcLerp(a,b,t){return a+(b-a)*t}
function gcHex(r,g,b){return '#'+[r,g,b].map(function(x){return Math.round(x).toString(16).padStart(2,'0');}).join('')}
var GCP_LOW=[245,242,236],GCP_MID=[198,155,90],GCP_HIGH=[120,60,10];
function gcPaleta(t){
  var r,g,b,s;
  if(t<0.5){s=t*2;r=gcLerp(GCP_LOW[0],GCP_MID[0],s);g=gcLerp(GCP_LOW[1],GCP_MID[1],s);b=gcLerp(GCP_LOW[2],GCP_MID[2],s);}
  else{s=(t-0.5)*2;r=gcLerp(GCP_MID[0],GCP_HIGH[0],s);g=gcLerp(GCP_MID[1],GCP_HIGH[1],s);b=gcLerp(GCP_MID[2],GCP_HIGH[2],s);}
  return gcHex(r,g,b);
}
// Paleta divergente para sobre-índice do candidato (centrada em 1.0)
var GCP_NEG=[120,30,30],GCP_NEU=[230,228,222],GCP_POS=[12,90,55];
function gcPaletaDiv(t){
  var r,g,b,s;
  if(t<0.5){s=t*2;r=gcLerp(GCP_NEG[0],GCP_NEU[0],s);g=gcLerp(GCP_NEG[1],GCP_NEU[1],s);b=gcLerp(GCP_NEG[2],GCP_NEU[2],s);}
  else{s=(t-0.5)*2;r=gcLerp(GCP_NEU[0],GCP_POS[0],s);g=gcLerp(GCP_NEU[1],GCP_POS[1],s);b=gcLerp(GCP_NEU[2],GCP_POS[2],s);}
  return gcHex(r,g,b);
}

// ── Navegação ───────────────────────────────────────────────────────────────
// A função irGeoCandidato é chamada pelo click no item 'ni-geo-candidato'
// (definido pelo fase4_v2.py). Ela esconde o conteúdo principal e a seção
// Território (se visível), mostra a seção Candidato, e marca o item ativo.
function irGeoCandidato(){
  var c = document.getElementById('content');       if(c) c.style.display='none';
  var gs = document.getElementById('geo-section');  if(gs) gs.classList.remove('geo-vis');
  var gcs = document.getElementById('geo-cand-section'); if(gcs) gcs.classList.add('gc-vis');
  document.querySelectorAll('.nav-item, .nav-sub-item').forEach(function(el){el.classList.remove('active');});
  var niC = document.getElementById('ni-geo-candidato'); if(niC) niC.classList.add('active');
  var cb = document.getElementById('nav-collapse-btn'); if(cb) cb.classList.add('geo-visible');
  if(!gcMapInit){ gcInitMap(); gcMapInit=true; }
  else { setTimeout(function(){if(gcMap) gcMap.invalidateSize();},50); }
  gcRenderLista();
}

// Quando o usuário sai da seção Candidato (indo pro Território ou qualquer
// outra seção), esconder nossa seção. Fazemos isso interceptando os cliques
// em outros itens de nav — não sobrescrevemos irGeoTerritorio/irSec.
document.addEventListener('DOMContentLoaded', function(){
  document.querySelectorAll('.nav-item, .nav-sub-item').forEach(function(el){
    if(el.id === 'ni-geo-candidato') return;
    el.addEventListener('click', function(){
      var gcs = document.getElementById('geo-cand-section'); if(gcs) gcs.classList.remove('gc-vis');
    });
  });
});
// Se o DOM já carregou quando o script executa, rodar direto
if(document.readyState !== 'loading'){
  document.querySelectorAll('.nav-item, .nav-sub-item').forEach(function(el){
    if(el.id === 'ni-geo-candidato') return;
    el.addEventListener('click', function(){
      var gcs = document.getElementById('geo-cand-section'); if(gcs) gcs.classList.remove('gc-vis');
    });
  });
}

// ── Mapa ────────────────────────────────────────────────────────────────────
var GC_INIT_VIEW={center:[-15.82,-47.93],zoom:10};
function gcResetView(){
  if(!gcMap) return;
  if(gcLayer && gcLayer.getBounds && gcLayer.getBounds().isValid()){
    gcMap.fitBounds(gcLayer.getBounds(), {paddingTopLeft:[10,20], paddingBottomRight:[80,20], animate:true});
  } else {
    gcMap.setView(GC_INIT_VIEW.center, GC_INIT_VIEW.zoom, {animate:true});
  }
}
function gcInitMap(){
  gcMap=L.map('gc-map',{center:GC_INIT_VIEW.center,zoom:GC_INIT_VIEW.zoom,zoomControl:false});
  var zoomCtl=L.control.zoom({position:'bottomright'});
  zoomCtl.addTo(gcMap);
  // Anexa botão "Voltar ao DF" no mesmo bar do zoom (herda estilo Leaflet)
  var zoomBar=zoomCtl.getContainer();
  var alvoBtn=L.DomUtil.create('a','leaflet-control-zoom-fit',zoomBar);
  alvoBtn.href='#'; alvoBtn.title='Voltar ao DF (enquadrar tudo)';
  alvoBtn.role='button';
  alvoBtn.innerHTML='<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display:block;margin:auto"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="4"/><line x1="12" y1="1" x2="12" y2="4"/><line x1="12" y1="20" x2="12" y2="23"/><line x1="1" y1="12" x2="4" y2="12"/><line x1="20" y1="12" x2="23" y2="12"/></svg>';
  L.DomEvent.on(alvoBtn,'click',function(e){L.DomEvent.preventDefault(e);L.DomEvent.stopPropagation(e);gcResetView();});
  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',{
    attribution:'&copy; CARTO &copy; OpenStreetMap',
    subdomains:'abcd',maxZoom:18
  }).addTo(gcMap);
  gcDrawBaseLayer();
}

function gcDrawBaseLayer(){
  if(gcLayer) gcMap.removeLayer(gcLayer);
  if(typeof GEO_DATA === 'undefined'){ return; }
  gcLayer=L.geoJSON(GEO_DATA,{
    style:function(){return{fillColor:'#E5E7EB',fillOpacity:0.35,color:'rgba(0,0,0,0.15)',weight:0.8};},
    onEachFeature:function(feat,layer){
      layer.on('mouseover',function(){layer.setStyle({fillOpacity:0.5,weight:1.2});});
      layer.on('mouseout', function(){gcLayer.resetStyle(layer);});
    }
  }).addTo(gcMap);
}

function gcRenderMapa(){
  if(!gcMap) return;
  if(!gcCandSel){ gcDrawBaseLayer(); return; }
  document.getElementById('gc-map-empty').style.display='none';
  document.getElementById('gc-map-legend').style.display='block';
  var ehDiv = (gcVarSel==='idx');
  var byRa = {};
  gcCandSel.ras.forEach(function(r){ byRa[r.ra] = r[gcVarSel]; });
  var vals = [];
  Object.keys(byRa).forEach(function(k){ if(byRa[k]!=null && !isNaN(byRa[k])) vals.push(byRa[k]); });
  var mn, mx;
  if(ehDiv && vals.length){
    // Centrar em 1.0, pegando o máximo afastamento
    var maxAfast = Math.max.apply(null, vals.map(function(v){return Math.abs(v-1);}));
    if(maxAfast<0.05) maxAfast=0.05;
    mn = 1 - maxAfast; mx = 1 + maxAfast;
  } else {
    mn = vals.length ? Math.min.apply(null,vals) : 0;
    mx = vals.length ? Math.max.apply(null,vals) : 1;
  }
  var rng = mx-mn || 1;
  var paletaFn = ehDiv ? gcPaletaDiv : gcPaleta;
  if(gcLayer) gcMap.removeLayer(gcLayer);
  if(typeof GEO_DATA === 'undefined'){ return; }
  gcLayer = L.geoJSON(GEO_DATA,{
    style:function(feat){
      var nome = feat.properties.RA_PIPE;
      var v = byRa[nome];
      if(v==null){ return{fillColor:'#E5E7EB',fillOpacity:0.25,color:'rgba(0,0,0,0.10)',weight:0.6}; }
      var t = (v-mn)/rng;
      return{fillColor:paletaFn(t),fillOpacity:0.82,color:'rgba(0,0,0,0.15)',weight:0.8};
    },
    onEachFeature:function(feat,layer){
      var nome = feat.properties.RA_PIPE;
      var raObj = gcCandSel.ras.find(function(r){return r.ra===nome;});
      layer.on('mouseover',function(e){
        layer.setStyle({fillOpacity:0.95,weight:1.4});
        var tip = '<div class="gp-tip-nome">'+nome+'</div>';
        if(raObj){
          tip += '<div class="gp-tip-val">Votos: <strong>'+raObj.votos.toLocaleString('pt-BR')+'</strong></div>';
          tip += '<div class="gp-tip-val">% do cargo: <strong>'+raObj.pct_cargo.toFixed(1).replace('.',',')+'%</strong></div>';
          tip += '<div class="gp-tip-val">% do campo: <strong>'+raObj.pct_campo.toFixed(1).replace('.',',')+'%</strong></div>';
          if(raObj.idx!=null){
            var d=Math.round((raObj.idx-1)*100);
            tip += '<div class="gp-tip-val">Performance: <strong>'+(d>=0?'+':'')+d+'%</strong></div>';
          }
        } else {
          tip += '<div class="gp-tip-val" style="font-style:italic">Sem votos nesta RA</div>';
        }
        layer.bindTooltip(tip,{className:'gp-tip',sticky:true,offset:[10,0]}).openTooltip(e.latlng);
      });
      layer.on('mouseout',function(){gcLayer.resetStyle(layer);layer.unbindTooltip();});
    }
  }).addTo(gcMap);
  document.getElementById('gcml-title').innerHTML = (GC_VAR_LBL[gcVarSel]||gcVarSel)+'<span style="font-size:8px;letter-spacing:.5px;text-transform:none;color:var(--muted);font-weight:400;margin-left:6px">· TSE 2022</span>';
  document.getElementById('gcml-min').textContent = gcFmtVal(mn);
  document.getElementById('gcml-max').textContent = gcFmtVal(mx);
  document.getElementById('gcml-grad').style.background = 'linear-gradient(to right,'+paletaFn(0)+','+paletaFn(0.5)+','+paletaFn(1)+')';
}

function gcFmtVal(v){
  if(v==null) return '-';
  if(gcVarSel==='votos') return v>=1000 ? (v/1000).toFixed(1).replace('.',',')+'K' : String(Math.round(v));
  if(gcVarSel==='idx'){
    var d=Math.round((v-1)*100);
    return (d>=0?'+':'')+d+'%';
  }
  return v.toFixed(1).replace('.',',')+'%';
}

function gcRecolor(){
  gcVarSel = document.getElementById('gc-var-sel').value;
  gcRenderMapa();
}

// ── Impressão da consulta (Candidato) ─────────────────────────────────────────
function _gcVarLabel(){
  var sel=document.getElementById('gc-var-sel');
  if(!sel) return gcVarSel;
  var opt=sel.options[sel.selectedIndex];
  return opt ? opt.text : gcVarSel;
}
function _gcCargoLabel(c){
  var L={GOVERNADOR:'Governador',SENADOR:'Senador',
         DEPUTADO_FEDERAL:'Deputado Federal',DEPUTADO_DISTRITAL:'Deputado Distrital'};
  return L[c]||c;
}
function _gcDataPt(){
  var d=new Date();
  function p(n){return String(n).padStart(2,'0');}
  return p(d.getDate())+'/'+p(d.getMonth()+1)+'/'+d.getFullYear()+' às '+p(d.getHours())+':'+p(d.getMinutes());
}

function imprimirCand(){
  if(!gcCandSel){
    alert('Selecione um candidato antes de imprimir.');
    return;
  }

  var varLbl=_gcVarLabel();

  // Cabeçalho
  var dEl=document.getElementById('gc-print-data');
  if(dEl) dEl.textContent='Gerado em '+_gcDataPt();
  var fEl=document.getElementById('gc-print-filtros');
  if(fEl){
    var html='<span class="pf-chip"><strong>Candidato:</strong> '+(gcCandSel.nm||gcCandSel.nome||'')+'</span>';
    html+='<span class="pf-chip"><strong>Cargo:</strong> '+_gcCargoLabel(gcCandSel.cargo)+'</span>';
    html+='<span class="pf-chip"><strong>Partido:</strong> '+(gcCandSel.partido||'?')+'</span>';
    if(gcCandSel.eleito) html+='<span class="pf-chip" style="background:#E1F5EE;color:#085041"><strong>Eleito 2022</strong></span>';
    html+='<span class="pf-chip"><strong>Variável:</strong> '+varLbl+'</span>';
    fEl.innerHTML=html;
  }

  // Tabela top RAs do candidato
  var ras = (gcCandSel.ras||[]).slice();
  ras.sort(function(a,b){
    var av=a[gcVarSel], bv=b[gcVarSel];
    av=(av==null)?-Infinity:av;
    bv=(bv==null)?-Infinity:bv;
    return bv-av;
  });
  var titEl=document.getElementById('gc-print-tabela-titulo');
  if(titEl) titEl.textContent='Ranking das regiões — '+(gcCandSel.nm||gcCandSel.nome||'')+' · '+varLbl;
  var tbl=document.getElementById('gc-print-tabela');
  if(tbl){
    var html='<thead><tr><th style="width:32pt">Pos.</th><th>Região</th><th class="num">'+varLbl+'</th></tr></thead><tbody>';
    ras.forEach(function(r,i){
      html+='<tr><td>'+(i+1)+'</td><td>'+r.ra+'</td><td class="num">'+gcFmtVal(r[gcVarSel])+'</td></tr>';
    });
    html+='</tbody>';
    tbl.innerHTML=html;
  }

  // Renderiza o paper analítico (visível só no print)
  var paperWrap = document.getElementById('gc-paper-wrap');
  if(paperWrap){
    try {
      paperWrap.innerHTML = paperRenderCandidato(gcCandSel);
    } catch(err){
      console.error('Erro ao renderizar paper:', err);
      paperWrap.innerHTML = '';
    }
  }

  if(gcMap){ try{ gcMap.invalidateSize(); }catch(e){} }
  setTimeout(function(){ window.print(); }, 200);
}

// ── Lista ───────────────────────────────────────────────────────────────────
function gcFiltrarLista(){
  gcBusca = (document.getElementById('gc-search').value||'').toLowerCase().trim();
  gcRenderLista();
}

function gcSetCargo(c,btn){
  gcCargoFiltro = c;
  document.querySelectorAll('#gc-cargo-pills .gc-cargo-pill').forEach(function(b){b.classList.remove('gc-active');});
  btn.classList.add('gc-active');
  gcRenderLista();
}

function gcRenderLista(){
  var list = document.getElementById('gc-list');
  list.innerHTML = '';
  var filtrados = GC_DATA.filter(function(c){
    if(gcCargoFiltro!=='TODOS' && c.cargo!==gcCargoFiltro) return false;
    if(gcBusca){
      var alvo = (c.nm+' '+c.partido).toLowerCase();
      if(alvo.indexOf(gcBusca)<0) return false;
    }
    return true;
  });
  if(!filtrados.length){
    list.innerHTML = '<div class="gc-empty-list">Nenhum candidato encontrado</div>';
    return;
  }
  // Eleitos no topo (ordenados por total desc), depois não-eleitos
  filtrados.sort(function(a,b){
    if(a.eleito && !b.eleito) return -1;
    if(!a.eleito && b.eleito) return 1;
    return (b.total||0)-(a.total||0);
  });
  var primeiroNaoEleito = filtrados.findIndex(function(c){ return !c.eleito; });
  filtrados.forEach(function(c, i){
    if(i===primeiroNaoEleito && primeiroNaoEleito>0){
      var sep = document.createElement('div');
      sep.style.cssText = 'height:0.5px;background:var(--bd2);margin:6px 12px;opacity:0.6';
      list.appendChild(sep);
    }
    var div = document.createElement('div');
    div.className = 'gc-item' + (gcCandSel && gcCandSel.nm===c.nm ? ' gc-sel' : '');
    var dotCls = GC_CAMPO_DOT[c.campo]||'gc-dot-out';
    var votosLbl = c.total>=1000 ? (c.total/1000).toFixed(0)+'K' : String(c.total);
    var eleitoBadge = c.eleito
      ? '<span style="font-size:9px;padding:1px 6px;border-radius:8px;background:#E1F5EE;color:#085041;font-weight:500;margin-left:auto;flex-shrink:0">Eleito</span>'
      : '';
    div.innerHTML =
      '<div class="gc-item-dot '+dotCls+'"></div>'+
      '<div class="gc-item-body">'+
        '<div class="gc-item-nome" style="display:flex;align-items:center;gap:6px"><span style="flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis">'+c.nm+'</span>'+eleitoBadge+'</div>'+
        '<div class="gc-item-meta">'+c.partido+' · '+(GC_CARGO_LBL[c.cargo]||c.cargo)+'</div>'+
      '</div>'+
      '<div class="gc-item-votos">'+votosLbl+'</div>';
    div.onclick = function(){ gcSelecionar(c, div); };
    list.appendChild(div);
  });
}

function gcSelecionar(c, el){
  gcCandSel = c;
  gcStatusFiltro = null;
  document.querySelectorAll('.gc-item').forEach(function(e){e.classList.remove('gc-sel');});
  if(el) el.classList.add('gc-sel');
  document.getElementById('gc-candidato-ativo').textContent = c.nm;
  gcRenderMapa();
  gcRenderPanel();
}

// ── Painel direito ──────────────────────────────────────────────────────────
function gcRenderPanel(){
  document.getElementById('gc-right-empty').style.display='none';
  var pb = document.getElementById('gc-panel-body');
  pb.style.display='block';
  var c = gcCandSel;
  var campoTagCls = GC_CAMPO_TAG[c.campo]||'gcp-tag-out';
  var campoLbl = GC_CAMPO_LBL[c.campo]||c.campo;
  var tip = gcTipologia(c);
  var BADGE_STYLE = 'font-size:10px;padding:3px 10px;border-radius:10px;font-weight:500;display:inline-block';
  var PREFIX_STYLE = 'font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.5px';
  var tipBadge = tip
    ? '<span class="tt"><span style="cursor:help;'+BADGE_STYLE+';'+tip.css+'">'+tip.lbl+'</span><span class="tt-box">'+tip.desc+'</span></span>'
    : '';

  // Ranking entre candidatos do mesmo cargo (por votos absolutos)
  var sameCargo = GC_DATA.filter(function(x){ return x.cargo === c.cargo; })
                         .sort(function(a,b){ return (b.total||0) - (a.total||0); });
  var rank = sameCargo.findIndex(function(x){ return x.nm === c.nm; }) + 1;
  var cargoLbl = GC_CARGO_LBL[c.cargo] || c.cargo;
  var statusBg = c.eleito ? '#DCFCE7' : '#FEE2E2';
  var statusCol = c.eleito ? '#15803D' : '#991B1B';
  var statusTxt = c.eleito ? 'Eleito' : 'Não eleito';
  var rankTxt = rank>0 ? rank+'º mais votado · '+cargoLbl : cargoLbl;

  var html = '<div class="gcp-id">'+
    '<div class="gcp-nome" style="display:flex;align-items:center;gap:8px;flex-wrap:wrap">'+
      '<span style="'+BADGE_STYLE+';background:'+statusBg+';color:'+statusCol+';font-weight:600;flex-shrink:0">'+statusTxt+'</span>'+
      '<span>'+c.nm+'</span>'+
    '</div>'+
    '<div style="font-size:11px;color:var(--muted);margin-bottom:8px">'+rankTxt+'</div>'+
    '<div class="gcp-tags" style="display:flex;flex-direction:column;gap:5px;align-items:flex-start">'+
      '<div style="display:flex;align-items:center;gap:5px"><span style="'+PREFIX_STYLE+'">Campo:</span><span class="gcp-tag '+campoTagCls+'" style="'+BADGE_STYLE+'">'+campoLbl+'</span></div>'+
      (tip?'<div style="display:flex;align-items:center;gap:5px"><span style="'+PREFIX_STYLE+'">Voto:</span>'+tipBadge+'</div>':'')+
    '</div>'+
    '<div class="gcp-total-row">'+
      '<div class="gcp-total">'+c.total.toLocaleString('pt-BR')+'</div>'+
      '<div class="gcp-total-lbl">votos em 2022</div>'+
    '</div>'+
  '</div>';


  // 5 zonas estratégicas — cruzamento Performance(candidato) × Força(campo) por RA
  // Idêntico à lógica da Estratégia (Contexto > Estratégia)
  function _idxCampoOf(raName){
    var d = (typeof D !== 'undefined' && D[raName]) ? D[raName] : null;
    if(!d || !d.votos) return null;
    var vc = d.votos[c.cargo] || {};
    var dc = vc[c.campo] || {};
    return (dc.idx != null) ? dc.idx : null;
  }
  function _aptosOf(raName){
    var d = (typeof D !== 'undefined' && D[raName]) ? D[raName] : null;
    return d ? (d.el_aptos || 0) : 0;
  }
  function _zonaCat(idxCand, idxCampo){
    if(idxCand == null || idxCampo == null) return null;
    if(idxCand >= 1.15 && idxCampo >= 1.15) return 'compartilhado';
    if(idxCand >= 1.15)                      return 'pessoal';
    if(idxCand <  0.85 && idxCampo >= 1.15)  return 'conquistar';
    if(idxCand <  0.85)                      return 'sem_espaco';
    return 'esperado';
  }
  var ZONA_DEF = {
    compartilhado: {lbl:'Reduto consolidado',  cor:'#0B5A2E', bg:'#A7F3C8', desc:'Você é forte E o campo é forte aqui — base segura.'},
    pessoal:       {lbl:'Voto pessoal',         cor:'#075985', bg:'#E0F2FE', desc:'Você é forte mas o campo não — voto pessoal, ativo valioso.'},
    esperado:      {lbl:'Esperado',             cor:'#B45309', bg:'#FEF3C7', desc:'Performance proporcional ao tamanho da RA.'},
    conquistar:    {lbl:'Espaço a conquistar',  cor:'#9A3412', bg:'#FFE4D6', desc:'Campo é forte, você não — onde dá pra crescer.'},
    sem_espaco:    {lbl:'Sem espaço pelo campo',cor:'#5A1010', bg:'#FCA5A5', desc:'Nem você nem o campo são fortes — fora do jogo.'}
  };
  var ZONA_ORD = ['compartilhado','pessoal','esperado','conquistar','sem_espaco'];
  var zonaCnt = {compartilhado:0, pessoal:0, esperado:0, conquistar:0, sem_espaco:0};
  // Augmenta cada RA com zona + idxCampo + aptos para uso nas listas estratégicas
  var rasZ = c.ras.map(function(r){
    var idxCampo = _idxCampoOf(r.ra);
    var cat = _zonaCat(r.idx, idxCampo);
    if(cat) zonaCnt[cat]++;
    return {ra:r.ra, votos:r.votos, idx:r.idx, status:r.status,
            pct_cargo:r.pct_cargo, pct_campo:r.pct_campo,
            idxCampo:idxCampo, zona:cat, aptos:_aptosOf(r.ra)};
  });
  var zonaTotal = ZONA_ORD.reduce(function(s,k){return s+zonaCnt[k];}, 0) || 1;

  var zonaTip = '<span class="tt">Mapa estratégico<span class="tt-icon">?</span><span class="tt-box">Cruzamento Performance (do candidato) × Força do campo por RA. Reduto consolidado: ambos fortes (base segura). Voto pessoal: você forte, campo fraco (ativo seu). Esperado: voto proporcional. Espaço a conquistar: campo forte mas você fraco (potencial de crescimento). Sem espaço pelo campo: nem você nem o campo são fortes.</span></span>';
  html += '<div class="gcp-section">'+
    '<div class="gcp-sec-title">'+zonaTip+'</div>'+
    '<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:4px">'+
      ZONA_ORD.map(function(k){
        var z = ZONA_DEF[k];
        var n = zonaCnt[k];
        var pct = Math.round(n/zonaTotal*100);
        return '<div style="background:'+z.bg+';border-radius:6px;padding:6px 5px;text-align:center;min-width:0" title="'+z.desc+'">'+
          '<div style="font-size:18px;font-weight:600;color:'+z.cor+';line-height:1">'+n+'</div>'+
          '<div style="font-size:8px;color:'+z.cor+';font-weight:500;line-height:1.2;margin-top:3px;white-space:normal">'+z.lbl+'</div>'+
          '<div style="font-size:8px;color:'+z.cor+';opacity:.7;margin-top:1px">'+pct+'%</div>'+
        '</div>';
      }).join('')+
    '</div>'+
  '</div>';

  // ── LISTAS ESTRATÉGICAS ─────────────────────────────────────────────────────
  // Lista 1 — Onde já é forte: top 3 RAs em Reduto/Base forte por votos absolutos.
  var fortes = rasZ.filter(function(r){
      return r.status === 'REDUTO' || r.status === 'BASE FORTE';
    })
    .sort(function(a,b){ return (b.votos||0) - (a.votos||0); })
    .slice(0, 3);

  // Lista 2 — Onde dá pra crescer: top 3 da zona "espaço a conquistar" por aptos.
  var conquistar = rasZ.filter(function(r){ return r.zona === 'conquistar'; })
    .sort(function(a,b){ return (b.aptos||0) - (a.aptos||0); })
    .slice(0, 3);

  function _idxTxt(idx){
    if(idx == null) return '—';
    var d = Math.round((idx-1)*100);
    return (d>=0 ? '+' : '') + d + '%';
  }
  function _idxCol(idx){
    if(idx == null) return 'var(--muted)';
    return idx >= 1 ? '#085041' : '#791F1F';
  }
  function _fmtK(v){ return v>=1000 ? (Math.round(v/100)/10).toFixed(1).replace('.',',')+'k' : (v||0).toLocaleString('pt-BR'); }

  // Render lista item — variant 'forte' ou 'conquistar'
  function _listItem(r, variant){
    var stLbl = (r.status==='REDUTO') ? 'Reduto' : (r.status==='BASE FORTE' ? 'Base forte' : '—');
    var stBg = (r.status==='REDUTO') ? '#A7F3C8' : '#DCFCE7';
    var stCol = (r.status==='REDUTO') ? '#0B5A2E' : '#15803D';
    if(variant === 'forte'){
      return '<div style="background:var(--s2);border-radius:7px;padding:7px 10px;display:flex;align-items:center;gap:8px;min-width:0">'+
        '<div style="flex:1;min-width:0">'+
          '<div style="font-size:11px;font-weight:500;color:var(--txt);white-space:nowrap;overflow:hidden;text-overflow:ellipsis" title="'+r.ra+'">'+r.ra+'</div>'+
          '<div style="font-size:9px;color:var(--muted);margin-top:1px"><strong style="color:var(--amber)">'+_fmtK(r.votos)+'</strong> votos do candidato · Performance <strong style="color:'+_idxCol(r.idx)+'">'+_idxTxt(r.idx)+'</strong></div>'+
        '</div>'+
        '<span style="font-size:9px;padding:2px 7px;border-radius:10px;background:'+stBg+';color:'+stCol+';font-weight:500;flex-shrink:0">'+stLbl+'</span>'+
      '</div>';
    } else {
      // conquistar: campo forte, candidato fraco — mostrar gap
      return '<div style="background:var(--s2);border-radius:7px;padding:7px 10px;display:flex;align-items:center;gap:8px;min-width:0">'+
        '<div style="flex:1;min-width:0">'+
          '<div style="font-size:11px;font-weight:500;color:var(--txt);white-space:nowrap;overflow:hidden;text-overflow:ellipsis" title="'+r.ra+'">'+r.ra+'</div>'+
          '<div style="font-size:9px;color:var(--muted);margin-top:1px"><strong>'+_fmtK(r.aptos)+'</strong> eleitores · Campo <strong style="color:#085041">'+_idxTxt(r.idxCampo)+'</strong> · Você <strong style="color:'+_idxCol(r.idx)+'">'+_idxTxt(r.idx)+'</strong></div>'+
        '</div>'+
        '<span style="font-size:9px;padding:2px 7px;border-radius:10px;background:#FFE4D6;color:#9A3412;font-weight:500;flex-shrink:0">A conquistar</span>'+
      '</div>';
    }
  }

  // Lista "Onde já é forte"
  html += '<div class="gcp-section">'+
    '<div class="gcp-sec-title">Onde já é forte</div>'+
    '<div style="font-size:10px;color:var(--muted);margin-bottom:6px;line-height:1.4">Top 3 RAs onde a base eleitoral está consolidada — ordenadas por volume absoluto de votos.</div>'+
    (fortes.length === 0
      ? '<div style="font-size:11px;color:var(--muted);font-style:italic;padding:8px 10px;background:var(--s2);border-radius:7px">Nenhuma RA em Reduto ou Base forte — sem base territorial consolidada.</div>'
      : '<div style="display:flex;flex-direction:column;gap:5px">'+ fortes.map(function(r){return _listItem(r,'forte');}).join('') +'</div>')+
  '</div>';

  // Lista "Onde dá pra crescer"
  html += '<div class="gcp-section">'+
    '<div class="gcp-sec-title">Onde dá pra crescer</div>'+
    '<div style="font-size:10px;color:var(--muted);margin-bottom:6px;line-height:1.4">Top 3 RAs onde o campo político é forte mas o candidato fica abaixo do esperado — prioridades naturais para alocar tempo de campanha.</div>'+
    (conquistar.length === 0
      ? '<div style="font-size:11px;color:var(--muted);font-style:italic;padding:8px 10px;background:var(--s2);border-radius:7px">Não há RAs em "espaço a conquistar" — o candidato já capturou o que dá no seu campo, ou o próprio campo não tem forte presença em RAs onde ele é fraco.</div>'
      : '<div style="display:flex;flex-direction:column;gap:5px">'+ conquistar.map(function(r){return _listItem(r,'conquistar');}).join('') +'</div>')+
  '</div>';

  // Lista 3 — Risco de aliança canibal: RAs onde o candidato é forte E existe outro
  // candidato do mesmo cargo+campo também forte. Aliança ali divide o mesmo voto.
  var sameCargoCampo = GC_DATA.filter(function(x){
    return x.nm !== c.nm && x.cargo === c.cargo && x.campo === c.campo;
  });
  // Threshold: concorrente precisa ter pelo menos 30% dos votos do candidato na RA
  // pra ser uma disputa real (filtra pulverizados que pegaram Reduto sobre base mínima).
  var canibal = rasZ
    .filter(function(r){ return r.status === 'REDUTO' || r.status === 'BASE FORTE'; })
    .map(function(r){
      var minVotos = (r.votos||0) * 0.3;
      var concs = [];
      sameCargoCampo.forEach(function(o){
        var oRa = (o.ras||[]).find(function(x){ return x.ra === r.ra; });
        if(oRa && (oRa.status === 'REDUTO' || oRa.status === 'BASE FORTE') && (oRa.votos||0) >= minVotos){
          concs.push({nm:o.nm, votos:oRa.votos||0});
        }
      });
      concs.sort(function(a,b){ return (b.votos||0) - (a.votos||0); });
      return {ra:r.ra, votosCand:r.votos, concs:concs};
    })
    .filter(function(r){ return r.concs.length > 0; })
    .sort(function(a,b){
      var d = b.concs.length - a.concs.length;
      if(d !== 0) return d;
      return (b.votosCand||0) - (a.votosCand||0);
    })
    .slice(0, 3);

  function _firstNm(s){ return (s||'').split(' ').slice(0,2).join(' '); }
  function _canibalItem(r){
    var lista = r.concs.slice(0,2).map(function(co){
      return '<span style="color:var(--txt)">'+_firstNm(co.nm)+'</span> <span style="color:var(--muted)">('+_fmtK(co.votos)+')</span>';
    }).join(' · ');
    var maisStr = r.concs.length > 2 ? ' <span style="color:var(--muted)">+'+(r.concs.length-2)+' outros</span>' : '';
    return '<div style="background:var(--s2);border-radius:7px;padding:7px 10px;display:flex;align-items:center;gap:8px;min-width:0">'+
      '<div style="flex:1;min-width:0">'+
        '<div style="font-size:11px;font-weight:500;color:var(--txt);white-space:nowrap;overflow:hidden;text-overflow:ellipsis" title="'+r.ra+'">'+r.ra+'</div>'+
        '<div style="font-size:9px;color:var(--muted);margin-top:1px;line-height:1.4">'+r.concs.length+' concorrente'+(r.concs.length>1?'s':'')+' do mesmo campo: '+lista+maisStr+'</div>'+
      '</div>'+
      '<span style="font-size:9px;padding:2px 7px;border-radius:10px;background:#FEE2E2;color:#991B1B;font-weight:500;flex-shrink:0">Disputa</span>'+
    '</div>';
  }

  html += '<div class="gcp-section">'+
    '<div class="gcp-sec-title">Risco de aliança canibal</div>'+
    '<div style="font-size:10px;color:var(--muted);margin-bottom:6px;line-height:1.4">Top 3 RAs onde o candidato é forte mas existe outro do mesmo cargo+campo também forte ali — aliança eleitoral nesses territórios divide o mesmo voto.</div>'+
    (canibal.length === 0
      ? '<div style="font-size:11px;color:var(--muted);font-style:italic;padding:8px 10px;background:var(--s2);border-radius:7px">Sem disputa interna no campo — nenhum outro '+campoLbl+' do mesmo cargo é forte nas mesmas RAs.</div>'
      : '<div style="display:flex;flex-direction:column;gap:5px">'+ canibal.map(_canibalItem).join('') +'</div>')+
  '</div>';

  // ── DIAGNÓSTICO ─────────────────────────────────────────────────────────────
  // Narrativa em 2-3 frases composta dinamicamente a partir das contagens.
  var nCompart = zonaCnt.compartilhado, nPessoal = zonaCnt.pessoal,
      nConq = zonaCnt.conquistar, nSem = zonaCnt.sem_espaco;
  var campoLblLow = (campoLbl||'').toLowerCase();
  var tipLbl = (tip && tip.lbl) ? tip.lbl : null;

  // Frase 1 — perfil do voto + base
  var f1;
  if(tipLbl && nCompart >= 5){
    f1 = 'Voto <strong>'+tipLbl+'</strong> com base sólida no campo <strong>'+campoLbl+'</strong> — '+nCompart+' RAs em Reduto consolidado.';
  } else if(tipLbl && nCompart >= 1){
    f1 = 'Voto <strong>'+tipLbl+'</strong> com base modesta no campo <strong>'+campoLbl+'</strong> ('+nCompart+' RA'+(nCompart>1?'s':'')+' em Reduto consolidado).';
  } else if(tipLbl){
    f1 = 'Voto <strong>'+tipLbl+'</strong> sem RAs de Reduto consolidado — base ainda não consolidada no campo.';
  } else {
    f1 = nCompart > 0 ? 'Base com '+nCompart+' RAs em Reduto consolidado.' : 'Sem RAs de Reduto consolidado.';
  }

  // Frase 2 — voto pessoal (só aparece se relevante)
  var f2 = '';
  if(nPessoal >= 3){
    f2 = ' Tem '+nPessoal+' RAs de <strong>voto pessoal</strong> (forte ali sem o campo) — ativo independente da legenda.';
  } else if(nPessoal >= 1){
    f2 = ' Tem '+nPessoal+' RA'+(nPessoal>1?'s':'')+' de voto pessoal — voto que segue ele, não o campo.';
  }

  // Frase 3 — oportunidade de crescimento
  var f3;
  if(nConq >= 3){
    f3 = ' <strong>'+nConq+' RAs em espaço a conquistar</strong>: campo é forte mas o candidato fica abaixo do esperado — território natural pra crescer numa próxima campanha.';
  } else if(nConq >= 1){
    f3 = ' '+nConq+' RA'+(nConq>1?'s':'')+' em espaço a conquistar (campo forte, ele fraco) — janela limitada pra crescer dentro do mesmo campo.';
  } else {
    f3 = ' Sem RAs em espaço a conquistar — o candidato já capturou o que existe de força do campo, crescer agora exige ir além da base ideológica.';
  }

  // Frase 4 — limitação (só se sem_espaco for muitos)
  var f4 = '';
  if(nSem >= zonaTotal*0.4){
    f4 = ' Em '+nSem+' RAs nem o candidato nem o campo são fortes — terreno improdutivo, fora do mapa de prioridade.';
  }

  var diagTxt = f1 + f2 + f3 + f4;

  html += '<div class="gcp-section">'+
    '<div class="gcp-sec-title">Diagnóstico</div>'+
    '<div class="gp-narr">'+diagTxt+'</div>'+
  '</div>';

  pb.innerHTML = html;
}

function gcStatusBoxHtml(status, cls, count, lbl){
  var ativo = gcStatusFiltro===status ? ' gcp-sb-active' : '';
  return "<div class=\"gcp-status-box "+cls+ativo+"\" onclick=\"gcToggleStatus('"+status+"')\">"+
    "<div class=\"gcp-status-val\">"+count+"</div>"+
    "<div class=\"gcp-status-lbl\">"+lbl+"</div>"+
  "</div>";
}

function gcToggleStatus(st){
  gcStatusFiltro = (gcStatusFiltro===st) ? null : st;
  gcRenderPanel();
}

// ── Tabela ──────────────────────────────────────────────────────────────────
function gcRenderTabela(){
  var wrap = document.getElementById('gcp-tbl-wrap');
  if(!wrap) return;
  var c = gcCandSel;
  var ras = c.ras.slice();
  if(gcStatusFiltro){
    ras = ras.filter(function(r){
      if(gcStatusFiltro==='CAMPO MEDIO'){ return r.status==='CAMPO MEDIO' || r.status==='CAMPO MÉDIO'; }
      return r.status===gcStatusFiltro;
    });
  }
  ras.sort(function(a,b){
    var va, vb;
    if(gcSortCol==='ra'){ va=a.ra; vb=b.ra; }
    else { va=a[gcSortCol]||0; vb=b[gcSortCol]||0; }
    if(va<vb) return gcSortDir==='asc'? -1 : 1;
    if(va>vb) return gcSortDir==='asc'?  1 : -1;
    return 0;
  });
  var cls = function(col){ return gcSortCol===col ? ' class="gcp-sorted"' : ''; };
  var idxTipBox = '<span class="tt">Performance<span class="tt-icon">?</span><span class="tt-box">Mostra se a região entrega mais ou menos votos do que esperado pelo seu tamanho. Plano Piloto tem cerca de 9% do eleitorado do DF — se o candidato fosse perfeitamente proporcional, deveria ter 9% dos votos dele lá. +30% ou mais = reduto; +15% a +30% = base forte; −15% a +15% = no esperado; −15% a −30% = base fraca; ≤ −30% = ausência. Compara o candidato com ele mesmo, não entre candidatos.</span></span>';
  var head = '<table class="gcp-tbl"><thead><tr>'+
      "<th"+cls('ra')+" onclick=\"gcSort('ra')\">RA</th>"+
      "<th"+cls('votos')+" onclick=\"gcSort('votos')\" style=\"text-align:right\">Votos</th>"+
      "<th"+cls('pct_cargo')+" onclick=\"gcSort('pct_cargo')\" style=\"text-align:right\">% cargo</th>"+
      "<th"+cls('pct_campo')+" onclick=\"gcSort('pct_campo')\" style=\"text-align:right\">% campo</th>"+
      "<th"+cls('idx')+" onclick=\"gcSort('idx')\" style=\"text-align:right\">"+idxTipBox+"</th>"+
      '<th>Status</th>'+
    '</tr></thead><tbody>';
  var body = '';
  if(!ras.length){
    body = '<tr><td colspan="6" style="text-align:center;color:var(--muted);padding:10px;font-style:italic">Nenhuma RA com este filtro</td></tr>';
  } else {
    var STCLS = {'REDUTO':'gcp-st-reduto','BASE FORTE':'gcp-st-forte','CAMPO MEDIO':'gcp-st-medio','CAMPO MÉDIO':'gcp-st-medio','BASE FRACA':'gcp-st-fraca','AUSENCIA':'gcp-st-ausencia'};
    var STLBL = {'REDUTO':'Reduto','BASE FORTE':'Base forte','CAMPO MEDIO':'Esperado','CAMPO MÉDIO':'Esperado','BASE FRACA':'Base fraca','AUSENCIA':'Ausência'};
    ras.forEach(function(r){
      var stCls = STCLS[r.status] || 'gcp-st-medio';
      var stLbl = STLBL[r.status] || '—';
      var idxDelta = (r.idx!=null) ? Math.round((r.idx-1)*100) : null;
      var idxTxt = (idxDelta==null) ? '—' : ((idxDelta>=0?'+':'') + idxDelta + '%');
      var idxColor = (idxDelta==null) ? 'var(--muted)' : (idxDelta>=0 ? '#085041' : '#791F1F');
      body += '<tr>'+
        '<td class="gcp-ra" title="'+r.ra+'">'+r.ra+'</td>'+
        '<td class="gcp-num">'+r.votos.toLocaleString('pt-BR')+'</td>'+
        '<td class="gcp-num">'+r.pct_cargo.toFixed(1).replace('.',',')+'%</td>'+
        '<td class="gcp-num">'+r.pct_campo.toFixed(1).replace('.',',')+'%</td>'+
        '<td class="gcp-num" style="color:'+idxColor+';font-weight:500">'+idxTxt+'</td>'+
        '<td><span class="gcp-status-tag '+stCls+'">'+stLbl+'</span></td>'+
      '</tr>';
    });
  }
  wrap.innerHTML = head + body + '</tbody></table>';
}

function gcSort(col){
  if(gcSortCol===col){ gcSortDir = gcSortDir==='asc'?'desc':'asc'; }
  else { gcSortCol = col; gcSortDir = (col==='ra') ? 'asc' : 'desc'; }
  gcRenderTabela();
}

// ════════════════════════ PAPER DO CANDIDATO (PDF) ════════════════════════════
// Gera o relatório analítico de uma página A4 paisagem que sai junto com o
// mapa quando o usuário clica Imprimir. Lógica espelhada de exemplo_relatorio_pdf.py.

var PAPER_ZONA_DEF = {
  compartilhado: {lbl:'Reduto consolidado',  cor:'#0B5A2E', bg:'#A7F3C8'},
  pessoal:       {lbl:'Voto pessoal',         cor:'#075985', bg:'#E0F2FE'},
  esperado:      {lbl:'Esperado',             cor:'#B45309', bg:'#FEF3C7'},
  conquistar:    {lbl:'Espaço a conquistar',  cor:'#9A3412', bg:'#FFE4D6'},
  sem_espaco:    {lbl:'Sem espaço pelo campo','cor':'#5A1010', bg:'#FCA5A5'}
};
var PAPER_PDAD_KEYS = ['renda_pc','pct_ab','pct_super','pct_serv_fed','el_jov','el_ido'];
var PAPER_PERFIL_LBL = {
  renda_pc:   {nm:'Renda p/capita', fmt:'rs'},
  pct_ab:     {nm:'Classe A/B',     fmt:'pct'},
  pct_super:  {nm:'Ensino superior',fmt:'pct'},
  pct_serv_fed:{nm:'Serv. federal', fmt:'pct'},
  el_jov:     {nm:'Jovens (16-24)', fmt:'pct'},
  el_ido:     {nm:'Idosos (60+)',   fmt:'pct'}
};
var PAPER_CARGO_LBL = {GOVERNADOR:'Governador',SENADOR:'Senador',DEPUTADO_FEDERAL:'Dep. Federal',DEPUTADO_DISTRITAL:'Dep. Distrital'};
var PAPER_CN = {progressista:'Progressista',moderado:'Moderado',liberal_conservador:'Liberal/Cons.',outros:'Outros'};
var PAPER_CCOR = {progressista:'#A32D2D',moderado:'#0F6E56',liberal_conservador:'#854F0B',outros:'#6B7280'};
var PAPER_CBG  = {progressista:'#FCEBEB',moderado:'#E1F5EE',liberal_conservador:'#FAEEDA',outros:'#F1EFE8'};

// DF baseline (calculado uma vez)
var PAPER_DF = (function(){
  var avg = {};
  PAPER_PDAD_KEYS.forEach(function(k){
    var s=0,w=0;
    Object.keys(D).forEach(function(ra){
      var d = D[ra]; if(!d || d.sem_zona) return;
      var v = d[k], p = d.el_aptos;
      if(v!=null && p){ s+=v*p; w+=p; }
    });
    avg[k] = w ? s/w : null;
  });
  return avg;
})();

function paperFmt(v){ return (v==null?'—':String(Math.round(v)).replace(/\B(?=(\d{3})+(?!\d))/g,'.')); }
function paperFmtK(v){
  if(v==null) return '—';
  if(v>=1000) return (Math.round(v/100)/10).toFixed(1).replace('.',',')+'k';
  return paperFmt(v);
}
function paperIdxPct(idx){
  if(idx==null) return '—';
  var d = Math.round((idx-1)*100);
  return (d>=0?'+':'')+d+'%';
}
function paperIdxCol(idx){
  if(idx==null) return 'var(--muted)';
  return idx>=1 ? '#085041' : '#791F1F';
}
function paperFmtPct(v){ return v==null?'—':v.toFixed(1).replace('.',',')+'%'; }
function paperFmtRs(v){ return v==null?'—':'R$ '+paperFmt(v); }
function paperFirst2(s){ return (s||'').split(' ').slice(0,2).join(' '); }
function paperEsc(s){ return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

function paperZonaCat(idxC, idxK){
  if(idxC==null || idxK==null) return null;
  if(idxC>=1.15 && idxK>=1.15) return 'compartilhado';
  if(idxC>=1.15)               return 'pessoal';
  if(idxC<0.85 && idxK>=1.15)  return 'conquistar';
  if(idxC<0.85)                return 'sem_espaco';
  return 'esperado';
}

function paperTipologia(c){
  var deltas=[];
  (c.ras||[]).forEach(function(r){ if(r.idx!=null) deltas.push((r.idx-1)*100); });
  if(deltas.length<2) return null;
  var media = deltas.reduce(function(a,b){return a+b;},0)/deltas.length;
  var sigma = Math.sqrt(deltas.reduce(function(a,b){return a+(b-media)*(b-media);},0)/deltas.length);
  if(sigma<30) return {lbl:'Distribuído', css:'background:#E0F2FE;color:#075985'};
  if(sigma<60) return {lbl:'Híbrido',     css:'background:#FEF3C7;color:#92400E'};
  return            {lbl:'Concentrado', css:'background:#FCE7F3;color:#9D174D'};
}

function paperRenderCandidato(c){
  if(!c) return '';

  // Augmenta RAs com zona, idxCampo, aptos
  var rasZ = (c.ras||[]).map(function(r){
    var d = D[r.ra] || {};
    var idxCampo = (((d.votos||{})[c.cargo]||{})[c.campo]||{}).idx;
    if(idxCampo==null) idxCampo = null;
    var aptos = d.el_aptos || 0;
    var cat = paperZonaCat(r.idx, idxCampo);
    return {ra:r.ra, votos:r.votos, idx:r.idx, status:r.status,
            pct_cargo:r.pct_cargo, pct_campo:r.pct_campo,
            idxCampo:idxCampo, zona:cat, aptos:aptos};
  });

  var zCnt = {compartilhado:0,pessoal:0,esperado:0,conquistar:0,sem_espaco:0};
  rasZ.forEach(function(r){ if(r.zona) zCnt[r.zona]++; });
  var zTot = Object.keys(zCnt).reduce(function(s,k){return s+zCnt[k];},0) || 1;

  // Ranking
  var same = GC_DATA.filter(function(x){return x.cargo===c.cargo;}).slice()
                    .sort(function(a,b){return (b.total||0)-(a.total||0);});
  var rank = same.findIndex(function(x){return x.nm===c.nm;}) + 1;
  var tip = paperTipologia(c);

  // Listas
  var fortes = rasZ.filter(function(r){return r.status==='REDUTO'||r.status==='BASE FORTE';})
                   .sort(function(a,b){return (b.votos||0)-(a.votos||0);}).slice(0,3);
  var conquistar = rasZ.filter(function(r){return r.zona==='conquistar';})
                       .sort(function(a,b){return (b.aptos||0)-(a.aptos||0);}).slice(0,3);

  // Perfil
  function _wAvg(items, key, weight){
    var s=0,w=0;
    items.forEach(function(x){
      var v = (x.pdad? x.pdad[key] : null);
      if(v==null){ var d = D[x.ra]; if(d) v = d[key]; }
      var p = x[weight];
      if(v!=null && p){ s+=v*p; w+=p; }
    });
    return w?s/w:null;
  }
  var perfil = {};
  PAPER_PDAD_KEYS.forEach(function(k){
    perfil[k] = _wAvg(rasZ, k, 'votos');
  });

  // Header
  var statusLbl = c.eleito ? 'Eleito' : 'Não eleito';
  var statusBg  = c.eleito ? '#DCFCE7' : '#FEE2E2';
  var statusCor = c.eleito ? '#15803D' : '#991B1B';
  var campoLbl  = PAPER_CN[c.campo] || c.campo;
  var voto = tip ? '<span class="paper-tag" style="'+tip.css+'">'+tip.lbl+'</span>' : '';

  // Logo: reaproveita a logomarca já embarcada no DOM (em .print-logo)
  var _logoEl = document.querySelector('.print-logo');
  var logoHtml = (_logoEl && _logoEl.src)
    ? '<img class="paper-logo-img" src="'+_logoEl.src+'" alt="Opinião"/>'
    : '<div class="paper-logo">opinião</div>';

  var header = ''+
    '<div class="paper-hd">'+
      logoHtml+
      '<div class="paper-info">'+
        '<div class="paper-nome">'+paperEsc(c.nm)+'</div>'+
        '<div class="paper-line">'+
          '<span class="paper-tag" style="background:'+statusBg+';color:'+statusCor+';font-weight:600">'+statusLbl+'</span>'+
          '<span style="font-size:9pt;color:var(--muted)">· '+rank+'º mais votado · '+(PAPER_CARGO_LBL[c.cargo]||c.cargo)+' · <strong style="color:#B45309">'+paperFmt(c.total)+'</strong> votos</span>'+
        '</div>'+
        '<div class="paper-line">'+
          '<span class="paper-tag" style="background:'+(PAPER_CBG[c.campo]||'#F1EFE8')+';color:'+(PAPER_CCOR[c.campo]||'#6B7280')+'">'+campoLbl+'</span>'+
          voto+
          '<span style="font-size:9pt;color:var(--muted)">· '+paperEsc(c.partido||'?')+'</span>'+
        '</div>'+
      '</div>'+
      '<div class="paper-data">Diagnóstico estratégico</div>'+
    '</div>';

  // Card "Onde já é forte"
  function cardForte(r){
    var z = r.zona, zd = z?PAPER_ZONA_DEF[z]:null;
    var tagBg = zd?zd.bg:'#F1EFE8', tagCor = zd?(zd.cor||zd['cor']):'#6B7280', tagLbl = zd?zd.lbl:'—';
    return '<div class="paper-card">'+
      '<div class="paper-card-head">'+
        '<div class="paper-card-ra">'+paperEsc(r.ra)+'</div>'+
        '<div class="paper-card-tag" style="background:'+tagBg+';color:'+tagCor+'">'+tagLbl+'</div>'+
      '</div>'+
      '<div class="paper-card-meta">'+
        '<span style="color:#B45309;font-weight:600">'+paperFmtK(r.votos)+'</span> votos'+
        ' · <span style="color:'+paperIdxCol(r.idx)+';font-weight:600">'+paperIdxPct(r.idx)+'</span>'+
      '</div>'+
    '</div>';
  }
  function cardConquistar(r){
    return '<div class="paper-card">'+
      '<div class="paper-card-head">'+
        '<div class="paper-card-ra">'+paperEsc(r.ra)+'</div>'+
        '<div class="paper-card-tag" style="background:#FFE4D6;color:#9A3412">A conquistar</div>'+
      '</div>'+
      '<div class="paper-card-meta">'+
        '<strong>'+paperFmtK(r.aptos)+'</strong> eleitores'+
        ' · campo <span style="color:#085041;font-weight:600">'+paperIdxPct(r.idxCampo)+'</span>'+
        ' · você <span style="color:#791F1F;font-weight:600">'+paperIdxPct(r.idx)+'</span>'+
      '</div>'+
    '</div>';
  }
  function padded(items, fn){
    var out = items.slice(0,3).map(fn);
    while(out.length<3) out.push('<div class="paper-card paper-card-empty">—</div>');
    return out.join('');
  }
  var fortesHtml = fortes.length ? padded(fortes, cardForte) :
    '<div class="paper-empty">Nenhuma RA em Reduto ou Base forte.</div>';
  var conquistarHtml = conquistar.length ? padded(conquistar, cardConquistar) :
    '<div class="paper-empty">Sem RAs em "espaço a conquistar" — base do campo já capturada.</div>';

  // Diagnóstico
  var nC=zCnt.compartilhado, nP=zCnt.pessoal, nQ=zCnt.conquistar, nS=zCnt.sem_espaco;
  var tipNm = tip ? tip.lbl : null;
  var f1;
  if(tipNm && nC>=5)      f1 = 'Voto <strong>'+tipNm+'</strong> com base sólida no campo <strong>'+campoLbl+'</strong> — '+nC+' RAs em Reduto consolidado.';
  else if(tipNm && nC>=1) f1 = 'Voto <strong>'+tipNm+'</strong> com base modesta no campo <strong>'+campoLbl+'</strong> ('+nC+' RA'+(nC>1?'s':'')+' em Reduto consolidado).';
  else if(tipNm)          f1 = 'Voto <strong>'+tipNm+'</strong> sem RAs de Reduto consolidado — base ainda não consolidada no campo.';
  else                    f1 = nC>0 ? 'Base com '+nC+' RAs em Reduto consolidado.' : 'Sem RAs de Reduto consolidado.';
  var f2 = '';
  if(nP>=3)      f2 = ' Tem '+nP+' RAs de <strong>voto pessoal</strong> (forte ali sem o campo) — ativo independente da legenda.';
  else if(nP>=1) f2 = ' Tem '+nP+' RA'+(nP>1?'s':'')+' de voto pessoal — voto que segue ele, não o campo.';
  var f3;
  if(nQ>=3)      f3 = ' <strong>'+nQ+' RAs em espaço a conquistar</strong>: campo é forte mas o candidato fica abaixo do esperado — território natural pra crescer numa próxima campanha.';
  else if(nQ>=1) f3 = ' '+nQ+' RA'+(nQ>1?'s':'')+' em espaço a conquistar (campo forte, ele fraco) — janela limitada pra crescer dentro do mesmo campo.';
  else           f3 = ' Sem RAs em espaço a conquistar — o candidato já capturou o que existe de força do campo, crescer agora exige ir além da base ideológica.';
  var f4 = '';
  if(nS >= zTot*0.4) f4 = ' Em '+nS+' RAs nem o candidato nem o campo são fortes — terreno improdutivo, fora do mapa de prioridade.';
  var diagTxt = f1+f2+f3+f4;

  // Perfil cards
  function fmtPdadVal(k, v){
    if(v==null) return '—';
    if(PAPER_PERFIL_LBL[k].fmt==='rs') return paperFmtRs(v);
    return paperFmtPct(v);
  }
  var perfilHtml = PAPER_PDAD_KEYS.map(function(k){
    var lbl = PAPER_PERFIL_LBL[k].nm;
    var cv = perfil[k], dv = PAPER_DF[k];
    var cor = 'var(--txt)';
    if(cv!=null && dv!=null){
      var d = cv-dv;
      if(Math.abs(d) < (dv*0.02 || 0.5)) cor = 'var(--txt)';
      else if(d>0) cor = '#085041';
      else         cor = '#791F1F';
    }
    return '<div class="paper-perfil-card">'+
      '<div class="paper-perfil-lbl">'+lbl+'</div>'+
      '<div class="paper-perfil-val" style="color:'+cor+'">'+fmtPdadVal(k,cv)+'</div>'+
      '<div class="paper-perfil-ref">DF: '+fmtPdadVal(k,dv)+'</div>'+
    '</div>';
  }).join('');

  // Tabela
  var rasOrd = rasZ.slice().sort(function(a,b){return (b.idx||0)-(a.idx||0);});
  var tbodyHtml = rasOrd.map(function(r){
    var z = r.zona, zd = z?PAPER_ZONA_DEF[z]:null;
    var tagBg = zd?zd.bg:'#F1EFE8', tagCor = zd?(zd.cor||zd['cor']):'#6B7280', tagLbl = zd?zd.lbl:'—';
    return '<tr>'+
      '<td class="ra">'+paperEsc(r.ra)+'</td>'+
      '<td class="num">'+paperFmt(r.votos)+'</td>'+
      '<td class="num" style="color:'+paperIdxCol(r.idx)+';font-weight:500">'+paperIdxPct(r.idx)+'</td>'+
      '<td class="num" style="color:'+paperIdxCol(r.idxCampo)+';font-weight:500">'+paperIdxPct(r.idxCampo)+'</td>'+
      '<td><span class="paper-st-badge" style="background:'+tagBg+';color:'+tagCor+'">'+tagLbl+'</span></td>'+
    '</tr>';
  }).join('');

  // Hoje (data)
  var d = new Date();
  function pp(n){return String(n).padStart(2,'0');}
  var today = pp(d.getDate())+'/'+pp(d.getMonth()+1)+'/'+d.getFullYear();

  // Monta paper completo
  return ''+
    '<div class="paper-report">'+
      header+
      '<div class="paper-2col">'+
        '<div class="paper-left">'+
          '<div class="paper-sec">'+
            '<div class="paper-sec-title">Onde já é forte</div>'+
            '<div class="paper-cards-row">'+fortesHtml+'</div>'+
          '</div>'+
          '<div class="paper-sec">'+
            '<div class="paper-sec-title">Onde dá pra crescer</div>'+
            '<div class="paper-cards-row">'+conquistarHtml+'</div>'+
          '</div>'+
          '<div class="paper-sec">'+
            '<div class="paper-sec-title">Diagnóstico</div>'+
            '<div class="paper-diag">'+diagTxt+'</div>'+
          '</div>'+
          '<div class="paper-sec">'+
            '<div class="paper-sec-title">Perfil Médio do Eleitor do Candidato (Estimado)</div>'+
            '<div class="paper-perfil-grid">'+perfilHtml+'</div>'+
          '</div>'+
        '</div>'+
        '<div class="paper-right">'+
          '<div class="paper-sec" style="margin-top:0">'+
            '<div class="paper-sec-title">Desempenho por RA</div>'+
            '<div class="paper-tbl-wrap"><table class="paper-tbl">'+
              '<thead><tr>'+
                '<th>RA</th>'+
                '<th style="text-align:right">Votos</th>'+
                '<th style="text-align:right">Perf.</th>'+
                '<th style="text-align:right">Campo</th>'+
                '<th>Zona</th>'+
              '</tr></thead>'+
              '<tbody>'+tbodyHtml+'</tbody>'+
            '</table></div>'+
          '</div>'+
        '</div>'+
      '</div>'+
      '<div class="paper-foot">Fontes: <strong>PDAD 2021</strong> (IPEDF) · <strong>TSE 2022</strong>. Instrumento gerado pelo painel <strong>Estrategos</strong> — solução de Inteligência Política da <strong>Opinião Informação Estratégica</strong>. '+today+'</div>'+
    '</div>';
}

// Atalho pra imprimir relatório do candidato a partir de outros menus
// (Contexto > Candidatos). Renderiza só o paper, sem o mapa.
function imprimirRelCandidatoPorNome(nome){
  if(!nome){ alert('Selecione um candidato antes de imprimir o relatório.'); return; }
  var c = (typeof GC_DATA !== 'undefined') ? GC_DATA.find(function(x){ return x.nm === nome; }) : null;
  if(!c){ alert('Candidato "'+nome+'" não encontrado nos dados.'); return; }
  var iso = document.getElementById('rel-paper-iso');
  if(!iso) return;
  iso.innerHTML = paperRenderCandidato(c);
  document.body.classList.add('print-iso');
  setTimeout(function(){
    window.print();
    setTimeout(function(){ document.body.classList.remove('print-iso'); }, 300);
  }, 120);
}

// (Diagnóstico estratégico — ex 4 quadrantes — removido no Bloco D.5;
//  reconstrução sob nova fórmula prevista no Bloco E, dentro de Estratégia.)
"""


def main():
    import time
    t0 = time.time()
    print()
    print("  Candidato -- Injetando no dashboard")
    print("  " + "-" * 42)

    if not DASHBOARD_IN.exists():
        print(f"  ERRO: {DASHBOARD_IN} nao encontrado. Rode injeta_geopolitica.py primeiro.")
        return
    if not CSV_IN.exists():
        print(f"  ERRO: {CSV_IN} nao encontrado.")
        return

    print(f"  [1/4] Lendo {DASHBOARD_IN}...", end="", flush=True)
    html = DASHBOARD_IN.read_text(encoding="utf-8")
    print(f"\r  [1/4] Dashboard lido ({len(html)//1024} KB)          ")

    # Verificar se o item de nav ja existe (fase4_v2.py deve ter criado)
    if 'id="ni-geo-candidato"' not in html:
        print(f"  AVISO: item 'ni-geo-candidato' nao encontrado na nav.")
        print(f"         Verifique se o fase4_v2.py esta atualizado (deve ter os")
        print(f"         sub-items de Geopolitica: Territorio e Candidato).")
        print(f"         A secao sera injetada mesmo assim, mas pode ficar inacessivel.")

    print(f"  [2/4] Processando CSV...", end="", flush=True)
    candidatos = carregar_dados()
    por_cargo = defaultdict(int)
    for c in candidatos: por_cargo[c["cargo"]] += 1
    resumo_cargo = " / ".join(
        f"{por_cargo.get(k,0)} {lbl}" for k, lbl in [
            ("DEPUTADO_DISTRITAL","Dist."),("DEPUTADO_FEDERAL","Fed."),
            ("SENADOR","Sen."),("GOVERNADOR","Gov.")
        ] if por_cargo.get(k,0) > 0
    )
    print(f"\r  [2/4] {len(candidatos)} candidatos ({resumo_cargo})")

    print(f"  [3/4] Injetando CSS + HTML + JS...", end="", flush=True)

    # CSS antes de </style>
    html = html.replace("</style>", CSS_CAND + "\n</style>", 1)

    # Substituir placeholder da logo (mesmo arquivo cacheado pelo injeta_geopolitica.py)
    logo_path = Path("logo_opiniao.png")
    if logo_path.exists():
        import base64 as _b64
        logo_src = "data:image/png;base64," + _b64.b64encode(logo_path.read_bytes()).decode("ascii")
    else:
        logo_src = "https://raw.githubusercontent.com/aag1974/dashboard-ivv/main/logo.png"
    cand_html = CAND_SECTION_HTML.replace("__LOGO_SRC__", logo_src)

    # Seção HTML — inserir dentro de #app. Múltiplos marcadores em ordem de preferência:
    inserted = False
    markers = [
        # Depois do fim do geo-section (padrão do injeta_geopolitica.py v1)
        '<!-- ══ /GEOPOLÍTICA ═════════════════════════════════════════ -->',
        '<!-- /GEOPOLITICA -->',
        # Antes do fechamento do #app (fallback genérico)
        '</div>\n\n<!-- MODAL',
        '</div>\n<!-- MODAL',
    ]
    for m in markers:
        if m in html:
            html = html.replace(m, m + "\n" + cand_html, 1)
            inserted = True
            break
    if not inserted:
        # Último recurso: antes de </body>
        html = html.replace("</body>", cand_html + "\n</body>", 1)

    # JS com dados embarcados — antes do último </script>
    cand_b64 = base64.b64encode(
        json.dumps(candidatos, ensure_ascii=True, separators=(",", ":")).encode("utf-8")
    ).decode("ascii")
    js = CAND_JS.replace("__CAND_B64__", cand_b64)
    last = html.rfind("</script>")
    html = html[:last] + js + "\n</script>" + html[last+9:]
    print(f"\r  [3/4] CSS + HTML + JS injetados                     ")

    print(f"  [4/4] Salvando...", end="", flush=True)
    OUTPUT.write_text(html, encoding="utf-8")
    kb = len(html.encode()) // 1024
    elapsed = time.time() - t0
    print(f"\r  [4/4] Salvo: {OUTPUT}  ({kb} KB)       ")
    print()
    print(f"  Concluido em {elapsed:.1f}s -- abra {OUTPUT} no navegador")
    print()


if __name__ == "__main__":
    main()
