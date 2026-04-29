"""
Gera os dados consolidados de um candidato para alimentar o protótipo
do playbook standalone (playbook_<NOME>.html).

Saída: playbook_dados_<APELIDO>.json — embutido inline no HTML.

Uso: python gerar_playbook_dados.py MANZONI
"""
import csv
import json
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent

# ────────── candidatos suportados ──────────────────────────────────
# match: substring que identifica o candidato no NM_CANDIDATO
# cargo: filtro de cargo (precisa para candidatos com nomes parecidos em cargos diferentes)
CANDIDATOS = {
    # Expressivos
    "FELIX":     {"match":"FÁBIO FELIX",                "cargo":"DEPUTADO_DISTRITAL", "nome_curto":"FÁBIO FELIX"},
    "MANZONI":   {"match":"MANZONI",                    "cargo":"DEPUTADO_DISTRITAL", "nome_curto":"THIAGO MANZONI"},
    "BELMONTE":  {"match":"PAULA MORENO PARO BELMONTE", "cargo":"DEPUTADO_DISTRITAL", "nome_curto":"PAULA BELMONTE"},
    "DAMARES":   {"match":"DAMARES",                    "cargo":"SENADOR",            "nome_curto":"DAMARES ALVES"},
    "KICIS":     {"match":"BEATRIZ KICIS",              "cargo":"DEPUTADO_FEDERAL",   "nome_curto":"BIA KICIS"},
    "IBANEIS":   {"match":"IBANEIS ROCHA",              "cargo":"GOVERNADOR",         "nome_curto":"IBANEIS ROCHA"},
    # Não expressivos (para validar edge cases)
    "ROGERIO":   {"match":"ROGÉRIO EDUARDO PEREIRA",    "cargo":"DEPUTADO_DISTRITAL", "nome_curto":"ROGÉRIO PEREIRA"},
    "RITA":      {"match":"RITA DE CÁSSIA",             "cargo":"DEPUTADO_FEDERAL",   "nome_curto":"RITA DE CÁSSIA"},
    "YARA":      {"match":"YARA MARISTELA",             "cargo":"SENADOR",            "nome_curto":"YARA MARISTELA"},
}

# Lote de revisão expressa (ordem de leitura sugerida)
BATCH_REVISAO = [
    "FELIX", "MANZONI", "BELMONTE",       # expressivos · Distrital
    "DAMARES", "KICIS", "IBANEIS",        # expressivos · cargos majoritários
    "ROGERIO", "RITA", "YARA",            # não expressivos · derrotados
]

# ────────── thresholds (alinhados com fase4_v2.py) ─────────────────
T_PERF = 0.15  # ±15% para classificar
T_CAMPO = 0.15

# Configurações por cargo
VAGAS_CARGO = {
    "GOVERNADOR": 1, "SENADOR": 2,
    "DEPUTADO_FEDERAL": 8, "DEPUTADO_DISTRITAL": 24,
}

# Referências de votos para cenários simulados (paridade com PB_STATS_ELEITOS_2022 do dashboard).
# SENADOR 2026 elege 2 vagas: cada eleitor vota em 2 → universo de votos no cargo
#   ≈ 2× comparecimento. Top 2 não dividem fatias distintas: ambos podem ser
#   escolhidos pelo mesmo eleitor. Modelagem realista usa "% de aderência dos top
#   candidatos sobre o comparecimento (~1,7M)" e calibra 3 cenários distintos
#   (não 3 níveis de intensidade do mesmo cenário). Defaults aqui = ESTRUTURADO.
# GOVERNADOR: 1 vaga; cenário único (~maioria absoluta dos válidos = Ibaneis 2022).
STATS_VOTOS_2022 = {
    "GOVERNADOR":         {"min": 830071, "mediana": 830071, "lider": 830071, "n_eleitos": 1},
    "SENADOR":            {"min": 680000, "mediana": 765000, "lider": 850000, "n_eleitos": 2},
    "DEPUTADO_FEDERAL":   {"min": 45823,  "mediana": 98316,  "lider": 214321, "n_eleitos": 8},
    "DEPUTADO_DISTRITAL": {"min": 17187,  "mediana": 20890,  "lider": 51781,  "n_eleitos": 24},
}
# Cenários SENADOR 2026 — usados no diag config quando o usuário seleciona simulação
# para Senador. Cada cenário traz a expectativa do líder, mediana e mínimo eleito,
# ancorada em 2018 (último DF com 2 vagas) e em hipóteses de polarização.
SENADOR_CENARIOS = {
    "polarizado":  {"min": 1190000, "mediana": 1232000, "lider": 1275000,
                    "label": "2 nomes dominam · ambos top fazem ~70% (Damares+Ibaneis)"},
    "estruturado": {"min":  680000, "mediana":  765000, "lider":  850000,
                    "label": "3 nomes competitivos · top 2 fazem ~45% cada (cenário base)"},
    "fragmentado": {"min":  425000, "mediana":  467000, "lider":  510000,
                    "label": "5+ nomes competitivos · top 2 fazem ~28% cada (perfil 2018)"},
}
PATAMAR_CARGO = {
    "GOVERNADOR": 700000, "SENADOR": 765000,
    "DEPUTADO_FEDERAL": 30000, "DEPUTADO_DISTRITAL": 18000,
}

# ────────── conglomerados socioeconômicos (4 grupos) ──────────────
# Classificação editorial Estrategos: homogeneidade socioeconômica que
# correlaciona com comportamento eleitoral. Ver DECISOES_PROJETO.md.
GRUPOS_PED = [
    ("Brasília Central", [
        "Brasília (Plano Piloto)", "Jardim Botânico", "Lago Norte",
        "Lago Sul", "Park Way", "Sudoeste/Octogonal",
    ]),
    ("Regiões Maduras", [
        "Águas Claras", "Candangolândia", "Cruzeiro", "Gama", "Guará",
        "Núcleo Bandeirante", "Sobradinho", "Sobradinho II",
        "Taguatinga", "Vicente Pires", "SIA", "Arniqueira",
    ]),
    ("Regiões Populares", [
        "Brazlândia", "Ceilândia", "Planaltina", "Riacho Fundo",
        "Riacho Fundo II", "Samambaia", "Santa Maria", "São Sebastião",
    ]),
    ("Periferia em Formação", [
        "Fercal", "Itapoã", "Paranoá", "Recanto das Emas",
        "SCIA/Estrutural", "Varjão", "Sol Nascente/Pôr do Sol",
    ]),
]

# ────────── helpers ────────────────────────────────────────────────
def _norm(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().upper().strip()


def status_zona(perf, campo):
    """Retorna a zona estratégica (5 categorias) a partir de Performance × Força do campo.
    perf e campo são índices (1.00 = neutro)."""
    if perf is None or campo is None:
        return None
    pdesv = perf - 1
    cdesv = campo - 1
    if pdesv >= T_PERF and cdesv >= T_CAMPO:
        return "compartilhado"  # Reduto consolidado
    if pdesv >= T_PERF:
        return "pessoal"  # Voto pessoal
    if pdesv < -T_PERF and cdesv >= T_CAMPO:
        return "conquistar"  # Espaço a conquistar
    if pdesv < -T_PERF:
        return "sem_espaco"  # Sem espaço pelo campo
    return "esperado"


# ────────── 1. tabela mestre (aptos + PDAD) ────────────────────────
def carregar_mestre():
    """Retorna dict {ra_nome: {aptos, pdad...}}"""
    out = {}
    path = ROOT / "outputs_fase2" / "tabela_mestre_ra.csv"
    with path.open(encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            ra = r["RA_NOME"].strip()
            try:
                aptos = int(float(r["EL_total_aptos"]))
            except (ValueError, TypeError):
                aptos = 0
            out[ra] = {
                "aptos": aptos,
                # PDAD selecionado para o eleitor-tipo (8 KPIs da Pág. 6)
                "renda_pc": float(r.get("DOM_renda_pc_media", 0) or 0),
                "classe_ab": float(r.get("DOM_pct_classe_AB", 0) or 0),
                "superior": float(r.get("MOR_pct_superior", 0) or 0),
                "serv_fed": float(r.get("MOR_pct_servidor_fed", 0) or 0),
                "serv_dist": float(r.get("MOR_pct_servidor_dist", 0) or 0),
                "benef_social": float(r.get("MOR_pct_beneficio_social", 0) or 0),
                "nativo_df": float(r.get("MOR_pct_nativo_df", 0) or 0),
                "idosos_60": float(r.get("EL_pct_idoso_60mais", 0) or 0),
            }
    return out


# ────────── 2. votos do candidato + Performance ────────────────────
def carregar_votos_candidato(match, cargo="DEPUTADO_DISTRITAL"):
    """Retorna dict {ra_nome: {votos, perf, campo_str, partido, total_cand}}
    e meta {nome_oficial, campo_str, partido, total}."""
    path = ROOT / "outputs_fase3c" / "votos_candidato_ra.csv"
    rows = []
    nome_match = _norm(match)
    with path.open(encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            if _norm(r["NM_CANDIDATO"]).find(nome_match) >= 0 and r["DS_CARGO"] == cargo:
                rows.append(r)
    if not rows:
        raise RuntimeError(f"Candidato '{match}' (cargo={cargo}) não encontrado em votos_candidato_ra.csv")
    meta = {
        "nome": rows[0]["NM_CANDIDATO"].strip(),
        "campo": rows[0]["CAMPO"].strip(),
        "partido": rows[0]["SG_PARTIDO"].strip(),
        "cargo": rows[0]["DS_CARGO"].strip(),
        "total": int(rows[0]["TOTAL_CAND"]),
    }
    por_ra = {}
    for r in rows:
        ra = r["RA_NOME"].strip()
        por_ra[ra] = {
            "votos": int(r["QT_VOTOS_RA"]),
            "perf": float(r["INDICE_SOBRE"]),  # já é o sobre-índice
            "pct_do_campo": float(r["PCT_DO_CAMPO"]),
        }
    return meta, por_ra


# ────────── 3. votos do campo + Força do campo ─────────────────────
def carregar_votos_campo(campo, cargo="DEPUTADO_DISTRITAL"):
    """Retorna dict {ra_nome: votos_campo} e total do campo no DF."""
    path = ROOT / "outputs_fase3c" / "votos_campo_ra.csv"
    por_ra = {}
    with path.open(encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            if r["CAMPO"] == campo and r["DS_CARGO"] == cargo:
                ra = r["RA_NOME"].strip()
                por_ra[ra] = int(r["QT_VOTOS"])
    total = sum(por_ra.values())
    return por_ra, total


# ────────── 4. rivais por RA + agregado por zona ──────────────────
def carregar_nomes_urna(cargo):
    """Retorna {NM_CANDIDATO: NM_URNA} a partir do cadastro TSE 2022 (DF).
    cargo aqui usa underscore (ex: DEPUTADO_DISTRITAL); o CSV usa espaço."""
    out = {}
    path = ROOT / "outputs_tse_2022_DF" / "consulta_cand_DF.csv"
    if not path.exists():
        return out
    cargo_raw = cargo.replace("_", " ")
    with path.open(encoding="latin-1") as f:
        rdr = csv.reader(f, delimiter=";")
        header = [c.strip('"') for c in next(rdr)]
        idx = {c: i for i, c in enumerate(header)}
        for row in rdr:
            if row[idx["DS_CARGO"]].strip('"').upper() != cargo_raw:
                continue
            nm = row[idx["NM_CANDIDATO"]].strip('"').strip()
            urna = row[idx["NM_URNA_CANDIDATO"]].strip('"').strip()
            if nm and urna:
                out[nm] = urna
    return out


def carregar_rivais_por_ra(cargo, exclude_nome=None):
    """Para cada RA, ranking decrescente de candidatos do cargo por QT_VOTOS_RA.
    Retorna {ra: [{'nome', 'partido', 'campo', 'votos'}, ...]}."""
    path = ROOT / "outputs_fase3c" / "votos_candidato_ra.csv"
    by_ra = {}
    excl = _norm(exclude_nome) if exclude_nome else None
    with path.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["DS_CARGO"] != cargo:
                continue
            nome = r["NM_CANDIDATO"].strip()
            if excl and _norm(nome) == excl:
                continue
            try:
                v = int(r["QT_VOTOS_RA"])
            except ValueError:
                continue
            if v <= 0:
                continue
            ra = r["RA_NOME"].strip()
            by_ra.setdefault(ra, []).append({
                "nome": nome,
                "partido": r["SG_PARTIDO"].strip(),
                "campo": r["CAMPO"].strip(),
                "votos": v,
            })
    for ra in by_ra:
        by_ra[ra].sort(key=lambda x: -x["votos"])
    return by_ra


def montar_rivais(ras, cargo, exclude_nome, total_cand):
    """Anexa top 3 rivais (NM_URNA) a cada entrada de `ras` (in-place) e
    retorna {zona: {votos_cand, n_ras, pct_dos_votos, share_cand, rivais: [...]}}.

    Cada rival na lista vem com share = votos do rival / total da zona × 100
    (denominador inclui o candidato + todos os outros do cargo nas RAs daquela
    zona). share_cand é o equivalente do candidato. pct_dos_votos é o % do
    total do candidato que vem dessa zona — mede a importância da zona pro
    jogo dele."""
    rivais_lookup = carregar_rivais_por_ra(cargo, exclude_nome=exclude_nome)
    nomes_urna = carregar_nomes_urna(cargo)

    def _curto(nome):
        return nomes_urna.get(nome) or nome.title()

    acc = defaultdict(lambda: defaultdict(lambda: {"votos": 0, "partido": "", "campo": ""}))
    votos_cand_zona = defaultdict(int)
    n_ras_zona = defaultdict(int)
    total_zona = defaultdict(int)  # candidato + todos os rivais (denominador do share)
    for r in ras:
        ra = r["ra"]
        rivais_full = rivais_lookup.get(ra, [])
        r["top_rivais"] = [{
            "nome_urna": _curto(rv["nome"]),
            "partido": rv["partido"],
            "campo": rv["campo"],
            "votos": rv["votos"],
        } for rv in rivais_full[:3]]
        zona = r.get("zona")
        if not zona:
            continue
        v_cand = r.get("votos") or 0
        votos_cand_zona[zona] += v_cand
        n_ras_zona[zona] += 1
        total_zona[zona] += v_cand
        for rv in rivais_full:
            total_zona[zona] += rv["votos"]
            slot = acc[zona][rv["nome"]]
            slot["votos"] += rv["votos"]
            slot["partido"] = rv["partido"]
            slot["campo"] = rv["campo"]

    rivais_por_zona = {}
    for zona, mapa in acc.items():
        v_cand = votos_cand_zona.get(zona, 0)
        denom = total_zona.get(zona, 0) or 1
        lista = sorted([
            {"nome_urna": _curto(nome),
             "partido": m["partido"],
             "campo": m["campo"],
             "votos": m["votos"],
             "share": round(m["votos"] / denom * 100, 1)}
            for nome, m in mapa.items()
        ], key=lambda x: -x["votos"])[:3]
        rivais_por_zona[zona] = {
            "votos_cand": v_cand,
            "n_ras": n_ras_zona.get(zona, 0),
            "pct_dos_votos": (round(v_cand / total_cand * 100, 1)
                              if total_cand else 0),
            "share_cand": round(v_cand / denom * 100, 1),
            "rivais": lista,
        }
    return rivais_por_zona


# ────────── 4. consolidar tudo ─────────────────────────────────────
def gerar_dados(apelido, sim_cargo=None, sim_nivel=None, sim_nome=None):
    """Gera dados do playbook. Quando sim_cargo + sim_nivel são informados,
    aplica projeção do candidato base para o cargo destino preservando Performance:
    - Carrega votos reais do candidato base (de seu cargo original).
    - Aplica fator multiplicativo em todas as RAs para atingir votos_alvo do cargo
      destino (mín / mediana / líder).
    - Atualiza meta.cargo, meta.total. Os cálculos posteriores (zonas, alocação,
      orçamento) refletem o cargo destino.
    - sim_nome: troca o nome (cenário "Novo candidato").
    """
    cfg = CANDIDATOS[apelido]
    cargo_origem = cfg.get("cargo", "DEPUTADO_DISTRITAL")
    cargo = cargo_origem
    mestre = carregar_mestre()
    meta, votos_cand = carregar_votos_candidato(cfg["match"], cargo=cargo_origem)
    votos_campo, total_campo = carregar_votos_campo(meta["campo"], cargo=cargo_origem)

    # ─── Projeção (cenário simulado) ───
    simulado_info = None
    if sim_cargo and sim_nivel:
        if sim_cargo not in STATS_VOTOS_2022:
            raise ValueError(f"Cargo simulado desconhecido: {sim_cargo}")
        stats = STATS_VOTOS_2022[sim_cargo]
        # Para Senador, sim_nivel é um cenário (polarizado/estruturado/fragmentado).
        # Para os demais cargos, é intensidade (favoravel/possivel/conservador).
        if sim_cargo == "SENADOR" and sim_nivel in SENADOR_CENARIOS:
            votos_alvo = SENADOR_CENARIOS[sim_nivel]["mediana"]
        else:
            votos_alvo_map = {"conservador": stats["min"], "possivel": stats["mediana"], "favoravel": stats["lider"]}
            if sim_nivel not in votos_alvo_map:
                raise ValueError(f"Nível simulado desconhecido: {sim_nivel}")
            votos_alvo = votos_alvo_map[sim_nivel]
        total_atual = meta["total"] or 1
        fator = votos_alvo / total_atual
        # Aplica fator nas RAs (preserva Performance, todas as razões mantidas)
        for ra in votos_cand:
            votos_cand[ra]["votos"] = round(votos_cand[ra]["votos"] * fator)
        meta["total"] = int(round(total_atual * fator))
        meta["cargo"] = sim_cargo
        cargo = sim_cargo
        if sim_nome:
            meta["nome"] = sim_nome
        simulado_info = {
            "tipo": "estreante" if sim_nome else "outro_cargo",
            "referencia": cfg.get("nome_curto") or apelido,
            "cargo_origem": cargo_origem,
            "cargo_destino": sim_cargo,
            "nivel": sim_nivel,
            "fator": round(fator, 4),
            "votos_alvo": votos_alvo,
        }

    # Aptos totais DF
    aptos_df = sum(d["aptos"] for d in mestre.values())

    # Total de votos do cargo (todos os campos somados) — pra calcular PESO de cada RA
    total_cargo_por_ra = {}
    path = ROOT / "outputs_fase3c" / "votos_campo_ra.csv"
    with path.open(encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            if r["DS_CARGO"] != cargo:
                continue
            ra = r["RA_NOME"].strip()
            total_cargo_por_ra[ra] = int(r["TOTAL"])
    total_cargo_df = sum(total_cargo_por_ra.values())

    # Por RA: consolida tudo
    ras = []
    for ra, m in mestre.items():
        aptos = m["aptos"]
        if not aptos:
            continue
        v_cand = votos_cand.get(ra, {}).get("votos", 0)
        perf_cand = votos_cand.get(ra, {}).get("perf")
        v_campo = votos_campo.get(ra, 0)
        # Força do campo: (votos_campo_ra / total_campo) / (aptos_ra / aptos_df)
        if total_campo > 0 and aptos > 0:
            perf_campo = (v_campo / total_campo) / (aptos / aptos_df)
        else:
            perf_campo = None
        zona = status_zona(perf_cand, perf_campo)
        # % dos votos do candidato (frequência relativa)
        pct_votos_cand = (v_cand / meta["total"] * 100) if meta["total"] else 0
        # Peso eleitoral (= % do cargo no DF que veio dessa RA)
        peso = (total_cargo_por_ra.get(ra, 0) / total_cargo_df * 100) if total_cargo_df else 0

        # Grupo socioeconômico (BC/RC/RE/RF)
        grupo_ra = next((nome for nome, lst in GRUPOS_PED if ra in lst), "—")
        ras.append({
            "ra": ra,
            "aptos": aptos,
            "votos": v_cand,
            "votos_campo": v_campo,
            "pct_votos_cand": round(pct_votos_cand, 2),
            "perf": perf_cand,
            "perf_campo": perf_campo,
            "zona": zona,
            "grupo": grupo_ra,
            "peso": round(peso, 2),
            # PDAD
            "renda_pc": m["renda_pc"],
            "classe_ab": m["classe_ab"],
            "superior": m["superior"],
            "serv_fed": m["serv_fed"],
            "serv_dist": m["serv_dist"],
            "benef_social": m["benef_social"],
            "nativo_df": m["nativo_df"],
            "idosos_60": m["idosos_60"],
        })

    # Ordena por Performance descendente para análises
    ras.sort(key=lambda x: (x["perf"] if x["perf"] is not None else -9), reverse=True)

    # ─── Rivais por RA + agregado por zona (Concorrência F1+F2) ───
    # Usa o nome civil real para excluir self. Em cenário simulado, o candidato
    # não aparece no cargo destino — exclude_nome vira inócuo.
    rivais_por_zona = montar_rivais(ras, cargo, meta["nome"], meta["total"])

    # ─── Métricas agregadas (Pág. 1 = só descritivas) ───
    # Perfil de votação: σ do desvio percentual da Performance (mesma regra do dashboard)
    # σ<30 = Distribuído · 30-60 = Híbrido · ≥60 = Concentrado
    desvios = [(r["perf"] - 1) * 100 for r in ras if r["perf"] is not None]
    if desvios:
        media = sum(desvios) / len(desvios)
        var = sum((d - media) ** 2 for d in desvios) / len(desvios)
        sigma = var ** 0.5
    else:
        sigma = 0
    if sigma < 30:
        perfil = "Distribuído"
    elif sigma < 60:
        perfil = "Híbrido"
    else:
        perfil = "Concentrado"
    patamar_ref = PATAMAR_CARGO.get(meta["cargo"], 18000)
    patamar_pct = round((meta["total"] / patamar_ref - 1) * 100, 1)
    n_redutos = sum(1 for r in ras if r["zona"] in ("compartilhado", "pessoal"))

    # Métricas DESCRITIVAS para a Pág. 1 (sem usar conceitos da Pág. 2)
    pct_do_cargo = round(meta["total"] / total_cargo_df * 100, 2) if total_cargo_df else 0
    pct_no_campo = round(meta["total"] / total_campo * 100, 2) if total_campo else 0
    n_ras_com_voto = sum(1 for r in ras if r["votos"] > 0)

    # Top 3 RAs por volume bruto de votos
    ras_por_volume = sorted(ras, key=lambda x: x["votos"], reverse=True)
    top3_volume = [{"ra": r["ra"], "votos": r["votos"], "pct": r["pct_votos_cand"]}
                   for r in ras_por_volume[:3]]
    maior_ra = top3_volume[0] if top3_volume else None

    # ─── RA exemplo (Pág. 2 — usada na frase didática da Performance) ───
    # Pega a RA com MAIOR Performance positiva entre as do candidato com voto > 0.
    # Pré-requisitos pra ser bom exemplo: aptos > 0 e votos > 0.
    ra_exemplo = None
    cand_perfs = [r for r in ras if r["votos"] > 0 and r["perf"] is not None and r["perf"] > 1]
    if cand_perfs:
        topo = max(cand_perfs, key=lambda r: r["perf"])
        pct_apt = round(topo["aptos"] / aptos_df * 100, 2) if aptos_df else 0
        pct_vot = round(topo["votos"] / meta["total"] * 100, 2) if meta["total"] else 0
        ra_exemplo = {
            "ra": topo["ra"],
            "aptos": topo["aptos"],
            "votos": topo["votos"],
            "pct_aptos_df": pct_apt,    # % do eleitorado do DF que esta RA representa
            "pct_votos_cand": pct_vot,  # % dos votos do candidato que vieram daqui
            "perf_pct": round((topo["perf"] - 1) * 100, 1),
            "zona": topo["zona"],
        }

    # ─── Pág. 3 — RAs de Defesa (Reduto consolidado + Voto pessoal) ───
    # já sorted por Performance desc desde o início (linha onde fazemos sort em ras)
    ras_defesa = [r for r in ras if r["zona"] in ("compartilhado", "pessoal")]
    votos_defesa = sum(r["votos"] for r in ras_defesa)
    soma_pct_defesa = round(sum(r["pct_votos_cand"] for r in ras_defesa), 1)

    # Insight: 3 templates por nível de concentração
    if soma_pct_defesa >= 70:
        insight_defesa_tipo = "alta"
    elif soma_pct_defesa >= 40:
        insight_defesa_tipo = "equilibrada"
    else:
        insight_defesa_tipo = "diluida"

    # ─── Pág. 4 — RAs de Crescimento (Espaço a conquistar) ───
    ras_crescimento = [r for r in ras if r["zona"] == "conquistar"]
    # ordenar por estoque potencial (votos do campo - votos do candidato)
    for r in ras_crescimento:
        r["estoque"] = max(0, (r["votos_campo"] or 0) - (r["votos"] or 0))
    ras_crescimento.sort(key=lambda x: x["estoque"], reverse=True)
    estoque_total = sum(r["estoque"] for r in ras_crescimento)

    # Insight crescimento: 4 templates
    if not ras_crescimento:
        insight_cresc_tipo = "vazio"
    else:
        ratio_estoque = estoque_total / meta["total"] if meta["total"] else 0
        if ratio_estoque >= 0.30:
            insight_cresc_tipo = "grande"
        elif ratio_estoque >= 0.10:
            insight_cresc_tipo = "moderado"
        else:
            insight_cresc_tipo = "estreito"

    # ─── Pág. 5 — Decisões periféricas ───
    # Esperado top peso: RAs em Esperado com peso ≥ 5% dos votos do cargo
    ras_esperado_top = [r for r in ras if r["zona"] == "esperado" and r["peso"] >= 5.0]
    ras_esperado_top.sort(key=lambda x: x["peso"], reverse=True)

    # Insight Esperado top: 3 templates por contagem
    n_esp_top = len(ras_esperado_top)
    if n_esp_top == 0:
        insight_esp_tipo = "nenhum"
    elif n_esp_top <= 3:
        insight_esp_tipo = "poucos"
    else:
        insight_esp_tipo = "muitos"

    # Sem espaço pelo campo: TODAS as RAs nessa zona, ordenadas por aptos desc
    ras_sem_espaco = [r for r in ras if r["zona"] == "sem_espaco"]
    ras_sem_espaco.sort(key=lambda x: x["aptos"], reverse=True)
    aptos_sem_espaco_total = sum(r["aptos"] for r in ras_sem_espaco)
    pct_aptos_descartado = round(aptos_sem_espaco_total / aptos_df * 100, 1) if aptos_df else 0

    # Insight Sem espaço: 3 templates por % aptos descartado
    if pct_aptos_descartado >= 30:
        insight_sem_tipo = "alto"
    elif pct_aptos_descartado >= 10:
        insight_sem_tipo = "medio"
    else:
        insight_sem_tipo = "baixo"

    # ─── Distribuição por grupos PED-DF (Pág. 1) ───
    ras_por_nome = {r["ra"]: r for r in ras}
    pdad_keys_grupo = ["renda_pc", "classe_ab", "superior", "serv_fed",
                       "serv_dist", "benef_social", "nativo_df", "idosos_60"]
    grupos = []
    for nome_grupo, lst in GRUPOS_PED:
        aptos_g = sum(ras_por_nome[r]["aptos"] for r in lst if r in ras_por_nome)
        votos_g = sum(ras_por_nome[r]["votos"] for r in lst if r in ras_por_nome)
        # Perfil PDAD do grupo (ponderado por aptos)
        pdad_grupo = {}
        for k in pdad_keys_grupo:
            s = 0
            w = 0
            for raN in lst:
                r = ras_por_nome.get(raN)
                if r and r["aptos"] and r.get(k) is not None:
                    s += r[k] * r["aptos"]
                    w += r["aptos"]
            pdad_grupo[k] = round(s / w, 2) if w else None
        grupos.append({
            "nome": nome_grupo,
            "n_ras": len(lst),
            "aptos": aptos_g,
            "votos": votos_g,
            "pct_eleitorado": round(aptos_g / aptos_df * 100, 1) if aptos_df else 0,
            "pct_votos": round(votos_g / meta["total"] * 100, 1) if meta["total"] else 0,
            "pdad": pdad_grupo,
        })

    # Eleito? Rankeia todos os candidatos do cargo por total de votos.
    eleito = False
    posicao_geral = None
    posicao_eleitos = None
    n_candidatos_cargo = 0
    n_vagas = VAGAS_CARGO.get(meta["cargo"], 24)
    ranking = []
    cand_csv = ROOT / "outputs_fase0" / "candidatos_2022.csv"
    if cand_csv.exists():
        # CSV usa "DEPUTADO DISTRITAL" (espaço); meta["cargo"] usa "DEPUTADO_DISTRITAL"
        cargo_raw = meta["cargo"].replace("_", " ")
        totais = {}
        with cand_csv.open(encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r.get("DS_CARGO") != cargo_raw:
                    continue
                nome = r["NM_VOTAVEL"].strip()
                totais[nome] = int(r["TOTAL_VOTOS"])
        ranking = sorted(totais.items(), key=lambda x: x[1], reverse=True)
        top = [n for n, _ in ranking[:n_vagas]]
        eleito = meta["nome"] in top
        for i, (n, _v) in enumerate(ranking, start=1):
            if n == meta["nome"]:
                posicao_geral = i
                if eleito:
                    posicao_eleitos = i
                break

    # n_candidatos_cargo vem do CADASTRO OFICIAL TSE (consulta_cand), não do CSV
    # filtrado por voto. Em DF 2022: 610 Distrital, 216 Federal, 13 Senador, 12 Gov.
    cargo_raw_full = meta["cargo"].replace("_", " ")
    consulta_csv = ROOT / "outputs_tse_2022_DF" / "consulta_cand_DF.csv"
    if consulta_csv.exists():
        candidatos_unicos = set()
        with consulta_csv.open(encoding="latin-1") as f:
            rdr = csv.reader(f, delimiter=";")
            header = [c.strip('"') for c in next(rdr)]
            idx_cargo = header.index("DS_CARGO")
            idx_sq = header.index("SQ_CANDIDATO")
            for row in rdr:
                if row[idx_cargo].strip('"') == cargo_raw_full:
                    candidatos_unicos.add(row[idx_sq].strip('"'))
        n_candidatos_cargo = len(candidatos_unicos)
    if n_candidatos_cargo == 0:
        n_candidatos_cargo = len(ranking)

    # ─── Distância ao limiar de eleição ───
    # Conceito: folga sobre o ponto crítico de definição da eleição.
    # 1º a (n_vagas-1)        → referencial = candidato na posição n_vagas (último a entrar)
    # n_vagas (último eleito) → referencial = posição n_vagas+1 (1º suplente)
    # Não eleitos             → referencial = posição n_vagas (último a entrar)
    limiar_votos = None
    limiar_posicao = None
    limiar_nome = None
    distancia_limiar_pct = None
    distancia_limiar_votos = None
    if posicao_geral is not None and n_candidatos_cargo > n_vagas:
        if posicao_geral < n_vagas:
            limiar_posicao = n_vagas
        elif posicao_geral == n_vagas:
            limiar_posicao = n_vagas + 1
        else:
            limiar_posicao = n_vagas
        if limiar_posicao <= n_candidatos_cargo:
            limiar_nome, limiar_votos = ranking[limiar_posicao - 1]
            if limiar_votos:
                distancia_limiar_pct = round((meta["total"] / limiar_votos - 1) * 100, 1)
                distancia_limiar_votos = meta["total"] - limiar_votos

    # ─── Pág. 7 — Alocação + Síntese ───
    # Caso baseado em Perfil × Distância ao limiar de eleição (mesma referência da Pág. 1)
    ref_pct = distancia_limiar_pct if distancia_limiar_pct is not None else patamar_pct
    acima = ref_pct >= 0
    if perfil == "Concentrado":
        caso_aloc = 1 if acima else 3
    else:
        caso_aloc = 2 if acima else 4
    ALOC_BASE = {
        1: {"defesa": 60, "crescimento": 30, "esperado": 10},
        2: {"defesa": 50, "crescimento": 35, "esperado": 15},
        3: {"defesa": 45, "crescimento": 45, "esperado": 10},
        4: {"defesa": 40, "crescimento": 45, "esperado": 15},
    }
    alocacao = dict(ALOC_BASE[caso_aloc])
    # Ajuste: se não tem RA em Crescimento, redistribui 50/50 entre Defesa e Esperado top
    if not ras_crescimento:
        extra = alocacao["crescimento"]
        alocacao["crescimento"] = 0
        alocacao["defesa"] += extra // 2
        alocacao["esperado"] += extra - (extra // 2)
    # Ajuste: se não tem Esperado top, redistribui pra Defesa
    if n_esp_top == 0:
        extra = alocacao["esperado"]
        alocacao["esperado"] = 0
        alocacao["defesa"] += extra

    # ─── Presença mínima em Sem espaço pelo campo ───
    # Proporcional (Distrital/Federal): trigger 25%, fórmula com fator de cargo
    #   presença = 2 × √(24/vagas) × (pct_descartado/25), clamp [1, 12]
    # Majoritário (Senador/Governador): toda RA conta — cada voto soma para o
    # totalizador único do DF — não há "descarte" estratégico territorial.
    #   trigger 5%, presença = pct_descartado × 0,5, piso 3, clamp [3, 20]
    import math
    cargo_majoritario = meta["cargo"] in ("SENADOR", "GOVERNADOR")
    presenca_min = 0
    if cargo_majoritario:
        if pct_aptos_descartado >= 5:
            presenca_min = max(3, min(20, round(pct_aptos_descartado * 0.5)))
    else:
        if pct_aptos_descartado >= 25:
            fator_cargo = math.sqrt(24 / n_vagas)
            fator_volume = pct_aptos_descartado / 25
            presenca_min = max(1, min(12, round(2 * fator_cargo * fator_volume)))
    if presenca_min > 0:
        # Subtrai proporcionalmente de Defesa + Crescimento
        soma = alocacao["defesa"] + alocacao["crescimento"]
        if soma > 0:
            delta_def = round(presenca_min * alocacao["defesa"] / soma)
            delta_cresc = presenca_min - delta_def
            alocacao["defesa"] = max(0, alocacao["defesa"] - delta_def)
            alocacao["crescimento"] = max(0, alocacao["crescimento"] - delta_cresc)
    alocacao["sem_espaco"] = presenca_min

    # ─── Orçamento por RA (Performance-ponderado) ───
    # Carrega referências TSE 2022: limite legal, mediana entre eleitos, mínimo eleito.
    # Base do cálculo = mediana entre eleitos do cargo (régua do que funcionou).
    # Distribuição por RA: uniforme (∝ aptos) e ponderada (∝ aptos × Performance).
    cargo_ds = meta["cargo"].replace("_", " ")
    ref_path = ROOT / "outputs_tse_2022_DF" / "orcamento_referencia.json"
    orcamento = {"limite_legal": None, "mediana_eleitos": None, "min_eleito": None,
                 "historico_candidato": None, "n_eleitos": None}
    if ref_path.exists():
        ref = json.loads(ref_path.read_text(encoding="utf-8"))
        orcamento["limite_legal"] = ref["limite_legal"].get(cargo_ds)
        s = ref["stats_eleitos"].get(cargo_ds) or {}
        orcamento["mediana_eleitos"] = s.get("mediana")
        orcamento["min_eleito"] = s.get("min")
        orcamento["n_eleitos"] = s.get("n_eleitos")
        chave_cand = f"{_norm(meta['nome'])}|{cargo_ds}"
        orcamento["historico_candidato"] = ref["gasto_por_candidato"].get(chave_cand)
    base = orcamento["mediana_eleitos"] or orcamento["limite_legal"] or 0
    orcamento["base"] = base
    # Soma ponderada = aptos × perf. Quando perf é None (RA sem voto do candidato),
    # cai pra 0 — orc_pond da RA será 0, mas não quebra a soma.
    soma_pond = sum(r["aptos"] * (r["perf"] or 0) for r in ras) or 1
    for r in ras:
        perf_safe = r["perf"] if r["perf"] is not None else 0
        r["orc_unif"] = round(base * r["aptos"] / aptos_df) if aptos_df else 0
        r["orc_pond"] = round(base * r["aptos"] * perf_safe / soma_pond)
        r["mult_orc"] = round(r["orc_pond"] / r["orc_unif"], 2) if r["orc_unif"] else 0

    # ─── PDAD baseline DF (média ponderada por aptos) ───
    pdad_keys = ["renda_pc", "classe_ab", "superior", "serv_fed", "serv_dist",
                 "benef_social", "nativo_df", "idosos_60"]
    df_baseline = {}
    for k in pdad_keys:
        s = 0
        w = 0
        for ra in mestre.values():
            if ra["aptos"] and ra[k] is not None:
                s += ra[k] * ra["aptos"]
                w += ra["aptos"]
        df_baseline[k] = round(s / w, 2) if w else None

    # ─── PDAD eleitor-tipo (média ponderada pelos votos do candidato) ───
    eleitor_tipo = {}
    for k in pdad_keys:
        s = 0
        w = 0
        for r in ras:
            if r["votos"] and r[k] is not None:
                s += r[k] * r["votos"]
                w += r["votos"]
        eleitor_tipo[k] = round(s / w, 2) if w else None

    # ─── Override para cenário simulado ───
    # O ranking real do cargo destino não inclui o candidato projetado.
    # Estimamos limiar/posição/eleito a partir das referências de votos.
    if simulado_info:
        eleito = True
        n_vagas_dest = VAGAS_CARGO.get(cargo, 24)
        # Posição: top 1 no cenário polarizado/favorável, último eleito no
        # fragmentado/conservador, intermediária no estruturado/possível.
        if sim_nivel in ("favoravel", "polarizado"):  posicao_geral = 1
        elif sim_nivel in ("conservador", "fragmentado"): posicao_geral = n_vagas_dest
        else:                                          posicao_geral = max(1, round((1 + n_vagas_dest) / 2))
        # Limiar de eleição (mínimo eleito): para Senador usa o cenário escolhido.
        if cargo == "SENADOR" and sim_nivel in SENADOR_CENARIOS:
            limiar_votos = SENADOR_CENARIOS[sim_nivel]["min"]
            limiar_nome  = f"mínimo eleito (cenário {sim_nivel})"
        else:
            stats_dest = STATS_VOTOS_2022[cargo]
            limiar_votos = stats_dest["min"]
            limiar_nome  = "mínimo eleito 2022"
        limiar_posicao = n_vagas_dest + 1
        distancia_limiar_pct   = round((meta["total"] / limiar_votos - 1) * 100, 1) if limiar_votos else 0
        distancia_limiar_votos = meta["total"] - limiar_votos

    nome_curto_final = sim_nome if sim_nome else cfg["nome_curto"]

    return {
        "meta": {
            "nome": meta["nome"],
            "nome_curto": nome_curto_final,
            "apelido": apelido,
            "partido": meta["partido"],
            "campo": meta["campo"],
            "cargo": meta["cargo"],
            "total": meta["total"],
            "eleito": eleito,
            "perfil": perfil,
            "sigma_perf": round(sigma, 1),
            "patamar_pct": patamar_pct,
            "n_redutos": n_redutos,
            "aptos_df": aptos_df,
            # descritivas Pág. 1
            "pct_do_cargo": pct_do_cargo,
            "pct_no_campo": pct_no_campo,
            "total_cargo_df": total_cargo_df,
            "total_campo_df": total_campo,
            "n_ras_com_voto": n_ras_com_voto,
            "n_ras_total": len(ras),
            "posicao_geral": posicao_geral,
            "n_candidatos_cargo": n_candidatos_cargo,
            "top3_volume": top3_volume,
            "maior_ra": maior_ra,
            "grupos_ped": grupos,
            "ra_exemplo": ra_exemplo,
            # Pág. 3
            "ras_defesa": ras_defesa,
            "n_defesa": len(ras_defesa),
            "votos_defesa": votos_defesa,
            "soma_pct_defesa": soma_pct_defesa,
            "insight_defesa_tipo": insight_defesa_tipo,
            # Pág. 4
            "ras_crescimento": ras_crescimento,
            "n_crescimento": len(ras_crescimento),
            "estoque_total": estoque_total,
            "insight_cresc_tipo": insight_cresc_tipo,
            # Pág. 5
            "ras_esperado_top": ras_esperado_top,
            "n_esperado_top": n_esp_top,
            "insight_esp_tipo": insight_esp_tipo,
            "ras_sem_espaco": ras_sem_espaco,
            "n_sem_espaco": len(ras_sem_espaco),
            "aptos_sem_espaco_total": aptos_sem_espaco_total,
            "pct_aptos_descartado": pct_aptos_descartado,
            "insight_sem_tipo": insight_sem_tipo,
            # Pág. 7
            "caso_alocacao": caso_aloc,
            "alocacao": alocacao,
            "orcamento": orcamento,
            "simulado": simulado_info,
            # Concorrência (Pág. 3, 4 e nova — top 3 rivais agregados por zona)
            "rivais_por_zona": rivais_por_zona,
            # Pág. 8 — todas 33 RAs (já incluem grupo)
            "ras_apendice": ras,
            "n_vagas": n_vagas,
            "limiar_posicao": limiar_posicao,
            "limiar_votos": limiar_votos,
            "limiar_nome": limiar_nome,
            "distancia_limiar_pct": distancia_limiar_pct,
            "distancia_limiar_votos": distancia_limiar_votos,
        },
        "ras": ras,
        "df_baseline": df_baseline,
        "eleitor_tipo": eleitor_tipo,
    }


def gerar_html(apelido, dados):
    """Lê playbook_template.html, injeta os dados e salva como playbook_<APELIDO>.html"""
    tpl_path = ROOT / "playbook_template.html"
    if not tpl_path.exists():
        print(f"  (template não encontrado: {tpl_path}; pulei a geração de HTML)")
        return None
    tpl = tpl_path.read_text(encoding="utf-8")
    if "__DADOS_JSON__" not in tpl:
        print("  ⚠ template não tem placeholder __DADOS_JSON__")
        return None
    json_str = json.dumps(dados, ensure_ascii=False, indent=2)
    html = tpl.replace("__DADOS_JSON__", json_str)
    html = html.replace("THIAGO MANZONI", dados["meta"]["nome_curto"])
    out = ROOT / f"playbook_{apelido}.html"
    out.write_text(html, encoding="utf-8")
    return out


def gerar_pdf(apelido, html_path):
    """Converte o HTML em PDF via Google Chrome headless. Retorna o Path do PDF."""
    import subprocess
    chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    if not Path(chrome).exists():
        print(f"  (chrome não encontrado em {chrome}; pulei a geração de PDF)")
        return None
    pdf_path = ROOT / f"playbook_{apelido}.pdf"
    cmd = [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--virtual-time-budget=2000",
        f"--print-to-pdf={pdf_path}",
        str(html_path.absolute().as_uri()),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if pdf_path.exists() and pdf_path.stat().st_size > 1000:
            return pdf_path
        else:
            print(f"  ⚠ PDF não gerado ou muito pequeno. stderr: {result.stderr[:200]}")
            return None
    except subprocess.TimeoutExpired:
        print(f"  ⚠ Timeout ao gerar PDF de {apelido}")
        return None
    except Exception as exc:
        print(f"  ⚠ Erro ao gerar PDF: {exc}")
        return None


# ────────── main ───────────────────────────────────────────────────
def _processar(apelido, com_pdf=True, sim_cargo=None, sim_nivel=None, sim_nome=None, suffix=""):
    """Gera JSON + HTML + PDF para um candidato. Retorna (dados, html_path, pdf_path).

    Para cenário simulado, passa sim_cargo + sim_nivel (e opcionalmente sim_nome
    para "Novo candidato"). suffix é apenso ao nome dos arquivos de saída.
    """
    dados = gerar_dados(apelido, sim_cargo=sim_cargo, sim_nivel=sim_nivel, sim_nome=sim_nome)
    out_apelido = (apelido + suffix) if suffix else apelido
    out_json = ROOT / f"playbook_dados_{out_apelido}.json"
    with out_json.open("w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    html_path = gerar_html(out_apelido, dados)
    pdf_path = gerar_pdf(out_apelido, html_path) if (com_pdf and html_path) else None
    return dados, html_path, pdf_path


def _print_resumo(apelido, dados, html_path, pdf_path=None):
    m = dados["meta"]
    print(f"\n[{apelido}] {m['nome']}  ({m['partido']} · {m['cargo']} · {m['campo']})")
    print(f"  Total: {m['total']:,} votos · Eleito: {m['eleito']} · Posição: {m['posicao_geral']}/{m['n_candidatos_cargo']}")
    print(f"  Perfil: {m['perfil']} (σ={m['sigma_perf']}) · Patamar: {m['patamar_pct']:+.1f}% · Limiar: {m['distancia_limiar_pct']:+.1f}%")
    print(f"  Defesa: {m['n_defesa']} RAs ({m['soma_pct_defesa']}%) · Crescimento: {m['n_crescimento']} RAs · Sem espaço: {m['n_sem_espaco']} RAs ({m['pct_aptos_descartado']}% DF)")
    if pdf_path:
        print(f"  → {pdf_path.name} ({pdf_path.stat().st_size // 1024} KB)")
    elif html_path:
        print(f"  → {html_path.name}")


def _parse_sim_args(args):
    """Extrai args opcionais --sim-cargo, --sim-nivel, --sim-nome do sys.argv.
    Retorna (sim_cargo, sim_nivel, sim_nome)."""
    sim_cargo = sim_nivel = sim_nome = None
    for i, a in enumerate(args):
        if a == "--sim-cargo" and i + 1 < len(args):
            sim_cargo = args[i + 1]
        elif a == "--sim-nivel" and i + 1 < len(args):
            sim_nivel = args[i + 1]
        elif a == "--sim-nome" and i + 1 < len(args):
            sim_nome = args[i + 1]
    return sim_cargo, sim_nivel, sim_nome


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "MANZONI"

    if arg == "--batch" or arg == "BATCH":
        print(f"\n=== Gerando lote de {len(BATCH_REVISAO)} playbooks (HTML + PDF) ===")
        falhas = []
        for ap in BATCH_REVISAO:
            try:
                dados, html, pdf = _processar(ap, com_pdf=True)
                _print_resumo(ap, dados, html, pdf)
            except Exception as exc:
                print(f"\n[{ap}] ERRO: {exc}")
                falhas.append((ap, str(exc)))
        print(f"\n=== Concluído: {len(BATCH_REVISAO) - len(falhas)}/{len(BATCH_REVISAO)} OK ===")
        if falhas:
            print("Falhas:")
            for ap, err in falhas:
                print(f"  {ap}: {err}")
        sys.exit(0 if not falhas else 1)

    if arg not in CANDIDATOS:
        print(f"Candidato desconhecido: {arg}.")
        print(f"Disponíveis: {sorted(CANDIDATOS.keys())}")
        print(f"Ou use --batch para gerar a lista completa de revisão.")
        print(f"Ou use cenário simulado:")
        print(f"  python {sys.argv[0]} <APELIDO> --sim-cargo SENADOR --sim-nivel possivel")
        print(f"  python {sys.argv[0]} <APELIDO> --sim-cargo DEPUTADO_FEDERAL --sim-nivel favoravel --sim-nome 'João da Silva'")
        sys.exit(1)

    sim_cargo, sim_nivel, sim_nome = _parse_sim_args(sys.argv[2:])
    if sim_cargo or sim_nivel:
        if not (sim_cargo and sim_nivel):
            print("Erro: --sim-cargo e --sim-nivel devem vir juntos.")
            sys.exit(1)
        # suffix nos arquivos de output: APELIDO_SIMULADO_CARGO_NIVEL[_NOME]
        suf = f"_SIM_{sim_cargo}_{sim_nivel}"
        if sim_nome:
            suf += f"_{_norm(sim_nome).replace(' ', '_')[:20]}"
        dados, html, pdf = _processar(arg, com_pdf=True, sim_cargo=sim_cargo,
                                       sim_nivel=sim_nivel, sim_nome=sim_nome, suffix=suf)
        print(f"OK simulado: cargo={sim_cargo} nivel={sim_nivel}" + (f" nome={sim_nome}" if sim_nome else ""))
        _print_resumo(arg + suf, dados, html, pdf)
        sys.exit(0)

    dados, html, pdf = _processar(arg, com_pdf=True)
    print(f"OK json: playbook_dados_{arg}.json")
    if html: print(f"OK html: {html.name}")
    if pdf:  print(f"OK pdf:  {pdf.name}")
    _print_resumo(arg, dados, html, pdf)
