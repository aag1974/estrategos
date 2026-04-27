"""
injeta_geopolitica.py — adaptado para fase4_v2.py
===================================================
Lê dashboard_spe_df.html + Limite_RA_20190.json
e injeta a seção GeoPolítica integrada ao nav.

Uso:
  python3 injeta_geopolitica.py

Saída:
  dashboard_com_geo.html
"""

import json, base64, re, urllib.request
from pathlib import Path

DASHBOARD_IN = Path("dashboard_spe_df.html")
GEOJSON_PATH = Path("Limite_RA_20190.json")
OUTPUT       = Path("dashboard_com_geo.html")
LOGO_URL     = "https://raw.githubusercontent.com/aag1974/dashboard-ivv/main/logo.png"
LOGO_CACHE   = Path("logo_opiniao.png")


def carregar_logo_b64():
    """Baixa (uma vez) a logomarca e devolve como data URL para embutir no HTML."""
    try:
        if not LOGO_CACHE.exists():
            urllib.request.urlretrieve(LOGO_URL, str(LOGO_CACHE))
        b = base64.b64encode(LOGO_CACHE.read_bytes()).decode("ascii")
        return "data:image/png;base64," + b
    except Exception as e:
        print(f"   Aviso: falha ao embarcar logo ({e}); usando URL externa.")
        return LOGO_URL

GEO_PARA_PIPE = {
    "Plano Piloto":              "Brasília (Plano Piloto)",
    "Sudoeste/ Octogonal":       "Sudoeste/Octogonal",
    "SCIA":                      "SCIA/Estrutural",
    "Sol Nascente/  Pôr do Sol": "Sol Nascente/Pôr do Sol",
}

def processar_geojson():
    with open(GEOJSON_PATH, encoding="utf-8") as f:
        geo = json.load(f)
    for feat in geo["features"]:
        geo_nome  = feat["properties"]["ra"]
        pipe_nome = GEO_PARA_PIPE.get(geo_nome, geo_nome)
        feat["properties"]["RA_PIPE"]  = pipe_nome
    return geo

CSS_GEO = """
/* ══ GeoPolítica ══════════════════════════════════════════════════════════════ */
#sidenav{transition:width .22s ease,min-width .22s ease}
#sidenav.nav-collapsed{width:0!important;min-width:0!important;overflow:hidden;border-right:none}
#nav-collapse-btn{
  position:fixed;top:50%;left:188px;transform:translateY(-50%);
  width:16px;height:40px;background:var(--s1);border:0.5px solid var(--bd2);
  border-left:none;border-radius:0 6px 6px 0;cursor:pointer;z-index:150;
  display:none;align-items:center;justify-content:center;
  font-size:10px;color:var(--muted);transition:left .22s ease;
}
#nav-collapse-btn.geo-visible{display:flex}
#nav-collapse-btn:hover{color:var(--amber)}
#geo-section{display:none;flex:1;flex-direction:column;overflow:hidden;background:var(--bg)}
#geo-section.geo-vis{display:flex}

/* Toolbar */
#geo-toolbar{height:40px;display:flex;align-items:center;background:var(--s1);border-bottom:0.5px solid var(--bd);flex-shrink:0}
.geo-tb-group{display:flex;align-items:center;gap:8px;padding:0 14px;height:100%}
.geo-tb-sep{width:0.5px;background:var(--bd);height:100%;flex-shrink:0}
.geo-tb-lbl{font-size:9px;letter-spacing:1.5px;text-transform:uppercase;color:var(--muted);white-space:nowrap}
select.geo-sel{background:var(--s1);border:0.5px solid var(--bd2);border-radius:6px;color:var(--txt);font-size:12px;padding:4px 8px;cursor:pointer;outline:none;font-family:inherit}
select.geo-sel:hover{border-color:var(--amber)}

/* Pills — cargo (azul) e campo (roxo) */
.geo-pill{font-size:11px;padding:3px 10px;border-radius:20px;cursor:pointer;border:0.5px solid var(--bd2);background:var(--s1);color:var(--muted);font-family:inherit;transition:all .15s}
.geo-pill:hover{color:var(--txt)}
.geo-pill.gp-cargo-on{background:#E6F1FB;border-color:#185FA5;color:#0C447C;font-weight:500}
.geo-pill.gp-campo-on{background:#EEEDFE;border-color:#534AB7;color:#3C3489;font-weight:500}

/* 3 colunas */
#geo-body{display:grid;grid-template-columns:25% 50% 25%;flex:1;overflow:hidden;min-height:0}
#geo-left{background:var(--s1);border-right:0.5px solid var(--bd);display:flex;flex-direction:column;overflow:hidden}
.geo-col-head{padding:8px 14px;border-bottom:0.5px solid var(--bd);background:var(--s2);flex-shrink:0;font-size:9px;letter-spacing:2px;text-transform:uppercase;color:var(--muted)}
#geo-kpis{padding:10px 12px;border-bottom:0.5px solid var(--bd);flex-shrink:0}
.geo-kpi-grid{display:grid;grid-template-columns:1fr 1fr;gap:5px}
.geo-kpi{background:var(--s2);border-radius:8px;padding:7px 10px}
.geo-kpi-val{font-size:14px;font-weight:500;color:var(--txt)}
.geo-kpi-lbl{font-size:10px;color:var(--muted);margin-top:1px}
#geo-rank-head{padding:7px 12px 5px;border-bottom:0.5px solid var(--bd);flex-shrink:0;display:flex;align-items:center;justify-content:space-between}
.geo-rank-title{font-size:9px;letter-spacing:1.5px;text-transform:uppercase;color:var(--muted)}
#geo-search{background:var(--s2);border:0.5px solid var(--bd);border-radius:6px;color:var(--txt);font-size:11px;padding:3px 8px;width:80px;outline:none;font-family:inherit}
#geo-search:focus{border-color:var(--amber)}
#geo-rank-list{flex:1;overflow-y:auto;padding:3px 0}
#geo-rank-list::-webkit-scrollbar{width:3px}
#geo-rank-list::-webkit-scrollbar-thumb{background:var(--bd2)}
.geo-rank-item{display:flex;align-items:center;gap:5px;padding:5px 12px;cursor:pointer;transition:background .12s;border-left:2px solid transparent}
.geo-rank-item:hover{background:var(--s2)}
.geo-rank-item.geo-sel{background:var(--s2);border-left-color:var(--amber)}
.geo-rank-num{font-size:10px;color:var(--muted);width:14px;text-align:right;flex-shrink:0}
.geo-rank-nome{font-size:11px;flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:var(--txt)}
.geo-rank-bar-wrap{width:42px;flex-shrink:0}
.geo-rank-bar-bg{height:4px;background:var(--s3);border-radius:2px;overflow:hidden}
.geo-rank-bar-fill{height:100%;border-radius:2px;transition:width .3s}
.geo-rank-val{font-size:10px;color:var(--muted);text-align:right;margin-top:1px}

/* Mapa */
#geo-map-wrap{position:relative;overflow:hidden}
#geo-map{width:100%;height:100%}
.leaflet-container{font-family:inherit}
.leaflet-interactive{outline:none!important}
.leaflet-interactive:focus{outline:none!important}
/* Botão "Voltar ao DF" — anexado ao bar do zoom, mesmo estilo dos botões + e − */
.leaflet-control-zoom-fit{display:flex!important;align-items:center;justify-content:center;color:#333;text-decoration:none}
.leaflet-control-zoom-fit:hover{background:#f4f4f4;color:#000}
#geo-map-legend{position:absolute;bottom:28px;left:12px;z-index:500;background:var(--s1);border:0.5px solid var(--bd2);border-radius:8px;padding:8px 12px;box-shadow:0 2px 8px rgba(0,0,0,.08);min-width:155px}
.gml-title{font-size:9px;letter-spacing:1.5px;text-transform:uppercase;color:var(--muted);margin-bottom:5px}
.gml-grad-wrap{display:flex;align-items:center;gap:5px}
.gml-grad{flex:1;height:5px;border-radius:3px}
.gml-val{font-size:10px;color:var(--muted);white-space:nowrap}

/* Painel direito */
#geo-right{background:var(--s1);border-left:0.5px solid var(--bd);display:flex;flex-direction:column;overflow:hidden}
#geo-right-empty{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px;color:var(--muted);padding:20px;text-align:center}
.geo-empty-icon{font-size:28px;opacity:.25}
.geo-empty-txt{font-size:11px;line-height:1.6}
#geo-panel-body{flex:1;overflow-y:auto;padding:12px 14px}
#geo-panel-body::-webkit-scrollbar{width:3px}
#geo-panel-body::-webkit-scrollbar-thumb{background:var(--bd2)}
.gp-ra-nome{font-size:15px;font-weight:500;margin-bottom:10px}
.gp-section{margin-bottom:14px}
.gp-sec-title{font-size:9px;letter-spacing:1.5px;text-transform:uppercase;color:var(--amber);margin-bottom:7px;padding-bottom:4px;border-bottom:0.5px solid var(--bd)}
.gp-kpi-grid{display:grid;grid-template-columns:1fr 1fr;gap:5px;margin-bottom:6px}
.gp-kpi{background:var(--s2);border-radius:7px;padding:7px 10px}
.gp-kpi-val{font-size:13px;font-weight:500;color:var(--txt)}
.gp-kpi-lbl{font-size:10px;color:var(--muted);margin-top:1px}
.gp-narr{font-size:11px;color:var(--muted);line-height:1.7;background:var(--s2);padding:9px 11px;border-radius:7px;border-left:2px solid var(--amber)}
.gp-campo-row{display:flex;align-items:center;gap:6px;margin-bottom:5px}
.gp-campo-nome{font-size:11px;width:90px;flex-shrink:0;color:var(--muted)}
.gp-bar-bg{flex:1;height:6px;background:var(--s3);border-radius:3px;overflow:hidden}
.gp-bar-fill{height:100%;border-radius:3px;transition:width .35s}
.gp-bar-val{font-size:11px;width:32px;text-align:right;color:var(--txt)}

/* SPE grid 5 dimensões */
.gp-spe-score{background:var(--s2);border-radius:8px;padding:10px 12px;border-left:3px solid var(--amber);margin-bottom:6px;display:flex;align-items:baseline;gap:8px}
.gp-spe-score-val{font-size:26px;font-weight:500;color:var(--amber)}
.gp-spe-score-lbl{font-size:10px;color:var(--muted);letter-spacing:.5px;text-transform:uppercase}
.gp-spe-dims{display:grid;grid-template-columns:1fr 1fr;gap:5px;margin-bottom:8px}
.gp-spe-box{background:var(--s2);border-radius:7px;padding:7px 10px}
.gp-spe-val{font-size:16px;font-weight:500}
.gp-spe-lbl{font-size:9px;color:var(--muted);margin-top:2px;letter-spacing:.5px;text-transform:uppercase}
.gp-quadrante{display:inline-block;font-size:11px;font-weight:500;padding:4px 12px;border-radius:20px;margin-top:4px}

/* Tooltip */
.leaflet-tooltip.gp-tip{background:var(--s1);border:0.5px solid var(--bd2);color:var(--txt);font-family:-apple-system,'Segoe UI',system-ui,sans-serif;font-size:12px;padding:8px 11px;border-radius:8px;box-shadow:0 4px 16px rgba(0,0,0,.1);pointer-events:none;max-width:200px}
.gp-tip-nome{font-weight:500;margin-bottom:3px}
.gp-tip-val{color:var(--muted);font-size:11px}
.gp-tip-val strong{color:var(--amber)}

/* Botão "Imprimir" — mesma família dos pills, leve destaque */
.geo-pill-print{background:var(--s2);font-size:11px;padding:3px 10px;border-radius:20px;cursor:pointer;border:0.5px solid var(--bd2);color:var(--muted);font-family:inherit;display:inline-flex;align-items:center;gap:4px}
.geo-pill-print:hover{color:var(--amber);border-color:var(--amber)}

/* Cabeçalho de impressão — escondido na tela, visível só na impressão */
.print-only{display:none}
.print-header{display:none}
.print-tabela-wrap{display:none}

/* ══ Estilos exclusivos de impressão ════════════════════════════ */
@media print {
  /* Paisagem por padrão; cliente pode trocar para retrato no diálogo de impressão */
  @page { size: A4 landscape; margin: 10mm; }
  html, body { background:white !important; height:auto !important; overflow:visible !important; font-size:9pt; }
  body { font-family:Arial,Helvetica,sans-serif !important; color:#000 !important; }
  /* Ocultar navegação, controles, partes não-essenciais */
  #sidenav, #nav-collapse-btn, #content > .sec, .nav-foot, .met-modal, #cmp-overlay { display:none !important; }
  #app { display:block !important; }
  /* Só imprime o módulo ATIVO; o outro permanece oculto */
  #geo-section, #geo-cand-section { display:none !important; }
  #geo-section.geo-vis, #geo-cand-section.gc-vis { display:flex !important; flex-direction:column !important; height:auto !important; overflow:visible !important; }
  #geo-toolbar, #gc-toolbar { display:none !important; }

  /* Cabeçalho de impressão com LOGO + título + data + filtros */
  .print-header { display:flex !important; flex-direction:column; gap:6pt; padding:0 0 6pt; border-bottom:1pt solid #1A1A1A; margin-bottom:8pt; }
  .print-header-row { display:flex !important; align-items:center; justify-content:space-between; gap:14pt; }
  .print-header-left { display:flex; align-items:center; gap:10pt; }
  .print-logo { height:34pt; width:auto; filter:sepia(1) saturate(1.2) hue-rotate(5deg) brightness(0.7); }
  .print-titulo { font-size:14pt; font-weight:700; color:#1A1A1A; margin:0; line-height:1.1 }
  .print-kicker { font-size:7pt; letter-spacing:1.2pt; text-transform:uppercase; color:#6B7280; margin-bottom:2pt; font-weight:600 }
  .print-data { font-size:8pt; color:#6B7280; white-space:nowrap; text-align:right }
  .print-filtros { font-size:9pt; margin-top:0; color:#1A1A1A }
  .print-filtros strong { color:#1A1A1A }
  .print-filtros .pf-chip { display:inline-block; background:#F1EFE8; padding:2pt 7pt; border-radius:10pt; margin-right:5pt; font-size:8.5pt }

  /* Corpo: 3 colunas — ranking | mapa | painel da RA selecionada */
  #geo-body, #gc-body { display:grid !important; grid-template-columns: 20% 56% 24% !important; height:460pt !important; flex:0 0 auto !important; gap:0; overflow:hidden !important; }

  /* Coluna esquerda: KPIs + ranking compacto */
  #geo-left, #gc-left { display:flex !important; flex-direction:column !important; height:460pt !important; max-height:460pt !important; overflow:hidden !important; border-right:0.5pt solid #ccc !important; padding-right:6pt; background:white !important; }
  .geo-col-head, .gc-col-head { background:transparent !important; padding:2pt 6pt !important; font-size:7pt !important; flex-shrink:0 }
  #geo-kpis, #gc-filters { padding:5pt 4pt !important; border-bottom:0.5pt solid #ddd !important; flex-shrink:0 }
  .geo-kpi-grid { gap:3pt !important }
  .geo-kpi { background:#FAFAFA !important; padding:4pt 6pt !important; border-radius:4pt }
  .geo-kpi-val { font-size:9.5pt !important }
  .geo-kpi-lbl { font-size:6pt !important }
  #geo-rank-head, #gc-search { display:none !important; }
  #geo-rank-list, #gc-list { flex:1 1 auto !important; overflow:hidden !important; max-height:none !important; padding:2pt 0 !important; }
  .geo-rank-item, .gc-list-item { padding:1.5pt 6pt !important; }
  .geo-rank-num { font-size:6.5pt !important }
  .geo-rank-nome { font-size:7.5pt !important }
  .geo-rank-bar-wrap { width:28pt !important }
  .geo-rank-bar-bg { height:3pt !important }
  .geo-rank-val { font-size:6.5pt !important }

  /* Mapa — coluna central */
  #geo-map-wrap, #gc-map-wrap { position:relative !important; display:block !important; height:460pt !important; page-break-inside:avoid; overflow:hidden !important; }
  #geo-map, #gc-map { width:100% !important; height:460pt !important; page-break-inside:avoid; border:0.5pt solid #ccc; }
  #geo-map-legend, #gc-map-legend { position:absolute !important; bottom:6pt !important; left:6pt !important; box-shadow:none !important; border:0.5pt solid #ccc !important; padding:4pt 6pt !important; max-width:65%; background:white !important; }
  .gml-title, .gcml-title { font-size:7pt !important }
  .gml-val, .gcml-val { font-size:7pt !important }

  /* Coluna direita: painel da região / candidato selecionado */
  #geo-right, #gc-right { display:flex !important; flex-direction:column !important; height:460pt !important; max-height:460pt !important; overflow:hidden !important; border-left:0.5pt solid #ccc !important; padding-left:6pt; background:white !important; }
  #geo-right-empty, #gc-right-empty { display:none !important; }
  #geo-panel-body, #gc-panel-body { display:block !important; flex:1 1 auto !important; overflow:hidden !important; padding:6pt 4pt !important; }
  /* Painel compacto */
  .gp-ra-nome, .gcp-nome { font-size:11pt !important; margin-bottom:5pt !important; line-height:1.15 !important; }
  .gp-section, .gcp-section { margin-bottom:6pt !important; }
  .gp-sec-title, .gcp-sec-title { font-size:6.5pt !important; padding-bottom:2pt !important; margin-bottom:3pt !important; letter-spacing:1pt !important; }
  .gp-kpi-grid, .gcp-kpi-grid { gap:3pt !important; margin-bottom:3pt !important; }
  .gp-kpi, .gcp-kpi { padding:4pt 6pt !important; background:#FAFAFA !important; border-radius:4pt; }
  .gp-kpi-val, .gcp-kpi-val { font-size:9.5pt !important }
  .gp-kpi-lbl, .gcp-kpi-lbl { font-size:6pt !important }
  .gp-narr, .gcp-narr { font-size:7pt !important; padding:4pt 6pt !important; line-height:1.45 !important; background:#FAFAFA !important; }
  .gp-campo-row { margin-bottom:2pt !important; gap:4pt !important; }
  .gp-campo-nome { font-size:6.5pt !important; width:54pt !important; }
  .gp-bar-bg { height:4pt !important; }
  .gp-bar-val { font-size:6.5pt !important; width:24pt !important; }
  .gp-spe-score { padding:5pt 7pt !important; margin-bottom:4pt !important; }
  .gp-spe-score-val { font-size:18pt !important }
  .gp-spe-score-lbl { font-size:6.5pt !important }
  .gp-spe-dims { gap:3pt !important }
  .gp-spe-box { padding:4pt 6pt !important }
  .gp-spe-val { font-size:11pt !important }
  .gp-spe-lbl { font-size:6pt !important }
  .gp-quadrante { font-size:7.5pt !important; padding:2pt 7pt !important }

  /* Tabela print exclusiva — desativada (o ranking lateral já cumpre o papel) */
  .print-tabela-wrap { display:none !important; }

  /* Rodapé */
  .print-rodape { display:block !important; margin-top:8pt; padding-top:4pt; border-top:0.5pt solid #aaa; font-size:7.5pt; color:#6B7280 }

  /* Esconder controles do Leaflet na impressão */
  .leaflet-control-zoom { display:none !important; }
  .leaflet-control-attribution { font-size:6.5pt !important; }
  .gp-bar-fill, .geo-rank-bar-fill, .gml-grad, .gcml-grad { -webkit-print-color-adjust:exact !important; print-color-adjust:exact !important }
  path, .leaflet-interactive { -webkit-print-color-adjust:exact !important; print-color-adjust:exact !important }
}
"""

NAV_PLACEHOLDER = '      <div class="nav-sub-item" id="ni-geo-territorio" onclick="irGeoTerritorio()">\n        <div class="nav-dot" style="background:#9FE1CB"></div><span>Território</span>\n      </div>\n      <div class="nav-sub-item" id="ni-geo-candidato" onclick="irGeoCandidato()">\n        <div class="nav-dot" style="background:#9FE1CB"></div><span>Candidato</span>\n      </div>'
NAV_GEO_ITEM    = '      <div class="nav-sub-item" id="ni-geo-territorio" onclick="irGeoTerritorio()">\n        <div class="nav-dot" style="background:#9FE1CB"></div><span>Território</span>\n      </div>\n      <div class="nav-sub-item" id="ni-geo-candidato" onclick="irGeoCandidato()">\n        <div class="nav-dot" style="background:#9FE1CB"></div><span>Candidato</span>\n      </div>'

GEO_SECTION_HTML = """
  <!-- ══ GEOPOLÍTICA ══════════════════════════════════════════ -->
  <button id="nav-collapse-btn" onclick="toggleNav()" title="Recolher menu">‹</button>
  <div id="geo-section">
    <div id="geo-toolbar">
      <div class="geo-tb-group">
        <span class="geo-tb-lbl">Colorir por</span>
        <select class="geo-sel" id="geo-var-sel" onchange="geoRecolor()">
          <optgroup label="População · PDAD 2021">
            <option value="renda_pc">Renda per capita</option>
            <option value="pct_ab">% Classe A/B</option>
            <option value="pct_de">% Classe D/E</option>
            <option value="pct_super">% Superior</option>
            <option value="pct_sem_fund">% Sem ensino fund.</option>
            <option value="pct_serv">% Funcionalismo</option>
            <option value="pct_beneficio">% Benefício social</option>
            <option value="pct_migrante">% Migrantes</option>
          </optgroup>
          <optgroup label="Eleitorado · TSE 2022">
            <option value="el_aptos">Eleitores aptos</option>
            <option value="el_jov">% Jovens 16-24</option>
            <option value="el_ido">% Idosos 60+</option>
            <option value="el_fem">% Feminino</option>
          </optgroup>
          <optgroup label="Campo político — domínio · TSE 2022">
            <option value="voto_progressista">% Progressista</option>
            <option value="voto_moderado">% Moderado</option>
            <option value="voto_liberal_conservador">% Liberal/Conservador</option>
          </optgroup>
          <optgroup label="Campo político — Performance · TSE 2022">
            <option value="idx_progressista">Performance Progressista</option>
            <option value="idx_moderado">Performance Moderado</option>
            <option value="idx_liberal_conservador">Performance Liberal/Cons.</option>
          </optgroup>
          <optgroup label="Cargo · TSE 2022">
            <option value="margem">Margem 1º-2º (competitividade)</option>
          </optgroup>
        </select>
      </div>
      <div style="margin-left:auto" class="geo-tb-group" id="geo-cargo-group">
        <span class="geo-tb-lbl">Cargo</span>
        <div style="display:flex;gap:4px" id="geo-cargo-pills">
          <button class="geo-pill gp-cargo-on" onclick="geoSetCargo('GOVERNADOR',this)">Governador</button>
          <button class="geo-pill" onclick="geoSetCargo('SENADOR',this)">Senador</button>
          <button class="geo-pill" onclick="geoSetCargo('DEPUTADO_FEDERAL',this)">Dep. Federal</button>
          <button class="geo-pill" onclick="geoSetCargo('DEPUTADO_DISTRITAL',this)">Dep. Distrital</button>
        </div>
      </div>
      <div class="geo-tb-group" style="padding-right:14px">
        <button class="geo-pill-print" onclick="imprimirGeo()" title="Imprimir consulta atual"><span style="font-size:13px">🖨</span> Imprimir</button>
      </div>
    </div>

    <!-- Cabeçalho de impressão (oculto na tela, visível só no @media print) -->
    <div class="print-header" id="geo-print-header">
      <div class="print-header-row">
        <div class="print-header-left">
          <img class="print-logo" src="__LOGO_SRC__" alt="Opinião"/>
          <div>
            <div class="print-kicker">Opinião · Informação Estratégica</div>
            <div class="print-titulo">Geopolítica · Território</div>
          </div>
        </div>
        <div class="print-data" id="geo-print-data"></div>
      </div>
      <div class="print-filtros" id="geo-print-filtros"></div>
    </div>

    <div id="geo-body">
      <div id="geo-left">
        <div class="geo-col-head">Distrito Federal</div>
        <div id="geo-kpis">
          <div class="geo-kpi-grid">
            <div class="geo-kpi"><div class="geo-kpi-val" id="gkpi-el">—</div><div class="geo-kpi-lbl">Eleitores aptos</div></div>
            <div class="geo-kpi"><div class="geo-kpi-val" id="gkpi-ras">33</div><div class="geo-kpi-lbl">Regiões Adm.</div></div>
            <div class="geo-kpi"><div class="geo-kpi-val" id="gkpi-renda">—</div><div class="geo-kpi-lbl">Renda média PC</div></div>
            <div class="geo-kpi"><div class="geo-kpi-val" id="gkpi-campo">—</div><div class="geo-kpi-lbl">Campo dominante</div></div>
          </div>
        </div>
        <div id="geo-rank-head">
          <span class="geo-rank-title">Ranking</span>
          <input id="geo-search" placeholder="Buscar RA…" oninput="geoFiltrarRanking()">
        </div>
        <div id="geo-rank-list"></div>
      </div>
      <div id="geo-map-wrap">
        <div id="geo-map"></div>
        <div id="geo-map-legend">
          <div class="gml-title" id="gml-title">Renda Per Capita</div>
          <div class="gml-grad-wrap">
            <span class="gml-val" id="gml-min">—</span>
            <div class="gml-grad" id="gml-grad"></div>
            <span class="gml-val" id="gml-max">—</span>
          </div>
        </div>
      </div>
      <div id="geo-right">
        <div class="geo-col-head">Região selecionada</div>
        <div id="geo-right-empty">
          <div class="geo-empty-icon">🗺</div>
          <div class="geo-empty-txt">Clique em uma região no mapa ou no ranking para ver a análise</div>
        </div>
        <div id="geo-panel-body" style="display:none"></div>
      </div>
    </div>

    <!-- Tabela de top RAs (visível só no print) -->
    <div class="print-tabela-wrap" id="geo-print-tabela-wrap">
      <div class="print-tabela-titulo" id="geo-print-tabela-titulo">Ranking das regiões</div>
      <table class="print-tabela" id="geo-print-tabela"></table>
    </div>

    <!-- Rodapé de impressão -->
    <div class="print-rodape print-only">
      Fontes: TSE 2022 (votos por seção, cadastro eleitoral) · PDAD 2021 (perfil socioeconômico).
      Instrumento gerado pelo painel <strong>Estrategos</strong> — solução de Inteligência Política da <strong>Opinião Informação Estratégica</strong>.
    </div>

    <!-- Paper analítico de contexto DF (visível só no print) -->
    <div class="paper-wrap" id="geo-paper-wrap"></div>
  </div>
  <!-- ══ /GEOPOLÍTICA ═════════════════════════════════════════ -->
"""

GEO_JS = """
// ══ GeoPolítica ═══════════════════════════════════════════════════════════════

function toggleNav(){
  var nav=document.getElementById('sidenav');
  var btn=document.getElementById('nav-collapse-btn');
  var collapsed=nav.classList.toggle('nav-collapsed');
  btn.textContent=collapsed?'›':'‹';
  btn.style.left=collapsed?'0':'188px';
  if(geoMap) setTimeout(function(){geoMap.invalidateSize();btn.style.left=collapsed?'0':'188px';},250);
}

const GEO_DATA=JSON.parse(atob("__GEO_B64__"));

var geoVarSel='renda_pc';
var geoCargo='GOVERNADOR';
// (geoCampo removido — filtro Campo era resíduo do SPE morto, não afetava nada.)
var geoRaSel=null;
var geoLayer=null;
var geoMap=null;
var geoMapInit=false;

// Variáveis que dependem de cargo selecionado nos pills
var GEO_VARS_CARGO=['voto_progressista','voto_moderado','voto_liberal_conservador',
                    'idx_progressista','idx_moderado','idx_liberal_conservador',
                    'margem'];
// Variáveis estruturais (não reagem a cargo/campo)
// Variáveis com escala divergente centrada (verde-cinza-vermelho ao redor de 0 ou 1)
var GEO_VARS_DIV=['idx_progressista','idx_moderado','idx_liberal_conservador'];

// (geoAtualizarToolbar removida — a nota textual desapareceu junto com a remoção
//  do filtro Campo. Cargo continua reagindo no mapa quando a variável é sensível.)

function geoLerp(a,b,t){return a+(b-a)*t}
function geoHex(r,g,b){return '#'+[r,g,b].map(function(x){return Math.round(x).toString(16).padStart(2,'0');}).join('')}
var GP_LOW=[245,242,236],GP_MID=[198,155,90],GP_HIGH=[120,60,10];
function geoPaleta(t){
  var r,g,b,s;
  if(t<0.5){s=t*2;r=geoLerp(GP_LOW[0],GP_MID[0],s);g=geoLerp(GP_LOW[1],GP_MID[1],s);b=geoLerp(GP_LOW[2],GP_MID[2],s);}
  else{s=(t-0.5)*2;r=geoLerp(GP_MID[0],GP_HIGH[0],s);g=geoLerp(GP_MID[1],GP_HIGH[1],s);b=geoLerp(GP_MID[2],GP_HIGH[2],s);}
  return geoHex(r,g,b);
}
// Paleta divergente para sobre-índice (centrada em 1.0): vermelho < 1 < verde
// t em [0..1], onde 0.5 = idx 1.0 (neutro)
var GP_NEG=[120,30,30],GP_NEU=[230,228,222],GP_POS=[12,90,55];
function geoPaletaDiv(t){
  var r,g,b,s;
  if(t<0.5){s=t*2;r=geoLerp(GP_NEG[0],GP_NEU[0],s);g=geoLerp(GP_NEG[1],GP_NEU[1],s);b=geoLerp(GP_NEG[2],GP_NEU[2],s);}
  else{s=(t-0.5)*2;r=geoLerp(GP_NEU[0],GP_POS[0],s);g=geoLerp(GP_NEU[1],GP_POS[1],s);b=geoLerp(GP_NEU[2],GP_POS[2],s);}
  return geoHex(r,g,b);
}

function irGeoTerritorio(){
  document.getElementById('content').style.display='none';
  document.getElementById('geo-section').classList.add('geo-vis');
  // Desselecionar todos os outros nav-items e sub-items
  document.querySelectorAll('.nav-item,.nav-sub-item').forEach(function(el){el.classList.remove('active');});
  var niGeo=document.getElementById('ni-geo-territorio');
  if(niGeo)niGeo.classList.add('active');
  document.getElementById('nav-collapse-btn').classList.add('geo-visible');
  if(!geoMapInit){geoInitMap();geoMapInit=true;}
  else{setTimeout(function(){geoMap.invalidateSize();},50);}
}

function irGeoCandidato(){
  // Stub — será implementado na próxima etapa
  irGeoTerritorio(); // por ora abre território
}

var _irSecOrig=irSec;
irSec=function(id){
  document.getElementById('content').style.display='';
  document.getElementById('geo-section').classList.remove('geo-vis');
  ['ni-geo-territorio','ni-geo-candidato'].forEach(function(id){
    var el=document.getElementById(id);if(el)el.classList.remove('active');
  });
  document.getElementById('nav-collapse-btn').classList.remove('geo-visible');
  _irSecOrig(id);
};

var GEO_INIT_VIEW={center:[-15.82,-47.93],zoom:10};
function geoResetView(){
  if(!geoMap) return;
  if(geoLayer && geoLayer.getBounds && geoLayer.getBounds().isValid()){
    // Padding assimétrico — empurra o DF mais para a esquerda visualmente
    geoMap.fitBounds(geoLayer.getBounds(), {paddingTopLeft:[10,20], paddingBottomRight:[80,20], animate:true});
  } else {
    geoMap.setView(GEO_INIT_VIEW.center, GEO_INIT_VIEW.zoom, {animate:true});
  }
}
function geoInitMap(){
  geoMap=L.map('geo-map',{center:GEO_INIT_VIEW.center,zoom:GEO_INIT_VIEW.zoom,zoomControl:false});
  var zoomCtl=L.control.zoom({position:'bottomright'});
  zoomCtl.addTo(geoMap);
  // Anexa o botão "Voltar ao DF" no MESMO leaflet-bar do zoom — herda estilo (sem moldura própria)
  var zoomBar=zoomCtl.getContainer();
  var alvoBtn=L.DomUtil.create('a','leaflet-control-zoom-fit',zoomBar);
  alvoBtn.href='#'; alvoBtn.title='Voltar ao DF (enquadrar tudo)';
  alvoBtn.role='button';
  alvoBtn.innerHTML='<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display:block;margin:auto"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="4"/><line x1="12" y1="1" x2="12" y2="4"/><line x1="12" y1="20" x2="12" y2="23"/><line x1="1" y1="12" x2="4" y2="12"/><line x1="20" y1="12" x2="23" y2="12"/></svg>';
  L.DomEvent.on(alvoBtn,'click',function(e){L.DomEvent.preventDefault(e);L.DomEvent.stopPropagation(e);geoResetView();});
  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',{
    attribution:'&copy; <a href="https://carto.com/">CARTO</a> &copy; <a href="https://openstreetmap.org">OpenStreetMap</a>',
    subdomains:'abcd',maxZoom:18
  }).addTo(geoMap);
  geoRender();
  geoUpdateKPIs();
}

// Compatível com novo formato {pct, idx} e legado number
function geoVotoPct(o){ if(o==null)return null; if(typeof o==='number')return o; return (o.pct!=null)?o.pct:null; }

function geoGetVal(dados){
  if(!dados) return null;
  if(geoVarSel.indexOf('voto_')===0){
    var campo=geoVarSel.replace('voto_','');
    var v=(dados.votos&&dados.votos[geoCargo])?dados.votos[geoCargo][campo]:null;
    return geoVotoPct(v);
  }
  if(geoVarSel.indexOf('idx_')===0){
    var campoIdx=geoVarSel.replace('idx_','');
    var vIdx=(dados.votos&&dados.votos[geoCargo])?dados.votos[geoCargo][campoIdx]:null;
    return (vIdx && typeof vIdx==='object' && vIdx.idx!=null) ? vIdx.idx : null;
  }
  if(geoVarSel==='margem'){
    var m=(dados.margem&&dados.margem[geoCargo])?dados.margem[geoCargo]:null;
    return (m && m.margem_pp!=null) ? m.margem_pp : null;
  }
  return (dados[geoVarSel]!=null)?dados[geoVarSel]:null;
}

function geoCalcRange(){
  var vals=[];
  GEO_DATA.features.forEach(function(f){var v=geoGetVal(f.properties.dados);if(v!=null)vals.push(v);});
  if(!vals.length)return[0,1];
  // Para variáveis divergentes (sobre-índice), centrar em 1.0
  if(GEO_VARS_DIV.indexOf(geoVarSel)>=0){
    var maxAfast = Math.max.apply(null, vals.map(function(v){return Math.abs(v-1);}));
    if(maxAfast<0.05) maxAfast=0.05;
    return [1-maxAfast, 1+maxAfast];
  }
  return[Math.min.apply(null,vals),Math.max.apply(null,vals)];
}

var GEO_VAR_LABEL={
  renda_pc:'Renda per capita (R$)',pct_ab:'% Classe A/B',pct_de:'% Classe D/E',
  pct_super:'% Superior',pct_sem_fund:'% Sem ensino fund.',pct_serv:'% Funcionalismo',
  pct_beneficio:'% Benefício social',pct_migrante:'% Migrantes',
  el_aptos:'Eleitores aptos',el_jov:'% Jovens 16-24',el_ido:'% Idosos 60+',el_fem:'% Feminino',
  voto_progressista:'% Progressista',voto_moderado:'% Moderado',
  voto_liberal_conservador:'% Liberal/Cons.',
  idx_progressista:'Performance Progressista',idx_moderado:'Performance Moderado',
  idx_liberal_conservador:'Performance Liberal/Cons.',
  margem:'Margem 1º-2º (pp)'
};
// Fonte/ano por variável (PDAD = perfil socioeconômico; TSE = eleitorado e voto)
var GEO_VAR_FONTE={
  renda_pc:'PDAD 2021',pct_ab:'PDAD 2021',pct_de:'PDAD 2021',
  pct_super:'PDAD 2021',pct_sem_fund:'PDAD 2021',pct_serv:'PDAD 2021',
  pct_beneficio:'PDAD 2021',pct_migrante:'PDAD 2021',
  el_aptos:'TSE 2022',el_jov:'TSE 2022',el_ido:'TSE 2022',el_fem:'TSE 2022',
  voto_progressista:'TSE 2022',voto_moderado:'TSE 2022',voto_liberal_conservador:'TSE 2022',
  idx_progressista:'TSE 2022',idx_moderado:'TSE 2022',idx_liberal_conservador:'TSE 2022',
  margem:'TSE 2022'
};

function geoFmt(v,key){
  if(v===null||v===undefined)return'—';
  if(key==='renda_pc')return'R$'+(v>=1000?((v/1000).toFixed(1).replace('.',','))+'K':v);
  if(key==='el_aptos')return v>=1000?Math.round(v/1000)+'K':String(v);
  if(key && key.indexOf('idx_')===0){
    // Sobre-índice: exibir como delta % (ex.: idx 1.27 → +27%)
    var d=Math.round((v-1)*100);
    return (d>=0?'+':'')+d+'%';
  }
  if(key==='margem'){
    return (typeof v==='number'?v.toFixed(1).replace('.',','):v)+'pp';
  }
  return (typeof v==='number'?v.toFixed(1).replace('.',','):v)+'%';
}

function geoRender(){
  if(!geoMap)return;
  var range=geoCalcRange(),mn=range[0],mx=range[1],rng=mx-mn||1;
  var ehDiv = GEO_VARS_DIV.indexOf(geoVarSel)>=0;
  var paletaFn = ehDiv ? geoPaletaDiv : geoPaleta;
  if(geoLayer)geoMap.removeLayer(geoLayer);
  geoLayer=L.geoJSON(GEO_DATA,{
    style:function(feat){
      var v=geoGetVal(feat.properties.dados),t=v!=null?(v-mn)/rng:-1;
      var cor=t>=0?paletaFn(t):'#ddd8cf';
      var isSel=geoRaSel===feat.properties.RA_PIPE;
      return{fillColor:cor,fillOpacity:isSel?0.92:0.72,color:isSel?'#B45309':'rgba(0,0,0,0.15)',weight:isSel?2:0.8};
    },
    onEachFeature:function(feat,layer){
      var nome=feat.properties.RA_PIPE,dados=feat.properties.dados||{},v=geoGetVal(dados);
      layer.on('mouseover',function(e){
        if(geoRaSel!==nome)layer.setStyle({fillOpacity:0.88,weight:1.2});
        layer.bindTooltip(
          '<div class="gp-tip-nome">'+nome+'</div>'
          +'<div class="gp-tip-val">'+(GEO_VAR_LABEL[geoVarSel]||geoVarSel)+': <strong>'+geoFmt(v,geoVarSel)+'</strong></div>',
          {className:'gp-tip',sticky:true,offset:[10,0]}
        ).openTooltip(e.latlng);
      });
      layer.on('mouseout',function(){geoLayer.resetStyle(layer);layer.unbindTooltip();});
      layer.on('click',function(){
        geoRaSel=nome;geoRender();geoAbrirPanel(nome,dados);
        document.querySelectorAll('.geo-rank-item').forEach(function(el){
          el.classList.toggle('geo-sel',el.dataset.nome===nome);
        });
      });
    }
  }).addTo(geoMap);
  geoUpdateLegenda(mn,mx);
  geoUpdateRanking(mn,mx);
}

function geoUpdateLegenda(mn,mx){
  document.getElementById('gml-min').textContent=geoFmt(mn,geoVarSel);
  document.getElementById('gml-max').textContent=geoFmt(mx,geoVarSel);
  var lbl=GEO_VAR_LABEL[geoVarSel]||geoVarSel;
  var fonte=GEO_VAR_FONTE[geoVarSel]||'';
  var titEl=document.getElementById('gml-title');
  if(titEl){
    titEl.innerHTML=lbl+(fonte?'<span style="font-size:8px;letter-spacing:.5px;text-transform:none;color:var(--muted);font-weight:400;margin-left:6px">· '+fonte+'</span>':'');
  }
  var pal = (GEO_VARS_DIV.indexOf(geoVarSel)>=0) ? geoPaletaDiv : geoPaleta;
  document.getElementById('gml-grad').style.background='linear-gradient(to right,'+pal(0)+','+pal(0.5)+','+pal(1)+')';
}

function geoUpdateKPIs(){
  var totalEl=0,totalR=0,nR=0,campos={};
  GEO_DATA.features.forEach(function(f){
    var d=f.properties.dados||{};
    if(d.el_aptos)totalEl+=d.el_aptos;
    if(d.renda_pc){totalR+=d.renda_pc;nR++;}
    var vg=d.votos&&d.votos['GOVERNADOR']||{};
    Object.keys(vg).forEach(function(c){var pct=geoVotoPct(vg[c]); if(pct!=null) campos[c]=(campos[c]||0)+pct;});
  });
  document.getElementById('gkpi-el').textContent=totalEl>1e6?(totalEl/1e6).toFixed(2).replace('.',',')+'M':(totalEl/1000).toFixed(0)+'K';
  document.getElementById('gkpi-renda').textContent=nR?'R$'+((totalR/nR)/1000).toFixed(1).replace('.',',')+'K':'—';
  var dom='—';
  if(Object.keys(campos).length){
    var top=Object.entries(campos).sort(function(a,b){return b[1]-a[1];})[0];
    dom={progressista:'Progressista',moderado:'Moderado',liberal_conservador:'Lib/Cons.'}[top[0]]||top[0];
  }
  document.getElementById('gkpi-campo').textContent=dom;
}

function geoUpdateRanking(mn,mx){
  var rng=mx-mn||1;
  var items=GEO_DATA.features.map(function(f){
    return{nome:f.properties.RA_PIPE,v:geoGetVal(f.properties.dados||{})};
  });
  items.sort(function(a,b){return(b.v===null?-Infinity:b.v)-(a.v===null?-Infinity:a.v);});
  var list=document.getElementById('geo-rank-list');list.innerHTML='';
  var q=(document.getElementById('geo-search').value||'').toLowerCase();
  items.forEach(function(item,i){
    if(q&&item.nome.toLowerCase().indexOf(q)<0)return;
    var t=item.v!=null?(item.v-mn)/rng:0;
    var cor=item.v!=null?geoPaleta(t):'#ccc';
    var div=document.createElement('div');
    div.className='geo-rank-item'+(geoRaSel===item.nome?' geo-sel':'');
    div.dataset.nome=item.nome;
    div.innerHTML='<span class="geo-rank-num">'+(i+1)+'</span>'
      +'<span class="geo-rank-nome">'+item.nome+'</span>'
      +'<div class="geo-rank-bar-wrap">'
        +'<div class="geo-rank-bar-bg"><div class="geo-rank-bar-fill" style="width:'+Math.round(t*100)+'%;background:'+cor+'"></div></div>'
        +'<div class="geo-rank-val">'+geoFmt(item.v,geoVarSel)+'</div>'
      +'</div>';
    div.onclick=function(){
      geoRaSel=item.nome;geoRender();
      var feat=GEO_DATA.features.find(function(f){return f.properties.RA_PIPE===item.nome;});
      geoAbrirPanel(item.nome,feat&&feat.properties.dados||{});
      if(geoLayer){
        Object.values(geoLayer._layers).forEach(function(l){
          if(l.feature&&l.feature.properties.RA_PIPE===item.nome)
            geoMap.fitBounds(l.getBounds(),{padding:[40,40]});
        });
      }
    };
    list.appendChild(div);
  });
}
function geoFiltrarRanking(){var r=geoCalcRange();geoUpdateRanking(r[0],r[1]);}

// ── Impressão da consulta ─────────────────────────────────────────────────────
function _geoVarLabel(){
  var sel=document.getElementById('geo-var-sel');
  if(!sel) return geoVarSel;
  var opt=sel.options[sel.selectedIndex];
  return opt ? opt.text : geoVarSel;
}
function _geoCargoLabel(){
  var L={GOVERNADOR:'Governador',SENADOR:'Senador',
         DEPUTADO_FEDERAL:'Deputado Federal',DEPUTADO_DISTRITAL:'Deputado Distrital'};
  return L[geoCargo]||geoCargo;
}
function _geoDataPt(){
  var d=new Date();
  var dd=String(d.getDate()).padStart(2,'0');
  var mm=String(d.getMonth()+1).padStart(2,'0');
  var yy=d.getFullYear();
  var hh=String(d.getHours()).padStart(2,'0');
  var mi=String(d.getMinutes()).padStart(2,'0');
  return dd+'/'+mm+'/'+yy+' às '+hh+':'+mi;
}

function imprimirGeo(){
  var varLbl=_geoVarLabel();
  var ehCargo=GEO_VARS_CARGO.indexOf(geoVarSel)>=0;

  // Cabeçalho
  var dEl=document.getElementById('geo-print-data');
  if(dEl) dEl.textContent='Gerado em '+_geoDataPt();
  var fEl=document.getElementById('geo-print-filtros');
  if(fEl){
    var html='<span class="pf-chip"><strong>Variável:</strong> '+varLbl+'</span>';
    if(ehCargo) html+='<span class="pf-chip"><strong>Cargo:</strong> '+_geoCargoLabel()+'</span>';
    fEl.innerHTML=html;
  }

  // Tabela top RAs
  var items=GEO_DATA.features.map(function(f){
    return {nome:f.properties.RA_PIPE, v:geoGetVal(f.properties.dados||{})};
  });
  items.sort(function(a,b){
    var av=(a.v===null||a.v===undefined)?-Infinity:a.v;
    var bv=(b.v===null||b.v===undefined)?-Infinity:b.v;
    return bv-av;
  });
  var titEl=document.getElementById('geo-print-tabela-titulo');
  if(titEl) titEl.textContent='Ranking das regiões — '+varLbl+(ehCargo?' ('+_geoCargoLabel()+')':'');
  var tbl=document.getElementById('geo-print-tabela');
  if(tbl){
    var html='<thead><tr><th style="width:32pt">Pos.</th><th>Região</th><th class="num">'+varLbl+'</th></tr></thead><tbody>';
    items.forEach(function(it,i){
      html+='<tr><td>'+(i+1)+'</td><td>'+it.nome+'</td><td class="num">'+geoFmt(it.v,geoVarSel)+'</td></tr>';
    });
    html+='</tbody>';
    tbl.innerHTML=html;
  }

  // Garante que o mapa esteja renderizado e dispara impressão
  // Renderiza paper de contexto DF (visível só no print)
  var paperWrap = document.getElementById('geo-paper-wrap');
  if(paperWrap){
    try { paperWrap.innerHTML = paperRenderContextoDF(); }
    catch(err){ console.error('Erro paper contexto:', err); paperWrap.innerHTML = ''; }
  }

  if(geoMap){ try{ geoMap.invalidateSize(); }catch(e){} }
  setTimeout(function(){ window.print(); }, 200);
}

// ════════════════════ PAPER DE CONTEXTO DF (PDF) ══════════════════════════════
var GEO_PAPER_CARGOS_ORD = ['GOVERNADOR','SENADOR','DEPUTADO_FEDERAL','DEPUTADO_DISTRITAL'];
var GEO_PAPER_CARGOS_LBL = {GOVERNADOR:'Governador',SENADOR:'Senador',DEPUTADO_FEDERAL:'Dep. Federal',DEPUTADO_DISTRITAL:'Dep. Distrital'};
var GEO_PAPER_CAMPOS_ORD = ['progressista','moderado','liberal_conservador','outros'];
var GEO_PAPER_CN  = {progressista:'Progressista',moderado:'Moderado',liberal_conservador:'Liberal/Cons.',outros:'Outros'};
var GEO_PAPER_CBG = {progressista:'#FCEBEB',moderado:'#E1F5EE',liberal_conservador:'#FAEEDA',outros:'#F1EFE8'};
var GEO_PAPER_CCOR= {progressista:'#A32D2D',moderado:'#0F6E56',liberal_conservador:'#854F0B',outros:'#6B7280'};

function _geoPaperFmt(v){ return v==null?'—':String(Math.round(v)).replace(/\B(?=(\d{3})+(?!\d))/g,'.'); }
function _geoPaperPct(v){ return v==null?'—':v.toFixed(1).replace('.',',')+'%'; }
function _geoPaperRs(v){ return v==null?'—':'R$ '+_geoPaperFmt(v); }

function paperRenderContextoDF(){
  if(typeof D === 'undefined') return '';

  // DF baseline
  function wAvg(key){
    var s=0,w=0;
    Object.keys(D).forEach(function(ra){
      var d=D[ra]; if(!d||d.sem_zona) return;
      var v=d[key], p=d.el_aptos;
      if(v!=null && p){ s+=v*p; w+=p; }
    });
    return w?s/w:null;
  }
  var renda = wAvg('renda_pc');
  var pctAB = wAvg('pct_ab');
  var pctDE = wAvg('pct_de');
  var pctSup = wAvg('pct_super');
  var aptosTotal = 0;
  Object.keys(D).forEach(function(ra){
    var d=D[ra]; if(!d||d.sem_zona) return;
    aptosTotal += (d.el_aptos||0);
  });
  var abst = wAvg('abstencao');
  var pctFem = wAvg('el_fem');
  var pctElSup = wAvg('el_super');

  // RAs extremas por renda
  var rasRenda = [];
  Object.keys(D).forEach(function(ra){
    var v = D[ra] && D[ra].renda_pc;
    if(v!=null) rasRenda.push({ra:ra, renda:v});
  });
  rasRenda.sort(function(a,b){return b.renda-a.renda;});
  var topRicas = rasRenda.slice(0,3);
  var topPobres = rasRenda.slice().reverse().slice(0,3);

  // Top 5 RAs por aptos
  var rasAptos = [];
  Object.keys(D).forEach(function(ra){
    var d=D[ra]; if(!d||d.sem_zona) return;
    if(d.el_aptos) rasAptos.push({ra:ra, aptos:d.el_aptos});
  });
  rasAptos.sort(function(a,b){return b.aptos-a.aptos;});
  var topAptos = rasAptos.slice(0,5);

  // Matriz cargos × campos (% do voto, ponderado por aptos)
  var matriz = {};
  GEO_PAPER_CARGOS_ORD.forEach(function(cargo){
    matriz[cargo] = {};
    GEO_PAPER_CAMPOS_ORD.forEach(function(campo){
      var s=0,w=0;
      Object.keys(D).forEach(function(ra){
        var d=D[ra]; if(!d||d.sem_zona) return;
        var pct = (((d.votos||{})[cargo]||{})[campo]||{}).pct;
        var p = d.el_aptos;
        if(pct!=null && p){ s+=pct*p; w+=p; }
      });
      matriz[cargo][campo] = w?s/w:0;
    });
  });

  // Logo
  var _logoEl = document.querySelector('.print-logo');
  var logoHtml = (_logoEl && _logoEl.src)
    ? '<img class="paper-logo-img" src="'+_logoEl.src+'" alt="Opinião"/>'
    : '<div class="paper-logo">opinião</div>';

  // KPI helper
  function kpi(num,lbl,sub){
    return '<div class="paper-kpi"><div class="paper-kpi-num">'+num+'</div><div class="paper-kpi-lbl">'+lbl+'</div>'+
      (sub?'<div class="paper-kpi-sub">'+sub+'</div>':'')+'</div>';
  }
  var popKpis = kpi(_geoPaperRs(renda),'Renda p/capita','(PDAD 2021)') +
    kpi(_geoPaperPct(pctAB),'Classe A/B','% pop. faixas mais altas') +
    kpi(_geoPaperPct(pctDE),'Classe D/E','% pop. faixas mais baixas') +
    kpi(_geoPaperPct(pctSup),'Ensino superior','% pop. com graduação');
  var eleiKpis = kpi(_geoPaperFmt(aptosTotal),'Eleitores aptos','Total no DF (TSE 2022)') +
    kpi(_geoPaperPct(abst),'Abstenção média','(TSE 2022)') +
    kpi(_geoPaperPct(pctFem),'Eleitor feminino','(TSE 2022)') +
    kpi(_geoPaperPct(pctElSup),'Com ensino superior','do eleitorado');

  // Tabelas mini
  var extremasHtml = topRicas.map(function(r){
    return '<tr><td class="ra">'+r.ra+'</td><td class="num">R$ '+_geoPaperFmt(r.renda)+'</td><td><span class="paper-st-badge" style="background:#DCFCE7;color:#15803D">Mais alta</span></td></tr>';
  }).join('') + topPobres.map(function(r){
    return '<tr><td class="ra">'+r.ra+'</td><td class="num">R$ '+_geoPaperFmt(r.renda)+'</td><td><span class="paper-st-badge" style="background:#FEE2E2;color:#991B1B">Mais baixa</span></td></tr>';
  }).join('');
  var topAptosHtml = topAptos.map(function(r){
    var pct = (r.aptos/aptosTotal*100).toFixed(1).replace('.',',');
    return '<tr><td class="ra">'+r.ra+'</td><td class="num">'+_geoPaperFmt(r.aptos)+'</td><td class="num">'+pct+'%</td></tr>';
  }).join('');

  // Matriz
  function matrizCell(campo,val){
    var bg=GEO_PAPER_CBG[campo], cor=GEO_PAPER_CCOR[campo];
    var fw = val>=40 ? '600' : '500';
    return '<td class="num campo-cell" style="background:'+bg+';color:'+cor+';font-weight:'+fw+'">'+val.toFixed(0)+'%</td>';
  }
  var matrizHtml = '<table class="paper-tbl-matriz"><thead><tr><th></th>';
  GEO_PAPER_CAMPOS_ORD.forEach(function(campo){
    matrizHtml += '<th style="color:'+GEO_PAPER_CCOR[campo]+';text-align:center">'+GEO_PAPER_CN[campo]+'</th>';
  });
  matrizHtml += '</tr></thead><tbody>';
  GEO_PAPER_CARGOS_ORD.forEach(function(cargo){
    matrizHtml += '<tr><td class="cargo-lbl">'+GEO_PAPER_CARGOS_LBL[cargo]+'</td>';
    GEO_PAPER_CAMPOS_ORD.forEach(function(campo){
      matrizHtml += matrizCell(campo, matriz[cargo][campo]);
    });
    matrizHtml += '</tr>';
  });
  matrizHtml += '</tbody></table>';

  // Narrativa do campo dominante
  var domLines = GEO_PAPER_CARGOS_ORD.map(function(cargo){
    var items = GEO_PAPER_CAMPOS_ORD.map(function(c){return [c, matriz[cargo][c]];});
    items.sort(function(a,b){return b[1]-a[1];});
    var top = items[0];
    return '<strong>'+GEO_PAPER_CARGOS_LBL[cargo]+'</strong>: <span style="color:'+GEO_PAPER_CCOR[top[0]]+';font-weight:500">'+GEO_PAPER_CN[top[0]]+'</span> dominante ('+top[1].toFixed(0)+'%)';
  });
  var campoNarr = domLines.join(' · ');

  var d = new Date();
  function pp(n){return String(n).padStart(2,'0');}
  var today = pp(d.getDate())+'/'+pp(d.getMonth()+1)+'/'+d.getFullYear();

  return ''+
    '<div class="paper-report">'+
      '<div class="paper-hd">'+
        logoHtml+
        '<div class="paper-info">'+
          '<div class="paper-nome">Distrito Federal · Panorama territorial</div>'+
          '<div class="paper-line"><span style="font-size:9pt;color:var(--muted)">Contexto demográfico, eleitoral e político — base PDAD 2021 e TSE 2022</span></div>'+
        '</div>'+
        '<div class="paper-data">'+today+'</div>'+
      '</div>'+
      '<div class="paper-row-2">'+
        '<div class="paper-col">'+
          '<div class="paper-sec-title">População (PDAD 2021)</div>'+
          '<div class="paper-sec-narr">DF tem <strong>33 regiões administrativas</strong> com altíssima desigualdade interna — renda per capita varia em ordem de grandeza entre RAs ricas (Plano Piloto, Lago Sul) e periferias.</div>'+
          '<div class="paper-kpis">'+popKpis+'</div>'+
          '<table class="paper-tbl-mini">'+
            '<thead><tr><th>RA</th><th style="text-align:right">Renda p/capita</th><th>Faixa</th></tr></thead>'+
            '<tbody>'+extremasHtml+'</tbody>'+
          '</table>'+
        '</div>'+
        '<div class="paper-col">'+
          '<div class="paper-sec-title">Eleitorado (TSE 2022)</div>'+
          '<div class="paper-sec-narr"><strong>'+_geoPaperFmt(aptosTotal)+'</strong> eleitores aptos distribuídos entre as RAs com zona TSE. Volume eleitoral concentrado nas RAs populosas — Ceilândia sozinha vale mais de 200 mil eleitores.</div>'+
          '<div class="paper-kpis">'+eleiKpis+'</div>'+
          '<table class="paper-tbl-mini">'+
            '<thead><tr><th>Top 5 RAs por eleitorado</th><th style="text-align:right">Aptos</th><th style="text-align:right">% do DF</th></tr></thead>'+
            '<tbody>'+topAptosHtml+'</tbody>'+
          '</table>'+
        '</div>'+
      '</div>'+
      '<div class="paper-sec">'+
        '<div class="paper-sec-title">Campo político (TSE 2022)</div>'+
        '<div class="paper-sec-narr">% do voto válido por campo em cada cargo, ponderado pelo eleitorado das RAs. '+campoNarr+'.</div>'+
        matrizHtml+
      '</div>'+
      '<div class="paper-foot">Fontes: <strong>PDAD 2021</strong> (IPEDF) · <strong>TSE 2022</strong>. Instrumento gerado pelo painel <strong>Estrategos</strong> — solução de Inteligência Política da <strong>Opinião Informação Estratégica</strong>.</div>'+
    '</div>';
}

// ── Painel da região ──────────────────────────────────────────────────────────
function fpt(v,dec){if(v===null||v===undefined)return'—';return v.toFixed(dec||1).replace('.',',');}
var CARGO_LBL={GOVERNADOR:'Governador',SENADOR:'Senador',DEPUTADO_FEDERAL:'Dep. Federal',DEPUTADO_DISTRITAL:'Dep. Distrital'};
var CAMPO_COR={progressista:'#534AB7',moderado:'#0F6E56',liberal_conservador:'#854F0B'};
var CAMPO_LBL={progressista:'Progressista',moderado:'Moderado',liberal_conservador:'Liberal/Cons.'};

function geoQuadrante(spe,afin){
  var ha=(afin||0)>=5,hi=(spe||0)>=4;
  if(ha&&hi)  return{lbl:'Prioridade',bg:'#FAEEDA',cor:'#633806'};
  if(!ha&&hi) return{lbl:'Expandir',  bg:'#E6F1FB',cor:'#0C447C'};
  if(ha&&!hi) return{lbl:'Consolidar',bg:'#E1F5EE',cor:'#085041'};
  return{lbl:'Não priorizar',bg:'#F1EFE8',cor:'#444441'};
}

function geoAbrirPanel(nome,dados){
  document.getElementById('geo-right-empty').style.display='none';
  var pb=document.getElementById('geo-panel-body');pb.style.display='block';
  var nomeBadge = dados && dados.sem_zona
    ? ' <span title="Esta RA não tem zona eleitoral própria no TSE 2022 — indicadores eleitorais não desagregáveis" style="background:#FAEEDA;color:#7A3E08;padding:2px 7px;border-radius:8px;font-size:10px;font-weight:500;vertical-align:middle">s/zona</span>'
    : '';
  var html='<div class="gp-ra-nome">'+nome+nomeBadge+'</div>';
  if(dados && dados.sem_zona){
    html += '<div style="font-size:11px;color:#7A3E08;background:#FFF7E6;border-left:3px solid #B45309;padding:6px 10px;border-radius:0 5px 5px 0;margin-bottom:10px;line-height:1.45"><strong>Observação:</strong> esta RA <strong>não tem zona eleitoral própria</strong> no TSE 2022 — seus eleitores votam em zonas das RAs vizinhas. Por isso, os indicadores eleitorais (eleitorado, votos, performance, margem) <strong>não são desagregáveis</strong> e aparecem zerados ou indisponíveis. Indicadores socioeconômicos da PDAD 2021 são preservados normalmente.</div>';
  }

  // ── População
  html+='<div class="gp-section"><div class="gp-sec-title">População</div><div class="gp-kpi-grid">'
    +'<div class="gp-kpi"><div class="gp-kpi-val">'+(dados.renda_pc?'R$'+fpt(dados.renda_pc/1000)+'K':'—')+'</div><div class="gp-kpi-lbl">Renda per capita</div></div>'
    +'<div class="gp-kpi"><div class="gp-kpi-val">'+(dados.pct_ab!=null?fpt(dados.pct_ab)+'%':'—')+'</div><div class="gp-kpi-lbl">Classe A/B</div></div>'
    +'<div class="gp-kpi"><div class="gp-kpi-val">'+(dados.pct_de!=null?fpt(dados.pct_de)+'%':'—')+'</div><div class="gp-kpi-lbl">Classe D/E</div></div>'
    +'<div class="gp-kpi"><div class="gp-kpi-val">'+(dados.pct_super!=null?fpt(dados.pct_super)+'%':'—')+'</div><div class="gp-kpi-lbl">Superior</div></div>'
    +'<div class="gp-kpi"><div class="gp-kpi-val">'+(dados.pct_serv!=null?fpt(dados.pct_serv)+'%':'—')+'</div><div class="gp-kpi-lbl">Funcionalismo</div></div>'
    +'<div class="gp-kpi"><div class="gp-kpi-val">'+(dados.pct_beneficio!=null?fpt(dados.pct_beneficio)+'%':'—')+'</div><div class="gp-kpi-lbl">Benefício social</div></div>'
    +'</div></div>';

  // ── Eleitorado
  html+='<div class="gp-section"><div class="gp-sec-title">Eleitorado</div><div class="gp-kpi-grid">'
    +'<div class="gp-kpi"><div class="gp-kpi-val">'+(dados.el_aptos?(dados.el_aptos/1000).toFixed(0)+'K':'—')+'</div><div class="gp-kpi-lbl">Eleitores aptos</div></div>'
    +'<div class="gp-kpi"><div class="gp-kpi-val">'+(dados.el_fem!=null?fpt(dados.el_fem)+'%':'—')+'</div><div class="gp-kpi-lbl">Feminino</div></div>'
    +'<div class="gp-kpi"><div class="gp-kpi-val">'+(dados.el_jov!=null?fpt(dados.el_jov)+'%':'—')+'</div><div class="gp-kpi-lbl">Jovens 16–24</div></div>'
    +'<div class="gp-kpi"><div class="gp-kpi-val">'+(dados.el_ido!=null?fpt(dados.el_ido)+'%':'—')+'</div><div class="gp-kpi-lbl">Idosos 60+</div></div>'
    +'</div></div>';

  // ── Campo Político
  var vts=dados.votos&&dados.votos[geoCargo];
  if(vts&&Object.keys(vts).length){
    html+='<div class="gp-section"><div class="gp-sec-title">Campo Político · '+CARGO_LBL[geoCargo]+'</div>';
    Object.entries(vts).map(function(e){return [e[0], geoVotoPct(e[1])||0, (e[1]&&e[1].idx!=null)?e[1].idx:null];})
      .sort(function(a,b){return b[1]-a[1];}).forEach(function(entry){
      var c=entry[0],pct=entry[1],idx=entry[2],cor=CAMPO_COR[c]||'#999',lbl=CAMPO_LBL[c]||c;
      var pctTxt=pct.toFixed(1).replace('.',',');
      var idxTxt='';
      if(idx!=null){
        var delta=Math.round((idx-1)*100);
        var sgn=delta>=0?'+':'';
        var idxColor=delta>=0?'#085041':'#791F1F';
        idxTxt=' <span style="font-size:10px;color:'+idxColor+';font-weight:500">('+sgn+delta+'%)</span>';
      }
      html+='<div class="gp-campo-row"><span class="gp-campo-nome">'+lbl+'</span>'
        +'<div class="gp-bar-bg"><div class="gp-bar-fill" style="width:'+pct+'%;background:'+cor+'"></div></div>'
        +'<span class="gp-bar-val">'+pctTxt+'%'+idxTxt+'</span></div>';
    });
    html+='</div>';
  }

  // ── Diagnóstico (estrutural do CSV + frase de voto dinâmica do cargo selecionado)
  if(dados.narrativa){
    var narrEstrut = dados.narrativa.replace(/^#+ */gm,'').trim();
    var fraseVoto = (dados && dados.sem_zona) ? '' : geoFraseVotoCargo(dados, geoCargo);
    var narrFull = narrEstrut + (fraseVoto ? ' ' + fraseVoto : '');
    // Converte **negrito** para <strong>
    narrFull = narrFull.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    html+='<div class="gp-section"><div class="gp-sec-title">Diagnóstico</div>'
      +'<div class="gp-narr">'+narrFull+'</div></div>';
  }

  pb.innerHTML=html;
}

// Frase ELI5 de voto, parametrizada pelo cargo selecionado no toolbar.
// Gerada em runtime para reagir à mudança de cargo sem precisar reabrir o painel.
function geoFraseVotoCargo(dados, cargo){
  var votos = (dados && dados.votos) || {};
  var v = votos[cargo] || {};
  var campos = {};
  Object.keys(v).forEach(function(k){
    var rec = v[k];
    if(rec && typeof rec === 'object' && rec.pct != null) campos[k] = rec.pct;
  });
  var keys = Object.keys(campos);
  if(!keys.length) return '';
  // Ordena por pct desc
  keys.sort(function(a,b){ return campos[b] - campos[a]; });
  var domK = keys[0], domV = campos[domK];
  var segV = keys.length > 1 ? campos[keys[1]] : 0;
  var margem = domV - segV;
  var lblCampo = {progressista:'progressista', moderado:'moderado',
                  liberal_conservador:'liberal-conservador', outros:'outros'};
  var lblCargo = {GOVERNADOR:'Governador', SENADOR:'Senador',
                  DEPUTADO_FEDERAL:'Deputado Federal', DEPUTADO_DISTRITAL:'Deputado Distrital'};
  var dCampo = lblCampo[domK] || domK;
  var dCargo = lblCargo[cargo] || cargo;
  function pct(x){ return Math.round(x) + '%'; }
  if(margem >= 25){
    return 'Em 2022, na disputa para ' + dCargo + ', o campo **' + dCampo +
           '** dominou com folga (' + pct(domV) + ' dos votos válidos).';
  }
  if(margem >= 12){
    return 'Em 2022, o campo **' + dCampo + '** liderou a disputa para ' + dCargo +
           ' com ' + pct(domV) + ' dos votos válidos.';
  }
  if(margem > 0){
    return 'Em 2022, o voto para ' + dCargo + ' se dividiu — campo **' + dCampo +
           '** levemente à frente (' + pct(domV) + ', contra ' + pct(segV) + ' do segundo).';
  }
  return '';
}

// ── Controles toolbar ─────────────────────────────────────────────────────────
function geoRecolor(){
  geoVarSel=document.getElementById('geo-var-sel').value;
  geoRender();
  if(geoRaSel){
    var feat=GEO_DATA.features.find(function(f){return f.properties.RA_PIPE===geoRaSel;});
    if(feat)geoAbrirPanel(geoRaSel,feat.properties.dados||{});
  }
}

function geoSetCargo(c,btn){
  geoCargo=c;
  document.querySelectorAll('#geo-cargo-pills .geo-pill').forEach(function(b){b.className='geo-pill';});
  btn.className='geo-pill gp-cargo-on';
  geoRender();
  if(geoRaSel){
    var feat=GEO_DATA.features.find(function(f){return f.properties.RA_PIPE===geoRaSel;});
    if(feat)geoAbrirPanel(geoRaSel,feat.properties.dados||{});
  }
}

// (geoSetCampo removido junto com o filtro Campo — resíduo do SPE morto.)
"""

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    import time
    t0 = time.time()
    print()
    print("  GeoPolítica — Injetando no SPE dashboard")
    print("  " + "─" * 42)

    if not DASHBOARD_IN.exists():
        print(f"  ERRO: {DASHBOARD_IN} não encontrado. Rode python3 fase4_v2.py primeiro.")
        return
    if not GEOJSON_PATH.exists():
        print(f"  ERRO: {GEOJSON_PATH} não encontrado.")
        return

    print(f"  [1/4] Lendo {DASHBOARD_IN}...", end="", flush=True)
    html = DASHBOARD_IN.read_text(encoding="utf-8")
    print(f"\r  [1/4] Dashboard lido ({len(html)//1024} KB)")

    print("  [2/4] Processando GeoJSON...", end="", flush=True)
    geo = processar_geojson()
    dados_match = re.search(r'JSON\.parse\(atob\("([A-Za-z0-9+/=]+)"\)\)', html)
    if dados_match:
        dados_raw = json.loads(base64.b64decode(dados_match.group(1)).decode("utf-8"))
        for feat in geo["features"]:
            pipe_nome = feat["properties"]["RA_PIPE"]
            feat["properties"]["dados"] = dados_raw.get(pipe_nome, {})
        n_inj = sum(1 for f in geo["features"] if f["properties"].get("dados"))
        print(f"\r  [2/4] GeoJSON processado — dados de {n_inj} RAs injetados")
    else:
        for feat in geo["features"]:
            feat["properties"]["dados"] = {}
        print(f"\r  [2/4] GeoJSON processado (sem dados — rode o pipeline primeiro)")

    print("  [3/4] Injetando componentes...", end="", flush=True)

    leaflet_css = '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css">\n'
    leaflet_js  = '<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>\n'
    html = html.replace("<style>", leaflet_css + leaflet_js + "<style>", 1)
    html = html.replace("</style>", CSS_GEO + "\n</style>", 1)
    html = html.replace(NAV_PLACEHOLDER, NAV_GEO_ITEM, 1)

    logo_src = carregar_logo_b64()
    geo_html = GEO_SECTION_HTML.replace("__LOGO_SRC__", logo_src)

    MARKER = "  </div>\n</div>\n\n<!-- MODAL"
    if MARKER in html:
        html = html.replace(MARKER, "  </div>\n" + geo_html + "\n</div>\n\n<!-- MODAL", 1)
    else:
        print("\n  Warning: marcador não encontrado — inserindo antes do modal")
        html = html.replace("<!-- MODAL", geo_html + "\n<!-- MODAL", 1)

    geo_b64 = base64.b64encode(
        json.dumps(geo, ensure_ascii=True, separators=(",", ":")).encode("utf-8")
    ).decode("ascii")
    geo_js = GEO_JS.replace("__GEO_B64__", geo_b64)
    last_script_pos = html.rfind("</script>")
    html = html[:last_script_pos] + geo_js + "\n</script>" + html[last_script_pos+9:]

    print(f"\r  [3/4] Componentes injetados")

    print("  [4/4] Salvando...", end="", flush=True)
    OUTPUT.write_text(html, encoding="utf-8")
    kb = len(html.encode()) // 1024
    elapsed = time.time() - t0
    print(f"\r  [4/4] Salvo: {OUTPUT}  ({kb} KB)")
    print()
    print(f"  ✅ Concluído em {elapsed:.1f}s — abra {OUTPUT} no navegador")
    print()

if __name__ == "__main__":
    main()
