"""Substitui o conteúdo do <s-pesquisas> no template pelo novo painel
consolidado (findings + small multiples + tabela pivô) + modal com lista
das pesquisas individuais.

Uso: python3 _substituir_pesquisas_section.py
"""
from pathlib import Path

NOVO_BLOCO = '''      <style>
        /* ── Botão "Ver pesquisas individuais" + modal ───────────────── */
        #s-pesquisas .pq-modal-toggle {
          display:flex; align-items:center; gap:8px; cursor:pointer;
          padding:6px 12px; border:0.5px solid var(--bd2); border-radius:6px;
          background:var(--s1); color:var(--txt); font-size:11px;
          font-family:inherit; white-space:nowrap;
        }
        #s-pesquisas .pq-modal-toggle:hover { background:var(--s2); }
        #s-pesquisas .pq-modal-toggle .pq-mt-count {
          font-size:10px; color:#fff; background:#534AB7;
          border-radius:10px; padding:1px 7px; font-weight:600;
        }
        #s-pesquisas .pq-modal-toggle-row {
          display:flex; justify-content:space-between; align-items:center;
          padding:10px 22px; border-bottom:0.5px solid var(--bd);
          background:var(--s1); flex-shrink:0;
        }
        #s-pesquisas .pq-modal-toggle-info {
          font-size:11px; color:var(--muted);
        }

        /* Modal overlay */
        #s-pesquisas .pq-modal {
          display:none; position:fixed; inset:0; z-index:9000;
          background:rgba(0,0,0,0.45); backdrop-filter:blur(2px);
          align-items:center; justify-content:center; padding:30px;
        }
        #s-pesquisas .pq-modal.on { display:flex; }
        #s-pesquisas .pq-modal-box {
          background:var(--bg); border:0.5px solid var(--bd2); border-radius:10px;
          width:100%; max-width:920px; max-height:88vh;
          display:flex; flex-direction:column; overflow:hidden;
          box-shadow:0 8px 32px rgba(0,0,0,0.2);
        }
        #s-pesquisas .pq-modal-head {
          display:flex; align-items:baseline; gap:12px;
          padding:16px 22px; border-bottom:0.5px solid var(--bd);
        }
        #s-pesquisas .pq-modal-titulo { font-size:15px; font-weight:600; color:var(--txt); }
        #s-pesquisas .pq-modal-sub { font-size:11px; color:var(--muted); margin-left:auto; margin-right:14px; }
        #s-pesquisas .pq-modal-close {
          background:transparent; border:none; cursor:pointer;
          font-size:18px; color:var(--muted); padding:0 6px;
        }
        #s-pesquisas .pq-modal-close:hover { color:var(--txt); }
        #s-pesquisas .pq-modal-toolbar {
          display:flex; gap:12px; align-items:center; padding:10px 22px;
          border-bottom:0.5px solid var(--bd); background:var(--s1); flex-wrap:wrap;
        }
        #s-pesquisas .pq-modal-toolbar label {
          font-size:9px; letter-spacing:1.5px; text-transform:uppercase; color:var(--muted);
        }
        #s-pesquisas .pq-modal-toolbar select,
        #s-pesquisas .pq-modal-toolbar input {
          padding:5px 10px; border:0.5px solid var(--bd2); border-radius:6px;
          font-size:12px; background:var(--s1); color:var(--txt); outline:none;
          font-family:inherit;
        }
        #s-pesquisas .pq-modal-toolbar input { min-width:160px; }
        #s-pesquisas .pq-stats { margin-left:auto; font-size:11px; color:var(--muted); }
        #s-pesquisas .pq-list {
          padding:14px 22px; flex:1; overflow-y:auto; min-height:0;
        }

        /* ── Painel principal: análise consolidada ───────────────────── */
        #s-pesquisas .pq-main {
          flex:1; overflow-y:auto; min-height:0; padding:14px 22px 22px;
        }

        /* Findings cards */
        #s-pesquisas .pq-findings {
          display:flex; flex-direction:column; gap:10px;
          margin-bottom:18px;
        }
        #s-pesquisas .pq-finding {
          display:flex; gap:12px; padding:12px 14px;
          background:var(--s1); border:0.5px solid var(--bd); border-radius:8px;
          border-left:3px solid #534AB7;
        }
        #s-pesquisas .pq-finding .pq-num {
          flex-shrink:0; width:24px; height:24px; border-radius:50%;
          background:#534AB7; color:#fff;
          display:flex; align-items:center; justify-content:center;
          font-size:11px; font-weight:700;
        }
        #s-pesquisas .pq-finding .pq-fin-title {
          font-weight:600; color:var(--txt); font-size:13px; margin-bottom:3px;
        }
        #s-pesquisas .pq-finding .pq-fin-body {
          font-size:12px; color:var(--muted); line-height:1.5;
        }
        #s-pesquisas .pq-finding .pq-fin-body strong { color:var(--txt); font-weight:500; }
        #s-pesquisas .pq-finding .up { color:#0F6E56; font-weight:600; }
        #s-pesquisas .pq-finding .dn { color:#A32D2D; font-weight:600; }

        /* Small multiples */
        #s-pesquisas .pq-sm-section-head {
          display:flex; align-items:baseline; gap:10px; margin-bottom:8px;
        }
        #s-pesquisas .pq-sm-titulo {
          font-size:13px; font-weight:600; color:var(--txt);
        }
        #s-pesquisas .pq-sm-sub {
          font-size:11px; color:var(--muted);
        }
        #s-pesquisas .pq-legend {
          display:flex; gap:14px; padding:8px 12px; margin-bottom:10px;
          background:var(--s1); border:0.5px solid var(--bd); border-radius:6px;
          font-size:11px; flex-wrap:wrap; align-items:center;
        }
        #s-pesquisas .pq-legend-item { display:flex; align-items:center; gap:6px; color:var(--txt); }
        #s-pesquisas .pq-legend-dot { width:10px; height:10px; border-radius:50%; }
        #s-pesquisas .pq-legend-trend {
          margin-left:auto; color:var(--muted); font-size:10.5px;
          display:flex; align-items:center; gap:6px;
        }
        #s-pesquisas .pq-legend-trend-line {
          display:inline-block; width:18px; border-top:1.5px dashed var(--muted); opacity:0.6;
        }
        #s-pesquisas .pq-small-multiples {
          display:grid; grid-template-columns:1fr 1fr; gap:8px;
          background:var(--s1); border:0.5px solid var(--bd); border-radius:8px;
          padding:12px; margin-bottom:18px;
        }
        #s-pesquisas .pq-small-multiples svg {
          display:block; background:var(--bg); border-radius:4px;
        }

        /* Tabela pivô */
        #s-pesquisas .pq-pivot-titulo {
          font-size:13px; font-weight:600; color:var(--txt); margin-bottom:6px;
        }
        #s-pesquisas .pq-pivot-tabela {
          width:100%; border-collapse:collapse; font-size:11px;
          font-variant-numeric:tabular-nums;
          background:var(--s1); border:0.5px solid var(--bd); border-radius:8px;
          overflow:hidden;
        }
        #s-pesquisas .pq-pivot-tabela th {
          font-size:9px; padding:8px 6px; border-bottom:0.5px solid var(--bd);
          text-align:right; vertical-align:bottom;
          color:var(--muted); font-weight:500;
        }
        #s-pesquisas .pq-pivot-tabela th:first-child {
          text-align:left; padding-left:14px;
        }
        #s-pesquisas .pq-pivot-tabela th .pq-col-data {
          display:block; font-weight:600; color:var(--txt); font-size:10px;
        }
        #s-pesquisas .pq-pivot-tabela th .pq-col-inst {
          display:block; font-size:8.5px; font-weight:500; margin-top:1px;
        }
        #s-pesquisas .pq-pivot-tabela th.pq-delta-col {
          font-size:9px; letter-spacing:.5px; text-transform:uppercase;
        }
        #s-pesquisas .pq-pivot-tabela td {
          padding:6px 6px; border-bottom:0.5px solid var(--bd);
          text-align:right; color:var(--txt);
        }
        #s-pesquisas .pq-pivot-tabela td.pq-cand-cell {
          text-align:left; padding-left:14px; display:flex; align-items:center; gap:6px;
        }
        #s-pesquisas .pq-pivot-tabela .pq-cor-dot { width:8px; height:8px; border-radius:50%; flex-shrink:0; }
        #s-pesquisas .pq-pivot-tabela .pq-partido {
          color:var(--muted); font-size:9px; margin-left:4px; font-weight:400;
        }
        #s-pesquisas .pq-pivot-tabela tr:last-child td { border-bottom:none; }
        #s-pesquisas .pq-pivot-tabela td.pq-delta { font-weight:600; }
        #s-pesquisas .pq-pivot-tabela td.pq-delta.up { color:#0F6E56; }
        #s-pesquisas .pq-pivot-tabela td.pq-delta.dn { color:#A32D2D; }
        #s-pesquisas .pq-pivot-tabela td.pq-delta.eq { color:var(--muted); }

        /* Cards individuais — quando dentro do modal */
        #s-pesquisas .pq-card {
          background:var(--s1); border:0.5px solid var(--bd); border-radius:8px;
          padding:12px 14px; margin-bottom:8px;
        }
        #s-pesquisas .pq-card-head { display:flex; align-items:baseline; gap:10px; flex-wrap:wrap; }
        #s-pesquisas .pq-instituto { font-size:13px; font-weight:600; color:var(--txt); }
        #s-pesquisas .pq-data-div { font-size:11px; color:var(--muted); margin-left:auto; font-variant-numeric:tabular-nums; }
        #s-pesquisas .pq-protocolo { font-size:10px; color:var(--muted); font-family:var(--mono,monospace); }
        #s-pesquisas .pq-status {
          font-size:9px; padding:2px 8px; border-radius:10px;
          letter-spacing:.5px; text-transform:uppercase;
        }
        #s-pesquisas .pq-status.extraido { background:#E1F5EE; color:#085041; }
        #s-pesquisas .pq-status.pendente { background:#FAEEDA; color:#633806; }
        #s-pesquisas .pq-status.falhou   { background:#FCEBEB; color:#791F1F; }
        #s-pesquisas .pq-status.sem_pdf  { background:var(--s2); color:var(--muted); }
        #s-pesquisas .pq-meta-row {
          display:flex; gap:18px; flex-wrap:wrap;
          margin-top:5px; font-size:11px; color:var(--muted);
        }
        #s-pesquisas .pq-meta-row strong { color:var(--txt); font-weight:500; }
        #s-pesquisas .pq-cargos { display:flex; gap:5px; flex-wrap:wrap; margin-top:6px; }
        #s-pesquisas .pq-cargo-badge {
          font-size:10px; padding:2px 8px; border-radius:10px;
          background:#EEEDFE; color:#3C3489; font-weight:500;
        }
        #s-pesquisas .pq-actions { margin-top:8px; }
        #s-pesquisas .pq-link {
          font-size:11px; color:#185FA5; text-decoration:none;
          padding:3px 8px; border-radius:5px; border:0.5px solid var(--bd2);
          background:var(--s1);
        }
        #s-pesquisas .pq-link:hover { background:var(--s2); }
        #s-pesquisas .pq-empty { padding:30px 22px; color:var(--muted); font-size:12px; text-align:center; }
        #s-pesquisas .pq-demo-badge {
          font-size:9px; padding:2px 7px; border-radius:10px;
          background:#534AB7; color:#fff; font-weight:600;
          letter-spacing:.5px; text-transform:uppercase;
        }
        #s-pesquisas .pq-card.demo { border-left:3px solid #534AB7; }
      </style>

      <div class="pq-modal-toggle-row">
        <span class="pq-modal-toggle-info" id="pq-mt-info">—</span>
        <button class="pq-modal-toggle" onclick="pqAbrirModal()">
          <span>Ver pesquisas individuais</span>
          <span class="pq-mt-count" id="pq-mt-count">—</span>
        </button>
      </div>

      <div class="pq-main">
        <div id="pq-findings-box"></div>

        <div class="pq-sm-section-head">
          <span class="pq-sm-titulo" id="pq-sm-titulo">Evolução por candidato</span>
          <span class="pq-sm-sub" id="pq-sm-sub">—</span>
        </div>
        <div class="pq-legend" id="pq-legend"></div>
        <div class="pq-small-multiples" id="pq-sm-grid"></div>

        <div class="pq-pivot-titulo">Tabela pivô · candidatos × pesquisas</div>
        <div id="pq-pivot-wrap"></div>
      </div>

      <!-- MODAL: lista das pesquisas individuais -->
      <div class="pq-modal" id="pq-modal" onclick="if(event.target.id===\'pq-modal\')pqFecharModal()">
        <div class="pq-modal-box">
          <div class="pq-modal-head">
            <span class="pq-modal-titulo">Pesquisas individuais</span>
            <span class="pq-modal-sub" id="pq-modal-sub">—</span>
            <button class="pq-modal-close" onclick="pqFecharModal()" aria-label="Fechar">×</button>
          </div>
          <div class="pq-modal-toolbar">
            <label for="pq-f-cargo">Cargo</label>
            <select id="pq-f-cargo" onchange="pqFiltrar()">
              <option value="">Todos</option>
              <option value="Governador">Governador</option>
              <option value="Senador">Senador</option>
              <option value="Deputado Federal">Dep. Federal</option>
              <option value="Deputado Distrital">Dep. Distrital</option>
            </select>
            <label for="pq-f-instituto">Instituto</label>
            <input id="pq-f-instituto" placeholder="filtrar..." oninput="pqFiltrar()">
            <label for="pq-f-status">Tipo</label>
            <select id="pq-f-status" onchange="pqFiltrar()">
              <option value="">Todas</option>
              <option value="demo">DEMO</option>
              <option value="extraido">Extraídas</option>
              <option value="pendente">Pendentes</option>
            </select>
            <span class="pq-stats" id="pq-stats"></span>
          </div>
          <div class="pq-list" id="pq-list"></div>
        </div>
      </div>

      <script>
      var PESQUISAS = JSON.parse(atob("__PESQUISAS_B64__"));
      var PQ = PESQUISAS || { pesquisas: [], n_pesquisas: 0, atualizado_em: null };

      function pqFmt(n, casas){
        casas = casas==null?1:casas;
        return n.toFixed(casas).replace(\'.\',\',\');
      }
      function pqFmtNum(n){ return n.toLocaleString(\'pt-BR\'); }
      function pqFmtData(s){
        if(!s) return \'—\';
        var p = s.split(\'-\');
        return p.length===3 ? p[2]+\'/\'+p[1]+\'/\'+p[0] : s;
      }
      function pqFmtDataCurta(s){
        if(!s) return \'\';
        var p = s.split(\'-\');
        return p.length===3 ? p[2]+\'/\'+p[1] : s;
      }

      function pqStatusLabel(st){
        return { extraido:\'Extraída\', pendente:\'Pendente\', falhou:\'Falhou\', sem_pdf:\'Sem PDF\' }[st] || st;
      }

      // ──────────────────────────────────────────────────────────────────
      // PAINEL CONSOLIDADO (findings + small multiples + pivô)
      // ──────────────────────────────────────────────────────────────────
      function pqRenderFindings(c){
        if (!c || !c.findings || !c.findings.length) {
          document.getElementById(\'pq-findings-box\').innerHTML = \'\';
          return;
        }
        var html = \'<div class="pq-findings">\' + c.findings.map(function(f, i){
          return \'<div class="pq-finding">\' +
            \'<div class="pq-num">\'+(i+1)+\'</div>\' +
            \'<div>\' +
              \'<div class="pq-fin-title">\'+f.titulo+\'</div>\' +
              \'<div class="pq-fin-body">\'+f.body+\'</div>\' +
            \'</div>\' +
          \'</div>\';
        }).join(\'\') + \'</div>\';
        document.getElementById(\'pq-findings-box\').innerHTML = html;
      }

      function pqRenderLegend(c){
        var legenda = c.institutos.map(function(i){
          return \'<div class="pq-legend-item"><span class="pq-legend-dot" style="background:\'+i.cor+\'"></span>\'+i.nome+\'</div>\';
        }).join(\'\');
        legenda += \'<span class="pq-legend-trend"><span class="pq-legend-trend-line"></span>linha = tendência consolidada (regressão linear)</span>\';
        document.getElementById(\'pq-legend\').innerHTML = legenda;
      }

      function pqSmallMultipleSvg(cand, datasMaxDia){
        var W = 340, H = 170;
        var padTop=18, padBot=30, padL=36, padR=14;
        var plotW = W - padL - padR;
        var plotH = H - padTop - padBot;
        var yMax = 25, yMin = 0;
        var diaMax = datasMaxDia;

        function xp(d){ return padL + (d / diaMax) * plotW; }
        function yp(pct){ return padTop + plotH - ((pct - yMin) / (yMax - yMin)) * plotH; }

        var instCor = {};
        (PQ.consolidacao_demo.institutos || []).forEach(function(i){ instCor[i.nome] = i.cor; });

        var parts = [];
        parts.push(\'<svg width="\'+W+\'" height="\'+H+\'" viewBox="0 0 \'+W+\' \'+H+\'" xmlns="http://www.w3.org/2000/svg">\');

        // Y gridlines + labels
        [0,5,10,15,20,25].forEach(function(v){
          var y = yp(v);
          parts.push(\'<line x1="\'+padL+\'" y1="\'+y.toFixed(1)+\'" x2="\'+(padL+plotW)+\'" y2="\'+y.toFixed(1)+\'" stroke="#E5E7EB" stroke-width="0.5"/>\');
          parts.push(\'<text x="\'+(padL-4)+\'" y="\'+(y+3).toFixed(1)+\'" font-size="9" fill="#9CA3AF" text-anchor="end" font-family="-apple-system,sans-serif">\'+v+\'%</text>\');
        });

        // X labels (meses fixos)
        var xLabels = [
          {dia: 0,  lbl: \'fev\'},
          {dia: 28, lbl: \'mar\'},
          {dia: 59, lbl: \'abr\'},
          {dia: 89, lbl: \'mai\'},
        ];
        xLabels.forEach(function(m){
          var x = xp(m.dia);
          parts.push(\'<text x="\'+x.toFixed(1)+\'" y="\'+(H-padBot+14)+\'" font-size="9" fill="#6B7280" text-anchor="middle" font-family="-apple-system,sans-serif">\'+m.lbl+\'</text>\');
        });

        // Linha de regressão (tracejada)
        var x1 = 0, x2 = diaMax;
        var y1 = cand.intercept + cand.slope * x1;
        var y2 = cand.intercept + cand.slope * x2;
        parts.push(\'<line x1="\'+xp(x1).toFixed(1)+\'" y1="\'+yp(y1).toFixed(1)+\'" x2="\'+xp(x2).toFixed(1)+\'" y2="\'+yp(y2).toFixed(1)+\'" stroke="\'+cand.cor+\'" stroke-width="1.5" stroke-dasharray="4,3" opacity="0.45"/>\');

        // Pontos por instituto
        cand.serie.forEach(function(p){
          var cor = instCor[p.instituto] || \'#9CA3AF\';
          parts.push(\'<circle cx="\'+xp(p.dia).toFixed(1)+\'" cy="\'+yp(p.pct).toFixed(1)+\'" r="4" fill="\'+cor+\'" stroke="#fff" stroke-width="1.2"/>\');
        });

        // Header: nome + delta
        var sgn = cand.delta >= 0 ? \'+\' : \'\';
        var corDelta = cand.delta >= 0.5 ? \'#0F6E56\' : (cand.delta <= -0.5 ? \'#A32D2D\' : \'#9CA3AF\');
        parts.push(\'<text x="\'+padL+\'" y="13" font-size="11" font-weight="600" fill="#1A1A1A" font-family="-apple-system,sans-serif">\'+cand.nome+\'</text>\');
        parts.push(\'<text x="\'+(padL+100)+\'" y="13" font-size="9" fill="#6B7280" font-family="-apple-system,sans-serif">\'+cand.partido+\'</text>\');
        parts.push(\'<text x="\'+(W-padR)+\'" y="13" font-size="11" font-weight="600" fill="\'+corDelta+\'" text-anchor="end" font-family="-apple-system,sans-serif">\'+sgn+pqFmt(cand.delta,1)+\'pp</text>\');

        parts.push(\'</svg>\');
        return parts.join(\'\');
      }

      function pqRenderSmallMultiples(c){
        // Calcula maior dia das séries
        var diaMax = 0;
        c.candidatos.forEach(function(cand){
          cand.serie.forEach(function(p){ if (p.dia > diaMax) diaMax = p.dia; });
        });
        var html = c.candidatos.map(function(cand){
          return pqSmallMultipleSvg(cand, diaMax);
        }).join(\'\');
        document.getElementById(\'pq-sm-grid\').innerHTML = html;

        document.getElementById(\'pq-sm-titulo\').textContent =
          \'Evolução por candidato — \' + c.cargo;
        document.getElementById(\'pq-sm-sub\').textContent =
          c.candidatos.length + \' candidatos · \' + c.n_pesquisas + \' pesquisas · escala fixa 0–25%\';
      }

      function pqRenderPivot(c){
        var headers = c.candidatos[0].serie.map(function(p){
          var instCor = (PQ.consolidacao_demo.institutos || []).find(function(i){return i.nome===p.instituto;});
          var cor = instCor ? instCor.cor : \'#9CA3AF\';
          return \'<th><span class="pq-col-data">\'+pqFmtDataCurta(p.data)+\'</span>\'+
                 \'<span class="pq-col-inst" style="color:\'+cor+\'">\'+p.instituto+\'</span></th>\';
        }).join(\'\');
        var linhas = c.candidatos.map(function(cand){
          var celulas = cand.serie.map(function(p){
            return \'<td>\'+pqFmt(p.pct,0)+\'%</td>\';
          }).join(\'\');
          var sgn = cand.delta >= 0 ? \'+\' : \'\';
          var cls = cand.delta >= 0.5 ? \'up\' : (cand.delta <= -0.5 ? \'dn\' : \'eq\');
          return \'<tr><td class="pq-cand-cell">\'+
            \'<span class="pq-cor-dot" style="background:\'+cand.cor+\'"></span>\'+
            cand.nome+\'<span class="pq-partido">\'+cand.partido+\'</span></td>\'+
            celulas+
            \'<td class="pq-delta \'+cls+\'">\'+sgn+pqFmt(cand.delta,1)+\'pp</td></tr>\';
        }).join(\'\');
        var html = \'<table class="pq-pivot-tabela">\'+
          \'<thead><tr><th>Candidato</th>\'+headers+\'<th class="pq-delta-col">Δ período</th></tr></thead>\'+
          \'<tbody>\'+linhas+\'</tbody></table>\';
        document.getElementById(\'pq-pivot-wrap\').innerHTML = html;
      }

      function pqRenderConsolidacao(){
        var c = PQ.consolidacao_demo;
        if (!c) {
          document.getElementById(\'pq-findings-box\').innerHTML =
            \'<div class="pq-empty">Análise consolidada não disponível.</div>\';
          return;
        }
        pqRenderFindings(c);
        pqRenderLegend(c);
        pqRenderSmallMultiples(c);
        pqRenderPivot(c);
      }

      // ──────────────────────────────────────────────────────────────────
      // MODAL: lista de pesquisas individuais
      // ──────────────────────────────────────────────────────────────────
      window.pqAbrirModal = function(){
        document.getElementById(\'pq-modal\').classList.add(\'on\');
        pqFiltrar();
      };
      window.pqFecharModal = function(){
        document.getElementById(\'pq-modal\').classList.remove(\'on\');
      };

      function pqEgoNome(){
        if (typeof CAND_ATIVO === \'undefined\' || !CAND_ATIVO) return null;
        return (CAND_ATIVO.nome || \'\').toLowerCase();
      }

      function pqCardHtml(p){
        var st = (p.extracao && p.extracao.status) || \'pendente\';
        var isDemo = !!p.is_demo;
        var cargosBadges = (p.cargo || []).map(function(c){
          return \'<span class="pq-cargo-badge">\'+c+\'</span>\';
        }).join(\'\');

        var meta = \'\';
        if (p.data_campo_inicio) {
          meta += \'<span><strong>Campo:</strong> \'+pqFmtData(p.data_campo_inicio)+
                  (p.data_campo_fim && p.data_campo_fim!==p.data_campo_inicio ? \' a \'+pqFmtData(p.data_campo_fim) : \'\')+\'</span>\';
        }
        if (p.n_entrevistados) {
          meta += \'<span><strong>\'+p.n_entrevistados.toLocaleString(\'pt-BR\')+\'</strong> entrevistas</span>\';
        }
        if (p.estatistico && !isDemo) {
          meta += \'<span><strong>Estatístico:</strong> \'+p.estatistico+(p.conre?\' (CONRE \'+p.conre+\')\':\'\')+\'</span>\';
        }

        var demoBadge = isDemo ? \'<span class="pq-demo-badge">DEMO</span>\' : \'\';
        var actions = \'\';
        if (p.url_tse_pesqele) {
          actions = \'<div class="pq-actions">\' +
            \'<a class="pq-link" href="\'+p.url_tse_pesqele+\'" target="_blank" rel="noopener">Página TSE ↗</a>\' +
          \'</div>\';
        }

        return \'<div class="pq-card\'+(isDemo?\' demo\':\'\')+\'">\' +
          \'<div class="pq-card-head">\' +
            \'<span class="pq-instituto">\'+(p.instituto || \'—\')+\'</span>\' +
            demoBadge +
            (isDemo ? \'\' : \'<span class="pq-status \'+st+\'">\'+pqStatusLabel(st)+\'</span>\') +
            \'<span class="pq-protocolo">\'+p.protocolo+\'</span>\' +
            \'<span class="pq-data-div">\'+pqFmtData(p.data_divulgacao)+\'</span>\' +
          \'</div>\' +
          \'<div class="pq-cargos">\'+cargosBadges+\'</div>\' +
          \'<div class="pq-meta-row">\'+meta+\'</div>\' +
          actions +
        \'</div>\';
      }

      window.pqFiltrar = function(){
        var fcargo = document.getElementById(\'pq-f-cargo\').value;
        var finst  = (document.getElementById(\'pq-f-instituto\').value || \'\').toLowerCase().normalize(\'NFD\').replace(/[\\u0300-\\u036f]/g,\'\');
        var fst    = document.getElementById(\'pq-f-status\').value;
        var lista = (PQ.pesquisas || []).filter(function(p){
          if (fcargo && !(p.cargo || []).includes(fcargo)) return false;
          if (finst) {
            var nm = (p.instituto||\'\').toLowerCase().normalize(\'NFD\').replace(/[\\u0300-\\u036f]/g,\'\');
            if (!nm.includes(finst)) return false;
          }
          if (fst === \'demo\') {
            if (!p.is_demo) return false;
          } else if (fst) {
            if ((p.extracao && p.extracao.status) !== fst) return false;
          }
          return true;
        });

        var el = document.getElementById(\'pq-list\');
        if (!lista.length) {
          el.innerHTML = \'<div class="pq-empty">Nenhuma pesquisa para esses filtros.</div>\';
        } else {
          el.innerHTML = lista.map(pqCardHtml).join(\'\');
        }
        document.getElementById(\'pq-stats\').textContent =
          lista.length + \' de \' + (PQ.pesquisas||[]).length + \' pesquisas\';
      };

      // ──────────────────────────────────────────────────────────────────
      // INIT
      // ──────────────────────────────────────────────────────────────────
      function pqInit(){
        var sub = document.getElementById(\'pq-meta-sub\');
        if (PQ.atualizado_em) {
          var dt = new Date(PQ.atualizado_em);
          sub.textContent = \'· TSE Dados Abertos · atualizado em \' + dt.toLocaleDateString(\'pt-BR\');
        }
        var n = (PQ.pesquisas||[]).length;
        var nDemo = (PQ.pesquisas||[]).filter(function(p){return p.is_demo;}).length;
        document.getElementById(\'pq-mt-count\').textContent = n;
        document.getElementById(\'pq-mt-info\').textContent =
          \'Análise consolidada em destaque. \' + (n - nDemo) + \' pesquisas TSE + \' + nDemo + \' DEMO disponíveis.\';
        document.getElementById(\'pq-modal-sub\').textContent = n + \' pesquisas\';

        pqRenderConsolidacao();
      }
      pqInit();
      </script>
    </div>'''

p = Path("estrategos_template.html")
src = p.read_text(encoding="utf-8")

inicio_marker = "      <style>\n        #s-pesquisas .pq-toolbar"
fim_marker = "      pqInit();\n      </script>\n    </div>"

i_inicio = src.find(inicio_marker)
i_fim_busca = src.find(fim_marker)
if i_inicio == -1 or i_fim_busca == -1:
    raise SystemExit("Marcadores não encontrados")
i_fim = i_fim_busca + len(fim_marker)

novo_src = src[:i_inicio] + NOVO_BLOCO + src[i_fim:]
p.write_text(novo_src, encoding="utf-8")
print(f"OK: substituído ({len(NOVO_BLOCO):,} chars novos vs {i_fim-i_inicio:,} antigos)")
