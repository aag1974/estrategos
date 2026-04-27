"""
FASE 4 v2 - Dashboard SPE - Nova arquitetura
"""
import json, base64
from pathlib import Path
import pandas as pd
import numpy as np

from classificacao_base import (
    carregar_aptos_por_ra,
    classificar_ras,
)

CACHE = Path("dados_tse_cache")

# Mapeamento número → campo (pelos dois primeiros dígitos)
NUMERO_CAMPO = {
    13:"progressista", 12:"progressista", 40:"progressista",
    50:"progressista", 65:"progressista", 18:"progressista",
    43:"progressista", 77:"progressista", 70:"progressista",
    15:"moderado",     45:"moderado",     23:"moderado",
    55:"moderado",     20:"moderado",     51:"moderado",
    22:"liberal_conservador", 11:"liberal_conservador",
    10:"liberal_conservador", 44:"liberal_conservador",
    30:"liberal_conservador", 14:"liberal_conservador",
    25:"liberal_conservador", 28:"liberal_conservador",
}

# Mapeamento nome → campo para eleições majoritárias (DF 2022, 1º turno)
NOME_CAMPO_MAJOR = {
    "IBANEIS ROCHA":          "moderado",
    "LEANDRO GRASS":          "progressista",
    "JOSE EDMAR":             "moderado",
    "IZALCI LUCAS":           "liberal_conservador",
    "DAMARES ALVES":          "liberal_conservador",
    "ROGERIO CORREIA":        "progressista",
    "LEILA BARROS":           "moderado",
    "FABIO FELIX":            "progressista",
}

# Número → partido (primeiros 2 dígitos)
NUMERO_PARTIDO = {
    10:"Rep.",11:"PP",12:"PDT",13:"PT",14:"PTB",15:"MDB",
    16:"PSTU",17:"PSL",18:"REDE",20:"PSC",21:"Podemos",22:"PL",
    23:"Cidadania",25:"UB",27:"DC",28:"PRTB",30:"NOVO",
    33:"PMN",36:"Agir",40:"PSB",43:"PV",44:"União",45:"PSDB",
    50:"PSOL",51:"Patriota",55:"PSD",65:"PC do B",70:"Avante",
    77:"Solidariedade",
}

DIR_F2  = Path("outputs_fase2")
DIR_F3  = Path("outputs_fase3")
DIR_F3C = Path("outputs_fase3c")
OUTPUT  = Path("dashboard_spe_df.html")

CARGOS_VALIDOS = {
    "GOVERNADOR", "SENADOR",
    "DEPUTADO FEDERAL", "DEPUTADO DISTRITAL",
}

# Normalização de cargos para chave interna
CARGO_NORM = {
    "GOVERNADOR":         "GOVERNADOR",
    "SENADOR":            "SENADOR",
    "DEPUTADO FEDERAL":   "DEPUTADO_FEDERAL",
    "DEPUTADO DISTRITAL": "DEPUTADO_DISTRITAL",
}

# RA_SEM_ZONA descontinuado em abr/2026 — todas as 33 RAs têm dado eleitoral
# próprio via atribuição seção→RA por point-in-polygon (fase1c_perfil_secao.py).
RA_SEM_ZONA = set()

PERSONA_TERRITORIOS = {
    "servidor":     ["Brasilia (Plano Piloto)","Lago Sul","Lago Norte","Sudoeste/Octogonal","Jardim Botanico","Park Way","Aguas Claras","Cruzeiro","Guara"],
    "expansionista":["Brasilia (Plano Piloto)","Lago Sul","Lago Norte","Taguatinga","Sobradinho","Aguas Claras"],
    "gestor":       ["Ceilandia","Samambaia","Taguatinga","Planaltina","Santa Maria","Recanto das Emas","Brazlandia","Riacho Fundo","Riacho Fundo II","SCIA/Estrutural"],
    "territorial":  ["Samambaia","Ceilandia","Taguatinga","Gama","Planaltina","Santa Maria","Recanto das Emas","Riacho Fundo","Riacho Fundo II","Sao Sebastiao"],
    "nicho":        ["Lago Sul","Park Way","Aguas Claras","Sudoeste/Octogonal","Jardim Botanico","Lago Norte"],
    "desafiante":   ["Taguatinga","Brasilia (Plano Piloto)","Ceilandia","Guara","Sobradinho","Aguas Claras"],
}

PERSONA_IPE_KEY = {
    "servidor":     "DEPUTADO_FEDERAL|progressista",
    "expansionista":"GOVERNADOR|progressista",
    "gestor":       "GOVERNADOR|moderado",
    "territorial":  "DEPUTADO_DISTRITAL|moderado",
    "nicho":        "DEPUTADO_FEDERAL|liberal_conservador",
    "desafiante":   "GOVERNADOR|liberal_conservador",
}

def carregar():
    df_ipe    = pd.read_csv(DIR_F3 / "ipe_completo.csv")
    df_mestre = pd.read_csv(DIR_F2 / "tabela_mestre_ra.csv")
    df_mestre = df_mestre[df_mestre["RA_NOME"].notna()].copy()
    df_narr   = pd.read_csv(DIR_F3 / "narrativas_ra.csv")
    campo_path = DIR_F3C / "votos_campo_ra.csv"
    df_campo  = pd.read_csv(campo_path) if campo_path.exists() else None
    cand_path = DIR_F3C / "votos_candidato_ra.csv"
    df_cand   = pd.read_csv(cand_path) if cand_path.exists() else None
    return df_ipe, df_mestre, df_narr, df_campo, df_cand

def montar_dados(df_ipe, df_mestre, df_narr, df_campo, df_cand=None):
    ras = {}
    for _, r in df_mestre.iterrows():
        n = r["RA_NOME"]
        if pd.isna(n): continue
        def v(col, dec=1):
            # 1. Exato, 2. _x/_y (merge pandas), 3. busca por substring
            for c in [col, col+"_x", col+"_y"]:
                val = r.get(c)
                if val is not None and not pd.isna(val):
                    try: return round(float(val), dec)
                    except: pass
            # Busca por substring: encontrar coluna que contem o nome
            for c in df_mestre.columns:
                if col in c or col.lower() in c.lower():
                    val = r.get(c)
                    if val is not None and not pd.isna(val):
                        try: return round(float(val), dec)
                        except: pass
            return None
        ras[n] = {
            "renda_pc":     v("DOM_renda_pc_media", 0),
            "pct_ab":       v("DOM_pct_classe_AB"),
            "pct_de":       v("DOM_pct_classe_DE"),
            "pct_inseg":    v("DOM_pct_inseg_alimentar"),
            "pct_super":    v("MOR_pct_superior"),
            "pct_sem_fund": v("MOR_pct_sem_fund"),
            "pct_nativo":   v("MOR_pct_nativo_df"),
            "pct_migrante": v("MOR_pct_migrante"),
            "pct_serv":     v("MOR_pct_servidor_total"),
            "pct_serv_fed": v("MOR_pct_servidor_fed"),
            "pct_privado":  v("MOR_pct_privado"),
            "pct_conta":    v("MOR_pct_conta_propria"),
            "pct_desoc":    v("MOR_pct_desocupado"),
            "pct_beneficio":v("MOR_pct_beneficio_social"),
            "pct_plano":    v("MOR_pct_plano_saude"),
            "pct_jov_mor":  v("MOR_pct_jovem_pop"),  # % 16-24 / todos moradores
            "pct_ido_mor":  v("MOR_pct_idoso_pop"),  # % 60+ / todos moradores
            "renda_ind":    v("MOR_renda_ind_media", 0),
            "abstencao":    v("ABSTENCAO_GOVERNADOR"),
            "el_aptos":     v("EL_total_aptos", 0),
            "el_jov":       v("EL_pct_jovem_1624_y") or v("EL_pct_jovem_1624"),
            "el_ido":       v("EL_pct_idoso_60mais"),
            "el_fem":       v("EL_pct_feminino"),
            "el_super":     v("EL_pct_superior"),
            "el_sem_fund":  v("EL_pct_sem_fund"),
            "sem_zona":     n in RA_SEM_ZONA,
            "spe": {}, "votos": {}, "narrativa": "",
        }
    for _, r in df_ipe.iterrows():
        n = r.get("RA_NOME")
        cargo  = str(r.get("CARGO", r.get("DS_CARGO",""))).strip().upper().replace(" ","_")
        perfil = str(r.get("PERFIL","")).strip().lower()
        if n not in ras: continue
        key = cargo + "|" + perfil
        ras[n]["spe"][key] = {
            "spe":    round(float(r.get("IPE", 0) or 0), 1),
            "afin":  round(float(r.get("SCORE_AFINIDADE", r.get("AFIN_COMBO",0)) or 0), 1),
            "conv":  round(float(r.get("SCORE_CONVERSAO",  r.get("CONV", 0)) or 0), 1),
            "massa": round(float(r.get("SCORE_MASSA",      r.get("MASSA",0)) or 0), 1),
            "logist":round(float(r.get("SCORE_LOGISTICA",  0) or 0), 1),
        }
    for _, r in df_narr.iterrows():
        n = r.get("RA_NOME")
        if n in ras: ras[n]["narrativa"] = str(r.get("NARRATIVA","")).strip()
    if df_campo is not None:
        try:
            # Normalizar cargo: maiusculo, strip, espacos -> underscore
            df_campo["_cargo_norm"] = (df_campo["DS_CARGO"]
                .str.upper().str.strip()
                .str.replace(" ", "_", regex=False)
                .str.replace("-", "_", regex=False))
            df_campo["QT_VOTOS"] = pd.to_numeric(df_campo.get("QT_VOTOS", 0), errors="coerce").fillna(0)
            df_campo["_campo_norm"] = df_campo["CAMPO"].astype(str).str.lower().str.strip().str.replace(" ", "_", regex=False)

            # Total do campo no DF (por cargo × campo) — denominador do sobre-índice
            tot_campo_df = (df_campo.groupby(["_cargo_norm","_campo_norm"])["QT_VOTOS"].sum()).to_dict()

            # Total de aptos por RA + DF
            aptos_df = {n: (ras[n].get("el_aptos") or 0) for n in ras}
            tot_aptos = sum(v for v in aptos_df.values() if v)

            for cargo_str in ["GOVERNADOR","SENADOR","DEPUTADO_FEDERAL","DEPUTADO_DISTRITAL"]:
                sub = df_campo[df_campo["_cargo_norm"] == cargo_str]
                if sub.empty:
                    cargo_alt = cargo_str.replace("_", " ")
                    sub = df_campo[df_campo["DS_CARGO"].str.upper().str.strip() == cargo_alt]
                for _, r in sub.iterrows():
                    n = r.get("RA_NOME")
                    if n not in ras: continue
                    cn = r.get("_campo_norm","")
                    if not cn: continue
                    p = float(r.get("PCT", 0) or 0)
                    qt = float(r.get("QT_VOTOS", 0) or 0)

                    # Sobre-índice do campo
                    apt = aptos_df.get(n, 0)
                    tot_c = tot_campo_df.get((cargo_str, cn), 0)
                    if qt > 0 and apt > 0 and tot_c > 0 and tot_aptos > 0:
                        share_voto = qt / tot_c
                        share_apt  = apt / tot_aptos
                        idx = round(share_voto / share_apt, 3) if share_apt > 0 else None
                    else:
                        idx = None

                    if cargo_str not in ras[n]["votos"]:
                        ras[n]["votos"][cargo_str] = {}
                    ras[n]["votos"][cargo_str][cn] = {
                        "pct": round(p, 1),
                        "idx": idx,
                    }
            print(f"   Votos carregados para {sum(1 for r in ras.values() if r['votos'])} RAs")
        except Exception as e:
            import traceback; traceback.print_exc()
            print(f"   Aviso votos: {e}")

    # ── Margem 1º-2º por RA × cargo (Visão Cargo) ───────────────────────────
    if df_cand is not None:
        try:
            df_cand["QT_VOTOS_RA"] = pd.to_numeric(df_cand["QT_VOTOS_RA"], errors="coerce").fillna(0)
            for n in ras:
                ras[n]["margem"] = {}
            for cargo_str in ["GOVERNADOR","SENADOR","DEPUTADO_FEDERAL","DEPUTADO_DISTRITAL"]:
                sub = df_cand[df_cand["DS_CARGO"] == cargo_str]
                if sub.empty: continue
                # Total do cargo por RA (denominador)
                tot_ra = sub.groupby("RA_NOME")["QT_VOTOS_RA"].sum().to_dict()
                # Top 2 por RA
                for ra_nome, grp in sub.groupby("RA_NOME"):
                    if ra_nome not in ras: continue
                    g = grp.sort_values("QT_VOTOS_RA", ascending=False)
                    if len(g) < 2: continue
                    v1 = float(g.iloc[0]["QT_VOTOS_RA"])
                    v2 = float(g.iloc[1]["QT_VOTOS_RA"])
                    nm1 = str(g.iloc[0]["NM_CANDIDATO"]).strip().title()
                    nm2 = str(g.iloc[1]["NM_CANDIDATO"]).strip().title()
                    tot = float(tot_ra.get(ra_nome, 0))
                    if tot <= 0: continue
                    margem_pp = round((v1 - v2) / tot * 100, 1)
                    peso_pct  = None  # calculado depois com total DF
                    ras[ra_nome]["margem"][cargo_str] = {
                        "v1": int(v1), "v2": int(v2),
                        "nm1": nm1, "nm2": nm2,
                        "margem_pp": margem_pp,
                        "tot_ra": int(tot),
                    }
                # Calcular peso eleitoral da RA no cargo (votos_ra / votos_DF do cargo)
                tot_df_cargo = float(sum(tot_ra.values()))
                if tot_df_cargo > 0:
                    for ra_nome in tot_ra:
                        if ra_nome in ras and cargo_str in ras[ra_nome]["margem"]:
                            ras[ra_nome]["margem"][cargo_str]["peso_pct"] = round(
                                tot_ra[ra_nome] / tot_df_cargo * 100, 2
                            )
            print(f"   Margens calculadas para {sum(1 for r in ras.values() if r.get('margem'))} RAs")
        except Exception as e:
            import traceback; traceback.print_exc()
            print(f"   Aviso margens: {e}")

    return ras

def gerar_scatter_servidor_prog(ras):
    """
    Scatter SVG: % servidor federal (X) × % voto progressista Federal (Y), 28 RAs.
    Cor dos pontos por % classe AB (cinza claro → roxo). Linha de regressão e r exibido.
    Usado como evidência visual do achado central da seção Campo político.

    Tamanho fixo (380×220) — não usa max-width:100% para evitar esticar.
    """
    pontos = []
    for nome, d in ras.items():
        sf  = d.get("pct_serv_fed")
        ab  = d.get("pct_ab")
        v   = d.get("votos", {}).get("DEPUTADO_FEDERAL", {}).get("progressista", {})
        pct = v.get("pct") if isinstance(v, dict) else None
        if sf is None or pct is None or ab is None: continue
        pontos.append({"ra": nome, "x": float(sf), "y": float(pct), "ab": float(ab)})
    if len(pontos) < 5: return ""

    xs  = [p["x"]  for p in pontos]
    ys  = [p["y"]  for p in pontos]
    abs_= [p["ab"] for p in pontos]
    n = len(xs)
    mx = sum(xs)/n; my = sum(ys)/n
    cov = sum((xs[i]-mx)*(ys[i]-my) for i in range(n))
    vx  = sum((x-mx)**2 for x in xs)
    vy  = sum((y-my)**2 for y in ys)
    a = cov/vx if vx > 0 else 0
    b = my - a*mx
    r = cov/((vx*vy)**0.5) if vx>0 and vy>0 else 0

    W, H = 380, 220
    pl, pr, pt_, pb = 42, 14, 26, 38
    pw, ph = W - pl - pr, H - pt_ - pb
    x_min = 0; x_max = max(xs) * 1.08
    y_min = max(0, min(ys) - 4); y_max = max(ys) + 3
    fx = lambda x: pl + (x - x_min)/(x_max - x_min) * pw
    fy = lambda y: H - pb - (y - y_min)/(y_max - y_min) * ph

    ab_min, ab_max = min(abs_), max(abs_)
    def cor(ab):
        t = (ab - ab_min)/(ab_max - ab_min) if ab_max > ab_min else 0.5
        rr = int(210 + (83 - 210)*t)
        gg = int(210 + (74 - 210)*t)
        bb = int(210 + (183 - 210)*t)
        return f"#{rr:02x}{gg:02x}{bb:02x}"

    # SVG com width/height fixos — evita esticar com max-width:100%
    parts = [f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" style="display:block">']

    # Título do gráfico (dentro do SVG)
    parts.append(f'<text x="{pl}" y="14" font-size="11" font-weight="500" fill="#412402">Servidor federal × voto progressista (Federal 2022)</text>')

    # Caixa do plot
    parts.append(f'<rect x="{pl}" y="{pt_}" width="{pw}" height="{ph}" fill="none" stroke="#e5e7eb" stroke-width="0.5"/>')

    # Gridlines horizontais sutis + ticks Y
    for ty in (10, 20, 30, 40, 50):
        if ty < y_min or ty > y_max: continue
        yp = fy(ty)
        parts.append(f'<line x1="{pl}" y1="{yp:.1f}" x2="{pl + pw}" y2="{yp:.1f}" stroke="#f1f1f1" stroke-width="0.5"/>')
        parts.append(f'<text x="{pl - 4}" y="{yp + 3:.1f}" font-size="9" fill="#888" text-anchor="end">{ty}%</text>')
    # Ticks X
    for tx in (0, 5, 10, 15, 20, 25):
        if tx > x_max: continue
        xp = fx(tx)
        parts.append(f'<line x1="{xp:.1f}" y1="{H - pb}" x2="{xp:.1f}" y2="{H - pb + 3}" stroke="#888" stroke-width="0.5"/>')
        parts.append(f'<text x="{xp:.1f}" y="{H - pb + 12}" font-size="9" fill="#888" text-anchor="middle">{tx}%</text>')

    # Labels dos eixos (texto curto)
    parts.append(f'<text x="{W/2:.0f}" y="{H - 6}" font-size="10" fill="#666" text-anchor="middle">% Servidor federal na população (PDAD)</text>')
    parts.append(f'<text x="14" y="{H/2:.0f}" font-size="10" fill="#666" text-anchor="middle" transform="rotate(-90 14 {H/2:.0f})">% Voto progressista</text>')

    # Linha de regressão
    x1v = x_min; y1v = a*x1v + b
    x2v = x_max; y2v = a*x2v + b
    parts.append(f'<line x1="{fx(x1v):.1f}" y1="{fy(y1v):.1f}" x2="{fx(x2v):.1f}" y2="{fy(y2v):.1f}" stroke="#534AB7" stroke-width="1.5" stroke-dasharray="3,2" opacity="0.6"/>')

    # Pontos com tooltip nativo
    for p in pontos:
        cx, cy = fx(p["x"]), fy(p["y"])
        c = cor(p["ab"])
        ra_safe = p["ra"].replace('"','&quot;').replace('<','&lt;').replace('>','&gt;')
        parts.append(
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="4" fill="{c}" stroke="#fff" stroke-width="0.8">'
            f'<title>{ra_safe}: {str(round(p["x"],1)).replace(".",",")}% serv fed · '
            f'{str(round(p["y"],1)).replace(".",",")}% prog · '
            f'{str(round(p["ab"],1)).replace(".",",")}% classe AB</title></circle>'
        )

    # Anotação r=
    r_str = ("+" if r >= 0 else "") + str(round(r, 2)).replace(".", ",")
    parts.append(f'<text x="{W - pr - 4}" y="{pt_ + 12}" font-size="11" font-weight="600" fill="#534AB7" text-anchor="end">r = {r_str}</text>')

    parts.append('</svg>')
    return "".join(parts)


def montar_candidatos():
    """
    Extrai candidatos 2022 com votos por RA.
    Fonte primária: dados_tse_cache/ (votação por seção)
    Fallback:       candidatos_2022.csv (já agregado por RA)
    """
    votos_path  = CACHE / "votacao_secao_2022_DF.csv"
    locais_path = CACHE / "locais_votacao_2022_enriched.csv"

    # ── Fallback: usar candidatos_2022.csv pré-agregado ───────────────────────
    if not votos_path.exists() or not locais_path.exists():
        csv_paths = [
            CACHE / "candidatos_2022.csv",
            CACHE.parent / "candidatos_2022.csv",
            Path("candidatos_2022.csv"),
            Path("outputs_fase3") / "candidatos_2022.csv",
            Path("fase3") / "candidatos_2022.csv",
        ]
        csv_path = next((p for p in csv_paths if p.exists()), None)
        if csv_path:
            print(f"   Usando fallback: {csv_path}")
            return _montar_candidatos_csv(csv_path)
        print("   Aviso: nenhuma fonte de candidatos encontrada — lista vazia")
        return []

    # ── Pipeline primário: votação por seção ──────────────────────────────────
    print("   Lendo mapa de seções...", end="", flush=True)
    df_loc = pd.read_csv(locais_path, dtype=str, usecols=["NR_ZONA","NR_SECAO","RA_NOME"])
    df_loc = df_loc.dropna(subset=["RA_NOME"])
    secao_ra = {
        (r["NR_ZONA"].strip(), r["NR_SECAO"].strip()): r["RA_NOME"].strip()
        for _, r in df_loc.iterrows()
    }
    print(f" {len(secao_ra):,} seções mapeadas")

    print("   Lendo votação por seção...", end="", flush=True)
    df = pd.read_csv(votos_path, sep=";", encoding="latin1", dtype=str)
    df.columns = [c.strip() for c in df.columns]
    col_map = {}
    for c in df.columns:
        cu = c.upper()
        if   cu == "NR_VOTAVEL":  col_map[c] = "NR_VOTAVEL"
        elif cu == "NM_VOTAVEL":  col_map[c] = "NM_VOTAVEL"
        elif cu == "QT_VOTOS":    col_map[c] = "QT_VOTOS"
        elif cu == "NR_TURNO":    col_map[c] = "NR_TURNO"
        elif cu == "DS_CARGO":    col_map[c] = "DS_CARGO"
        elif cu == "NR_ZONA":     col_map[c] = "NR_ZONA"
        elif cu == "NR_SECAO":    col_map[c] = "NR_SECAO"
        elif cu == "SG_PARTIDO":  col_map[c] = "SG_PARTIDO"
    df = df.rename(columns=col_map)
    df = df[df["NR_TURNO"].astype(str).str.strip() == "1"].copy()
    df["DS_CARGO"] = df["DS_CARGO"].str.upper().str.strip()
    df = df[df["DS_CARGO"].isin(CARGOS_VALIDOS)].copy()
    df["QT_VOTOS"] = pd.to_numeric(df["QT_VOTOS"], errors="coerce").fillna(0)
    df["NR_ZONA"]  = df["NR_ZONA"].astype(str).str.strip()
    df["NR_SECAO"] = df["NR_SECAO"].astype(str).str.strip()
    df = df[~df["NR_VOTAVEL"].astype(str).str.strip().isin(["95","96","97","98","99"])]
    # Remover votos de legenda em cargos proporcionais
    _nr_len = df["NR_VOTAVEL"].astype(str).str.strip().str.len()
    df = df[~(df["DS_CARGO"].isin(["DEPUTADO DISTRITAL","DEPUTADO FEDERAL"]) & (_nr_len <= 2))].copy()
    print(f" {len(df):,} linhas · {df['NM_VOTAVEL'].nunique():,} candidatos")

    df["RA_NOME"] = df.apply(
        lambda r: secao_ra.get((r["NR_ZONA"], r["NR_SECAO"])), axis=1
    )
    df = df.dropna(subset=["RA_NOME"])

    def campo_de(nr, cargo, nome):
        cargo_n = CARGO_NORM.get(cargo, cargo)
        if "DEPUTADO" in cargo_n:
            try:
                prefixo = int(str(nr).strip()[:2])
                return NUMERO_CAMPO.get(prefixo, "outros")
            except: return "outros"
        else:
            nome_u = str(nome).upper().strip()
            for k, v in NOME_CAMPO_MAJOR.items():
                if k in nome_u:
                    return v
            try:
                prefixo = int(str(nr).strip()[:2])
                return NUMERO_CAMPO.get(prefixo, "outros")
            except: return "outros"

    df["CAMPO"] = df.apply(
        lambda r: campo_de(r["NR_VOTAVEL"], r["DS_CARGO"], r.get("NM_VOTAVEL","")), axis=1
    )
    if "SG_PARTIDO" in df.columns:
        df["PARTIDO"] = df.apply(
            lambda r: str(r["SG_PARTIDO"]).strip() if pd.notna(r["SG_PARTIDO"]) and str(r["SG_PARTIDO"]).strip()
                      else NUMERO_PARTIDO.get(int(str(r["NR_VOTAVEL"]).strip()[:2]), "?") if str(r["NR_VOTAVEL"]).strip().isdigit() else "?",
            axis=1
        )
    else:
        df["PARTIDO"] = df["NR_VOTAVEL"].apply(
            lambda nr: NUMERO_PARTIDO.get(int(str(nr).strip()[:2]), "?") if str(nr).strip().isdigit() else "?"
        )

    total_cand    = df.groupby(["NM_VOTAVEL","DS_CARGO"])["QT_VOTOS"].sum()
    grp           = df.groupby(["NM_VOTAVEL","DS_CARGO","RA_NOME","CAMPO","PARTIDO"])["QT_VOTOS"].sum().reset_index()
    total_cargo_ra = df.groupby(["DS_CARGO","RA_NOME"])["QT_VOTOS"].sum().to_dict()
    total_campo_ra = df.groupby(["DS_CARGO","RA_NOME","CAMPO"])["QT_VOTOS"].sum().to_dict()

    cands = {}
    for _, r in grp.iterrows():
        nome  = str(r["NM_VOTAVEL"]).strip()
        cargo = CARGO_NORM.get(r["DS_CARGO"], r["DS_CARGO"])
        ra    = r["RA_NOME"]
        campo = r["CAMPO"]
        part  = r["PARTIDO"]
        votos = int(r["QT_VOTOS"])
        key   = (nome, cargo)
        total_c = int(total_cand.get((r["NM_VOTAVEL"], r["DS_CARGO"]), 0))
        if total_c < 50:
            continue
        if key not in cands:
            cands[key] = {"nome":nome,"cargo":cargo,"campo":campo,"partido":part,"total":total_c,"ras":{}}
        vt_cargo = int(total_cargo_ra.get((r["DS_CARGO"], ra), 1) or 1)
        vt_campo = int(total_campo_ra.get((r["DS_CARGO"], ra, campo), 1) or 1)
        cands[key]["ras"][ra] = {
            "v":  votos,
            "pe": round(votos / total_c * 100, 2) if total_c else 0,
            "pc": round(votos / vt_cargo * 100, 2),
            "pp": round(votos / vt_campo * 100, 2),
        }

    # Classificação territorial unificada (helper compartilhado)
    aptos_por_ra, total_aptos_df = carregar_aptos_por_ra()
    for c in cands.values():
        ras_votos = [(ra, v["v"]) for ra, v in c["ras"].items()]
        out = classificar_ras(ras_votos, c["total"], aptos_por_ra, total_aptos_df)
        for (ra, _), o in zip(ras_votos, out):
            c["ras"][ra]["idx"] = o["idx"]
            c["ras"][ra]["s"]   = o["status"]

    result = list(cands.values())
    print(f"   {len(result)} candidatos extraídos")
    return result


def _montar_candidatos_csv(csv_path):
    """
    Monta A5_CANDS a partir do candidatos_2022.csv pré-agregado por RA.
    Mesmo formato que montar_candidatos() para compatibilidade total.
    """
    df = pd.read_csv(str(csv_path))
    df["DS_CARGO"] = df["DS_CARGO"].str.upper().str.strip()
    df = df[df["DS_CARGO"].isin(CARGOS_VALIDOS)].copy()

    # Remover votos de legenda (partidos): NR_VOTAVEL de 2 dígitos em cargos proporcionais
    df["_nr_len"] = df["NR_VOTAVEL"].astype(str).str.len()
    df = df[~(
        df["DS_CARGO"].isin(["DEPUTADO DISTRITAL","DEPUTADO FEDERAL"]) &
        (df["_nr_len"] <= 2)
    )].copy()
    df = df.drop(columns=["_nr_len"])

    df["CAMPO"] = df["NR_VOTAVEL"].apply(
        lambda x: NUMERO_CAMPO.get(int(str(x)[:2]), "outros") if str(x).isdigit() else "outros"
    )
    if "SG_PARTIDO" not in df.columns or df["SG_PARTIDO"].isna().all():
        df["SG_PARTIDO"] = df["NR_VOTAVEL"].apply(
            lambda nr: NUMERO_PARTIDO.get(int(str(nr)[:2]), "?") if str(nr).isdigit() else "?"
        )

    total_cargo_ra = df.groupby(["DS_CARGO","RA_NOME"])["QT_VOTOS"].sum().to_dict()
    total_campo_ra = df.groupby(["DS_CARGO","RA_NOME","CAMPO"])["QT_VOTOS"].sum().to_dict()

    cands = {}
    for _, r in df.iterrows():
        nome  = str(r["NM_VOTAVEL"]).strip()
        cargo = CARGO_NORM.get(r["DS_CARGO"], r["DS_CARGO"])
        ra    = str(r["RA_NOME"]).strip()
        campo = r["CAMPO"]
        part  = str(r.get("SG_PARTIDO","?")).strip() or "?"
        votos = int(r["QT_VOTOS"])
        total_c = int(r["TOTAL_VOTOS"])
        if total_c < 50:
            continue
        key = (nome, cargo)
        if key not in cands:
            cands[key] = {"nome":nome,"cargo":cargo,"campo":campo,"partido":part,"total":total_c,"ras":{}}
        vt_cargo = int(total_cargo_ra.get((r["DS_CARGO"], ra), 1) or 1)
        vt_campo = int(total_campo_ra.get((r["DS_CARGO"], ra, campo), 1) or 1)
        cands[key]["ras"][ra] = {
            "v":  votos,
            "pe": round(votos / total_c * 100, 2) if total_c else 0,
            "pc": round(votos / vt_cargo * 100, 2),
            "pp": round(votos / vt_campo * 100, 2),
        }

    # Classificação territorial unificada (helper compartilhado)
    aptos_por_ra, total_aptos_df = carregar_aptos_por_ra()
    for c in cands.values():
        ras_votos = [(ra, v["v"]) for ra, v in c["ras"].items()]
        out = classificar_ras(ras_votos, c["total"], aptos_por_ra, total_aptos_df)
        for (ra, _), o in zip(ras_votos, out):
            c["ras"][ra]["idx"] = o["idx"]
            c["ras"][ra]["s"]   = o["status"]

    result = list(cands.values())
    print(f"   {len(result)} candidatos carregados de {csv_path.name}")
    return result



def calcular_votos_eleitos():
    """P25/P50/P75 dos eleitos por cargo|campo|RA usando candidatos_2022.csv."""
    NUMERO_CAMPO = {
        10:'moderado',11:'moderado',12:'moderado',13:'progressista',
        14:'progressista',15:'moderado',16:'progressista',17:'progressista',
        20:'moderado',22:'liberal_conservador',23:'moderado',
        25:'liberal_conservador',30:'liberal_conservador',31:'moderado',
        33:'moderado',36:'moderado',40:'progressista',43:'progressista',
        44:'moderado',50:'progressista',55:'moderado',65:'progressista',
        77:'moderado',90:'moderado',
    }
    VAGAS={'DEPUTADO DISTRITAL':24,'DEPUTADO FEDERAL':8,'GOVERNADOR':1,'SENADOR':2}
    CN={'DEPUTADO DISTRITAL':'DEPUTADO_DISTRITAL','DEPUTADO FEDERAL':'DEPUTADO_FEDERAL',
        'GOVERNADOR':'GOVERNADOR','SENADOR':'SENADOR'}
    SEM=set()  # descontinuado em abr/2026 \u2014 todas as RAs t\u00eam dado pr\u00f3prio via PIP
    csv_paths = [
        CACHE / "candidatos_2022_ra.csv",
        CACHE.parent / "candidatos_2022.csv",
    ]
    csv_path = next((p for p in csv_paths if p.exists()), None)
    if csv_path is None:
        return {}
    df = pd.read_csv(str(csv_path))
    df['CAMPO'] = df['NR_VOTAVEL'].apply(
        lambda x: NUMERO_CAMPO.get(int(str(x)[:2]),'outros') if str(x).isdigit() else 'outros')
    for cargo,vagas in VAGAS.items():
        top=df[df['DS_CARGO']==cargo].drop_duplicates('NM_VOTAVEL')            .sort_values('TOTAL_VOTOS',ascending=False).head(vagas)['NM_VOTAVEL'].tolist()
        df.loc[df['DS_CARGO']==cargo,'ELEITO']=df['NM_VOTAVEL'].isin(top)
    result={}
    for cargo_raw,vagas in VAGAS.items():
        for campo in ['moderado','progressista','liberal_conservador']:
            key=CN[cargo_raw]+'|'+campo
            sub=df[(df['DS_CARGO']==cargo_raw)&(df['CAMPO']==campo)&(df['ELEITO']==True)]
            n=sub['NM_VOTAVEL'].nunique()
            if n==0: continue
            ra_stats={}
            for ra in sub['RA_NOME'].dropna().unique():
                if ra in SEM: continue
                vals=sub[sub['RA_NOME']==ra]['QT_VOTOS'].values
                if len(vals)==0: continue
                ra_stats[ra]={'p25':int(np.percentile(vals,25)),'p50':int(np.percentile(vals,50)),'p75':int(np.percentile(vals,75))}
            ra_stats['_n']=n
            result[key]=ra_stats
    return result

def calcular_metas_campo():
    """Mínimo de votos para eleição por cargo|campo usando candidatos_2022.csv."""
    NUMERO_CAMPO = {
        10:'moderado',11:'moderado',12:'moderado',13:'progressista',
        14:'progressista',15:'moderado',16:'progressista',17:'progressista',
        20:'moderado',22:'liberal_conservador',23:'moderado',
        25:'liberal_conservador',30:'liberal_conservador',31:'moderado',
        33:'moderado',36:'moderado',40:'progressista',43:'progressista',
        44:'moderado',50:'progressista',55:'moderado',65:'progressista',
        77:'moderado',90:'moderado',
    }
    VAGAS={'DEPUTADO DISTRITAL':24,'DEPUTADO FEDERAL':8,'GOVERNADOR':1,'SENADOR':2}
    CN={'DEPUTADO DISTRITAL':'DEPUTADO_DISTRITAL','DEPUTADO FEDERAL':'DEPUTADO_FEDERAL',
        'GOVERNADOR':'GOVERNADOR','SENADOR':'SENADOR'}
    csv_paths = [
        CACHE / "candidatos_2022_ra.csv",
        CACHE.parent / "candidatos_2022.csv",
    ]
    csv_path = next((p for p in csv_paths if p.exists()), None)
    if csv_path is None:
        return {}
    df = pd.read_csv(str(csv_path))
    df['CAMPO'] = df['NR_VOTAVEL'].apply(
        lambda x: NUMERO_CAMPO.get(int(str(x)[:2]),'outros') if str(x).isdigit() else 'outros')
    for cargo,vagas in VAGAS.items():
        top=df[df['DS_CARGO']==cargo].drop_duplicates('NM_VOTAVEL')            .sort_values('TOTAL_VOTOS',ascending=False).head(vagas)['NM_VOTAVEL'].tolist()
        df.loc[df['DS_CARGO']==cargo,'ELEITO']=df['NM_VOTAVEL'].isin(top)
    result={}
    for cargo_raw in VAGAS:
        for campo in ['moderado','progressista','liberal_conservador']:
            key=CN[cargo_raw]+'|'+campo
            sub=df[(df['DS_CARGO']==cargo_raw)&(df['CAMPO']==campo)&(df['ELEITO']==True)]                .drop_duplicates('NM_VOTAVEL').sort_values('TOTAL_VOTOS')
            if sub.empty: continue
            r=sub.iloc[0]
            result[key]={'votos':int(r['TOTAL_VOTOS']),'ref':r['NM_VOTAVEL'].title(),'n':len(sub)}
    return result
def main():
    import time
    t0 = time.time()
    print()
    print("  Estrategos \u2014 Intelig\u00eancia Eleitoral DF 2026")
    print("  " + "\u2500" * 38)
    print("  [1/3] Carregando dados...", end="", flush=True)
    df_ipe, df_mestre, df_narr, df_campo, df_cand = carregar()
    n_ras = len(df_mestre["RA_NOME"].dropna().unique())
    print(f"\r  [1/3] Dados carregados       {n_ras} RAs")
    print("  [2/3] Montando estrutura...", end="", flush=True)
    ras = montar_dados(df_ipe, df_mestre, df_narr, df_campo, df_cand)
    n_votos = sum(1 for r in ras.values() if r["votos"])
    print(f"\r  [2/3] Estrutura montada      {len(ras)} regi\u00f5es \u00b7 votos em {n_votos} RAs")
    print("  [2b] Extraindo candidatos TSE 2022...")
    cands = montar_candidatos()
    print("  [3/3] Gerando dashboard...", end="", flush=True)
    dados_b64 = base64.b64encode(json.dumps(ras, ensure_ascii=True, separators=(",",":")).encode("utf-8")).decode("ascii")
    pt_b64    = base64.b64encode(json.dumps(PERSONA_TERRITORIOS, ensure_ascii=True, separators=(",",":")).encode("utf-8")).decode("ascii")
    pk_b64    = base64.b64encode(json.dumps(PERSONA_IPE_KEY, ensure_ascii=True, separators=(",",":")).encode("utf-8")).decode("ascii")
    cands_b64 = base64.b64encode(json.dumps(cands, ensure_ascii=True, separators=(",",":")).encode("utf-8")).decode("ascii")
    ve_b64    = base64.b64encode(json.dumps(calcular_votos_eleitos(), ensure_ascii=True, separators=(",",":")).encode("utf-8")).decode("ascii")
    mc_b64    = base64.b64encode(json.dumps(calcular_metas_campo(), ensure_ascii=True, separators=(",",":")).encode("utf-8")).decode("ascii")
    # Credenciais do login: carrega de credenciais.json (não versionado).
    # Se não existir, login fica vazio (ninguém consegue entrar até criar credencial).
    cred_path = Path("credenciais.json")
    if cred_path.exists():
        creds_dict = json.loads(cred_path.read_text(encoding="utf-8"))
    else:
        creds_dict = {}
        print("\n  ⚠️  credenciais.json não encontrado.")
        print("     Para criar usuário: python3 gerar_credencial.py")
    creds_json = json.dumps(creds_dict, ensure_ascii=False, separators=(",",":"))

    js_final = (JS_CODE
        .replace("__DADOS_B64__", dados_b64)
        .replace("__PT_B64__", pt_b64)
        .replace("__PK_B64__", pk_b64)
        .replace("__CANDS_B64__", cands_b64)
        .replace("__VOTOS_ELEITOS_B64__", ve_b64)
        .replace("__METAS_CAMPO_B64__", mc_b64)
        .replace("__ESTRATEGOS_USERS__", creds_json))
    # gerar_scatter_servidor_prog() segue disponível como função — usada futuramente
    # pelo gerador de relatório Word (Cap. 2). Não inserida na tela conforme decisão
    # de storytelling: achados + scatter migram pro relatório editorial.
    html = HTML_TEMPLATE.replace("// __JS__", js_final)
    OUTPUT.write_text(html, encoding="utf-8")
    kb = len(html.encode()) // 1024
    elapsed = time.time() - t0
    print(f"\r  [3/3] Dashboard gerado       {OUTPUT}  ({kb} KB)")
    print()
    print(f"  \u2705 Conclu\u00eddo em {elapsed:.1f}s \u2014 abra o arquivo no navegador")
    print()


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Estrategos — Inteligência Eleitoral DF 2026</title>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;overflow:hidden;font-family:-apple-system,'Segoe UI',system-ui,sans-serif}
:root{--bg:#F5F2EC;--s1:#FFFFFF;--s2:#F0EDE6;--s3:#E8E4DC;--bd:rgba(0,0,0,.08);--bd2:rgba(0,0,0,.15);--txt:#1A1A1A;--muted:#6B7280;--amber:#B45309;}
body{background:var(--bg);color:var(--txt);display:flex;flex-direction:column;height:100vh}
#app{display:flex;flex:1;overflow:hidden}
#sidenav{width:200px;flex-shrink:0;background:var(--s1);border-right:0.5px solid var(--bd);display:flex;flex-direction:column;overflow:hidden}
.nav-logo{padding:12px 16px 10px;border-bottom:0.5px solid var(--bd);text-align:center}
.nav-sec-lbl{padding:10px 16px 3px;font-size:9px;letter-spacing:2px;text-transform:uppercase;color:var(--muted)}
.nav-sep{height:0.5px;background:var(--bd);margin:5px 0}
.nav-item{display:flex;align-items:center;gap:10px;padding:8px 16px;cursor:pointer;border-left:2px solid transparent;transition:background .12s}
.nav-item:hover{background:var(--s2)}
.nav-item.active{background:var(--s2);border-left-color:var(--amber)}
.nav-item.active .nav-lbl{color:var(--txt);font-weight:500}
.nav-dot{width:6px;height:6px;border-radius:50%;background:var(--bd2);flex-shrink:0;transition:background .15s}
.nav-sub-item{display:flex;align-items:center;gap:10px;padding:6px 16px 6px 28px;cursor:pointer;border-left:2px solid transparent;transition:all .15s;color:var(--muted);font-size:12px}
.nav-sub-item:hover{background:var(--s2);color:var(--txt)}
.nav-sub-item.active{border-left-color:var(--amber);background:var(--s2);color:var(--txt)}
.nav-item.active .nav-dot{background:var(--amber)}
.nav-lbl{font-size:12px;color:var(--muted)}
.nav-foot{margin-top:auto;padding:10px 16px;border-top:0.5px solid var(--bd);font-size:9px;color:var(--muted);line-height:1.6}
#content{flex:1;display:flex;flex-direction:column;overflow:hidden;background:var(--bg)}
.sec{display:none;flex:1;flex-direction:column;overflow:hidden;min-height:0}
.sec.active{display:flex}
.sec-head{padding:16px 22px 14px;border-bottom:0.5px solid var(--bd);flex-shrink:0;background:var(--bg)}
.sec-kicker{font-size:9px;letter-spacing:2px;text-transform:uppercase;margin-bottom:4px}
.sec-titulo{font-size:20px;font-weight:500;margin-bottom:5px}
.sec-lead{font-size:13px;color:var(--muted);line-height:1.6;max-width:720px}
.home-wrap{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:32px;gap:22px}
.home-headline{font-size:20px;font-weight:500;color:var(--txt);text-align:center;line-height:1.4}
.home-sub{font-size:13px;color:var(--muted);text-align:center;max-width:460px;line-height:1.6;margin-top:-8px}
.home-routes{display:grid;grid-template-columns:1fr 1fr;gap:14px;width:100%;max-width:560px}
.home-card{background:var(--s1);border:0.5px solid var(--bd);border-radius:12px;padding:18px;cursor:pointer;transition:border-color .15s}
.home-card:hover{border-color:var(--bd2)}
.home-card-kicker{font-size:9px;letter-spacing:2px;text-transform:uppercase;margin-bottom:6px;font-weight:500}
.home-card-title{font-size:15px;font-weight:500;color:var(--txt);margin-bottom:5px}
.home-card-desc{font-size:12px;color:var(--muted);line-height:1.5;margin-bottom:12px}
.home-card-steps{display:flex;flex-direction:column;gap:4px;margin-bottom:12px}
.home-card-step{font-size:11px;color:var(--muted);display:flex;align-items:center;gap:6px}
.home-step-dot{width:14px;height:14px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:8px;font-weight:700;flex-shrink:0}
.home-card-cta{padding:7px 0;border-radius:7px;font-size:12px;font-weight:500;text-align:center}
.home-base-note{font-size:11px;color:var(--muted);text-align:center;max-width:360px;line-height:1.6}
.achado{margin:10px 22px;padding:10px 14px;border-left:3px solid var(--amber);background:#FAEEDA;border-radius:0 8px 8px 0;flex-shrink:0}
.achado-lbl{font-size:9px;letter-spacing:2px;text-transform:uppercase;color:var(--amber);margin-bottom:3px}
.achado-txt{font-size:13px;color:#412402;line-height:1.6}
.achado-txt strong{color:#1A1A1A}
/* Nota de rodapé das tabelas (5 RAs sem zona TSE) — neutra, baixo destaque */
/* Módulo Estratégia — badge da categoria na tabela */
.estr-cat-badge{display:inline-block;font-size:9.5px;font-weight:500;padding:2px 8px;border-radius:10px}
.tabela-rodape-nota{margin:8px 22px 14px;padding:9px 14px;background:var(--s2);border-left:2px solid var(--bd2);border-radius:0 6px 6px 0;font-size:11.5px;color:var(--muted);line-height:1.55;flex-shrink:0}
.tabela-rodape-nota strong{color:var(--txt);font-weight:500}
.tabela-rodape-nota em{color:var(--muted);font-style:italic}
.chips-bar{padding:8px 22px;border-bottom:0.5px solid var(--bd);display:flex;align-items:center;gap:8px;flex-wrap:wrap;flex-shrink:0;background:var(--bg)}
.chip-input{font-size:12px;border:0.5px solid var(--bd2);border-radius:20px;padding:3px 10px;background:var(--s1);color:var(--txt);width:160px}
.toggle-group{display:inline-flex;gap:4px;background:var(--s2);border-radius:20px;padding:3px}
.toggle-btn{padding:4px 14px;font-size:12px;background:transparent;color:var(--muted);border:none;cursor:pointer;border-radius:20px;transition:all .15s;font-family:inherit}
.toggle-btn.on{background:var(--s1);color:var(--txt);box-shadow:0 1px 3px rgba(0,0,0,0.08)}
.tablewrap{overflow:auto;flex:1;min-height:0;margin:0 22px 20px}
.tablewrap table{border-collapse:separate;border-spacing:0;border:0.5px solid var(--bd);border-radius:10px;background:var(--bg);width:100%}
.tablewrap::-webkit-scrollbar{width:3px;height:3px}
.tablewrap::-webkit-scrollbar-thumb{background:var(--bd2)}
table{width:100%;border-collapse:collapse;font-size:12px}
thead th{position:sticky;top:0;background:var(--s1);text-align:left;padding:7px 8px 5px;font-size:10px;letter-spacing:1px;text-transform:uppercase;color:var(--muted);border-bottom:0.5px solid var(--bd);cursor:pointer;user-select:none;white-space:nowrap;z-index:10}


thead th:last-child{border-radius:0 10px 0 0}thead th:hover{color:var(--txt)}
td{padding:7px 10px;border-bottom:0.5px solid var(--bd);color:var(--txt);white-space:nowrap}
td:first-child{position:sticky;left:0;background:var(--bg);z-index:2;box-shadow:2px 0 4px rgba(0,0,0,.06)}
thead{position:relative;z-index:10}
thead th:first-child{position:sticky;left:0;z-index:20;background:var(--s1);border-radius:10px 0 0 0}
tr.persona-row td{background:#F0FDF4}
tr.persona-row td:first-child{border-left:2px solid #0F6E56;padding-left:6px;background:#F0FDF4}
tr:hover td:first-child{background:var(--s2)}
tr.persona-row:hover td:first-child{background:#DCFCE7}
/* Filtro inline em colunas (estilo Excel) — input texto e select dropdown */
.th-filter{display:inline-block;width:90px;border:0.5px solid var(--bd2);border-radius:4px;padding:2px 6px;font-size:10px;font-family:inherit;margin-left:8px;background:var(--s2);color:var(--txt);letter-spacing:0;text-transform:none;outline:none;vertical-align:middle;font-weight:400}
.th-filter:focus{border-color:var(--amber);background:var(--s1)}
.th-filter::placeholder{color:var(--muted);font-style:italic}
select.th-filter{cursor:pointer;width:auto;min-width:90px;padding-right:18px;background-image:linear-gradient(45deg,transparent 50%,var(--muted) 50%),linear-gradient(135deg,var(--muted) 50%,transparent 50%);background-position:calc(100% - 9px) 50%,calc(100% - 5px) 50%;background-size:4px 4px,4px 4px;background-repeat:no-repeat;-webkit-appearance:none;appearance:none}
select.th-filter.on{background-color:#FAEEDA;border-color:#B45309;color:#7A3E08;font-weight:500}
tr:hover td{background:var(--s2)}tr:hover td:first-child{background:var(--s2)}
tr.persona-row:hover td{background:#DCFCE7}
tr.sel td{background:#FAEEDA}
tr.sel td:first-child{border-left:2px solid var(--amber);padding-left:6px;background:#FAEEDA}
.sa{font-size:9px;margin-left:2px}
.tt{position:relative;display:inline-block}
.tt-icon{width:13px;height:13px;border-radius:50%;background:var(--s2);border:0.5px solid var(--bd2);font-size:9px;color:var(--muted);display:inline-flex;align-items:center;justify-content:center;cursor:help;margin-left:2px;vertical-align:middle}
.tt-box{display:none;position:absolute;top:20px;left:0;background:var(--txt);color:var(--bg);font-size:11px;padding:7px 10px;border-radius:6px;white-space:normal;width:220px;line-height:1.5;z-index:100;letter-spacing:0;text-transform:none;font-weight:400}
.tt:hover .tt-box{display:block}
thead th:nth-last-child(1) .tt-box,thead th:nth-last-child(2) .tt-box,thead th:nth-last-child(3) .tt-box{left:auto;right:0}
.vol-wrap{padding:10px 22px;border-bottom:0.5px solid var(--bd);flex-shrink:0;max-height:180px;overflow-y:auto}
.vol-titulo{font-size:10px;letter-spacing:1.5px;text-transform:uppercase;color:var(--muted);margin-bottom:8px}
.vol-item{display:flex;align-items:center;gap:8px;margin-bottom:4px}
.vol-nome{font-size:11px;width:140px;flex-shrink:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.vol-bar-bg{flex:1;height:12px;background:var(--s2);border-radius:3px;overflow:hidden}
.vol-bar-fill{height:100%;border-radius:3px}
.vol-val{font-size:11px;color:var(--muted);width:40px;text-align:right}
.cargo-bar{padding:8px 22px;border-bottom:0.5px solid var(--bd);display:flex;align-items:center;gap:8px;flex-shrink:0;background:var(--bg)}
.cargo-lbl{font-size:11px;color:var(--muted)}
.cargo-btn{font-size:12px;padding:4px 14px;border-radius:20px;border:0.5px solid var(--bd2);background:var(--s1);color:var(--muted);cursor:pointer;font-family:inherit}
.cargo-btn.on{background:#E6F1FB;color:#0C447C;border-color:#185FA5}
.campo-btn.on{background:#EEEDFE;color:#3C3489;border-color:#534AB7}
.ato4-body{display:flex;flex:1;overflow:hidden;flex-direction:column}
.ato4-top{display:grid;grid-template-columns:1fr 300px;flex:1;overflow:hidden;min-height:0}
.ato4-left{display:flex;flex-direction:column;overflow:hidden;border-right:0.5px solid var(--bd)}
.ato4-right{display:flex;flex-direction:column;overflow:hidden}
.ficha-wrap{flex:1;overflow-y:auto;padding:14px 16px;background:var(--bg)}
.ficha-wrap::-webkit-scrollbar{width:3px}
.ficha-wrap::-webkit-scrollbar-thumb{background:var(--bd2)}
.ficha-vazio{font-size:12px;color:var(--muted);text-align:center;padding-top:2rem}
.ficha-ra-nome{font-size:16px;font-weight:500;margin-bottom:3px}
.ficha-tag{margin-bottom:10px}
.ftag{display:inline-block;font-size:11px;padding:3px 10px;border-radius:20px;font-weight:500}
.ficha-kpis{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:10px}
.fkpi{background:var(--s1);border:0.5px solid var(--bd2);border-radius:8px;padding:8px 10px}
.fkpi-val{font-size:17px;font-weight:500}
.fkpi-lbl{font-size:10px;color:var(--muted);margin-top:1px}
.ficha-narr{font-size:12px;color:var(--muted);line-height:1.6}
.matriz-outer{padding:12px 22px;border-top:0.5px solid var(--bd);flex-shrink:0}
.matriz-titulo{font-size:10px;letter-spacing:1.5px;text-transform:uppercase;color:var(--muted);margin-bottom:8px}
.matriz-grid{display:grid;grid-template-columns:1fr 1fr;grid-template-rows:120px 120px;gap:2px}
.quad{border-radius:6px;padding:7px;position:relative;overflow:hidden}
.quad-lbl{font-size:9px;font-weight:600;text-transform:uppercase;letter-spacing:1px;margin-bottom:3px}
.mpt{position:absolute;width:7px;height:7px;border-radius:50%;cursor:pointer;transform:translate(-50%,-50%);z-index:2}
.mpt:hover{transform:translate(-50%,-50%) scale(2);z-index:10}
.mpt.sel{transform:translate(-50%,-50%) scale(2.2);z-index:10;outline:2px solid #B45309}
.eixo-x{text-align:center;font-size:9px;color:var(--muted);letter-spacing:1px;text-transform:uppercase;margin-top:3px}
.ps-campo-card{background:var(--s1);border:0.5px solid var(--bd);border-radius:12px;padding:1.25rem;cursor:pointer;transition:border-color .15s}
.ps-campo-card:hover{border-color:var(--bd2)}
.ps-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:16px;margin-bottom:1.5rem}
.ps-card{background:var(--s1);border:0.5px solid var(--bd);border-radius:12px;padding:1.5rem;display:none}
.ps-card.visible{display:block}
.ps-card.sel{border-width:2px}
.ps-nome{font-size:18px;font-weight:500;color:var(--txt);margin-bottom:3px}
.ps-cargo{font-size:12px;color:var(--muted);margin-bottom:14px}
.ps-frase{font-size:13px;line-height:1.6;padding:12px 14px;background:var(--s2);border-radius:8px;margin-bottom:14px;color:var(--txt)}
.ps-stats{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:14px}
.ps-stat{background:var(--s2);border-radius:8px;padding:8px 12px}
.ps-stat-val{font-size:16px;font-weight:500}
.ps-stat-lbl{font-size:11px;color:var(--muted);margin-top:2px}
.ps-desafio{font-size:12px;color:var(--muted);line-height:1.6;padding-top:12px;border-top:0.5px solid var(--bd);margin-bottom:14px}
.ps-desafio strong{color:var(--txt)}
.ps-btn{width:100%;padding:10px;border-radius:8px;font-size:13px;font-weight:500;cursor:pointer;background:transparent}
.ps-banner{display:none;align-items:center;gap:16px;background:var(--s1);border:0.5px solid var(--bd);border-radius:12px;padding:1rem 1.25rem;margin-top:.5rem}
.ps-banner.visible{display:flex}
.ps-banner-nome{font-size:15px;font-weight:500}
.ps-banner-sub{font-size:12px;color:var(--muted);margin-top:2px}
.ps-iniciar{padding:10px 24px;border-radius:8px;border:none;font-size:13px;font-weight:500;cursor:pointer;margin-left:auto}
.persona-chip{display:flex;align-items:center;gap:10px;padding:7px 22px;border-bottom:0.5px solid var(--bd);flex-shrink:0;background:var(--bg)}
.persona-chip-nome{font-size:11px;font-weight:500;color:var(--txt)}
.persona-chip-sub{font-size:10px;color:var(--muted)}
.persona-chip-trocar{font-size:11px;color:var(--amber);cursor:pointer;margin-left:auto;text-decoration:underline;text-underline-offset:3px}
.cand-search-bar{padding:8px 22px 8px;border-bottom:0.5px solid var(--bd);display:flex;align-items:center;gap:10px;flex-shrink:0;background:var(--bg);flex-wrap:wrap}
.cand-search-input{flex:1;border:0.5px solid var(--bd2);border-radius:20px;padding:6px 14px;font-size:12px;font-family:inherit;color:var(--txt);background:var(--s1);outline:none;max-width:240px}
.cand-search-input:focus{border-color:var(--amber)}
.cf-btn{font-size:11px;padding:4px 14px;border-radius:20px;border:0.5px solid var(--bd2);background:var(--s1);color:var(--muted);cursor:pointer;transition:all .15s;font-family:inherit}
.cf-btn:hover{background:var(--s2)}
.cf-btn.on{background:#E6F1FB;color:#0C447C;border-color:#185FA5;font-weight:500}
.cand-stat-card{background:var(--s1);border:0.5px solid var(--bd);border-radius:8px;padding:8px 12px;flex-shrink:0}
.cand-stat-lbl{font-size:9px;text-transform:uppercase;letter-spacing:1.2px;color:var(--muted);margin-bottom:2px}
.cand-stat-val{font-size:18px;font-weight:500;color:var(--txt);line-height:1.1}
.cand-stat-sub{font-size:10px;color:var(--muted);margin-top:1px}
.cand-body{display:flex;flex:1;overflow:hidden;margin:0 22px 16px;border:0.5px solid var(--bd);border-radius:10px}
.cand-list{width:200px;flex-shrink:0;border-right:0.5px solid var(--bd);overflow-y:auto;display:flex;flex-direction:column}
.cand-list::-webkit-scrollbar{width:3px}
.cand-list::-webkit-scrollbar-thumb{background:var(--bd2)}
.cand-item{display:flex;align-items:stretch;cursor:pointer;border-bottom:0.5px solid var(--bd);transition:background .1s}
.cand-item:hover,.cand-item.sel{background:var(--s2)}
.cand-item-bar{width:3px;flex-shrink:0;border-radius:0}
.cand-item-inner{padding:9px 10px;flex:1}
.cand-item-nome{font-size:12px;font-weight:500;color:var(--txt)}
.cand-item-sub{font-size:10px;color:var(--muted);margin-top:2px}
.cand-detail{flex:1;overflow:hidden;display:flex;flex-direction:column}
.cand-empty{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px;color:var(--muted)}
.cand-empty-icon{font-size:22px;opacity:.2;letter-spacing:-2px}
.cand-empty-txt{font-size:11px;text-align:center;max-width:220px;line-height:1.6}
.cand-detail-sub{font-size:12px;color:var(--muted);margin-top:3px}
.est-config{padding:10px 22px;border-bottom:0.5px solid var(--bd);display:flex;align-items:center;gap:10px;flex-shrink:0;background:var(--bg)}
.est-label{font-size:11px;color:var(--muted)}
.est-cargo-btn{font-size:11px;padding:4px 12px;border-radius:20px;border:0.5px solid var(--bd2);background:var(--s1);color:var(--muted);cursor:pointer;font-family:inherit;transition:all .15s}
.est-cargo-btn.on{background:#3B6D11;color:#fff;border-color:#3B6D11}
.a5-tablewrap{overflow:auto;flex:1}
.a5-tablewrap::-webkit-scrollbar{width:3px;height:3px}
.a5-tablewrap::-webkit-scrollbar-thumb{background:var(--bd2)}
.met-modal{display:none;position:fixed;inset:0;z-index:500;background:var(--s1);flex-direction:column;overflow:hidden}
.met-modal.open{display:flex}
.met-header{display:flex;align-items:center;gap:12px;padding:12px 20px;border-bottom:0.5px solid var(--bd);flex-shrink:0;background:var(--s1)}
.met-close{padding:5px 12px;border-radius:8px;border:0.5px solid var(--bd2);background:transparent;color:var(--txt);font-size:11px;cursor:pointer;font-family:inherit;margin-left:auto}
.met-nav{display:flex;gap:4px;flex:1;overflow-x:auto}
.met-nav-btn{padding:4px 10px;border-radius:20px;border:none;background:transparent;color:var(--muted);font-size:11px;cursor:pointer;font-family:inherit;white-space:nowrap}
.met-nav-btn:hover,.met-nav-btn.on{background:var(--s2);color:var(--txt)}
.met-nav-btn.on{font-weight:500}
.met-body{flex:1;overflow-y:auto}
.met-section{padding:36px 44px;border-bottom:0.5px solid var(--bd);max-width:760px}
.met-kicker{font-size:9px;letter-spacing:2px;text-transform:uppercase;color:var(--amber);margin-bottom:8px}
.met-titulo{font-size:22px;font-weight:500;margin-bottom:14px}
.met-txt{font-size:13px;color:var(--muted);line-height:1.8;margin-bottom:12px}
.met-txt p{margin-bottom:10px}
.met-txt strong{color:var(--txt)}
.met-table{width:100%;border-collapse:collapse;font-size:12px;margin:14px 0}
.met-table th{text-align:left;padding:6px 10px;font-size:9px;letter-spacing:1px;text-transform:uppercase;color:var(--muted);border-bottom:0.5px solid var(--bd)}
.met-table td{padding:7px 10px;border-bottom:0.5px solid var(--bd);color:var(--txt)}
.met-table tr:last-child td{border-bottom:none}
.met-link{font-size:11px;color:var(--muted);cursor:pointer;border:none;background:none;font-family:inherit;padding:0;text-decoration:underline;text-underline-offset:3px}
.met-link:hover{color:var(--amber)}
/* Diagnóstico — wizard */
#s-diagnostico{overflow-y:auto}
.diag-stepper{display:flex;align-items:center;justify-content:center;gap:0;padding:18px 22px;border-bottom:0.5px solid var(--bd);background:var(--bg);flex-shrink:0}
.diag-step{display:flex;flex-direction:column;align-items:center;gap:4px;min-width:96px}
.diag-step-num{width:26px;height:26px;border-radius:50%;background:var(--s2);color:var(--muted);font-size:12px;font-weight:500;display:flex;align-items:center;justify-content:center;border:0.5px solid var(--bd2);transition:all .15s ease}
.diag-step-lbl{font-size:11px;color:var(--muted);font-weight:400}
.diag-step.on .diag-step-num{background:#B45309;color:#fff;border-color:#B45309}
.diag-step.on .diag-step-lbl{color:var(--txt);font-weight:500}
.diag-step.done .diag-step-num{background:#FAEEDA;color:#B45309;border-color:#B45309}
.diag-step-line{flex:0 0 70px;height:1px;background:var(--bd2);margin:0 -8px;margin-bottom:18px}
.diag-pg{display:none;padding:22px;flex:1;overflow-y:auto}
.diag-pg.active{display:block}
.diag-types{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px;max-width:1100px;margin:0 auto 18px}
.diag-type-card{background:var(--s1);border:0.5px solid var(--bd2);border-radius:10px;padding:16px 16px 14px;position:relative;transition:all .15s ease}
.diag-type-card.available{cursor:pointer}
.diag-type-card.available:hover{border-color:#B45309;box-shadow:0 2px 10px rgba(180,83,9,.12)}
.diag-type-card.selected{border-color:#B45309;background:#FFFBF3;box-shadow:0 2px 10px rgba(180,83,9,.18)}
.diag-type-card.disabled{opacity:.55;background:var(--s2)}
.diag-type-num{font-size:9px;letter-spacing:2px;color:var(--muted);margin-bottom:6px}
.diag-type-title{font-size:14px;font-weight:500;margin-bottom:6px;color:var(--txt)}
.diag-type-desc{font-size:11.5px;color:var(--muted);line-height:1.5}
.diag-type-tag{position:absolute;top:12px;right:12px;font-size:9px;letter-spacing:1px;text-transform:uppercase;padding:2px 7px;border-radius:10px;background:var(--s3);color:var(--muted)}
.diag-type-tag.avail{background:#FAEEDA;color:#B45309}
.diag-skel{max-width:1100px;margin:0 auto}
.diag-skel-hdr{padding:14px 4px 18px;border-bottom:0.5px dashed var(--bd2);margin-bottom:14px}
.diag-skel-body{display:flex;flex-direction:column;gap:10px}
.diag-cap{background:var(--s1);border:0.5px dashed var(--bd2);border-radius:8px;padding:14px 16px}
.diag-cap-lbl{font-size:9px;letter-spacing:1.5px;text-transform:uppercase;color:var(--muted)}
.diag-cap-title{font-size:14px;font-weight:500;margin-top:3px}
.diag-cap-skel{font-size:11px;color:var(--muted);font-style:italic;margin-top:8px}
.diag-actions{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:14px 22px;border-top:0.5px solid var(--bd);background:var(--bg);max-width:1100px;margin:18px auto 0}
.diag-btn{font-family:inherit;font-size:12px;padding:7px 14px;border-radius:6px;border:0.5px solid var(--bd2);background:var(--s1);color:var(--txt);cursor:pointer;transition:all .15s ease}
.diag-btn:hover:not(:disabled){background:var(--s2)}
.diag-btn.primary{background:#B45309;border-color:#B45309;color:#fff}
.diag-btn.primary:hover:not(:disabled){background:#92400E;border-color:#92400E}
.diag-btn:disabled{opacity:.45;cursor:not-allowed}
/* Diagnóstico — configurador (Passo 2) */
.diag-config{padding:14px 22px;border-bottom:0.5px solid var(--bd);background:var(--bg);display:flex;flex-direction:column;gap:8px;flex-shrink:0;margin:-22px -22px 0 -22px}
.diag-config-row{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.diag-config-lbl{font-size:9px;letter-spacing:1.5px;text-transform:uppercase;color:var(--muted);font-weight:500;min-width:170px}
#diag-orig-chip,#diag-ref-chip{align-items:center;gap:6px;padding:4px 8px 4px 10px;border-radius:20px;border:0.5px solid var(--bd2);background:var(--s1);font-size:12px;display:none}
.diag-config .cargo-btn{font-size:11px;padding:5px 10px}
.diag-config .cargo-btn.on{background:#B45309;border-color:#B45309;color:#fff}
.diag-config .cargo-btn[disabled]{opacity:.35;cursor:not-allowed;background:var(--s2);color:var(--muted)}
/* Diagnóstico — conteúdo dos capítulos */
.diag-content{max-width:1100px;margin:18px auto 0;width:100%}
.diag-cap-full{margin-bottom:30px}
.diag-cap-num{font-size:9px;letter-spacing:2px;text-transform:uppercase;color:var(--amber);font-weight:500;margin-bottom:4px}
.diag-cap-h{font-size:20px;font-weight:500;margin-bottom:16px;border-bottom:0.5px solid var(--bd);padding-bottom:8px}
.diag-sub{margin-bottom:18px}
.diag-sub-num{font-size:10px;letter-spacing:1px;color:var(--muted);font-weight:500;margin-bottom:3px}
.diag-sub-h{font-size:14px;font-weight:500;margin-bottom:10px}
.diag-sub-body{font-size:12.5px;line-height:1.65;color:var(--txt)}
.diag-sub-body p{margin-bottom:10px}
.diag-sub-body strong{color:var(--txt);font-weight:600}
.diag-card{background:var(--s1);border:0.5px solid var(--bd);border-radius:10px;padding:16px 18px;margin-top:6px}
.diag-card-hdr{display:flex;align-items:center;gap:10px;margin-bottom:10px;flex-wrap:wrap}
.diag-card-nome{font-size:15px;font-weight:500}
.diag-card-meta{font-size:11px;color:var(--muted)}
.diag-card-tag{font-size:9px;padding:3px 8px;border-radius:10px;letter-spacing:1px;text-transform:uppercase;font-weight:500}
.diag-kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(110px,1fr));gap:10px;margin-top:10px;padding-top:10px;border-top:0.5px dashed var(--bd2)}
.diag-kpi{text-align:center}
.diag-kpi-v{font-size:18px;font-weight:500;color:var(--amber);line-height:1}
.diag-kpi-l{font-size:10px;color:var(--muted);margin-top:4px}
.diag-tip-box{background:var(--s2);border-left:2px solid var(--amber);padding:8px 12px;font-size:11.5px;color:var(--txt);margin-top:10px;line-height:1.55}
.diag-ras-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:8px}
.diag-ra-card{background:var(--s1);border:0.5px solid var(--bd);border-radius:8px;padding:10px 12px}
.diag-ra-nome{font-size:12px;font-weight:500;margin-bottom:6px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.diag-ra-row{display:flex;justify-content:space-between;align-items:baseline;font-size:11px;color:var(--muted);margin-top:2px}
.diag-ra-val{font-size:14px;font-weight:500;color:var(--txt)}
.diag-search-item{padding:7px 10px;border-bottom:0.5px solid var(--bd);cursor:pointer;font-size:12px;display:flex;justify-content:space-between;align-items:center;gap:8px}
.diag-search-item:hover{background:var(--s2)}
.diag-search-item:last-child{border-bottom:none}
.diag-search-item-meta{font-size:10px;color:var(--muted)}
/* Diagnóstico — 5 categorias */
.diag-cat-bars{display:flex;flex-direction:column;gap:6px;margin-top:6px}
.diag-cat-bar{display:grid;grid-template-columns:200px 1fr 110px;align-items:center;gap:10px;padding:8px 12px;background:var(--s1);border:0.5px solid var(--bd);border-radius:6px}
.diag-cat-bar-lbl{display:flex;align-items:center;gap:8px;font-size:12px;font-weight:500}
.diag-cat-dot{width:10px;height:10px;border-radius:3px;flex-shrink:0}
.diag-cat-bar-track{height:8px;background:var(--s3);border-radius:4px;overflow:hidden;position:relative}
.diag-cat-bar-fill{height:100%;border-radius:4px}
.diag-cat-bar-num{font-size:11px;color:var(--muted);text-align:right;font-variant-numeric:tabular-nums}
.diag-cat-bar-num strong{color:var(--txt);font-size:14px;font-weight:500}
.diag-cat-block{margin-top:14px;background:var(--s1);border:0.5px solid var(--bd);border-radius:8px;overflow:hidden}
.diag-cat-block-hdr{display:flex;align-items:center;gap:8px;padding:10px 14px;background:var(--s2);border-bottom:0.5px solid var(--bd);font-size:12px;font-weight:500}
.diag-cat-block-body{padding:10px 14px}
.diag-cat-explica{font-size:11px;color:var(--muted);font-style:italic;line-height:1.55;margin-bottom:8px}
.diag-cat-table{width:100%;border-collapse:collapse;font-size:11.5px}
.diag-cat-table th{text-align:left;padding:6px 8px;font-size:9px;letter-spacing:1px;text-transform:uppercase;color:var(--muted);border-bottom:0.5px solid var(--bd);font-weight:500}
.diag-cat-table td{padding:7px 8px;border-bottom:0.5px solid var(--bd)}
.diag-cat-table tr:last-child td{border-bottom:none}
.diag-cat-table td.num{text-align:right;font-variant-numeric:tabular-nums}
.diag-cat-empty{color:var(--muted);font-style:italic;font-size:11.5px}
.diag-scenario-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:8px}
.diag-scenario{background:var(--s1);border:0.5px solid var(--bd);border-radius:8px;padding:14px}
.diag-scenario-h{font-size:11px;letter-spacing:1px;text-transform:uppercase;color:var(--amber);font-weight:500;margin-bottom:6px}
.diag-scenario-v{font-size:22px;font-weight:500;color:var(--txt);font-variant-numeric:tabular-nums;line-height:1.1}
.diag-scenario-vmeta{font-size:10px;color:var(--muted);margin-top:3px}
.diag-scenario-desc{font-size:11.5px;color:var(--txt);line-height:1.55;margin-top:10px;padding-top:10px;border-top:0.5px dashed var(--bd2)}
.diag-meta-bar{display:flex;align-items:baseline;gap:14px;margin-top:6px;padding:10px 14px;background:var(--s1);border:0.5px solid var(--bd);border-radius:8px;flex-wrap:wrap}
.diag-meta-v{font-size:22px;font-weight:500;color:#085041;line-height:1}
.diag-meta-l{font-size:11px;color:var(--muted)}
</style>
</head>
<body>

<!-- ════════════ LOGIN OVERLAY (decorativo — porta com fechadura simbólica) ════════════ -->
<div id="estr-login" style="position:fixed;inset:0;z-index:10000;display:flex;font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif">

  <!-- ESQUERDA: Orientação -->
  <div style="flex:1.3;background:#F5F2EC;padding:54px 70px;display:flex;flex-direction:column;overflow-y:auto">
    <div style="display:flex;align-items:center;gap:14px;margin-bottom:36px">
      <img src="https://raw.githubusercontent.com/aag1974/dashboard-ivv/main/logo.png" alt="Opinião" style="height:42px;width:auto;filter:sepia(1) saturate(1.2) hue-rotate(5deg) brightness(0.7)"/>
      <div>
        <div style="font-size:22px;font-weight:600;color:#1A1A1A;letter-spacing:-.4px;line-height:1">Estrategos</div>
        <div style="font-size:10px;color:#6B7280;text-transform:uppercase;letter-spacing:1.5px;margin-top:3px">Inteligência Política · DF 2026</div>
      </div>
    </div>

    <div style="max-width:560px">
      <div style="font-size:26px;font-weight:600;color:#1A1A1A;line-height:1.25;margin-bottom:12px;letter-spacing:-.5px">Análise eleitoral do Distrito Federal — voto, território e estratégia.</div>
      <div style="font-size:14px;color:#1A1A1A;line-height:1.65;margin-bottom:28px">Combinamos perfil socioeconômico das 33 regiões administrativas (<strong>PDAD 2021</strong>) com a votação real da eleição (<strong>TSE 2022</strong>) pra mostrar como o voto se distribui no território — e o que isso significa pra cada candidato.</div>

      <div style="font-size:10px;color:#B45309;text-transform:uppercase;letter-spacing:1.2px;font-weight:600;margin-bottom:10px">O que você vai encontrar</div>
      <ul style="list-style:none;padding:0;margin:0 0 26px 0;font-size:13px;color:#1A1A1A;line-height:1.65">
        <li style="padding:5px 0;border-bottom:0.5px solid rgba(0,0,0,.08)"><strong style="color:#B45309">Território</strong> · perfil demográfico e eleitoral por RA</li>
        <li style="padding:5px 0;border-bottom:0.5px solid rgba(0,0,0,.08)"><strong style="color:#B45309">Contexto</strong> · campos políticos, candidatos e estratégia (Performance × Força do campo)</li>
        <li style="padding:5px 0"><strong style="color:#B45309">Geopolítica</strong> · leitura territorial em mapa por RA e por candidato</li>
      </ul>

      <div style="font-size:10px;color:#B45309;text-transform:uppercase;letter-spacing:1.2px;font-weight:600;margin-bottom:10px">Por onde começar</div>
      <div style="font-size:13px;color:#1A1A1A;line-height:1.7">
        Pra entender o panorama do DF: comece em <strong>Território › População</strong>. Pra estudar um candidato específico: vá em <strong>Geopolítica › Candidato</strong>, escolha pelo nome e clique em <strong>🖨 Imprimir</strong> pra gerar o PDF de 1–2 páginas com o diagnóstico estratégico.
      </div>
    </div>

    <div style="margin-top:auto;padding-top:30px;font-size:10px;color:#6B7280;line-height:1.5">
      Solução de Inteligência Política da <strong style="color:#1A1A1A">Opinião Informação Estratégica</strong> · <a href="mailto:alexandre@opiniao.inf.br" style="color:#B45309;text-decoration:none">alexandre@opiniao.inf.br</a>
    </div>
  </div>

  <!-- DIREITA: Login -->
  <div style="flex:1;background:#FFFFFF;display:flex;align-items:center;justify-content:center;padding:54px;border-left:0.5px solid rgba(0,0,0,.08);min-width:340px">
    <div style="width:100%;max-width:340px">
      <div style="font-size:20px;font-weight:600;color:#1A1A1A;margin-bottom:6px;letter-spacing:-.3px">Acesso</div>
      <div style="font-size:12px;color:#6B7280;margin-bottom:24px;line-height:1.5">Identifique-se para entrar no painel.</div>
      <form id="estr-login-form" onsubmit="event.preventDefault();_estrLogin();" style="display:flex;flex-direction:column;gap:11px">
        <input id="estr-login-user" type="text" autocomplete="username" placeholder="Usuário" autofocus style="padding:11px 14px;border:0.5px solid rgba(0,0,0,.18);border-radius:8px;font-size:13px;font-family:inherit;outline:none;background:#FAFAFA"/>
        <input id="estr-login-pwd" type="password" autocomplete="current-password" placeholder="Senha" style="padding:11px 14px;border:0.5px solid rgba(0,0,0,.18);border-radius:8px;font-size:13px;font-family:inherit;outline:none;background:#FAFAFA"/>
        <button type="submit" style="margin-top:6px;padding:11px;border:0;border-radius:8px;background:#B45309;color:#fff;font-size:13px;font-weight:500;font-family:inherit;cursor:pointer;letter-spacing:.3px">Entrar</button>
        <div id="estr-login-msg" style="font-size:11px;color:#991B1B;text-align:center;min-height:14px;margin-top:2px"></div>
      </form>
      <div style="margin-top:24px;padding-top:18px;border-top:0.5px solid rgba(0,0,0,.08);font-size:11px;color:#6B7280;line-height:1.5">
        Acesso restrito. Para credenciais, contate <strong style="color:#1A1A1A">alexandre@opiniao.inf.br</strong>
      </div>
    </div>
  </div>
</div>

<div id="app">
  <nav id="sidenav">
    <div class="nav-logo">
      <img src="https://raw.githubusercontent.com/aag1974/dashboard-ivv/main/logo.png"
           style="height:48px;filter:sepia(1) saturate(1.2) hue-rotate(5deg) brightness(0.7)"
           alt="Logo">
    </div>
    <div style="flex:1;overflow-y:auto;overflow-x:hidden">
      <div class="nav-sep" style="margin-top:6px"></div>
      <div class="nav-sec-lbl" style="color:#854F0B">Território</div>

      <div class="nav-item active" id="ni-populacao" onclick="irSec('populacao')">
        <div class="nav-dot" style="background:#FAC775"></div><span class="nav-lbl">População</span>
      </div>
      <div class="nav-item" id="ni-eleitor" onclick="irSec('eleitor')">
        <div class="nav-dot" style="background:#FAC775"></div><span class="nav-lbl">Eleitorado</span>
      </div>
      <div class="nav-sep"></div>
      <div class="nav-sec-lbl" style="color:#185FA5">Contexto</div>
      <div class="nav-item" id="ni-campo" onclick="irSec('campo')">
        <div class="nav-dot" style="background:#B5D4F4"></div><span class="nav-lbl">Campo político</span>
      </div>
      <div class="nav-item" id="ni-candidato" onclick="irSec('candidato')">
        <div class="nav-dot" style="background:#B5D4F4"></div><span class="nav-lbl">Candidatos</span>
      </div>
      <div class="nav-item" id="ni-estrategia" onclick="irSec('estrategia')">
        <div class="nav-dot" style="background:#B5D4F4"></div><span class="nav-lbl">Estratégia</span>
      </div>
      <div class="nav-sep"></div>
      <div class="nav-sec-lbl" style="color:#1D9E75">Geopolítica</div>
      <div class="nav-item" id="ni-geo-territorio" onclick="irGeoTerritorio()">
        <div class="nav-dot" style="background:#9FE1CB"></div><span class="nav-lbl">Território</span>
      </div>
      <div class="nav-item" id="ni-geo-candidato" onclick="irGeoCandidato()">
        <div class="nav-dot" style="background:#9FE1CB"></div><span class="nav-lbl">Candidato</span>
      </div>
      <!-- Menu Relatório oculto temporariamente — Projeções e Diagnóstico em stand-by.
      <div class="nav-sep"></div>
      <div class="nav-sec-lbl" style="color:#B45309">Relatório</div>
      <div class="nav-item" id="ni-projecoes" onclick="irSec('projecoes')">
        <div class="nav-dot" style="background:#EF9F27"></div><span class="nav-lbl">Projeções</span>
      </div>
      <div class="nav-item" id="ni-diagnostico" onclick="irSec('diagnostico')">
        <div class="nav-dot" style="background:#EF9F27"></div><span class="nav-lbl">Diagnóstico</span>
      </div>
      -->

    </div>
    <div style="padding:8px 14px;border-top:0.5px solid var(--bd);font-size:11px;color:var(--muted);cursor:pointer;display:flex;align-items:center;gap:6px" onclick="abrirMet('intro')"><span>ⓘ</span> Sobre o Estrategos</div>
    <div class="nav-foot">PDAD 2021 — TSE 2022<br>Estrategos · Inteligência Política DF</div>
  </nav>
  <div id="content">

    <!-- A POPULAÇÃO -->
    <div class="sec active" id="s-populacao">
      <div class="sec-head">
        <div class="sec-kicker" style="color:#854F0B">Território</div>
        <div class="sec-titulo">População <span style="font-size:13px;color:var(--muted);font-weight:400">· PDAD 2021</span></div>
        <div class="sec-lead">A PDAD 2021, realizada pelo IPEDF (antigo CODEPLAN), entrevistou 83 mil moradores nas 33 regiões do DF. Renda, escolaridade, ocupação e origem constroem perfis socioeconômicos radicalmente distintos entre territórios às vezes vizinhos — e esses perfis determinam o que cada eleitorado valoriza, o que rejeita e que tipo de candidato tem chance real de ganhar ali.</div>
      </div>
      <div class="achado"><div class="achado-lbl">O dado que muda tudo</div><div class="achado-txt">A renda per capita varia de <strong>R$ 626</strong> (SCIA/Estrutural) a <strong>R$ 11.622</strong> (Lago Sul) — diferença de <strong>quase 19 vezes</strong> dentro do mesmo Distrito Federal.</div></div>
      <div class="tablewrap"><table><thead><tr>
        <th style="min-width:200px" onclick="srt(1,'nome')">Região <span class="sa" id="s1-nome"></span><input class="th-filter" id="fi1" placeholder="filtrar..." oninput="filtrar(1)" onclick="event.stopPropagation()"></th>
        <th style="min-width:95px" onclick="srt(1,'renda_pc')"><span class="tt">Renda P/Capita<span class="tt-icon">?</span><span class="tt-box">Renda per capita média dos moradores (PDAD 2021)</span></span> <span class="sa" id="s1-renda_pc">&#9660;</span></th>
        <th style="min-width:78px" onclick="srt(1,'pct_super')"><span class="tt">Superior<span class="tt-icon">?</span><span class="tt-box">% moradores de 16+ anos com nível superior — incompleto e completo (escolaridade 6 e 7, PDAD 2021). Mesmo denominador do TSE — gap diretamente comparável.</span></span> <span class="sa" id="s1-pct_super"></span></th>
        <th style="min-width:78px" onclick="srt(1,'pct_sem_fund')"><span class="tt">Sem fund.<span class="tt-icon">?</span><span class="tt-box">% sem ensino fundamental completo</span></span> <span class="sa" id="s1-pct_sem_fund"></span></th>
        <th style="min-width:78px" onclick="srt(1,'pct_ab')"><span class="tt">Classe A/B<span class="tt-icon">?</span><span class="tt-box">% em domicílios de classe A ou B</span></span> <span class="sa" id="s1-pct_ab"></span></th>
        <th style="min-width:78px" onclick="srt(1,'pct_de')"><span class="tt">Classe D/E<span class="tt-icon">?</span><span class="tt-box">% em domicílios de classe D ou E</span></span> <span class="sa" id="s1-pct_de"></span></th>
        <th style="min-width:78px" onclick="srt(1,'pct_inseg')"><span class="tt">Inseg. alimentar<span class="tt-icon">?</span><span class="tt-box">% em situação de insegurança alimentar</span></span> <span class="sa" id="s1-pct_inseg"></span></th>
        <th style="min-width:78px" onclick="srt(1,'pct_serv')"><span class="tt">Func. público<span class="tt-icon">?</span><span class="tt-box">% no serviço público — inclui servidores federais, distritais e militares (FA, PM e CB)</span></span> <span class="sa" id="s1-pct_serv"></span></th>
        <th style="min-width:78px" onclick="srt(1,'pct_serv_fed')"><span class="tt">Serv. federal<span class="tt-icon">?</span><span class="tt-box">% especificamente no serviço federal</span></span> <span class="sa" id="s1-pct_serv_fed"></span></th>
        <th style="min-width:78px" onclick="srt(1,'pct_privado')"><span class="tt">Privado<span class="tt-icon">?</span><span class="tt-box">% empregado no setor privado — exclui trabalhadores domésticos</span></span> <span class="sa" id="s1-pct_privado"></span></th>
        <th style="min-width:78px" onclick="srt(1,'pct_conta')"><span class="tt">Autônomo<span class="tt-icon">?</span><span class="tt-box">% que trabalha por conta própria</span></span> <span class="sa" id="s1-pct_conta"></span></th>
        <th style="min-width:78px" onclick="srt(1,'pct_desoc')"><span class="tt">Desempr.<span class="tt-icon">?</span><span class="tt-box">% que não trabalhou nos últimos 30 dias E procurou emprego (desocupado stricto sensu)</span></span> <span class="sa" id="s1-pct_desoc"></span></th>
        <th style="min-width:78px" onclick="srt(1,'pct_beneficio')"><span class="tt">Bolsa Família<span class="tt-icon">?</span><span class="tt-box">% que recebeu benefício social no mês anterior — Bolsa Família, BPC ou LOAS (I22_1 PDAD 2021)</span></span> <span class="sa" id="s1-pct_beneficio"></span></th>
        <th style="min-width:78px" onclick="srt(1,'pct_plano')"><span class="tt">Plano Saúde<span class="tt-icon">?</span><span class="tt-box">% com plano de saúde privado</span></span> <span class="sa" id="s1-pct_plano"></span></th>
        <th style="min-width:78px" onclick="srt(1,'pct_jov_mor')"><span class="tt">Jovens 16-24<span class="tt-icon">?</span><span class="tt-box">% de moradores com 16 a 24 anos (total de residentes, PDAD 2021).</span></span> <span class="sa" id="s1-pct_jov_mor"></span></th>
        <th style="min-width:78px" onclick="srt(1,'pct_ido_mor')"><span class="tt">Idosos 60+<span class="tt-icon">?</span><span class="tt-box">% de moradores com 60 anos ou mais (total de residentes, PDAD 2021).</span></span> <span class="sa" id="s1-pct_ido_mor"></span></th>
        <th style="min-width:78px" onclick="srt(1,'pct_nativo')"><span class="tt">Nativo<span class="tt-icon">?</span><span class="tt-box">% nascido no Distrito Federal</span></span> <span class="sa" id="s1-pct_nativo"></span></th>
        <th style="min-width:78px" onclick="srt(1,'pct_migrante')"><span class="tt">Migrante<span class="tt-icon">?</span><span class="tt-box">% nascido fora do DF</span></span> <span class="sa" id="s1-pct_migrante"></span></th>
      </tr></thead><tbody id="tb1"></tbody></table></div>
    </div>

    <!-- O ELEITORADO -->
    <div class="sec" id="s-eleitor">
      <div class="sec-head">
        <div class="sec-kicker" style="color:#854F0B">Território</div>
        <div class="sec-titulo">Eleitorado <span style="font-size:13px;color:var(--muted);font-weight:400">· TSE 2022</span></div>
        <div class="sec-lead"><strong>Eleitor não é morador.</strong> A população (PDAD) inclui crianças, residentes sem título e estrangeiros; o eleitorado é apenas quem pode votar. O cadastro TSE 2022 revela quantos eleitores aptos cada região tem e qual o perfil por idade, gênero e escolaridade — diferenças que o cliente precisa enxergar antes de decidir onde investir.</div>
      </div>
      <div class="achado"><div class="achado-lbl">O dado que muda tudo</div><div class="achado-txt">Ceilândia sozinha tem <strong>302 mil eleitores aptos</strong> — mais do que as <strong>15 menores regiões somadas</strong>. Escolher mal o território significa perder antes de começar.</div></div>
      <div class="tablewrap"><table><thead><tr>
        <th style="min-width:200px" onclick="srt(2,'nome')">Região <span class="sa" id="s2-nome"></span><input class="th-filter" id="fi2" placeholder="filtrar..." oninput="filtrar(2)" onclick="event.stopPropagation()"></th>
        <th style="min-width:88px" onclick="srt(2,'el_aptos')"><span class="tt">Aptos<span class="tt-icon">?</span><span class="tt-box">Total de eleitores aptos na RA — fonte: TSE 2022. Atribuição seção→RA via point-in-polygon dos locais de votação.</span></span> <span class="sa" id="s2-el_aptos">&#9660;</span></th>
        <th onclick="srt(2,'abstencao')"><span class="tt">Abstenção<span class="tt-icon">?</span><span class="tt-box">% de eleitores aptos que não compareceram no 1º turno do Governador 2022. Fonte: TSE.</span></span> <span class="sa" id="s2-abstencao"></span></th>
        <th style="min-width:88px" onclick="srt(2,'el_fem')"><span class="tt">Feminino<span class="tt-icon">?</span><span class="tt-box">% de eleitoras do sexo feminino no cadastro eleitoral — TSE 2022.</span></span> <span class="sa" id="s2-el_fem"></span></th>
        <th style="min-width:90px" onclick="srt(2,'el_jov')"><span class="tt">Jovens 16-24<span class="tt-icon">?</span><span class="tt-box">% do eleitorado com 16 a 24 anos — TSE 2022.</span></span> <span class="sa" id="s2-el_jov"></span></th>
        <th style="min-width:90px" onclick="srt(2,'el_ido')"><span class="tt">Idosos 60+<span class="tt-icon">?</span><span class="tt-box">% do eleitorado com 60 anos ou mais — TSE 2022.</span></span> <span class="sa" id="s2-el_ido"></span></th>
        <th style="min-width:100px" onclick="srt(2,'el_super')"><span class="tt">Superior<span class="tt-icon">?</span><span class="tt-box">% de eleitores com ensino superior completo declarado no cadastro eleitoral — TSE 2022. Inclui pós-graduação.</span></span> <span class="sa" id="s2-el_super"></span></th>
        <th style="min-width:100px" onclick="srt(2,'el_sem_fund')"><span class="tt">Sem fund.<span class="tt-icon">?</span><span class="tt-box">% de eleitores sem ensino fundamental completo — analfabetos e que apenas lêem e escrevem. TSE 2022.</span></span> <span class="sa" id="s2-el_sem_fund"></span></th>
        <th onclick="srt(2,'gap_jov')"><span class="tt">Gap jovens<span class="tt-icon">?</span><span class="tt-box">Diferença pp: % jovens 16-24 no eleitorado (TSE) menos % jovens 16-24 na população (PDAD). Positivo = jovens mais presentes na urna que na população.</span></span> <span class="sa" id="s2-gap_jov"></span></th>
        <th onclick="srt(2,'gap_ido')"><span class="tt">Gap idosos<span class="tt-icon">?</span><span class="tt-box">Diferença pp: % idosos 60+ no eleitorado (TSE) menos % idosos 60+ na população (PDAD). Positivo = idosos sobre-representados nas urnas.</span></span> <span class="sa" id="s2-gap_ido"></span></th>
        <th style="min-width:110px" onclick="srt(2,'gap')"><span class="tt">Gap escolaridade<span class="tt-icon">?</span><span class="tt-box">Diferença em pp: % eleitores com superior (TSE) menos % moradores 16+ com superior (PDAD). Bases comparáveis — ambas usam 16+ e incluem incompleto + completo. Positivo = eleitorado mais escolarizado que a população adulta.</span></span> <span class="sa" id="s2-gap"></span></th>
      </tr></thead><tbody id="tb2"></tbody></table></div>
    </div>

    <!-- O VOTO -->
    <div class="sec" id="s-campo">
      <div class="sec-head">
        <div class="sec-kicker" style="color:#185FA5">Contexto</div>
        <div class="sec-titulo">Campo político <span style="font-size:13px;color:var(--muted);font-weight:400">· TSE 2022</span></div>
        <div class="sec-lead">O DF não vota em bloco. Cada região tem uma composição ideológica própria — e ela muda conforme o cargo. Os dados de 2022 mostram a distribuição real de votos entre campo progressista, moderado e liberal/conservador em cada território.</div>
      </div>
      <div class="achado" style="margin:10px 22px 0">
        <div class="achado-lbl">Como ler esta tabela</div>
        <div class="achado-txt">
          <strong>Moderado / Progressista / Liberal-Cons. / Outros</strong>: % dos votos válidos do cargo na RA capturados por cada campo (domínio).
          <strong>Em verde/vermelho, entre parênteses</strong>: sobre/sub-índice — quanto a RA entrega ao campo <em>acima</em> ou <em>abaixo</em> do esperado pelo seu tamanho. Exemplo: <strong>+27%</strong> significa que a RA dá 27% mais voto àquele campo do que daria se a votação fosse proporcional ao seu eleitorado; <strong>−27%</strong>, o oposto.
          <strong>Margem</strong>: diferença em pontos percentuais entre o 1º e o 2º colocado do cargo na RA. Margem pequena = RA disputada (a eleição vira lá). Margem grande = RA cativa.
        </div>
      </div>
      <div class="cargo-bar"><span class="cargo-lbl">Cargo</span>
        <button class="cargo-btn" data-cargo="GOVERNADOR" onclick="setCargo('GOVERNADOR',this)">Governador</button>
        <button class="cargo-btn" data-cargo="SENADOR" onclick="setCargo('SENADOR',this)">Senador</button>
        <button class="cargo-btn on" data-cargo="DEPUTADO_FEDERAL" onclick="setCargo('DEPUTADO_FEDERAL',this)">Dep. Federal</button>
        <button class="cargo-btn" data-cargo="DEPUTADO_DISTRITAL" onclick="setCargo('DEPUTADO_DISTRITAL',this)">Dep. Distrital</button>
      </div>
      <div id="vol3" style="padding:14px 22px;border-bottom:0.5px solid var(--bd);background:var(--bg);flex-shrink:0">
        <div style="font-size:9px;letter-spacing:1.5px;text-transform:uppercase;color:var(--muted);margin-bottom:6px" id="vol3-label">Composição do DF</div>
        <div id="vol3-bar" style="display:flex;height:22px;border-radius:5px;overflow:hidden;gap:2px"></div>
        <div id="vol3-legend" style="display:flex;gap:16px;margin-top:7px"></div>
      </div>
      <div class="tablewrap"><table><thead><tr>
        <th style="min-width:200px" onclick="srt(3,'nome')">Região <span class="sa" id="s3-nome"></span><input class="th-filter" id="fi3" placeholder="filtrar..." oninput="filtrar(3)" onclick="event.stopPropagation()"></th>
        <th style="min-width:130px" onclick="srt(3,'moderado')"><span class="tt">Moderado<span class="tt-icon">?</span><span class="tt-box">% do voto do cargo capturado pelo campo moderado naquela RA. Em verde/vermelho: performance em relação ao tamanho da RA — entrega votos acima ou abaixo do esperado.</span></span> <span class="sa" id="s3-moderado">&#9660;</span></th>
        <th style="min-width:130px" onclick="srt(3,'progressista')"><span class="tt">Progressista<span class="tt-icon">?</span><span class="tt-box">% do voto do cargo capturado pelo campo progressista naquela RA. Em verde/vermelho: performance em relação ao tamanho da RA — entrega votos acima ou abaixo do esperado.</span></span> <span class="sa" id="s3-progressista"></span></th>
        <th style="min-width:140px" onclick="srt(3,'liberal_conservador')"><span class="tt">Liberal/Cons.<span class="tt-icon">?</span><span class="tt-box">% do voto do cargo capturado pelo campo liberal/conservador naquela RA. Em verde/vermelho: performance em relação ao tamanho da RA — entrega votos acima ou abaixo do esperado.</span></span> <span class="sa" id="s3-liberal_conservador"></span></th>
        <th style="min-width:80px" onclick="srt(3,'outros')">Outros <span class="sa" id="s3-outros"></span></th>
        <th style="min-width:90px" onclick="srt(3,'margem_pp')"><span class="tt">Margem<span class="tt-icon">?</span><span class="tt-box">Diferença em pontos percentuais entre o 1º e o 2º colocado do cargo na RA. Margem pequena = RA disputada (a eleição vira lá). Margem grande = RA cativa.</span></span> <span class="sa" id="s3-margem_pp"></span></th>
      </tr></thead><tbody id="tb3"></tbody></table></div>
    </div>

    <!-- O CANDIDATO -->
    <div class="sec" id="s-candidato">
      <div class="sec-head">
        <div class="sec-kicker" style="color:var(--muted)">Contexto</div>
        <div class="sec-titulo">Candidatos <span style="font-size:13px;color:var(--muted);font-weight:400">· TSE 2022</span></div>
        <div class="sec-lead">Fotografia eleitoral de 2022: todos os candidatos que disputaram no DF, com os votos recebidos em cada região. Esta seção é descritiva — para a leitura estratégica (Performance, Status, zonas), ver <em>Estratégia</em>.</div>
      </div>
      <div class="achado" style="margin:10px 22px 0">
        <div class="achado-lbl">Como ler esta tabela</div>
        <div class="achado-txt">
          <strong>Votos 2022</strong>: total de votos recebidos na região.
          <strong>% dos votos</strong>: frequência relativa — que fração dos votos do candidato no DF veio desta RA. Soma 100% no total. Mostra de onde vieram os votos dele.
          <strong>% do campo</strong>: fatia do campo político que o candidato capturou na RA.
          <strong>% do cargo</strong>: penetração no total de votos válidos do cargo naquela RA.
        </div>
      </div>
      <div class="cand-search-bar">
        <input class="cand-search-input" id="cand-search" placeholder="Buscar por nome ou partido..." oninput="candFiltrar()" style="margin-left:0">
        <button id="cf-cargo-all" class="cf-btn on" data-cargo="all" onclick="candSetCargo(this)">Todos</button>
        <button id="cf-dd" class="cf-btn" data-cargo="DEPUTADO_DISTRITAL" onclick="candSetCargo(this)">Distrital</button>
        <button id="cf-df" class="cf-btn" data-cargo="DEPUTADO_FEDERAL" onclick="candSetCargo(this)">Federal</button>
        <button id="cf-sen" class="cf-btn" data-cargo="SENADOR" onclick="candSetCargo(this)">Senador</button>
        <button id="cf-gov" class="cf-btn" data-cargo="GOVERNADOR" onclick="candSetCargo(this)">Governador</button>
      </div>

      <div class="cand-body">
        <div class="cand-list" id="cand-list"></div>
        <div class="cand-detail" id="cand-detail">
          <div class="cand-empty" id="cand-empty">
            <div class="cand-empty-icon" style="font-size:22px;opacity:.25">◎</div>
            <div class="cand-empty-txt">Selecione um candidato para ver a análise por região</div>
          </div>
          <div id="cand-detail-content" style="display:none;flex-direction:column;flex:1;overflow:hidden">
            <div id="cand-ctx-line" style="padding:7px 14px;border-bottom:0.5px solid var(--bd);background:var(--s2);display:flex;align-items:center;gap:8px;flex-shrink:0;flex-wrap:wrap"></div>
            <div id="cand-tbl-scroll" style="overflow:auto;flex:1;max-height:100%">
              <table style="width:100%;border-collapse:separate;border-spacing:0">
                <thead><tr>
                  <th onclick="candSrt('nome')" style="font-size:10px;font-weight:700;color:var(--muted);letter-spacing:1px;text-transform:uppercase;padding:7px 10px;position:sticky;top:0;background:var(--s1);z-index:6;border-bottom:0.5px solid var(--bd2);text-align:left;left:0;min-width:230px;cursor:pointer;user-select:none">Região <span class="sa" id="cand-s-nome"></span><input class="th-filter" id="cand-filtro-ra" placeholder="filtrar..." oninput="candFiltrarRA()" onclick="event.stopPropagation()"></th>
                  <th onclick="candSrt('v')" style="font-size:10px;font-weight:700;color:var(--muted);letter-spacing:1px;text-transform:uppercase;padding:7px 10px;position:sticky;top:0;background:var(--s1);z-index:4;border-bottom:0.5px solid var(--bd2);text-align:left;min-width:90px;cursor:pointer;user-select:none">Votos 2022 <span class="sa" id="cand-s-v">▼</span></th>
                  <th onclick="candSrt('pe')" style="font-size:10px;font-weight:700;color:var(--muted);letter-spacing:1px;text-transform:uppercase;padding:7px 10px;position:sticky;top:0;background:var(--s1);z-index:4;border-bottom:0.5px solid var(--bd2);text-align:left;min-width:110px;cursor:pointer;user-select:none"><span class="tt">% dos votos<span class="tt-icon">?</span><span class="tt-box">Frequência relativa: que fração do total de votos que o candidato teve no DF veio desta RA. Soma 100% no total. Mostra de onde vieram os votos do candidato.</span></span> <span class="sa" id="cand-s-pe"></span></th>
                  <th onclick="candSrt('pp')" style="font-size:10px;font-weight:700;color:var(--muted);letter-spacing:1px;text-transform:uppercase;padding:7px 10px;position:sticky;top:0;background:var(--s1);z-index:4;border-bottom:0.5px solid var(--bd2);text-align:left;min-width:110px;cursor:pointer;user-select:none">% do campo <span class="sa" id="cand-s-pp"></span></th>
                  <th onclick="candSrt('pc')" style="font-size:10px;font-weight:700;color:var(--muted);letter-spacing:1px;text-transform:uppercase;padding:7px 10px;position:sticky;top:0;background:var(--s1);z-index:4;border-bottom:0.5px solid var(--bd2);text-align:left;min-width:90px;cursor:pointer;user-select:none">% do cargo <span class="sa" id="cand-s-pc"></span></th>
                </tr></thead>
                <tbody id="cand-tb"></tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ESTRATÉGIA — Performance × Campo (5 categorias estratégicas) — mesmo padrão do submenu Candidatos -->
    <div class="sec" id="s-estrategia">
      <div class="sec-head">
        <div class="sec-kicker" style="color:#185FA5">Contexto</div>
        <div class="sec-titulo">Estratégia <span style="font-size:13px;color:var(--muted);font-weight:400">· por candidato</span></div>
        <div class="sec-lead">Leitura estratégica de qualquer candidato cruzando sua <strong>Performance</strong> (relativo ao tamanho da RA) com a <strong>Força do campo</strong> dele naquela região (Progressista, Moderado ou Liberal/Conservador). Cada RA é classificada em uma de cinco zonas: Reduto consolidado, Voto pessoal, Esperado, Espaço a conquistar e Sem espaço pelo campo.</div>
      </div>
      <div class="achado" style="margin:10px 22px 0">
        <div class="achado-lbl">Como ler esta tabela</div>
        <div class="achado-txt">
          <strong>Performance</strong>: força do candidato na RA — quanto recebeu de voto comparado ao que seria esperado pelo tamanho do eleitorado da região.
          <strong>Força do campo</strong>: o quanto o campo político do candidato (progressista, moderado ou liberal/conservador) é forte naquela RA no mesmo cargo, na mesma escala da Performance.
          <strong>Status</strong>: cruzamento das duas em cinco zonas — <em>Reduto consolidado</em> (ambos fortes), <em>Voto pessoal</em> (só candidato forte), <em>Esperado</em> (candidato proporcional ao tamanho), <em>Espaço a conquistar</em> (campo dele forte mas candidato não chegou) e <em>Sem espaço pelo campo</em> (ambos fracos).
        </div>
      </div>
      <div class="cand-search-bar">
        <input class="cand-search-input" id="estr-search" placeholder="Buscar por nome ou partido..." oninput="estrFiltrar()" style="margin-left:0">
        <button id="estr-cf-all" class="cf-btn on" data-cargo="all" onclick="estrSetCargo(this)">Todos</button>
        <button class="cf-btn" data-cargo="DEPUTADO_DISTRITAL" onclick="estrSetCargo(this)">Distrital</button>
        <button class="cf-btn" data-cargo="DEPUTADO_FEDERAL" onclick="estrSetCargo(this)">Federal</button>
        <button class="cf-btn" data-cargo="SENADOR" onclick="estrSetCargo(this)">Senador</button>
        <button class="cf-btn" data-cargo="GOVERNADOR" onclick="estrSetCargo(this)">Governador</button>
      </div>

      <div class="cand-body">
        <div class="cand-list" id="estr-list"></div>
        <div class="cand-detail" id="estr-detail">
          <div class="cand-empty" id="estr-empty">
            <div class="cand-empty-icon" style="font-size:22px;opacity:.25">◎</div>
            <div class="cand-empty-txt">Selecione um candidato para ver a leitura estratégica por região</div>
          </div>
          <div id="estr-detail-content" style="display:none;flex-direction:column;flex:1;overflow:hidden">
            <div id="estr-ctx-line" style="padding:7px 14px;border-bottom:0.5px solid var(--bd);background:var(--s2);display:flex;align-items:center;gap:8px;flex-shrink:0;flex-wrap:wrap"></div>
            <div id="estr-tbl-scroll" style="overflow:auto;flex:1;max-height:100%">
              <table style="width:100%;border-collapse:separate;border-spacing:0">
                <thead><tr>
                  <th onclick="estrSrt('ra')" style="font-size:10px;font-weight:700;color:var(--muted);letter-spacing:1px;text-transform:uppercase;padding:7px 10px;position:sticky;top:0;background:var(--s1);z-index:6;border-bottom:0.5px solid var(--bd2);text-align:left;left:0;min-width:230px;cursor:pointer;user-select:none">Região <span class="sa" id="estr-s-ra"></span><input class="th-filter" id="estr-filtro-ra" placeholder="filtrar..." oninput="estrFiltrarRA()" onclick="event.stopPropagation()"></th>
                  <th onclick="estrSrt('aptos')" style="font-size:10px;font-weight:700;color:var(--muted);letter-spacing:1px;text-transform:uppercase;padding:7px 10px;position:sticky;top:0;background:var(--s1);z-index:4;border-bottom:0.5px solid var(--bd2);text-align:right;min-width:80px;cursor:pointer;user-select:none">Aptos <span class="sa" id="estr-s-aptos"></span></th>
                  <th onclick="estrSrt('votos')" style="font-size:10px;font-weight:700;color:var(--muted);letter-spacing:1px;text-transform:uppercase;padding:7px 10px;position:sticky;top:0;background:var(--s1);z-index:4;border-bottom:0.5px solid var(--bd2);text-align:right;min-width:120px;cursor:pointer;user-select:none"><span class="tt">Votos do candidato<span class="tt-icon">?</span><span class="tt-box">Total de votos que o candidato selecionado recebeu nessa RA em 2022. Não é o total de votos válidos da RA — é só a fatia que ficou com ele.</span></span> <span class="sa" id="estr-s-votos">▼</span></th>
                  <th onclick="estrSrt('pe')" style="font-size:10px;font-weight:700;color:var(--muted);letter-spacing:1px;text-transform:uppercase;padding:7px 10px;position:sticky;top:0;background:var(--s1);z-index:4;border-bottom:0.5px solid var(--bd2);text-align:right;min-width:110px;cursor:pointer;user-select:none"><span class="tt">% dos votos<span class="tt-icon">?</span><span class="tt-box">Frequência relativa: que fração do total de votos que o candidato teve no DF veio desta RA. Soma 100% no total. Mostra de onde vieram os votos do candidato.</span></span> <span class="sa" id="estr-s-pe"></span></th>
                  <th onclick="estrSrt('idxCand')" style="font-size:10px;font-weight:700;color:var(--muted);letter-spacing:1px;text-transform:uppercase;padding:7px 10px;position:sticky;top:0;background:var(--s1);z-index:4;border-bottom:0.5px solid var(--bd2);text-align:right;min-width:110px;cursor:pointer;user-select:none"><span class="tt">Performance<span class="tt-icon">?</span><span class="tt-box">Indicador de força do candidato na RA. Compara os votos que ele recebeu com os que seria esperado pelo tamanho da RA. +30%+ = Reduto; +15%–30% = Base forte; ±15% = Esperado; −15%–30% = Base fraca; ≤−30% = Ausência.</span></span> <span class="sa" id="estr-s-idxCand"></span></th>
                  <th onclick="estrSrt('idxCampo')" style="font-size:10px;font-weight:700;color:var(--muted);letter-spacing:1px;text-transform:uppercase;padding:7px 10px;position:sticky;top:0;background:var(--s1);z-index:4;border-bottom:0.5px solid var(--bd2);text-align:right;min-width:120px;cursor:pointer;user-select:none"><span class="tt">Força do campo<span class="tt-icon">?</span><span class="tt-box">Mesma escala da Performance, mas aplicada ao campo político do candidato (Progressista, Moderado ou Liberal/Conservador) na RA × cargo. Mostra se o campo dele é forte ou fraco naquela região, independente desse candidato específico.</span></span> <span class="sa" id="estr-s-idxCampo"></span></th>
                  <th onclick="estrSrt('cat')" style="font-size:10px;font-weight:700;color:var(--muted);letter-spacing:1px;text-transform:uppercase;padding:7px 10px;position:sticky;top:0;background:var(--s1);z-index:4;border-bottom:0.5px solid var(--bd2);text-align:left;min-width:230px;cursor:pointer;user-select:none"><span class="tt">Status<span class="tt-icon">?</span><span class="tt-box">Classificação da RA pelo cruzamento Performance (do candidato) × Força do campo. Cinco zonas estratégicas: Reduto consolidado (ambos fortes), Voto pessoal (só candidato forte), Esperado (proporcional), Espaço a conquistar (só campo forte) e Sem espaço pelo campo (ambos fracos).</span></span> <span class="sa" id="estr-s-cat"></span><select class="th-filter" id="estr-filtro-cat" onchange="estrFiltrarCat()" onclick="event.stopPropagation()"><option value="all">Todos</option><option value="compartilhado">Reduto consolidado</option><option value="pessoal">Voto pessoal</option><option value="esperado">Esperado</option><option value="conquistar">Espaço a conquistar</option><option value="sem_espaco">Sem espaço pelo campo</option></select></th>
                </tr></thead>
                <tbody id="estr-tb"></tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- PROJEÇÕES -->
    <div class="sec" id="s-projecoes">
      <div class="sec-head">
        <div class="sec-kicker" style="color:#B45309">Estratégia</div>
        <div class="sec-titulo">Projeções</div>
        <div class="sec-lead">Potencial de votos por região, com base em candidatos reais de 2022 ajustados pelo SPE. Escolha um candidato de referência e compare com até 3 outros.</div>
      </div>

      <div class="achado" style="border-color:#B45309;background:#FAEEDA">
        <div class="achado-lbl" style="color:#633806">Como usar</div>
        <div class="achado-txt" style="color:#412402">Escolha o cargo e o campo. As três colunas — Conservador, Moderado e Otimista — mostram 50%, 75% e 100% do desempenho de um candidato de referência em cada região, ajustado pelo SPE. Sem referência selecionada, o modelo usa a mediana dos eleitos do campo em 2022. Adicione candidatos reais para comparação direta.</div>
      </div>

      <div class="cargo-bar">
        <span class="cargo-lbl">Cargo</span>
        <button class="cargo-btn" data-val="GOVERNADOR" onclick="estCargoSel(this)">Governador</button>
        <button class="cargo-btn" data-val="SENADOR" onclick="estCargoSel(this)">Senador</button>
        <button class="cargo-btn on" data-val="DEPUTADO_FEDERAL" onclick="estCargoSel(this)">Dep. Federal</button>
        <button class="cargo-btn" data-val="DEPUTADO_DISTRITAL" onclick="estCargoSel(this)">Dep. Distrital</button>
      </div>

      <div class="chips-bar">
        <span class="cargo-lbl">Campo</span>
        <button class="cargo-btn campo-btn" data-val="progressista" onclick="estCampoSel(this)">Progressista</button>
        <button class="cargo-btn campo-btn on" data-val="moderado" onclick="estCampoSel(this)">Moderado</button>
        <button class="cargo-btn campo-btn" data-val="liberal_conservador" onclick="estCampoSel(this)">Liberal/Cons.</button>
        <span id="est-conf-badge" style="font-size:10px;padding:3px 8px;border-radius:10px;background:#EAF3DE;color:#27500A;display:none;margin-left:4px"></span>
      </div>

      <div class="chips-bar" style="flex-direction:column;align-items:flex-start;gap:6px;padding:10px 22px">
        <div style="font-size:9px;letter-spacing:1.5px;text-transform:uppercase;color:var(--muted);font-weight:500">Referência <span style="font-size:10px;text-transform:none;letter-spacing:0;font-weight:400;color:var(--muted)">— base do cálculo · obrigatória para majoritário</span></div>
        <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap">
          <div id="est-ref-chip" style="display:none;align-items:center;gap:6px;padding:4px 8px 4px 10px;border-radius:20px;border:0.5px solid #0F6E56;background:var(--s1);font-size:12px">
            <div style="width:8px;height:8px;border-radius:50%;background:#0F6E56;flex-shrink:0"></div>
            <span id="est-ref-nome" style="font-weight:500"></span>
            <span id="est-ref-sub" style="font-size:10px;color:var(--muted)"></span>
            <span onclick="estRefClear()" style="font-size:12px;color:var(--muted);cursor:pointer;margin-left:2px">×</span>
          </div>
          <div style="position:relative">
            <input id="est-ref-input" class="chip-input" placeholder="Buscar candidato de referência..." style="width:280px" oninput="estRefBuscar(this.value)">
            <div id="est-ref-results" style="display:none;position:absolute;top:34px;left:0;width:320px;background:var(--s1);border:0.5px solid var(--bd2);border-radius:8px;z-index:20;max-height:200px;overflow-y:auto;box-shadow:0 4px 12px rgba(0,0,0,.1)"></div>
          </div>
          <span id="est-ref-fallback" style="font-size:11px;color:var(--muted);font-style:italic">sem referência — usando mediana dos eleitos</span>
        </div>
      </div>

      <div class="chips-bar" style="gap:8px">
        <span class="cargo-lbl">Comparar com</span>
        <div id="est-chips" style="display:flex;gap:6px;flex-wrap:wrap;align-items:center"></div>
        <div style="position:relative">
          <button id="est-add-btn" onclick="estToggleAdd(event)" class="cargo-btn">+ candidato</button>
          <div id="est-add-panel" style="display:none;position:absolute;top:32px;left:0;z-index:30;background:var(--s1);border:0.5px solid var(--bd2);border-radius:8px;padding:8px;width:300px;box-shadow:0 4px 16px rgba(0,0,0,.12)">
            <input id="est-search" class="chip-input" placeholder="Buscar candidato..." style="width:100%;box-sizing:border-box;margin-bottom:6px" oninput="estSearch(this.value)">
            <div id="est-search-res" style="max-height:200px;overflow-y:auto"></div>
          </div>
        </div>
      </div>

      <div id="est-meta-bar" style="padding:8px 22px;border-bottom:0.5px solid var(--bd);background:var(--bg);display:flex;align-items:center;gap:10px;flex-shrink:0">
        <span style="font-size:11px;color:var(--muted)">Meta mínima para eleição:</span>
        <span id="est-meta-val" style="font-size:14px;font-weight:500;color:#085041"></span>
        <span id="est-meta-ref" style="font-size:11px;color:var(--muted)"></span>
      </div>

      <div class="tablewrap">
        <table>
          <thead><tr id="est-thead">
            <th style="min-width:150px" onclick="estSortBy('nome')">Região <span class="sa" id="est-s-nome"></span></th>
            <th style="min-width:70px" onclick="estSortBy('spe')">SPE <span class="sa" id="est-s-spe">▼</span></th>
            <th style="min-width:90px" onclick="estSortBy('cons')">Conservador <span class="sa" id="est-s-cons"></span><br><span style="font-weight:400;font-size:8px;color:var(--muted);text-transform:none;letter-spacing:0">50% da ref.</span></th>
            <th style="min-width:90px" onclick="estSortBy('med')">Moderado <span class="sa" id="est-s-med"></span><br><span style="font-weight:400;font-size:8px;color:var(--muted);text-transform:none;letter-spacing:0">75% da ref.</span></th>
            <th style="min-width:90px" onclick="estSortBy('otim')">Otimista <span class="sa" id="est-s-otim"></span><br><span style="font-weight:400;font-size:8px;color:var(--muted);text-transform:none;letter-spacing:0">100% da ref.</span></th>
          </tr></thead>
          <tbody id="est-tbody"></tbody>
        </table>
      </div>
      <div id="est-nota" style="display:none;padding:8px 22px 10px;font-size:11px;color:var(--muted);font-style:italic"></div>
    </div>

    <!-- DIAGNÓSTICO -->
    <div class="sec" id="s-diagnostico">
      <div class="sec-head">
        <div class="sec-kicker" style="color:#B45309">Estratégia</div>
        <div class="sec-titulo">Diagnóstico</div>
        <div class="sec-lead">Wizard que monta um relatório estratégico personalizado para um candidato em três passos: identificação do tipo, análise das cinco zonas territoriais e geração do documento em Word editável.</div>
      </div>

      <!-- Stepper -->
      <div class="diag-stepper">
        <div class="diag-step on" id="diag-st-1"><div class="diag-step-num">1</div><div class="diag-step-lbl">Quem é</div></div>
        <div class="diag-step-line"></div>
        <div class="diag-step" id="diag-st-2"><div class="diag-step-num">2</div><div class="diag-step-lbl">Configurar e gerar</div></div>
      </div>

      <!-- PASSO 1 — Tipo de candidato -->
      <div class="diag-pg active" id="diag-p1">
        <div style="max-width:1100px;margin:0 auto 14px;text-align:center">
          <div style="font-size:9px;letter-spacing:2px;text-transform:uppercase;color:var(--muted);margin-bottom:4px">Passo 1 de 3</div>
          <div style="font-size:18px;font-weight:500">Que tipo de candidato você vai diagnosticar?</div>
          <div style="font-size:12px;color:var(--muted);margin-top:6px;max-width:620px;margin-left:auto;margin-right:auto">A análise muda conforme o ponto de partida do candidato — base herdada, estreia absoluta, migração de cargo ou mandato vigente.</div>
        </div>
        <div class="diag-types">
          <div class="diag-type-card disabled">
            <div class="diag-type-tag">Em breve</div>
            <div class="diag-type-num">TIPO 01</div>
            <div class="diag-type-title">Estreante com referência</div>
            <div class="diag-type-desc">Candidato novo no cargo, mas com base eleitoral herdada de um aliado, padrinho político ou grupo organizado.</div>
          </div>
          <div class="diag-type-card disabled">
            <div class="diag-type-tag">Em breve</div>
            <div class="diag-type-num">TIPO 02</div>
            <div class="diag-type-title">Estreante sem referência</div>
            <div class="diag-type-desc">Primeira candidatura, sem base eleitoral pregressa nem figura de referência territorial direta.</div>
          </div>
          <div class="diag-type-card available" id="diag-card-reposicionamento" onclick="diagSelTipo('reposicionamento')">
            <div class="diag-type-tag avail">Disponível</div>
            <div class="diag-type-num">TIPO 03</div>
            <div class="diag-type-title">Reposicionamento</div>
            <div class="diag-type-desc">Candidato com mandato vigente em outro cargo, migrando para nova disputa em 2026 (ex.: Distrital → Federal).</div>
          </div>
          <div class="diag-type-card disabled">
            <div class="diag-type-tag">Em breve</div>
            <div class="diag-type-num">TIPO 04</div>
            <div class="diag-type-title">Reeleição</div>
            <div class="diag-type-desc">Mandato vigente buscando renovação no mesmo cargo, com base territorial consolidada nas eleições anteriores.</div>
          </div>
        </div>
        <div class="diag-actions">
          <span style="font-size:11px;color:var(--muted)" id="diag-p1-hint">Selecione um tipo disponível para continuar.</span>
          <button class="diag-btn primary" id="diag-btn-next1" onclick="diagAvancar(2)" disabled>Continuar →</button>
        </div>
      </div>

      <!-- PASSO 2 — Análise -->
      <div class="diag-pg" id="diag-p2">
        <!-- Configurador -->
        <div class="diag-config">
          <div class="diag-config-row">
            <span class="diag-config-lbl">Candidato origem (2022)</span>
            <div id="diag-orig-chip" style="display:none">
              <div style="width:8px;height:8px;border-radius:50%;background:#B45309;flex-shrink:0"></div>
              <span id="diag-orig-nome" style="font-weight:500"></span>
              <span id="diag-orig-sub" style="font-size:10px;color:var(--muted)"></span>
              <span onclick="diagOrigClear()" style="font-size:12px;color:var(--muted);cursor:pointer;margin-left:2px">×</span>
            </div>
            <div style="position:relative" id="diag-orig-wrap">
              <input id="diag-orig-input" class="chip-input" placeholder="Buscar candidato 2022..." style="width:280px" oninput="diagOrigBuscar(this.value)">
              <div id="diag-orig-results" style="display:none;position:absolute;top:34px;left:0;width:360px;background:var(--s1);border:0.5px solid var(--bd2);border-radius:8px;z-index:30;max-height:240px;overflow-y:auto;box-shadow:0 4px 12px rgba(0,0,0,.1)"></div>
            </div>
          </div>
          <div class="diag-config-row">
            <span class="diag-config-lbl">Cargo destino (2026)</span>
            <div id="diag-dest-buttons" style="display:flex;gap:6px;flex-wrap:wrap">
              <button class="cargo-btn" data-val="GOVERNADOR" onclick="diagDestSel(this)">Governador</button>
              <button class="cargo-btn" data-val="SENADOR" onclick="diagDestSel(this)">Senador</button>
              <button class="cargo-btn" data-val="DEPUTADO_FEDERAL" onclick="diagDestSel(this)">Dep. Federal</button>
              <button class="cargo-btn" data-val="DEPUTADO_DISTRITAL" onclick="diagDestSel(this)">Dep. Distrital</button>
            </div>
          </div>
          <div class="diag-config-row">
            <span class="diag-config-lbl">Referência destino (2022)</span>
            <div id="diag-ref-chip" style="display:none">
              <div style="width:8px;height:8px;border-radius:50%;background:#0F6E56;flex-shrink:0"></div>
              <span id="diag-ref-nome" style="font-weight:500"></span>
              <span id="diag-ref-sub" style="font-size:10px;color:var(--muted)"></span>
              <span onclick="diagRefClear()" style="font-size:12px;color:var(--muted);cursor:pointer;margin-left:2px">×</span>
            </div>
            <div style="position:relative" id="diag-ref-wrap">
              <input id="diag-ref-input" class="chip-input" placeholder="Selecione cargo destino primeiro..." style="width:280px" disabled oninput="diagRefBuscar(this.value)">
              <div id="diag-ref-results" style="display:none;position:absolute;top:34px;left:0;width:360px;background:var(--s1);border:0.5px solid var(--bd2);border-radius:8px;z-index:30;max-height:240px;overflow-y:auto;box-shadow:0 4px 12px rgba(0,0,0,.1)"></div>
            </div>
          </div>
        </div>

        <!-- Painel de geração (aparece quando os 3 itens estão setados) -->
        <div id="diag-painel" style="max-width:640px;margin:30px auto;padding:28px 32px;background:var(--s1);border:0.5px solid var(--bd2);border-radius:10px;text-align:center;display:none">
          <div style="font-size:9px;letter-spacing:2px;text-transform:uppercase;color:var(--amber);font-weight:500;margin-bottom:8px">Configuração pronta</div>
          <div id="diag-cfg-summary" style="font-size:12.5px;color:var(--txt);line-height:1.7;text-align:left;background:var(--s2);padding:14px 18px;border-radius:8px;margin-bottom:18px"></div>
          <button class="diag-btn primary" id="diag-btn-gerar" onclick="diagGerarRelatorio()" style="font-size:14px;padding:11px 22px">📄 Gerar e baixar relatório (.docx)</button>
          <div id="diag-gerar-status" style="font-size:11px;color:var(--muted);margin-top:10px;min-height:16px"></div>
          <div style="font-size:10px;color:var(--muted);margin-top:8px;font-style:italic">Word autocontido · imagens embarcadas · 5–10 segundos</div>
        </div>

        <!-- Placeholder enquanto a configuração não está completa -->
        <div id="diag-empty" style="text-align:center;padding:50px 22px;color:var(--muted);font-size:12.5px;font-style:italic">Selecione candidato origem, cargo destino e referência para liberar a geração do relatório.</div>

        <div class="diag-actions">
          <button class="diag-btn" onclick="diagAvancar(1)">← Voltar</button>
          <span id="diag-tipo-lbl" style="font-size:11px;color:var(--muted)">—</span>
          <span style="width:60px"></span>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- MODAL METODOLOGIA -->
<div id="met-modal" class="met-modal">
  <div class="met-header">
    <span style="font-size:13px;font-weight:500">Metodologia</span>
    <div class="met-nav">
      <button class="met-nav-btn" onclick="metNav('intro')">Visão geral</button>
      <button class="met-nav-btn" onclick="metNav('base')">Bases de dados</button>
      <button class="met-nav-btn" onclick="metNav('foto')">Candidatos</button>
      <button class="met-nav-btn" onclick="metNav('proj')">Projeções</button>
      <button class="met-nav-btn" onclick="metNav('spe')">SPE</button>
    </div>
    <button onclick="fecharMet()" style="background:transparent;border:none;font-size:18px;cursor:pointer;color:var(--muted);padding:4px 8px">×</button>
  </div>
  <div class="met-body">

    <!-- INTRO -->
    <div class="met-section" id="met-intro">
      <div class="met-kicker">Visão geral</div>
      <div class="met-titulo">Sobre o Estrategos</div>
      <div class="met-txt">
        <p>O SPE — Score Político-Estratégico — é um índice composto que mede o potencial de cada Região Administrativa do DF para uma candidatura específica. Ele responde a uma pergunta prática: <strong>onde vale mais a pena concentrar esforço de campanha?</strong></p>
        <p>O score combina quatro dimensões independentes — Afinidade, Conversão, Massa e Logística — ponderadas de forma diferente conforme o cargo disputado. O resultado é um número de 0 a 10 por região, que permite comparar territórios e priorizar a alocação de recursos.</p>
        <p>O SPE não prevê resultados eleitorais. Ele organiza o território a partir de dados históricos e estruturais para apoiar decisões táticas de campanha. A leitura correta é relativa: uma região com SPE 8 não garante vitória, mas indica que o retorno esperado por esforço investido é maior do que numa região com SPE 3.</p>
      </div>
    </div>

    <!-- BASES -->
    <div class="met-section" id="met-base">
      <div class="met-kicker">Bases de dados</div>
      <div class="met-titulo">Fontes e cobertura</div>
      <div class="met-txt">
        <p><strong>PDAD 2021 — Pesquisa Distrital por Amostra de Domicílios</strong><br>
        Conduzida pelo IPEDF (Instituto de Pesquisa e Estatística do Distrito Federal), a PDAD 2021 cobriu cerca de 83 mil moradores em ~30 mil domicílios amostrados nas 33 Regiões Administrativas do DF entre maio e dezembro de 2021. É a principal fonte de dados socioeconômicos do projeto: renda per capita, composição de classe, escolaridade, ocupação, origem migratória, acesso a benefícios sociais e cobertura de plano de saúde. Os dados são representativos por RA.</p>
        <p><strong>TSE 2022 — Cadastro Eleitoral e Resultados</strong><br>
        O Tribunal Superior Eleitoral disponibiliza o cadastro de eleitores aptos por seção eleitoral, com perfil de faixa etária, gênero e escolaridade. Cada seção é atribuída à sua Região Administrativa pelas coordenadas geográficas do local de votação cruzadas com os polígonos oficiais das RAs (point-in-polygon), o que permite agregar o perfil por RA sem dependência da zona eleitoral. O segundo conjunto é o arquivo de votação por seção do 1º turno de 2022, que dá os votos por candidato em cada RA pela mesma atribuição.</p>
      </div>
    </div>

    <!-- CANDIDATOS -->
    <div class="met-section" id="met-foto">
      <div class="met-kicker">Candidatos 2022</div>
      <div class="met-titulo">Fotografia eleitoral</div>
      <div class="met-txt">
        <p>A seção Candidatos apresenta todos os candidatos que disputaram eleições no DF em 2022 (1º turno), com os votos recebidos em cada Região Administrativa. Os dados são extraídos diretamente do arquivo de votação por seção eleitoral do TSE, agregados por RA a partir do mapeamento de locais de votação.</p>
        <p><strong>% do campo</strong> mede a fatia do campo político que aquele candidato capturou naquela RA. Por exemplo, 40% significa que 4 em cada 10 votos do campo político foram para aquele candidato naquele território. É a medida mais relevante para análise estratégica: indica a penetração relativa dentro do universo de eleitores potencialmente receptivos.</p>
        <p><strong>% do cargo</strong> mede a participação no total de votos válidos daquele cargo naquela RA. É útil para comparar candidatos de campos diferentes numa mesma métrica.</p>
        <p><strong>Base Forte / Base Fraca</strong> são classificações relativas ao desempenho médio do próprio candidato. Base Forte significa desempenho acima de 130% da mediana do candidato; Base Fraca significa abaixo de 70%. A comparação é interna ao candidato — não compara com outros.</p>
        <p>Votos de legenda (número de 1 ou 2 dígitos em cargos proporcionais) são excluídos da lista. Candidatos com menos de 50 votos no total também são excluídos por irrelevância estatística.</p>
      </div>
    </div>

    <!-- PROJEÇÕES -->
    <div class="met-section" id="met-proj">
      <div class="met-kicker">Projeções</div>
      <div class="met-titulo">Como os cenários são calculados</div>
      <div class="met-txt">
        <p>A seção Projeções estima o potencial de votos por região para uma candidatura em 2026. O modelo parte de um candidato de referência de 2022 — ou da mediana dos eleitos do campo, quando nenhum candidato específico é selecionado — e aplica o SPE de cada RA como fator de ajuste.</p>
        <p><strong>Fórmula base</strong><br>
        Votos projetados na RA = votos de referência na RA × fator de cenário × (1 + (SPE − 5) / 20)</p>
        <p>O ajuste pelo SPE significa que regiões com SPE 10 recebem +25% sobre a referência, e regiões com SPE 0 recebem −25%. Regiões com SPE 5 (mediana) ficam sem ajuste.</p>
        <p><strong>Três cenários</strong><br>
        Conservador (50% da referência), Moderado (75%) e Otimista (100%). Os cenários representam diferentes hipóteses sobre a capacidade de o candidato replicar ou superar o desempenho histórico. O cenário Otimista assume que o candidato terá desempenho equivalente à referência ajustada pelo SPE — não que vai superar o melhor resultado histórico.</p>
        <p><strong>Limitações</strong><br>
        As projeções são estimativas baseadas em padrões históricos. Não incorporam variáveis como mudanças no eleitorado, coligações, eventos de campanha ou alterações no cenário político. Devem ser interpretadas como balizas de planejamento, não como previsões.</p>
      </div>
    </div>

    <!-- SPE -->
    <div class="met-section" id="met-spe">
      <div class="met-kicker">SPE — Score Político-Estratégico</div>
      <div class="met-titulo">As quatro dimensões</div>
      <div class="met-txt">

        <p style="font-size:13px;color:var(--muted);border-left:3px solid var(--amber);padding-left:12px;margin-bottom:20px">O SPE é o índice central do modelo. Ele sintetiza quatro dimensões em um único score de 0 a 10, ponderadas conforme o cargo. Cada dimensão mede um aspecto distinto do potencial estratégico de uma região para uma candidatura específica.</p>

        <p><strong>1. Afinidade — o quanto o campo já está presente</strong><br>
        Mede o alinhamento histórico da RA com o campo político do candidato, naquele cargo específico. É calculada como um blend de dois componentes: 65% do voto real que o campo obteve naquela RA×cargo em 2022, e 35% do perfil socioeconômico da PDAD (renda, escolaridade, funcionalismo, dependência de benefícios) que estruturalmente predispõe o eleitorado a determinado campo.<br>
        <em>Interpretação: afinidade alta significa que o campo já tem raízes ali — o eleitor já votou no campo antes. Não garante o voto no candidato específico, mas reduz o custo de persuasão.</em></p>

        <p><strong>2. Conversão — o espaço ainda disponível</strong><br>
        Mede o potencial de conquistar eleitores que ainda não votam no campo. É calculada como o produto entre o volume de votos que o campo ainda não capturou naquela RA×cargo e a predisposição estrutural da PDAD. Regiões onde o campo poderia ter mais votos do que historicamente obteve têm conversão alta.<br>
        <em>Interpretação: conversão alta significa oportunidade real de crescimento — o eleitor tem perfil favorável mas ainda não foi convertido. Territórios de Conversão alta são os campos prioritários para investimento em mensagem e mobilização.</em></p>

        <p><strong>3. Massa — o volume disponível</strong><br>
        Mede o volume de votos válidos daquele cargo naquela RA, corrigido por um proxy de abstenção que considera a proporção de jovens de 16 a 24 anos e de domicílios de classe D/E (grupos com maior tendência de abstenção). Quanto maior o volume de votos realizados, maior a Massa.<br>
        <em>Interpretação: massa alta significa que a região vale em volume absoluto — mesmo uma penetração modesta gera muitos votos. Ignorar regiões de alta Massa é abrir mão de votos que estão disponíveis.</em></p>

        <p><strong>4. Logística — a eficiência operacional</strong><br>
        Mede o custo relativo de campanha por voto. RAs menores, com eleitorado mais concentrado geograficamente, têm logística mais eficiente. Calculada como o logaritmo do inverso do número de eleitores aptos — escala log para evitar que a diferença entre a maior (Ceilândia, 302k eleitores) e a menor (Varjão, 4k) seja desproporcional.<br>
        <em>Interpretação: logística alta não significa que a região é prioritária, mas que o custo por voto é menor. Para candidaturas com orçamento limitado, regiões de alta Logística oferecem o melhor retorno por real investido.</em></p>

        <div style="background:var(--s2);border-radius:10px;padding:16px 18px;margin-top:20px">
          <div style="font-size:10px;letter-spacing:1.5px;text-transform:uppercase;color:var(--muted);margin-bottom:12px">Pesos por cargo</div>
          <table style="width:100%;font-size:12px;border-collapse:collapse">
            <thead>
              <tr style="color:var(--muted);font-size:11px">
                <th style="text-align:left;padding:5px 10px;font-weight:400">Cargo</th>
                <th style="text-align:center;padding:5px 10px;font-weight:400;color:#534AB7">Afinidade</th>
                <th style="text-align:center;padding:5px 10px;font-weight:400;color:#185FA5">Conversão</th>
                <th style="text-align:center;padding:5px 10px;font-weight:400;color:#0F6E56">Massa</th>
                <th style="text-align:center;padding:5px 10px;font-weight:400;color:#854F0B">Logística</th>
                <th style="text-align:left;padding:5px 10px;font-weight:400">Lógica</th>
              </tr>
            </thead>
            <tbody>
              <tr style="border-top:0.5px solid var(--bd)">
                <td style="padding:7px 10px;font-weight:500">Governador</td>
                <td style="text-align:center;padding:7px 10px;color:#534AB7">25%</td>
                <td style="text-align:center;padding:7px 10px;color:#185FA5">35%</td>
                <td style="text-align:center;padding:7px 10px;color:#0F6E56">30%</td>
                <td style="text-align:center;padding:7px 10px;color:#854F0B">10%</td>
                <td style="padding:7px 10px;color:var(--muted);font-size:11px">Cobertura ampla — conversão e volume são decisivos</td>
              </tr>
              <tr style="border-top:0.5px solid var(--bd)">
                <td style="padding:7px 10px;font-weight:500">Senador</td>
                <td style="text-align:center;padding:7px 10px;color:#534AB7">20%</td>
                <td style="text-align:center;padding:7px 10px;color:#185FA5">40%</td>
                <td style="text-align:center;padding:7px 10px;color:#0F6E56">35%</td>
                <td style="text-align:center;padding:7px 10px;color:#854F0B">5%</td>
                <td style="padding:7px 10px;color:var(--muted);font-size:11px">Majoritário com 2 vagas — conversão crítica, nenhuma RA dispensável</td>
              </tr>
              <tr style="border-top:0.5px solid var(--bd)">
                <td style="padding:7px 10px;font-weight:500">Dep. Federal</td>
                <td style="text-align:center;padding:7px 10px;color:#534AB7">30%</td>
                <td style="text-align:center;padding:7px 10px;color:#185FA5">25%</td>
                <td style="text-align:center;padding:7px 10px;color:#0F6E56">35%</td>
                <td style="text-align:center;padding:7px 10px;color:#854F0B">10%</td>
                <td style="padding:7px 10px;color:var(--muted);font-size:11px">Disputa DF todo — volume importa tanto quanto afinidade</td>
              </tr>
              <tr style="border-top:0.5px solid var(--bd)">
                <td style="padding:7px 10px;font-weight:500">Dep. Distrital</td>
                <td style="text-align:center;padding:7px 10px;color:#534AB7">35%</td>
                <td style="text-align:center;padding:7px 10px;color:#185FA5">20%</td>
                <td style="text-align:center;padding:7px 10px;color:#0F6E56">25%</td>
                <td style="text-align:center;padding:7px 10px;color:#854F0B">20%</td>
                <td style="padding:7px 10px;color:var(--muted);font-size:11px">Concentração local — afinidade e eficiência operacional são chave</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div style="margin-top:20px;padding:14px 16px;background:var(--s2);border-radius:10px;border-left:3px solid var(--bd2)">
          <div style="font-size:10px;letter-spacing:1.5px;text-transform:uppercase;color:var(--muted);margin-bottom:8px">Quadrantes estratégicos</div>
          <p style="font-size:12px;margin-bottom:8px">O badge exibido no painel da região combina SPE e Afinidade em quatro categorias de decisão:</p>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:11px">
            <div style="background:#FAEEDA;border-radius:8px;padding:9px 12px">
              <strong style="color:#633806">Prioridade</strong><br>
              <span style="color:#854F0B">SPE alto + Afinidade alta — investir agora</span>
            </div>
            <div style="background:#E6F1FB;border-radius:8px;padding:9px 12px">
              <strong style="color:#0C447C">Expandir</strong><br>
              <span style="color:#185FA5">SPE alto + Afinidade baixa — converter eleitores</span>
            </div>
            <div style="background:#E1F5EE;border-radius:8px;padding:9px 12px">
              <strong style="color:#085041">Consolidar</strong><br>
              <span style="color:#0F6E56">SPE médio + Afinidade alta — não perder terreno</span>
            </div>
            <div style="background:#F1EFE8;border-radius:8px;padding:9px 12px">
              <strong style="color:#444441">Não priorizar</strong><br>
              <span style="color:#5F5E5A">SPE baixo + Afinidade baixa — presença mínima</span>
            </div>
          </div>
        </div>

      </div>
    </div>

  </div>
</div>


<!-- MODAL COMPARAÇÃO CANDIDATOS -->
<div id="cmp-overlay" onclick="if(event.target===this){cmpFechar()}" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.45);z-index:100;align-items:center;justify-content:center;padding:20px;overflow-y:auto">
  <div style="background:var(--s1);border-radius:12px;width:min(1100px,95vw);max-height:90vh;display:flex;flex-direction:column;box-shadow:0 8px 32px rgba(0,0,0,.25)">
    <div style="display:flex;align-items:center;gap:10px;padding:14px 18px;border-bottom:0.5px solid var(--bd);flex-shrink:0">
      <span style="font-size:10px;letter-spacing:1.5px;text-transform:uppercase;color:var(--amber);font-weight:700;flex-shrink:0">Alianças políticas</span>
      <span style="color:var(--bd2);flex-shrink:0">|</span>
      <div style="display:flex;align-items:center;gap:8px;flex:1;flex-wrap:wrap">
        <div id="cmp-a-dot" style="width:10px;height:10px;border-radius:50%;flex-shrink:0"></div>
        <span id="cmp-a-nome" style="font-size:14px;font-weight:500"></span>
        <span id="cmp-a-badge" style="font-size:9px;padding:2px 7px;border-radius:10px"></span>
        <span id="cmp-a-sub" style="font-size:11px;color:var(--muted)"></span>
      </div>
      <button onclick="cmpFechar()" style="font-size:20px;line-height:1;background:none;border:none;cursor:pointer;color:var(--muted);padding:0 4px">×</button>
    </div>
    <div style="padding:10px 18px;border-bottom:0.5px solid var(--bd);display:flex;align-items:center;gap:10px;flex-wrap:wrap">
      <span style="font-size:12px;color:var(--muted);flex-shrink:0">Aliar com</span>
      <div style="position:relative;flex:1;min-width:200px;max-width:380px">
        <input id="cmp-b-search" placeholder="Buscar candidato (qualquer cargo)..." style="width:100%;box-sizing:border-box;padding:6px 10px;border:0.5px solid var(--bd2);border-radius:6px;font-size:12px;background:var(--s1);color:var(--txt);font-family:inherit" oninput="cmpBuscar(this.value)">
        <div id="cmp-b-results" style="display:none;position:absolute;top:34px;left:0;right:0;background:var(--s1);border:0.5px solid var(--bd2);border-radius:8px;z-index:10;max-height:200px;overflow-y:auto;box-shadow:0 4px 12px rgba(0,0,0,.12)"></div>
      </div>
      <div id="cmp-b-tag" style="display:none;align-items:center;gap:6px;cursor:pointer"></div>
    </div>
    <div id="cmp-pick-hint" style="text-align:center;padding:40px 20px;color:var(--muted);font-size:13px">Selecione um candidato para comparar</div>
    <div id="cmp-content" style="display:none;padding:0 18px 18px">
      <div id="cmp-corr" style="display:none"></div>
      <!-- Veredito curto baseado em cargo+campo+padrão -->
      <div id="cmp-veredito" style="font-size:12px;line-height:1.5;padding:10px 12px;background:var(--s2);border-radius:8px;margin-bottom:12px;border-left:3px solid var(--amber)"></div>
      <!-- 4 KPI cards de quadrantes -->
      <div id="cmp-quad-cards" style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:10px"></div>
      <div style="font-size:11px;color:var(--muted);background:var(--s2);padding:8px 12px;border-radius:6px;margin-bottom:14px;line-height:1.5">
        <strong style="color:var(--txt)">Como ler:</strong> a Performance é normalizada pelo tamanho do candidato e da RA — diz se a região entrega <em>acima</em> ou <em>abaixo</em> do esperado pela proporção. <strong>Não confundir com volume absoluto</strong>: candidatos com totais muito diferentes podem ter Performance oposta na mesma RA mesmo com volumes similares — ou volumes muito distintos com Performance parecida.
      </div>
      <!-- Tabela com coluna Padrão -->
      <div style="overflow-y:scroll;overflow-x:auto;max-height:60vh;border:0.5px solid var(--bd);border-radius:8px;margin-bottom:14px;scrollbar-gutter:stable"><table style="width:100%;border-collapse:separate;border-spacing:0;font-size:12px"><thead id="cmp-thead" style="position:sticky;top:0;z-index:4;background:var(--s1)"></thead><tbody id="cmp-tbody"></tbody></table></div>
    </div>
  </div>
</div>

<!-- Paper isolado pra impressão "só relatório" (Candidatos > Imprimir relatório) -->
<div id="rel-paper-iso" class="paper-wrap" style="display:none"></div>

<script>// __JS__</script>
</body></html>

"""

JS_CODE = """

// ── DADOS ────────────────────────────────────────────────────────────────────
// ════════════ LOGIN (decorativo) ════════════
// Para gerar/atualizar senhas: rode `python3 gerar_credencial.py`
// Credenciais carregadas de credenciais.json (não versionado).
// Para gerar/atualizar: rode `python3 gerar_credencial.py`
var ESTRATEGOS_USERS = __ESTRATEGOS_USERS__;
async function _estrHash(s){
  var enc = new TextEncoder().encode(s||"");
  var buf = await crypto.subtle.digest('SHA-256', enc);
  return Array.from(new Uint8Array(buf)).map(function(b){return b.toString(16).padStart(2,'0');}).join('');
}
async function _estrLogin(){
  var u = (document.getElementById('estr-login-user').value||'').toLowerCase().trim();
  var p = document.getElementById('estr-login-pwd').value||'';
  var msg = document.getElementById('estr-login-msg');
  msg.textContent = '';
  if(!u || !p){ msg.textContent = 'Preencha usuário e senha.'; return; }
  if(!ESTRATEGOS_USERS[u]){ msg.textContent = 'Usuário ou senha incorretos.'; return; }
  var h = await _estrHash(p);
  if(h !== ESTRATEGOS_USERS[u]){ msg.textContent = 'Usuário ou senha incorretos.'; return; }
  try { localStorage.setItem('estrAuth', JSON.stringify({user:u, t:Date.now()})); } catch(e){}
  document.getElementById('estr-login').style.display = 'none';
}
function _estrLogout(){
  try { localStorage.removeItem('estrAuth'); } catch(e){}
  location.reload();
}
// Check on load: se já logado, esconde overlay
(function(){
  try {
    var saved = JSON.parse(localStorage.getItem('estrAuth') || 'null');
    if(saved && saved.user && ESTRATEGOS_USERS[saved.user]){
      var el = document.getElementById('estr-login');
      if(el) el.style.display = 'none';
    }
  } catch(e){}
})();

var D=JSON.parse(atob("__DADOS_B64__"));
var PT=JSON.parse(atob("__PT_B64__"));
var PK=JSON.parse(atob("__PK_B64__"));
var pAt=null,pNome="",pCargo="DEPUTADO_DISTRITAL",pPerfil="moderado";
var cargoV="DEPUTADO_FEDERAL",raAt4=null;
var SC={1:"renda_pc",2:"el_aptos",3:"moderado",4:"spe"};
var SA={1:false,2:false,3:false,4:false};
var FQ={1:"",2:"",3:"",4:""};
var FM={1:"all",2:"all",3:"all",4:"all"};
var URAS=Object.keys(D).sort();
function f1(v){return v.toFixed(1).replace(".",",");}
function fp(v){return v.toFixed(1).replace(".",",")+"%";}

// ── PERSONAS ─────────────────────────────────────────────────────────────────
var PERS=[
  {id:"servidor",campo:"progressista",nome:"O Servidor Ilustrado",cargo:"Dep. Federal ou Dep. Distrital",
   frase:"Meu eleitor estudou, trabalha no governo e mora no Plano Piloto. Ele já vota comigo.",
   tags:["Base sólida","Teto baixo","Nicho qualificado"],
   stats:[{v:"63%",l:"ensino superior"},{v:"26%",l:"funcionalismo"},{v:"R$ 7.000",l:"renda per capita"},{v:"35%",l:"campo progr. 2022"}],
   desafio:"Seu campo raramente passa de 36% fora do Plano Piloto. Precisa converter eleitor de média renda.",
   cor:"#534AB7",bg:"#EEEDFE"},
  {id:"expansionista",campo:"progressista",nome:"O Expansionista",cargo:"Governador ou Senador",
   frase:"Eu sei que minha base não basta. Meu trabalho é convencer quem nunca votou no meu campo.",
   tags:["Alto risco","Alto potencial","Conversão central"],
   stats:[{v:"19%",l:"campo progr. no DF 2022"},{v:"1,9M",l:"eleitores a conquistar"},{v:"r=0,93",l:"escolaridade × progr."},{v:"48%",l:"moderado em Taguatinga"}],
   desafio:"Eleitor das satélites votou 47-56% no campo moderado. Precisa tirar votos de lá sem perder a base.",
   cor:"#534AB7",bg:"#EEEDFE"},
  {id:"gestor",campo:"moderado",nome:"O Gestor das Satélites",cargo:"Governador",
   frase:"Meu eleitor não quer ideologia. Ele quer asfalto, hospital e segurança.",
   tags:["Base volumosa","Alta fidelidade","Periferia"],
   stats:[{v:"56%",l:"campo mod. no Recanto 2022"},{v:"302k",l:"eleitores em Ceilândia"},{v:"R$ 1.200",l:"renda média"},{v:"20%",l:"benefício social"}],
   desafio:"Campo moderado dominou a periferia, mas perdeu para o liberal no total do DF.",
   cor:"#0F6E56",bg:"#E1F5EE"},
  {id:"territorial",campo:"moderado",nome:"O Deputado Territorial",cargo:"Dep. Distrital ou Dep. Federal",
   frase:"Não preciso ganhar o DF inteiro. Preciso ser o mais votado em 2 ou 3 regiões.",
   tags:["Profundidade local","2 a 3 RAs","Enraizado"],
   stats:[{v:"52%",l:"campo mod. em Samambaia"},{v:"159k",l:"eleitores em Samambaia"},{v:"16%",l:"funcionalismo"},{v:"R$ 1.700",l:"renda média"}],
   desafio:"A logística importa mais que o volume total. Cada real fora do território é desperdiçado.",
   cor:"#0F6E56",bg:"#E1F5EE"},
  {id:"nicho",campo:"liberal",nome:"O Liberal de Nicho",cargo:"Dep. Federal ou Dep. Distrital",
   frase:"Eu sei exatamente quem é meu eleitor. Ele tem empresa, paga plano de saúde.",
   tags:["Nicho preciso","Alta renda","Teto definido"],
   stats:[{v:"32%",l:"campo lib./cons. no DF 2022"},{v:"74%",l:"superior Lago Sul"},{v:"R$ 8.000",l:"renda média"},{v:"60%",l:"plano de saúde"}],
   desafio:"Campo fragmentado. O quociente é atingível, mas exige concentração geográfica.",
   cor:"#854F0B",bg:"#FAEEDA"},
  {id:"desafiante",campo:"liberal",nome:"O Conservador Majoritário",cargo:"Governador ou Senador",
   frase:"O campo tem 32% dos votos, mas ninguém uniu. Se resolver esse problema, posso vencer.",
   tags:["Campo fragmentado","Unificação","Majoritário"],
   stats:[{v:"32%",l:"campo lib./cons. no DF 2022"},{v:"1 lugar",l:"maior campo no DF em 2022"},{v:"213k",l:"eleitores em Taguatinga"},{v:"48%",l:"moderado em Tag."}],
   desafio:"Precisa somar 32% do campo mais fatia do moderado nas satélites consolidadas.",
   cor:"#854F0B",bg:"#FAEEDA"},
];

// ── CANDIDATOS 2022 (extraídos do TSE) ───────────────────────────────────────
var A5_CANDS=JSON.parse(atob("__CANDS_B64__"));

// Tipologia do candidato baseada em σ dos deltas (sobre-índice − 1) entre RAs.
// Distribuído (σ<30) · Híbrido (30..60) · Concentrado (≥60).
function calcTipologia(cand){
  var deltas=[];
  Object.keys(cand.ras||{}).forEach(function(ra){
    var v = cand.ras[ra];
    if(v && v.idx != null) deltas.push((v.idx-1)*100);
  });
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

// Marcar eleitos com base na LISTA OFICIAL TSE/CLDF 2022
// Fonte: Câmara dos Deputados + CLDF (https://www.cl.df.gov.br/)
// Não usar ranking simples — sistema proporcional brasileiro depende de QE+sobras+federações.
var ELEITOS_2022 = {
  GOVERNADOR: ["IBANEIS"],
  SENADOR:    ["DAMARES"],  // 2022 = 1 vaga apenas (renovação alternada)
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
    A5_CANDS.filter(function(c){return c.cargo===cargo;}).forEach(function(c){
      var nm = (c.nome||"").toUpperCase();
      c.eleito = idents.some(function(id){ return nm.indexOf(id)>=0; });
    });
  });
})();
var A5_META={GOVERNADOR:700000,SENADOR:550000,DEPUTADO_FEDERAL:18000,DEPUTADO_DISTRITAL:18000};

// ── ESTADO CANDIDATO ─────────────────────────────────────────────────────────
var cargoCandAtivo="all", candSelecionado=null;
var estCargoAtivo="DEPUTADO_FEDERAL";

// ── NAVEGAÇÃO ─────────────────────────────────────────────────────────────────
var SECS=["populacao","eleitor","campo","candidato","estrategia","projecoes","diagnostico"];

function irSec(id) {
  SECS.forEach(function(s) {
    var el=document.getElementById("s-"+s);
    if(el) el.classList.toggle("active", s===id);
    var ni=document.getElementById("ni-"+s);
    if(ni) ni.classList.toggle("active", s===id);
  });
  if(id==="populacao") rT(1);
  else if(id==="eleitor") rT(2);
  else if(id==="campo") rT(3);
  else if(id==="candidato"){candRenderList();candRenderStats(cargoCandAtivo);}
  else if(id==="projecoes"){estAtualizarConf();estRender();}
  else if(id==="estrategia"){estrInit();}
}

// ── MODAL ─────────────────────────────────────────────────────────────────────
function abrirMet(s){document.getElementById("met-modal").classList.add("open");metNav(s);}
function fecharMet(){document.getElementById("met-modal").classList.remove("open");}
function metNav(s){
  document.querySelectorAll(".met-nav-btn").forEach(function(b){b.classList.remove("on");});
  var idx={intro:0,base:1,foto:2,proj:3,spe:4};
  var btns=document.querySelectorAll(".met-nav-btn");
  if(btns[idx[s]])btns[idx[s]].classList.add("on");
  var el=document.getElementById("met-"+s);
  if(el)el.scrollIntoView({behavior:"smooth",block:"start"});
}
document.addEventListener("keydown",function(e){if(e.key==="Escape")fecharMet();});

// ── PERSONAS ──────────────────────────────────────────────────────────────────
function criarCard(p) {
  var div=document.createElement("div");
  div.className="ps-card visible"; div.dataset.id=p.id; div.style.cursor="pointer";
  div.onclick=function(){selP(p.id);};
  var stats=p.stats.map(function(s){
    return "<div class='ps-stat'><div class='ps-stat-val' style='color:"+p.cor+"'>"+s.v+"</div><div class='ps-stat-lbl'>"+s.l+"</div></div>";
  }).join("");
  div.innerHTML="<div class='ps-nome'>"+p.nome+"</div><div class='ps-cargo' style='color:var(--muted)'>"+p.cargo+"</div>"+
    "<div class='ps-frase'>"+p.frase+"</div><div class='ps-stats'>"+stats+"</div>"+
    "<div class='ps-desafio'><strong>Desafio:</strong> "+p.desafio+"</div>";
  var btn=document.createElement("button");
  btn.className="ps-btn"; btn.style.background=p.bg; btn.style.color=p.cor;
  btn.style.border="0.5px solid "+p.cor; btn.textContent="Selecionar esta persona";
  btn.onclick=function(){selP(p.id);};
  div.appendChild(btn);
  return div;
}

function expandirCampo(campo,el) {
  document.querySelectorAll(".ps-campo-card").forEach(function(c){
    c.style.borderColor="var(--bd)"; c.style.borderWidth="0.5px";
  });
  if(el){el.style.borderColor={progressista:"#534AB7",moderado:"#0F6E56",liberal:"#854F0B"}[campo]||"var(--amber)";el.style.borderWidth="2px";}
  var area=document.getElementById("ps-personas-area");
  if(area)area.style.display="block";
  var g=document.getElementById("ps-grid"); if(!g)return;
  g.innerHTML="";
  PERS.forEach(function(p){
    if(p.campo!==campo)return;
    g.appendChild(criarCard(p));
  });
  var ps=document.getElementById("s-persona");
  if(ps)setTimeout(function(){ps.scrollTo({top:ps.scrollHeight,behavior:"smooth"});},80);
}

function selP(id) {
  var p=PERS.find(function(x){return x.id===id;});
  if(!p)return;
  pAt=id; pNome=p.nome;
  var k=PK[id]||""; var pts=k.split("|");
  pCargo=pts[0]||"GOVERNADOR"; pPerfil=pts[1]||"moderado";
  document.querySelectorAll(".ps-card").forEach(function(c){
    c.classList.remove("sel"); c.style.borderColor="";
    var b=c.querySelector(".ps-btn"); if(b)b.textContent="Selecionar esta persona";
  });
  var card=document.querySelector(".ps-card[data-id='"+id+"']");
  if(card){card.classList.add("sel"); card.style.borderColor=p.cor;
    var b=card.querySelector(".ps-btn"); if(b)b.textContent="Persona selecionada";}
  document.getElementById("ps-banner-nome").textContent=p.nome;
  document.getElementById("ps-banner-sub").textContent=p.cargo;
  var ini=document.getElementById("ps-iniciar");
  ini.style.background=p.cor; ini.style.color="#fff"; ini.style.border="none";
  document.getElementById("ps-banner").classList.add("visible");
  var ps=document.getElementById("s-persona");
  if(ps)setTimeout(function(){ps.scrollTo({top:ps.scrollHeight,behavior:"smooth"});},50);
}

function iniciarProjecao() {
  if(!pAt)return;
  document.getElementById("ps-banner").classList.remove("visible");
  // Atualizar chips de persona em potencial e estrategia
  atualizarChipsPersona();
  // Atualizar texto do achado4
  var p=PERS.find(function(x){return x.id===pAt;});
  var cl={GOVERNADOR:"Governador",SENADOR:"Senador",DEPUTADO_FEDERAL:"Dep. Federal",DEPUTADO_DISTRITAL:"Dep. Distrital"};
  var cm={progressista:"Progressista",moderado:"Moderado",liberal_conservador:"Liberal/Conservador"};
  var a4=document.getElementById("achado4-txt");
  if(a4&&p)a4.innerHTML="Para <strong>"+p.nome+"</strong> ("+( cl[pCargo]||pCargo)+" · campo "+(cm[pPerfil]||pPerfil)+"), as regiões estão ordenadas pelo SPE. <strong>Prioridade</strong>: concentre recursos. <strong>Expandir</strong>: mensagem adaptada. <strong>Consolidar</strong>: não sobre-invista.";
  irSec("potencial");
}

function atualizarChipsPersona() {
  var p=PERS.find(function(x){return x.id===pAt;});
  if(!p)return;
  var cl={GOVERNADOR:"Governador",SENADOR:"Senador",DEPUTADO_FEDERAL:"Dep. Federal",DEPUTADO_DISTRITAL:"Dep. Distrital"};
  var cm={progressista:"Progressista",moderado:"Moderado",liberal_conservador:"Liberal/Conservador"};
  var sub=p.nome+" · "+(cl[pCargo]||pCargo)+" · "+(cm[pPerfil]||pPerfil);
  ["","2"].forEach(function(sfx){
    var chip=document.getElementById("persona-chip"+sfx);
    var nome=document.getElementById("chip-nome"+sfx);
    var subsEl=document.getElementById("chip-sub"+sfx);
    if(chip)chip.style.display="flex";
    if(nome)nome.textContent=p.nome;
    if(subsEl)subsEl.textContent=sub;
  });
}

// ── CANDIDATO (Fotografia) ────────────────────────────────────────────────────
function candRenderList() {
  var q=(document.getElementById("cand-search").value||"").toLowerCase();
  var list=A5_CANDS.filter(function(c){
    if(q&&c.nome.toLowerCase().indexOf(q)<0)return false;
    if(cargoCandAtivo!=="all"&&c.cargo!==cargoCandAtivo)return false;
    return true;
  });
  // Eleitos no topo (ordenados por total desc), depois não-eleitos (mesmo critério)
  list.sort(function(a,b){
    if(a.eleito && !b.eleito) return -1;
    if(!a.eleito && b.eleito) return 1;
    return (b.total||0)-(a.total||0);
  });
  var primeiroNaoEleito = list.findIndex(function(c){ return !c.eleito; });
  var html="";
  var cl={GOVERNADOR:"Governador",SENADOR:"Senador",DEPUTADO_FEDERAL:"Dep. Federal",DEPUTADO_DISTRITAL:"Dep. Distrital"};
  var CC2={progressista:"#A32D2D",moderado:"#0F6E56",liberal_conservador:"#854F0B",outros:"#6B7280"};
  list.forEach(function(c, i){
    if(i===primeiroNaoEleito && primeiroNaoEleito>0){
      html += "<div style='height:0.5px;background:var(--bd2);margin:6px 12px;opacity:0.6'></div>";
    }
    var sel=candSelecionado&&candSelecionado.nome===c.nome?" sel":"";
    var totalStr=c.total>0?(c.total>=1000?Math.round(c.total/1000)+"k":c.total.toLocaleString("pt-BR"))+" votos":"";
    var eleitoBadge=c.eleito
      ? "<span style='font-size:9px;padding:1px 6px;border-radius:8px;background:#E1F5EE;color:#085041;font-weight:500;margin-left:auto;flex-shrink:0'>Eleito</span>"
      : "";
    html+="<div class='cand-item"+sel+"' data-nome='"+c.nome+"'>"
      +"<div class='cand-item-bar' style='background:"+(CC2[c.campo]||"#888")+"'></div>"
      +"<div class='cand-item-inner'>"
      +"<div class='cand-item-nome' style='display:flex;align-items:center;gap:6px'><span style='flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis'>"+c.nome+"</span>"+eleitoBadge+"</div>"
      +"<div class='cand-item-sub'>"+(c.partido||"?")+" · "+(cl[c.cargo]||c.cargo)
      +(totalStr?" · "+totalStr:"")+"</div>"
      +"</div></div>";
  });
  var listEl=document.getElementById("cand-list");
  listEl.innerHTML=html||"<div style='padding:16px;font-size:11px;color:var(--muted)'>Nenhum candidato encontrado</div>";
  listEl.querySelectorAll(".cand-item").forEach(function(el){
    el.onclick=function(){
      var nome=this.getAttribute("data-nome");
      var cand=A5_CANDS.find(function(c){return c.nome===nome;});
      if(cand)candSel(cand);
    };
  });
}

function candFiltrar(){candRenderList();}

function candSetCargo(btn) {
  var cargo=btn.getAttribute("data-cargo");
  cargoCandAtivo=cargo;
  document.querySelectorAll("#cf-cargo-all,#cf-gov,#cf-sen,#cf-df,#cf-dd").forEach(function(b){
    b.className="cf-btn";
  });
  btn.className="cf-btn on";
  candRenderList();
  candRenderStats(cargo);
}



function candSel(cand) {
  candSelecionado=cand;
  candFiltroStatus = null;
  var selSt = document.getElementById("cand-filtro-status");
  if(selSt){ selSt.value = "all"; selSt.classList.remove("on"); }
  var inpRA = document.getElementById("cand-filtro-ra");
  if(inpRA) inpRA.value = "";
  candRenderList();
  document.getElementById("cand-empty").style.display="none";
  var dc=document.getElementById("cand-detail-content");
  dc.style.display="flex";

  var cl={GOVERNADOR:"Governador",SENADOR:"Senador",DEPUTADO_FEDERAL:"Dep. Federal",DEPUTADO_DISTRITAL:"Dep. Distrital"};
  var cc={progressista:"#534AB7",moderado:"#0F6E56",liberal_conservador:"#854F0B"};
  var cn={progressista:"Progressista",moderado:"Moderado",liberal_conservador:"Liberal/Cons."};
  var total=cand.total||0;
  var totalStr=total>0?total.toLocaleString("pt-BR")+" votos":"";
  var SNbadge={progressista:"background:#FCEBEB;color:#791F1F",moderado:"background:#E1F5EE;color:#085041",
               liberal_conservador:"background:#FAEEDA;color:#633806",outros:"background:#F1EFE8;color:#444"};
  var CNbadge={progressista:"Progressista",moderado:"Moderado",liberal_conservador:"Liberal/Cons.",outros:"Outros"};
  var tip = calcTipologia(cand);
  var BADGE_STYLE = "font-size:10px;padding:3px 10px;border-radius:10px;font-weight:500;display:inline-block;line-height:1.4";
  var PREFIX_STYLE = "font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.5px";
  var WRAP_STYLE   = "display:inline-flex;align-items:center;gap:5px";
  var campoBadgeHtml = "<span style='"+WRAP_STYLE+"'>"
    + "<span style='"+PREFIX_STYLE+"'>Campo:</span>"
    + "<span style='"+BADGE_STYLE+";"+(SNbadge[cand.campo]||"")+"'>"+(CNbadge[cand.campo]||cand.campo)+"</span>"
    + "</span>";
  var votoBadgeHtml = tip
    ? "<span class='tt' style='"+WRAP_STYLE+"'>"
      + "<span style='"+PREFIX_STYLE+"'>Voto:</span>"
      + "<span style='cursor:help;"+BADGE_STYLE+";"+tip.css+"'>"+tip.lbl+"</span>"
      + "<span class='tt-box'>"+tip.desc+"</span>"
      + "</span>"
    : "";
  document.getElementById("cand-ctx-line").innerHTML=
    "<div style='width:3px;height:14px;background:"+(CC[cand.campo]||"#888")+";border-radius:1px;flex-shrink:0'></div>"
    +"<span style='font-size:13px;font-weight:500'>"+cand.nome+"</span>"
    +(totalStr?"<span style='font-size:11px;color:var(--muted)'>· "+totalStr+"</span>":"")
    +campoBadgeHtml
    +votoBadgeHtml;
  candRenderTab(cand);
  _candResetScroll();
}

// ── Top 3 regiões principais — por Performance (sobre-índice) ────────────────
// Filtro mínimo evita microRAs distorcerem (candidato pequeno com idx alto em RA de poucos votos).
function candRenderTop3(cand){
  var el = document.getElementById("cand-top3");
  if(!el) return;
  var ras = cand.ras || {};
  var minVotosTop = Math.max(30, Math.round((cand.total||0) * 0.01));
  var nomes = Object.keys(ras).filter(function(n){
    var r = ras[n];
    return (r.v||0) >= minVotosTop && r.idx != null;
  });
  nomes.sort(function(a,b){ return (ras[b].idx||0) - (ras[a].idx||0); });
  var top3 = nomes.slice(0,3);
  // Fallback: se filtro deixou < 3, completa por votos absolutos
  if(top3.length < 3){
    var resto = Object.keys(ras)
      .filter(function(n){ return (ras[n].v||0) > 0 && top3.indexOf(n) < 0; })
      .sort(function(a,b){ return (ras[b].v||0) - (ras[a].v||0); })
      .slice(0, 3 - top3.length);
    top3 = top3.concat(resto);
  }
  if(!top3.length || !cand.total){ el.innerHTML=""; return; }
  var slbl={"REDUTO":"Reduto","BASE FORTE":"Base forte","BASE FRACA":"Base fraca","CAMPO MEDIO":"Esperado","CAMPO MÉDIO":"Esperado","AUSENCIA":"Ausência","SEM DADOS":"—"};
  var smap={"REDUTO":"background:#A7F3C8;color:#0B5A2E",
            "BASE FORTE":"background:#E1F5EE;color:#085041",
            "BASE FRACA":"background:#FCEBEB;color:#791F1F",
            "CAMPO MEDIO":"background:#FEF3C7;color:#B45309",
            "CAMPO MÉDIO":"background:#FEF3C7;color:#B45309",
            "AUSENCIA":"background:#FCA5A5;color:#5A1010"};
  var html='<div style="font-size:9px;letter-spacing:1.5px;text-transform:uppercase;color:var(--muted);margin-bottom:6px;font-weight:500">3 regiões principais</div>'
    +'<div style="display:grid;grid-template-columns:repeat('+top3.length+',1fr);gap:8px">';
  top3.forEach(function(n){
    var r=ras[n];
    var pct=(r.v/cand.total*100).toFixed(1).replace(".",",");
    var idxDelta=(r.idx!=null)?Math.round((r.idx-1)*100):null;
    var idxTxt=idxDelta!=null?((idxDelta>=0?"+":"")+idxDelta+"%"):"—";
    var idxColor=(idxDelta==null)?"var(--muted)":(idxDelta>=0?"#085041":"#791F1F");
    html+='<div style="background:var(--s1);border:0.5px solid var(--bd);border-radius:8px;padding:10px 12px">'
      +'<div style="font-size:11px;color:var(--txt);font-weight:500;line-height:1.2;margin-bottom:8px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis" title="'+n+'">'+n+'</div>'
      +'<div style="display:grid;grid-template-columns:1fr auto;gap:6px;align-items:center">'
        +'<div>'
          +'<div style="font-size:18px;font-weight:500;color:var(--amber);font-family:var(--mono,inherit);line-height:1">'+r.v.toLocaleString("pt-BR")+'</div>'
          +'<div style="font-size:10px;color:var(--muted);margin-top:3px"><strong style="color:var(--txt)">'+pct+'%</strong> do total</div>'
        +'</div>'
        +'<div style="display:flex;flex-direction:column;align-items:flex-end;gap:5px">'
          +'<div style="font-size:13px;font-weight:600;color:'+idxColor+';font-family:var(--mono,inherit);line-height:1">'+idxTxt+'</div>'
          +'<span style="font-size:9px;padding:2px 8px;border-radius:10px;'+(smap[r.s]||"color:var(--muted)")+'">'+(slbl[r.s]||"—")+'</span>'
        +'</div>'
      +'</div>'
      +'</div>';
  });
  html+='</div>';
  el.innerHTML = html;
}

// ── Tabela RA × candidato (com ordenação clicável) ───────────────────────────
var candSortCol="v", candSortAsc=false;  // default: votos desc
var candFiltroStatus = null;

function candSrt(col){
  if(candSortCol===col) candSortAsc=!candSortAsc;
  else { candSortCol=col; candSortAsc=(col==="nome"); }
  if(candSelecionado) candRenderTab(candSelecionado);
}

function _candResetScroll(){ var s=document.getElementById("cand-tbl-scroll"); if(s) s.scrollTop=0; }
function imprimirRelCandSelecionado(){
  if(!candSelecionado){ alert('Selecione um candidato antes de imprimir o relatório.'); return; }
  if(typeof imprimirRelCandidatoPorNome === 'function'){
    imprimirRelCandidatoPorNome(candSelecionado.nome);
  }
}
function candFiltrarRA(){ if(candSelecionado){ candRenderTab(candSelecionado); _candResetScroll(); } }

function candFiltrarStatus(){
  var sel = document.getElementById("cand-filtro-status");
  candFiltroStatus = (sel && sel.value && sel.value !== "all") ? sel.value : null;
  if(sel) sel.classList.toggle("on", !!candFiltroStatus);
  if(candSelecionado){ candRenderTab(candSelecionado); _candResetScroll(); }
}

function candRenderTab(cand){
  if(!cand) return;
  var cc={moderado:"#185FA5",progressista:"#A32D2D",liberal_conservador:"#534AB7",outros:"#6B7280"};
  var ras=cand.ras||{};
  var slbl={"REDUTO":"Reduto","BASE FORTE":"Base forte","BASE FRACA":"Base fraca","CAMPO MEDIO":"Esperado","CAMPO MÉDIO":"Esperado","AUSENCIA":"Ausência","SEM DADOS":"—"};
  var smap={"REDUTO":"background:#A7F3C8;color:#0B5A2E",
            "BASE FORTE":"background:#E1F5EE;color:#085041",
            "BASE FRACA":"background:#FCEBEB;color:#791F1F",
            "CAMPO MEDIO":"background:#FEF3C7;color:#B45309",
            "CAMPO MÉDIO":"background:#FEF3C7;color:#B45309",
            "AUSENCIA":"background:#FCA5A5;color:#5A1010",
            "SEM DADOS":"color:var(--muted)"};
  var STATUS_ORD={"REDUTO":5,"BASE FORTE":4,"CAMPO MEDIO":3,"CAMPO MÉDIO":3,"BASE FRACA":2,"AUSENCIA":1,"SEM DADOS":0};
  // SEM_ZONA_SET descontinuado em abr/2026 — todas as 33 RAs têm dado eleitoral
  // próprio via atribuição seção→RA por point-in-polygon. Mantido vazio para
  // manter compatibilidade com referências legadas (d.sem_zona = false sempre).
  var SEM_ZONA_SET={};

  // Lista de RAs com zona TSE (com ou sem voto do candidato), aplicando filtros inline
  var fIn = document.getElementById("cand-filtro-ra");
  var qRA = (fIn && fIn.value || "").trim().toLowerCase();
  var todas=URAS.filter(function(n){
    if(SEM_ZONA_SET[n]) return false;
    if(qRA && n.toLowerCase().indexOf(qRA) < 0) return false;
    if(candFiltroStatus){
      var r = ras[n];
      if(!r) return false;
      var st = r.s;
      // CAMPO MEDIO casa com ambas grafias (com e sem acento)
      if(candFiltroStatus === "CAMPO MEDIO" && (st === "CAMPO MEDIO" || st === "CAMPO MÉDIO")) return true;
      if(st !== candFiltroStatus) return false;
    }
    return true;
  });

  // Ordenar pela coluna selecionada
  todas.sort(function(a,b){
    var ra=ras[a], rb=ras[b];
    // Sempre empurra "sem voto" pro fim (independente da direção)
    if(!ra && !rb) return a.localeCompare(b);
    if(!ra) return 1;
    if(!rb) return -1;
    var va, vb;
    if(candSortCol==="nome"){ return candSortAsc? a.localeCompare(b) : b.localeCompare(a); }
    if(candSortCol==="v"){ va=ra.v||0; vb=rb.v||0; }
    else if(candSortCol==="pe"){ va=ra.pe||0; vb=rb.pe||0; }
    else if(candSortCol==="pp"){ va=ra.pp||0; vb=rb.pp||0; }
    else if(candSortCol==="pc"){ va=ra.pc||0; vb=rb.pc||0; }
    else { va=ra.v||0; vb=rb.v||0; }
    return candSortAsc? va-vb : vb-va;
  });

  var html="";
  function bar(pct,cor,val){
    return "<td style='padding:0;position:relative;overflow:hidden'>"
      +"<div style='position:absolute;top:5px;bottom:5px;left:3px;right:0;border-radius:3px;max-width:calc(100% - 12px);width:"+Math.min(100,Math.round(pct))+"%;background:"+cor+";opacity:0.18'></div>"
      +"<span style='position:relative;display:inline-block;padding:6px 10px;font-size:12px;font-weight:500;color:"+cor+"'>"+val+"</span></td>";
  }
  todas.forEach(function(n){
    var r=ras[n];
    if(!r){
      html+="<tr><td style='font-size:12px;font-weight:500'>"+n+"</td>"
        +"<td colspan='4' style='color:var(--muted);font-size:11px;padding:7px 10px'>sem voto</td></tr>";
      return;
    }
    html+="<tr>"
      +"<td style='font-size:12px;font-weight:500'>"+n+"</td>"
      +"<td style='font-size:12px;font-weight:500;color:#185FA5;padding:7px 10px'>"+(r.v||0).toLocaleString("pt-BR")+"</td>"
      +bar(r.pe||0,"#185FA5",fp(r.pe||0))
      +bar(r.pp||0,cc[cand.campo]||"#6B7280",fp(r.pp||0))
      +bar(r.pc||0,"#6B7280",fp(r.pc||0))
      +"</tr>";
  });
  document.getElementById("cand-tb").innerHTML=html;

  // Atualizar setas das colunas
  ["nome","v","pe","pp","pc"].forEach(function(c){
    var el=document.getElementById("cand-s-"+c);
    if(el) el.textContent = candSortCol===c ? (candSortAsc?"▲":"▼") : "";
  });

  // (Nota legada de RAs sem zona em <tfoot> removida — substituída pela
  //  caixa neutra abaixo da tabela.)
}

// ══ ESTRATÉGIA (Contexto > Estratégia) ════════════════════════════════════════
// Estrutura espelhada do submenu Candidatos. Cruza Performance do candidato
// (idx_cand) com Força do campo dele na RA × cargo (idx_campo).

var ESTR_CAT_DEF = {
  compartilhado: {lbl:"Reduto consolidado",  cor:"#0B5A2E", bg:"#A7F3C8"},
  pessoal:       {lbl:"Voto pessoal",        cor:"#075985", bg:"#E0F2FE"},
  esperado:      {lbl:"Esperado",            cor:"#B45309", bg:"#FEF3C7"},
  conquistar:    {lbl:"Espaço a conquistar", cor:"#9A3412", bg:"#FFE4D6"},
  sem_espaco:    {lbl:"Sem espaço pelo campo", cor:"#5A1010", bg:"#FCA5A5"}
};
var ESTR_CAT_ORDER = ["compartilhado","pessoal","esperado","conquistar","sem_espaco"];
var ESTR_CAT_ORD = {compartilhado:5, pessoal:4, esperado:3, conquistar:2, sem_espaco:1};

var estrCargoAtivo  = "all";
var estrCandSel     = null;
var estrFiltroCat   = null;
var estrSortCol     = "votos";
var estrSortAsc     = false;

function estrCategoria(idxCand, idxCampo){
  if(idxCand == null || idxCampo == null) return null;
  if(idxCand >= 1.15 && idxCampo >= 1.15) return "compartilhado";
  if(idxCand >= 1.15)                      return "pessoal";
  if(idxCand <  0.85 && idxCampo >= 1.15)   return "conquistar";
  if(idxCand <  0.85)                       return "sem_espaco";
  return "esperado";
}

function estrDadosCand(cand){
  if(!cand || !cand.ras) return [];
  var out = [];
  Object.keys(cand.ras).forEach(function(ra){
    var r = cand.ras[ra];
    if(!r || (r.v||0)<=0) return;
    var dadoRa = D[ra] || {};
    var votosCargo = (dadoRa.votos || {})[cand.cargo] || {};
    var dadoCampo  = votosCargo[cand.campo] || {};
    var idxCand    = (r.idx != null) ? r.idx : null;
    var idxCampo   = (dadoCampo.idx != null) ? dadoCampo.idx : null;
    out.push({
      ra: ra,
      aptos: dadoRa.el_aptos || 0,
      votos: r.v || 0,
      pe: r.pe || 0,
      idxCand: idxCand,
      idxCampo: idxCampo,
      cat: estrCategoria(idxCand, idxCampo)
    });
  });
  return out;
}

// Lista de candidatos — espelha o pattern de candRenderList()
function estrRenderList(){
  var q = (document.getElementById("estr-search").value||"").toLowerCase();
  var list = A5_CANDS.filter(function(c){
    if(q && (c.nome+" "+(c.partido||"")).toLowerCase().indexOf(q) < 0) return false;
    if(estrCargoAtivo!=="all" && c.cargo!==estrCargoAtivo) return false;
    return true;
  });
  list.sort(function(a,b){
    if(a.eleito && !b.eleito) return -1;
    if(!a.eleito && b.eleito) return 1;
    return (b.total||0) - (a.total||0);
  });
  var primeiroNaoEleito = list.findIndex(function(c){ return !c.eleito; });
  var html = "";
  var cl = {GOVERNADOR:"Governador",SENADOR:"Senador",DEPUTADO_FEDERAL:"Dep. Federal",DEPUTADO_DISTRITAL:"Dep. Distrital"};
  var CC2 = {progressista:"#A32D2D",moderado:"#0F6E56",liberal_conservador:"#854F0B",outros:"#6B7280"};
  list.forEach(function(c, i){
    if(i===primeiroNaoEleito && primeiroNaoEleito>0){
      html += "<div style='height:0.5px;background:var(--bd2);margin:6px 12px;opacity:0.6'></div>";
    }
    var sel = estrCandSel && estrCandSel.nome===c.nome && estrCandSel.cargo===c.cargo ? " sel" : "";
    var totalStr = c.total>0 ? (c.total>=1000 ? Math.round(c.total/1000)+"k" : c.total.toLocaleString("pt-BR"))+" votos" : "";
    var eleitoBadge = c.eleito
      ? "<span style='font-size:9px;padding:1px 6px;border-radius:8px;background:#E1F5EE;color:#085041;font-weight:500;margin-left:auto;flex-shrink:0'>Eleito</span>"
      : "";
    html += "<div class='cand-item"+sel+"' data-nome='"+c.nome+"' data-cargo='"+c.cargo+"'>"
      + "<div class='cand-item-bar' style='background:"+(CC2[c.campo]||"#888")+"'></div>"
      + "<div class='cand-item-inner'>"
      + "<div class='cand-item-nome' style='display:flex;align-items:center;gap:6px'><span style='flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis'>"+c.nome+"</span>"+eleitoBadge+"</div>"
      + "<div class='cand-item-sub'>"+(c.partido||"?")+" · "+(cl[c.cargo]||c.cargo)
      + (totalStr?" · "+totalStr:"")+"</div>"
      + "</div></div>";
  });
  var listEl = document.getElementById("estr-list");
  listEl.innerHTML = html || "<div style='padding:16px;font-size:11px;color:var(--muted)'>Nenhum candidato encontrado</div>";
  listEl.querySelectorAll(".cand-item").forEach(function(el){
    el.onclick = function(){
      var nome = this.getAttribute("data-nome");
      var cargo = this.getAttribute("data-cargo");
      var cand = A5_CANDS.find(function(c){ return c.nome===nome && c.cargo===cargo; });
      if(cand) estrSel(cand);
    };
  });
}

function estrFiltrar(){ estrRenderList(); }

function estrSetCargo(btn){
  estrCargoAtivo = btn.getAttribute("data-cargo");
  var bar = btn.parentElement;
  if(bar) bar.querySelectorAll(".cf-btn").forEach(function(b){
    b.className = (b===btn) ? "cf-btn on" : "cf-btn";
  });
  estrRenderList();
}

function _estrResetScroll(){ var s=document.getElementById("estr-tbl-scroll"); if(s) s.scrollTop=0; }

function estrSel(cand){
  estrCandSel = cand;
  estrFiltroCat = null;
  var selCat = document.getElementById("estr-filtro-cat");
  if(selCat){ selCat.value = "all"; selCat.classList.remove("on"); }
  var inpRA = document.getElementById("estr-filtro-ra");
  if(inpRA) inpRA.value = "";
  document.getElementById("estr-empty").style.display = "none";
  document.getElementById("estr-detail-content").style.display = "flex";
  estrRenderList();
  estrRenderConteudo();
  _estrResetScroll();
}

function estrRenderConteudo(){
  var c = estrCandSel;
  if(!c) return;
  var cl = {GOVERNADOR:"Governador",SENADOR:"Senador",DEPUTADO_FEDERAL:"Dep. Federal",DEPUTADO_DISTRITAL:"Dep. Distrital"};
  var CC = {progressista:"Progressista", moderado:"Moderado", liberal_conservador:"Liberal/Cons.", outros:"Outros"};
  var CCOR = {progressista:"#A32D2D", moderado:"#0F6E56", liberal_conservador:"#534AB7", outros:"#6B7280"};
  var CCBG = {progressista:"#FCEBEB", moderado:"#E1F5EE", liberal_conservador:"#EEEDFE", outros:"#F1EFE8"};
  var votoBadge = "<span style='font-size:9px;padding:2px 7px;border-radius:10px;background:"+(CCBG[c.campo]||"#F1EFE8")+";color:"+(CCOR[c.campo]||"#6B7280")+"'>"+(CC[c.campo]||c.campo)+"</span>";
  var totalStr = c.total>0 ? c.total.toLocaleString("pt-BR")+" votos" : "";
  var eleitoStr = c.eleito ? " · <strong style='color:#085041'>Eleito</strong>" : "";
  document.getElementById("estr-ctx-line").innerHTML =
      "<strong style='font-size:13px'>"+c.nome+"</strong>"
    + votoBadge
    + "<span style='font-size:11px;color:var(--muted)'>"+(c.partido||"?")+" · "+(cl[c.cargo]||c.cargo)+eleitoStr+"</span>"
    + (totalStr ? "<span style='font-size:11px;color:var(--muted)'>· "+totalStr+"</span>" : "")
    + "<button onclick='abrirAliancas(estrCandSel)' style='margin-left:auto;font-size:11px;padding:4px 12px;border-radius:6px;border:0;background:var(--amber);color:white;cursor:pointer;white-space:nowrap;flex-shrink:0;font-weight:500;letter-spacing:0.5px;text-transform:uppercase'>Alianças políticas</button>";

  var dados = estrDadosCand(c);
  estrRenderTab(dados);
}

function estrFiltrarCat(){
  var sel = document.getElementById("estr-filtro-cat");
  estrFiltroCat = (sel && sel.value && sel.value !== "all") ? sel.value : null;
  if(sel) sel.classList.toggle("on", !!estrFiltroCat);
  if(estrCandSel){ estrRenderTab(estrDadosCand(estrCandSel)); _estrResetScroll(); }
}

function estrSrt(col){
  if(estrSortCol===col){ estrSortAsc = !estrSortAsc; }
  else { estrSortCol = col; estrSortAsc = (col==="ra"); }
  if(estrCandSel) estrRenderTab(estrDadosCand(estrCandSel));
}

function estrFiltrarRA(){ if(estrCandSel){ estrRenderTab(estrDadosCand(estrCandSel)); _estrResetScroll(); } }

function estrRenderTab(dados){
  var tb = document.getElementById("estr-tb");
  if(!tb) return;
  var fIn = document.getElementById("estr-filtro-ra");
  var qRA = (fIn && fIn.value || "").trim().toLowerCase();
  var rows = dados.slice();
  if(estrFiltroCat) rows = rows.filter(function(d){ return d.cat===estrFiltroCat; });
  if(qRA)           rows = rows.filter(function(d){ return d.ra.toLowerCase().indexOf(qRA) >= 0; });
  rows.sort(function(a,b){
    var va, vb;
    if(estrSortCol==="ra"){ return estrSortAsc ? a.ra.localeCompare(b.ra) : b.ra.localeCompare(a.ra); }
    if(estrSortCol==="cat"){ va = ESTR_CAT_ORD[a.cat]||0; vb = ESTR_CAT_ORD[b.cat]||0; }
    else if(estrSortCol==="idxCand"){ va = (a.idxCand!=null?a.idxCand:-9999); vb = (b.idxCand!=null?b.idxCand:-9999); }
    else if(estrSortCol==="idxCampo"){ va = (a.idxCampo!=null?a.idxCampo:-9999); vb = (b.idxCampo!=null?b.idxCampo:-9999); }
    else { va = a[estrSortCol]||0; vb = b[estrSortCol]||0; }
    return estrSortAsc ? va-vb : vb-va;
  });
  ["ra","aptos","votos","pe","idxCand","idxCampo","cat"].forEach(function(c){
    var el = document.getElementById("estr-s-"+c);
    if(el) el.textContent = (estrSortCol===c) ? (estrSortAsc?"▲":"▼") : "";
  });
  if(!rows.length){
    tb.innerHTML = "<tr><td colspan='7' style='padding:14px;text-align:center;color:var(--muted);font-style:italic;font-size:11.5px'>Nenhuma RA nesta categoria.</td></tr>";
    return;
  }
  var fmtIdx = function(v){ if(v==null) return "—"; var d=Math.round((v-1)*100); return (d>=0?"+":"")+d+"%"; };
  var corIdx = function(v){ if(v==null) return "var(--muted)"; var d=v-1; return d>=0.15?"#085041":(d<=-0.15?"#791F1F":"#444"); };
  var fpt1 = function(v){ return (v||0).toFixed(1).replace(".",","); };
  tb.innerHTML = rows.map(function(d){
    var def = ESTR_CAT_DEF[d.cat] || {lbl:"—", cor:"#444", bg:"#F1EFE8"};
    return "<tr>"
      + "<td style='padding:6px 10px;font-size:12px;font-weight:500'>"+d.ra+"</td>"
      + "<td style='padding:6px 10px;font-size:12px;text-align:right;font-variant-numeric:tabular-nums;color:var(--muted)'>"+(d.aptos||0).toLocaleString("pt-BR")+"</td>"
      + "<td style='padding:6px 10px;font-size:12px;text-align:right;font-variant-numeric:tabular-nums;font-weight:500;color:#185FA5'>"+(d.votos||0).toLocaleString("pt-BR")+"</td>"
      + "<td style='padding:6px 10px;font-size:12px;text-align:right;font-variant-numeric:tabular-nums;font-weight:500;color:#185FA5'>"+fpt1(d.pe)+"%</td>"
      + "<td style='padding:6px 10px;font-size:12px;text-align:right;font-variant-numeric:tabular-nums;font-weight:500;color:"+corIdx(d.idxCand)+"'>"+fmtIdx(d.idxCand)+"</td>"
      + "<td style='padding:6px 10px;font-size:12px;text-align:right;font-variant-numeric:tabular-nums;font-weight:500;color:"+corIdx(d.idxCampo)+"'>"+fmtIdx(d.idxCampo)+"</td>"
      + "<td style='padding:5px 8px'><span class='estr-cat-badge' style='background:"+def.bg+";color:"+def.cor+"'>"+def.lbl+"</span></td>"
      + "</tr>";
  }).join("");
}

function estrInit(){ estrRenderList(); }

var VOTOS_ELEITOS=JSON.parse(atob("__VOTOS_ELEITOS_B64__"));
var METAS_CAMPO=JSON.parse(atob("__METAS_CAMPO_B64__"));

// ── ESTRATÉGIA ────────────────────────────────────────────────────────────────────────────────
var estCargo="DEPUTADO_FEDERAL";
var estCampo="moderado";
var estRef=null;
var estCandsComp=[];
var EST_CORES=["#185FA5","#854F0B","#1D9E75"];
var EST_SORT={col:"spe",asc:false};

function estCargoSel(btn){
  estCargo=btn.dataset.val;
  btn.closest(".cargo-bar").querySelectorAll(".cargo-btn").forEach(function(b){b.classList.remove("on");});
  btn.classList.add("on");
  estAtualizarConf();estMetaBar();estRender();
}
function estCampoSel(btn){
  estCampo=btn.dataset.val;
  btn.closest(".chips-bar").querySelectorAll(".campo-btn").forEach(function(b){b.classList.remove("on");});
  btn.classList.add("on");
  estAtualizarConf();estMetaBar();estRender();
}
function estAtualizarConf(){
  var badge=document.getElementById("est-conf-badge");if(!badge)return;
  var key=estCargo+"|"+estCampo;
  var d=VOTOS_ELEITOS[key];var m=METAS_CAMPO[key];var n=d?d._n:0;
  // Só mostrar aviso se os dados foram carregados (METAS_CAMPO não vazio)
  var dadosCarregados=Object.keys(METAS_CAMPO).length>0;
  if(!dadosCarregados){badge.style.display="none";return;}
  if(!m||n===0){badge.style.display="inline-block";badge.style.background="#FCEBEB";badge.style.color="#791F1F";badge.textContent="Sem eleitos nesse campo em 2022";}
  else if(n===1){badge.style.display="inline-block";badge.style.background="#FAEEDA";badge.style.color="#633806";badge.textContent="1 eleito 2022";}
  else{badge.style.display="none";}
}
function estMetaBar(){
  var key=estCargo+"|"+estCampo;var m=METAS_CAMPO[key];
  var val=document.getElementById("est-meta-val");var ref=document.getElementById("est-meta-ref");var bar=document.getElementById("est-meta-bar");
  if(!m){if(val)val.textContent="—";if(ref)ref.textContent="sem eleitos nesse campo em 2022";if(bar)bar.style.opacity=".5";return;}
  if(bar)bar.style.opacity="1";
  if(val)val.textContent=m.votos.toLocaleString("pt-BR")+" votos";
  if(ref)ref.textContent="· mínimo do campo 2022 · "+m.ref+" ("+m.n+" eleito"+(m.n>1?"s":"")+")";
}

var estRefTimer=null;
function estRefBuscar(q){
  var res=document.getElementById("est-ref-results");if(!res)return;
  clearTimeout(estRefTimer);
  if(!q||q.length<2){res.style.display="none";return;}
  estRefTimer=setTimeout(function(){
    var ql=q.toLowerCase();
    var lista=(A5_CANDS||[]).filter(function(c){
      return (c.nome.toLowerCase().indexOf(ql)>=0||(c.partido||"").toLowerCase().indexOf(ql)>=0)&&(!estRef||c.nome!==estRef.nome);
    }).slice(0,8);
    res.innerHTML="";
    var CL={DEPUTADO_DISTRITAL:"Dep. Distrital",DEPUTADO_FEDERAL:"Dep. Federal",GOVERNADOR:"Governador",SENADOR:"Senador"};
    if(!lista.length){res.innerHTML="<div style='padding:8px 10px;font-size:12px;color:var(--muted)'>Sem resultados</div>";res.style.display="block";return;}
    lista.forEach(function(c){
      var item=document.createElement("div");
      item.style.cssText="padding:7px 10px;cursor:pointer;font-size:12px;border-bottom:0.5px solid var(--bd)";
      item.innerHTML="<strong>"+c.nome+"</strong><span style='color:var(--muted);margin-left:6px;font-size:11px'>"+(CL[c.cargo]||c.cargo)+" · "+(c.partido||"?")+" · "+(c.total||0).toLocaleString("pt-BR")+" votos</span>";
      item.onmousedown=function(){estRefSel(c);};
      res.appendChild(item);
    });
    res.style.display="block";
  },200);
}
function estRefSel(c){
  estRef=c;
  var inp=document.getElementById("est-ref-input");var res=document.getElementById("est-ref-results");
  var chip=document.getElementById("est-ref-chip");var fallback=document.getElementById("est-ref-fallback");
  var CL={DEPUTADO_DISTRITAL:"Dep. Dist.",DEPUTADO_FEDERAL:"Dep. Fed.",GOVERNADOR:"Gov.",SENADOR:"Sen."};
  if(inp){inp.value="";inp.style.display="none";}if(res)res.style.display="none";
  if(chip){document.getElementById("est-ref-nome").textContent=c.nome.split(" ").slice(0,3).join(" ");document.getElementById("est-ref-sub").textContent=(CL[c.cargo]||c.cargo)+" 2022 · "+(c.total||0).toLocaleString("pt-BR")+" votos";chip.style.display="inline-flex";}
  if(fallback)fallback.style.display="none";
  estRender();
}
function estRefClear(){
  estRef=null;
  var inp=document.getElementById("est-ref-input");var chip=document.getElementById("est-ref-chip");var fallback=document.getElementById("est-ref-fallback");
  if(inp){inp.value="";inp.style.display="";}if(chip)chip.style.display="none";if(fallback)fallback.style.display="";
  estRender();
}
document.addEventListener("click",function(e){
  var res=document.getElementById("est-ref-results");var inp=document.getElementById("est-ref-input");
  if(res&&!res.contains(e.target)&&e.target!==inp)res.style.display="none";
  var panel=document.getElementById("est-add-panel");var btn=document.getElementById("est-add-btn");
  if(panel&&panel.style.display!=="none"&&!panel.contains(e.target)&&e.target!==btn)panel.style.display="none";
});

function estToggleAdd(e){
  e.stopPropagation();var p=document.getElementById("est-add-panel");if(!p)return;
  var show=p.style.display==="none";p.style.display=show?"block":"none";
  if(show){var i=document.getElementById("est-search");if(i){i.value="";i.focus();}document.getElementById("est-search-res").innerHTML="";}
}
function estSearch(q){
  var res=document.getElementById("est-search-res");if(!res)return;
  if(!q||q.length<2){res.innerHTML="";return;}
  var ql=q.toLowerCase();var jaSel=estCandsComp.map(function(c){return c.nome;});if(estRef)jaSel.push(estRef.nome);
  var lista=(A5_CANDS||[]).filter(function(c){return !jaSel.includes(c.nome)&&(c.nome.toLowerCase().indexOf(ql)>=0||(c.partido||"").toLowerCase().indexOf(ql)>=0);}).slice(0,8);
  res.innerHTML="";
  if(!lista.length){res.innerHTML="<div style='padding:8px 10px;font-size:12px;color:var(--muted)'>Sem resultados</div>";return;}
  var CL={DEPUTADO_DISTRITAL:"Dep. Distrital",DEPUTADO_FEDERAL:"Dep. Federal",GOVERNADOR:"Governador",SENADOR:"Senador"};
  lista.forEach(function(c){
    var div=document.createElement("div");div.style.cssText="padding:7px 10px;cursor:pointer;font-size:12px;border-bottom:0.5px solid var(--bd)";
    div.innerHTML="<strong>"+c.nome+"</strong><span style='color:var(--muted);margin-left:6px;font-size:11px'>"+(CL[c.cargo]||c.cargo)+" · "+(c.partido||"?")+" · "+(c.total||0).toLocaleString("pt-BR")+" votos</span>";
    div.onmousedown=function(){estAddCand(c);};res.appendChild(div);
  });
}
function estAddCand(c){
  if(estCandsComp.length>=3)return;
  var CL={DEPUTADO_DISTRITAL:"Dep. Dist.",DEPUTADO_FEDERAL:"Dep. Fed.",GOVERNADOR:"Gov.",SENADOR:"Sen."};
  estCandsComp.push({nome:c.nome,cargo:c.cargo,partido:c.partido,ras:c.ras||{},cor:EST_CORES[estCandsComp.length],label:(CL[c.cargo]||c.cargo)+" 2022"});
  document.getElementById("est-add-panel").style.display="none";
  if(estCandsComp.length>=3)document.getElementById("est-add-btn").style.display="none";
  estRenderChips();estUpdateThead();estRender();
}
function estRemoveCand(i){
  estCandsComp.splice(i,1);estCandsComp.forEach(function(c,j){c.cor=EST_CORES[j];});
  document.getElementById("est-add-btn").style.display="";
  estRenderChips();estUpdateThead();estRender();
}
function estRenderChips(){
  var wrap=document.getElementById("est-chips");if(!wrap)return;wrap.innerHTML="";
  estCandsComp.forEach(function(c,i){
    var chip=document.createElement("span");chip.style.cssText="display:inline-flex;align-items:center;gap:5px;padding:3px 8px 3px 10px;border-radius:20px;font-size:11px;border:0.5px solid "+c.cor+";background:var(--s1)";
    var dot=document.createElement("span");dot.style.cssText="width:8px;height:8px;border-radius:50%;background:"+c.cor+";flex-shrink:0";
    var nome=document.createElement("span");nome.textContent=c.nome.split(" ").slice(0,2).join(" ");
    var lbl=document.createElement("span");lbl.style.cssText="color:var(--muted);font-size:10px";lbl.textContent=c.label;
    var x=document.createElement("span");x.style.cssText="font-size:11px;color:var(--muted);cursor:pointer;padding:0 2px";x.textContent="×";
    x.onclick=(function(idx){return function(){estRemoveCand(idx);};})(i);
    chip.appendChild(dot);chip.appendChild(nome);chip.appendChild(lbl);chip.appendChild(x);wrap.appendChild(chip);
  });
}
function estUpdateThead(){
  var thead=document.getElementById("est-thead");if(!thead)return;
  while(thead.children.length>5)thead.removeChild(thead.lastChild);
  var thS="position:sticky;top:0;background:var(--s1);text-align:left;padding:7px 8px 5px;font-size:10px;letter-spacing:1px;text-transform:uppercase;color:var(--muted);font-weight:400;border-bottom:0.5px solid var(--bd2);min-width:90px";
  var CL={DEPUTADO_DISTRITAL:"Dep. Dist.",DEPUTADO_FEDERAL:"Dep. Fed.",GOVERNADOR:"Gov.",SENADOR:"Sen."};
  estCandsComp.forEach(function(c){
    var th=document.createElement("th");th.style.cssText=thS;
    th.innerHTML="<span style='color:"+c.cor+";font-weight:500'>"+c.nome.split(" ").slice(0,2).join(" ")+"</span>"
      +"<br><span style='font-weight:400;font-size:8px;text-transform:none;letter-spacing:0;color:var(--muted)'>"+(CL[c.cargo]||c.cargo)+" 2022</span>";
    thead.appendChild(th);
  });
}
function estSortBy(col){
  if(EST_SORT.col===col)EST_SORT.asc=!EST_SORT.asc;else{EST_SORT.col=col;EST_SORT.asc=false;}
  ["nome","spe","cons","med","otim"].forEach(function(c){var el=document.getElementById("est-s-"+c);if(el)el.textContent=EST_SORT.col===c?(EST_SORT.asc?"▲":"▼"):"";});
  estRender();
}

function estRender(){
  var tbody=document.getElementById("est-tbody");if(!tbody)return;
  var key=estCargo+"|"+estCampo;var metaObj=METAS_CAMPO[key];var meta=metaObj?metaObj.votos:0;
  var SEM={};  // descontinuado em abr/2026 — todas as RAs têm dado próprio via PIP
  function getRef(ra){
    if(estRef&&estRef.ras&&estRef.ras[ra])return estRef.ras[ra].v||0;
    var vd=VOTOS_ELEITOS[key];return(vd&&vd[ra]&&vd[ra].p50)||0;
  }
  function getSpe(d){var ipd=d&&d.spe&&d.spe[key];return ipd?ipd.spe||0:0;}
  var lista=URAS.filter(function(n){return !SEM[n];}).map(function(n){
    var d=D[n];if(!d)return null;
    var spe=getSpe(d);var fSpe=1+(spe-5)/20;var ref=getRef(n);
    return{nome:n,spe:spe,ref:ref,
      cons:Math.max(0,Math.round(ref*0.50*fSpe)),
      med:Math.max(0,Math.round(ref*0.75*fSpe)),
      otim:Math.max(0,Math.round(ref*1.00*fSpe)),
      refCands:estCandsComp.map(function(c){var r=c.ras&&c.ras[n];return r?(r.v||0):null;})};
  }).filter(Boolean);
  var col=EST_SORT.col,asc=EST_SORT.asc;
  lista.sort(function(a,b){
    if(col==="nome")return asc?a.nome.localeCompare(b.nome):b.nome.localeCompare(a.nome);
    return asc?(a[col]||0)-(b[col]||0):(b[col]||0)-(a[col]||0);
  });
  var mx=lista.reduce(function(s,r){return Math.max(s,r.otim);},1)||1;
  function bar(v,cor){
    var pct=Math.min(100,Math.round(v/mx*100));
    return "<td style='padding:0;position:relative;overflow:hidden'>"
      +"<div style='position:absolute;top:5px;bottom:5px;left:3px;right:0;border-radius:3px;max-width:calc(100% - 16px);width:"+pct+"%;background:"+cor+";opacity:0.15'></div>"
      +"<span style='position:relative;display:inline-block;padding:6px 10px;font-size:12px;color:"+cor+"'>"+v.toLocaleString("pt-BR")+"</span></td>";
  }
  var html="";
  lista.forEach(function(r){
    var rc=" style='border-bottom:0.5px solid var(--bd)'";
    var spe10=(Math.round(r.spe*10)/10).toFixed(1).replace(".",",");
    var spePct=Math.round(r.spe/10*100);
    var candCols=r.refCands.map(function(v,ci){
      var cor=estCandsComp[ci]?estCandsComp[ci].cor:"var(--muted)";
      return v!==null&&v>0?"<td style='padding:6px 10px;font-size:12px;color:"+cor+"'>"+v.toLocaleString("pt-BR")+"</td>"
        :"<td style='padding:6px 10px;font-size:12px;color:var(--muted)'>—</td>";
    }).join("");
    html+="<tr"+rc+"><td style='font-size:12px' title='"+r.nome+"'>"+r.nome+"</td>"
      +"<td style='padding:0;position:relative;overflow:hidden'><div style='position:absolute;top:5px;bottom:5px;left:3px;right:0;border-radius:3px;width:"+spePct+"%;background:#0F6E56;opacity:0.15'></div><span style='position:relative;display:inline-block;padding:6px 10px;font-size:12px;font-weight:500;color:#0F6E56'>"+spe10+"</span></td>"
      +bar(r.cons,"#5F5E5A")+bar(r.med,"#185FA5")+bar(r.otim,"#0F6E56")
      +candCols+"</tr>";
  });
  tbody.innerHTML=html;
  var nota=document.getElementById("est-nota");
  if(nota){nota.style.display="none";}  // nota legada — todas as RAs têm dado próprio via PIP
}
function estInit(){
  estAtualizarConf();estMetaBar();
  document.getElementById("est-s-spe").textContent="▼";
  estRender();
}

// ── FUNÇÕES DE TABELA ─────────────────────────────────────────────────────────
function togglePersona(a,mode){
  FM[a]=mode;
  var all=document.getElementById("tog"+a+"-all");
  var per=document.getElementById("tog"+a+"-per");
  if(all)all.className="toggle-btn"+(mode==="all"?" on":"");
  if(per)per.className="toggle-btn"+(mode==="per"?" on":"");
  rT(a);
}

function filtrar(a){
  var inp=document.getElementById("fi"+a);
  if(inp)FQ[a]=inp.value.toLowerCase();
  rT(a);
}

function isP(n){
  if(!pAt)return false;
  return (PT[pAt]||[]).some(function(p){
    return n.toLowerCase().indexOf(p.toLowerCase())>=0||p.toLowerCase().indexOf(n.toLowerCase())>=0;
  });
}

function gDF(a){
  var q=FQ[a]||"", modoPersona=FM[a]==="per";
  return URAS.filter(function(n){
    if(!D[n])return false;
    if(modoPersona&&!isP(n))return false;
    if(q&&n.toLowerCase().indexOf(q)<0)return false;
    return true;
  }).map(function(n){return{nome:n,d:D[n]};});
}

function srt(a,col){
  if(SC[a]===col){SA[a]=!SA[a];}else{SC[a]=col;SA[a]=false;}
  document.querySelectorAll("[id^='s"+a+"-']").forEach(function(el){el.textContent="";});
  var el=document.getElementById("s"+a+"-"+col);
  if(el)el.textContent=SA[a]?"\u25b2":"\u25bc";
  rT(a);
}

function srtL(lista,a){
  var col=SC[a],asc=SA[a];
  return lista.slice().sort(function(x,y){
    if(col==="nome")return asc?x.nome.localeCompare(y.nome):y.nome.localeCompare(x.nome);
    var va=(x.d&&x.d[col]!=null)?x.d[col]:0;
    var vb=(y.d&&y.d[col]!=null)?y.d[col]:0;
    return asc?va-vb:vb-va;
  });
}

function bc(val,max,cor){
  if(val===null||val===undefined)return "<td><span style='color:var(--muted);font-size:11px'>-</span></td>";
  var isAbs=val>=100;
  var pct=isAbs?(max>0?Math.min(100,Math.round(val/max*100)):0):Math.min(100,Math.round(Math.abs(val)));
  var disp=val>100?Math.round(val).toLocaleString("pt-BR"):fp(val);
  return "<td style='padding:0;position:relative;overflow:hidden'>"
    +"<div style='position:absolute;top:5px;bottom:5px;left:3px;right:0;border-radius:3px;max-width:calc(100% - 16px);width:"+pct+"%;background:"+cor+";opacity:0.15'></div>"
    +"<span style='position:relative;display:inline-block;padding:7px 10px;font-size:12px;font-weight:500;color:"+cor+"'>"+disp+"</span>"
    +"</td>";
}

function mx(col){
  return Math.max.apply(null,URAS.map(function(n){return(D[n]&&D[n][col])||0;}));
}

function updInfo(a,lista){
  // (Antes escrevia textContent no input "fi"+a — agora o input é um filtro inline
  //  no TH da Região, não comporta texto acessório. Função mantida como no-op pra
  //  preservar a chamada nas funções rT2 e rT3.)
}

function rT(a){
  if(a===1)rT1();
  else if(a===2)rT2();
  else if(a===3)rT3();
  else if(a===4)rT4();
}

function rT1(){
  var lista=srtL(gDF(1),1);
  var M={};
  ["renda_pc","pct_ab","pct_de","pct_inseg","pct_super","pct_sem_fund",
   "pct_nativo","pct_migrante","pct_serv","pct_serv_fed","pct_privado","pct_conta",
   "pct_desoc","pct_beneficio","pct_plano"].forEach(function(c){M[c]=mx(c);});
  var html="";
  lista.forEach(function(item){
    var n=item.nome,d=item.d;
    html+="<tr><td style='font-size:12px;font-weight:500'>"+n+"</td>"
      +bc(d.renda_pc,M.renda_pc,"#854F0B")
      +bc(d.pct_super,M.pct_super,"#534AB7")
      +bc(d.pct_sem_fund,M.pct_sem_fund,"#A32D2D")
      +bc(d.pct_ab,M.pct_ab,"#534AB7")
      +bc(d.pct_de,M.pct_de,"#A32D2D")
      +bc(d.pct_inseg,M.pct_inseg,"#A32D2D")
      +bc(d.pct_serv,M.pct_serv,"#185FA5")
      +bc(d.pct_serv_fed,M.pct_serv_fed,"#0C447C")
      +bc(d.pct_privado,M.pct_privado,"#3B6D11")
      +bc(d.pct_conta,M.pct_conta,"#0F6E56")
      +bc(d.pct_desoc,M.pct_desoc,"#A32D2D")
      +bc(d.pct_beneficio,M.pct_beneficio,"#0F6E56")
      +bc(d.pct_plano,M.pct_plano,"#185FA5")
      +bc(d.pct_jov_mor,M.pct_jov_mor,"#0F6E56")
      +bc(d.pct_ido_mor,M.pct_ido_mor,"#534AB7")
      +bc(d.pct_nativo,M.pct_nativo,"#534AB7")
      +bc(d.pct_migrante,M.pct_migrante,"#6B7280")
      +"</tr>";
  });
  document.getElementById("tb1").innerHTML=html;
}

function rT2(){
  var lista=srtL(gDF(2),2);
  var mA=mx("el_aptos"),mP=25,mS=80,mAbs=mx("abstencao")||35;
  var html="";
  // Separar RAs estimadas (sem zona TSE)
  var listaPrincipal=lista.filter(function(i){return !i.d.sem_zona;});
  var listaEst=lista.filter(function(i){return !!i.d.sem_zona;});
  listaPrincipal.forEach(function(item){
    var n=item.nome,d=item.d;
    var sz=d.sem_zona?" <span title='Esta RA não tem zona eleitoral própria no TSE 2022 — indicadores eleitorais não desagregáveis' style='font-size:9px;color:var(--muted);font-style:italic'>(s/zona)</span>":"";
    var ap=d.el_aptos||0;
    var gap=(d.el_super!=null&&d.pct_super!=null)?parseFloat((d.el_super-d.pct_super).toFixed(1)):null;
    var gapJov=(d.el_jov!=null&&d.pct_jov_mor!=null)?parseFloat((d.el_jov-d.pct_jov_mor).toFixed(1)):null;
    var gapIdo=(d.el_ido!=null&&d.pct_ido_mor!=null)?parseFloat((d.el_ido-d.pct_ido_mor).toFixed(1)):null;
    d.gap=gap; d.gap_jov=gapJov; d.gap_ido=gapIdo;
    function fmtGap(g){
      if(g==null)return "--";
      if(g>2)return "<span style='background:#E1F5EE;color:#085041;font-size:10px;padding:1px 6px;border-radius:10px'>+"+f1(g)+"pp</span>";
      if(g<-2)return "<span style='background:#FCEBEB;color:#791F1F;font-size:10px;padding:1px 6px;border-radius:10px'>"+f1(g)+"pp</span>";
      return "<span style='font-size:10px;color:var(--muted)'>"+f1(g)+"pp</span>";
    }
    var gH=fmtGap(gap);
    html+="<tr><td style='font-size:12px;font-weight:500'>"+n+sz+"</td>"
      +"<td style='padding:7px 10px;font-size:12px;font-weight:500;color:#185FA5'>"+(ap>0?Math.round(ap/1000)+"k":"--")+"</td>"
      +bc(d.abstencao,mAbs,"#A32D2D")
      +bc(d.el_fem,60,"#993556")
      +bc(d.el_jov,mP,"#854F0B")
      +bc(d.el_ido,mP,"#6B7280")
      +bc(d.el_super,mS,"#534AB7")
      +bc(d.el_sem_fund,mP,"#A32D2D")
      +"<td>"+fmtGap(gapJov)+"</td>"
      +"<td>"+fmtGap(gapIdo)+"</td>"
      +"<td>"+gH+"</td>"
      +"</td></tr>";
  });
  document.getElementById("tb2").innerHTML=html;
  // (nota legada de RAs sem zona substituída pela caixa fixa abaixo da tabela)
  updInfo(2,lista);
}

function setCargo(c,btn){
  cargoV=c;
  btn.closest(".cargo-bar").querySelectorAll(".cargo-btn").forEach(function(b){b.classList.remove("on");});
  btn.classList.add("on");
  rT(3);
}

var CC={moderado:"#185FA5",progressista:"#A32D2D",liberal_conservador:"#534AB7",outros:"#6B7280"};
var CN={moderado:"Moderado",progressista:"Progressista",liberal_conservador:"Liberal/Cons.",outros:"Outros"};
var CP={moderado:"background:#E6F1FB;color:#0C447C",progressista:"background:#FCEBEB;color:#791F1F",liberal_conservador:"background:#EEEDFE;color:#3C3489",outros:"background:#F1EFE8;color:#444441"};

function gV(d,c){
  if(!d.votos)return null;
  if(d.votos[c])return d.votos[c];
  var norm=function(s){return s.toUpperCase().replace(/ /g,"_").replace(/-/g,"_");};
  var cn=norm(c);
  var keys=Object.keys(d.votos);
  var match=keys.find(function(k){return norm(k)===cn;});
  return match?d.votos[match]:null;
}

function rT3(){
  var lista=gDF(3);
  var col=SC[3],asc=SA[3];
  // Helper: extrai pct do dict {pct, idx} (compatível com formato antigo number)
  var vp=function(o){ if(o==null)return 0; if(typeof o==='number')return o; return (o.pct!=null)?o.pct:0; };
  lista.sort(function(a,b){
    if(col==="nome")return asc?a.nome.localeCompare(b.nome):b.nome.localeCompare(a.nome);
    if(col==="margem_pp"){
      var ma=((a.d.margem||{})[cargoV]||{}).margem_pp; if(ma==null)ma=999;
      var mb=((b.d.margem||{})[cargoV]||{}).margem_pp; if(mb==null)mb=999;
      return asc?ma-mb:mb-ma;
    }
    var va=vp((gV(a.d,cargoV)||{})[col]);
    var vb=vp((gV(b.d,cargoV)||{})[col]);
    return asc?va-vb:vb-va;
  });
  // Distribuição ponderada por eleitores aptos
  var totais={moderado:0,progressista:0,liberal_conservador:0,outros:0};
  var totalAptos=0;
  var listaEst3=lista.filter(function(i){return !!i.d.sem_zona;});
  var listaPrincipal3=lista.filter(function(i){return !i.d.sem_zona;});
  listaPrincipal3.forEach(function(item){
    var vc=gV(item.d,cargoV);
    var aptos=item.d.el_aptos||0;
    if(vc){["moderado","progressista","liberal_conservador","outros"].forEach(function(k){totais[k]+=vp(vc[k])*aptos;});}
    totalAptos+=aptos;
  });
  var sumT=totalAptos||1;
  var pcts={};
  ["moderado","progressista","liberal_conservador","outros"].forEach(function(c){pcts[c]=totais[c]/sumT;});
  var cl2={GOVERNADOR:"Governador",SENADOR:"Senador",DEPUTADO_FEDERAL:"Dep. Federal",DEPUTADO_DISTRITAL:"Dep. Distrital"};
  var lbl3=document.getElementById("vol3-label");
  if(lbl3)lbl3.textContent="Composição do DF · "+(cl2[cargoV]||cargoV)+" 2022";
  var barEl=document.getElementById("vol3-bar");
  if(barEl){
    barEl.innerHTML=["moderado","progressista","liberal_conservador","outros"].map(function(c){
      var p=pcts[c]; var cor=CC[c];
      var label=p>=5?p.toFixed(1).replace(".",",")+"%":"";
      return "<div style='width:"+p+"%;position:relative;overflow:hidden;min-width:0'>"
        +"<div style='position:absolute;inset:0;background:"+cor+";opacity:0.15'></div>"
        +"<span style='position:relative;display:flex;align-items:center;justify-content:center;height:100%;font-size:11px;font-weight:500;color:"+cor+";white-space:nowrap;overflow:hidden'>"+label+"</span>"
        +"</div>";
    }).join("");
  }
  var legEl=document.getElementById("vol3-legend");
  if(legEl){
    legEl.innerHTML=["moderado","progressista","liberal_conservador","outros"].map(function(c){
      return "<span style='display:flex;align-items:center;gap:5px;font-size:11px;color:var(--muted)'>"
        +"<span style='width:10px;height:10px;border-radius:2px;background:"+CC[c]+";opacity:0.55;display:inline-block'></span>"
        +CN[c]+"</span>";
    }).join("");
  }
  var html="";
  listaPrincipal3.forEach(function(item){
    var n=item.nome,d=item.d,per=isP(n);
    var rc=per?" class='persona-row'":"";
    var vc=gV(d,cargoV);
    if(!vc||Object.keys(vc).length===0){
      html+="<tr"+rc+"><td style='font-size:12px'>"+n+"</td><td colspan='5' style='color:var(--muted);font-size:11px'>Dados não disponíveis</td></tr>";
      return;
    }
    function pc(c){
      var raw=vc[c];
      var val=vp(raw);
      var idx=(raw&&typeof raw==='object'&&raw.idx!=null)?raw.idx:null;
      var pct=Math.min(100,Math.round(val));
      var bold=SC[3]===c?"font-weight:500;":"";
      var idxTxt='';
      if(idx!=null){
        var delta=Math.round((idx-1)*100);
        var sgn=delta>=0?'+':'';
        var idxColor=delta>=0?'#085041':'#791F1F';
        idxTxt=" <span style='font-size:10px;color:"+idxColor+";font-weight:500'>("+sgn+delta+"%)</span>";
      }
      return "<td style='padding:0;position:relative;overflow:hidden'>"
        +"<div style='position:absolute;top:5px;bottom:5px;left:3px;right:0;border-radius:3px;max-width:calc(100% - 16px);width:"+pct+"%;background:"+CC[c]+";opacity:0.15'></div>"
        +"<span style='position:relative;display:inline-block;padding:6px 10px;font-size:12px;"+bold+"color:"+CC[c]+"'>"+fp(val)+idxTxt+"</span></td>";
    }
    // Coluna margem 1º-2º
    var mg=(d.margem||{})[cargoV];
    var mgCell;
    if(mg){
      var mp=mg.margem_pp;
      var mgColor=mp<=10?'#791F1F':(mp<=25?'#B45309':'#444');
      var mgWeight=mp<=10?'font-weight:500;':'';
      var liderTit=' title="'+(mg.nm1||'').replace(/"/g,'&quot;')+' venceu por '+mp.toFixed(1).replace('.',',')+'pp"';
      mgCell="<td style='font-size:12px;padding:7px 10px;color:"+mgColor+";"+mgWeight+"'"+liderTit+">"+mp.toFixed(1).replace('.',',')+"pp</td>";
    } else {
      mgCell="<td style='font-size:11px;color:var(--muted)'>—</td>";
    }
    html+="<tr"+rc+"><td style='font-size:12px;font-weight:500' title='"+n+"'>"+n+"</td>"
      +pc("moderado")+pc("progressista")+pc("liberal_conservador")+pc("outros")
      +mgCell+"</tr>";
  });
  document.getElementById("tb3").innerHTML=html;
  // (nota legada de RAs sem zona substituída pela caixa fixa abaixo da tabela)
  updInfo(3,lista);
}

function tg(ipe,afin){
  var ha=afin>=5,hi=ipe>=4;
  if(ha&&hi)return["PRIORIDADE","#633806","#FAEEDA"];
  if(ha&&!hi)return["CONSOLIDAR","#085041","#E1F5EE"];
  if(!ha&&hi)return["EXPANDIR","#0C447C","#E6F1FB"];
  return["NAO PRIORIZAR","#444441","#F1EFE8"];
}

function rT4(){
  var key=pCargo+"|"+pPerfil;
  var q=FQ[4]||"", modoP=FM[4]==="per";
  var lista=URAS.filter(function(n){
    if(!D[n])return false;
    if(modoP&&!isP(n))return false;
    if(q&&n.toLowerCase().indexOf(q)<0)return false;
    return true;
  }).map(function(n){
    var d=D[n]; if(!d)return null;
    var ipd=d.spe[key]||{spe:0,afin:0,conv:0,massa:0,logist:0};
    return{nome:n,d:d,spe:ipd.spe,afin:ipd.afin,conv:ipd.conv,massa:ipd.massa,logist:ipd.logist};
  }).filter(Boolean);
  var col=SC[4],asc=SA[4];
  lista.sort(function(a,b){
    if(col==="nome")return asc?a.nome.localeCompare(b.nome):b.nome.localeCompare(a.nome);
    return asc?a[col]-b[col]:b[col]-a[col];
  });
  // Matriz
  var quad={PRIORIDADE:[],CONSOLIDAR:[],EXPANDIR:[],NAO_PRIORIZAR:[]};
  var html="",pers=0;
  lista.forEach(function(item){
    var per=isP(item.nome); if(per)pers++;
    var sel=item.nome===raAt4;
    var cls=(sel?"sel ":(per&&!sel?"persona-row":"")).trim();
    var t=tg(item.spe,item.afin);
    var qk=t[0].replace(" ","_");
    quad[qk]=quad[qk]||[];
    quad[qk].push({nome:item.nome,spe:item.spe,afin:item.afin});
    function sb(val,pct,cor){
      var w=Math.round(pct*0.78);
      return "<td style='padding:0;position:relative;overflow:hidden'>"
        +"<div style='position:absolute;top:5px;bottom:5px;left:4px;border-radius:3px;width:"+w+"%;background:"+cor+";opacity:0.15'></div>"
        +"<span style='position:relative;display:inline-block;padding:7px 10px;font-size:12px;font-weight:500;color:"+cor+"'>"+f1(val)+"</span></td>";
    }
    html+="<tr"+(cls?" class='"+cls+"'":"")+" data-nome='"+item.nome.replace(/'/g,"&#39;")+"'>"
      +"<td style='font-size:12px'>"+item.nome+"</td>"
      +sb(item.spe,Math.round(item.spe/10*100),"#854F0B")
      +sb(item.afin,Math.round(item.afin/10*100),"#534AB7")
      +sb(item.conv,Math.round(item.conv/10*100),"#185FA5")
      +sb(item.massa,Math.round(item.massa/10*100),"#0F6E56")
      +sb(item.logist,Math.round(item.logist/10*100),"#B45309")
      +"<td style='padding:7px 10px;vertical-align:middle'><span style='font-size:10px;font-weight:600;letter-spacing:0.5px;padding:2px 8px;border-radius:10px;background:"+t[2]+";color:"+t[1]+"'>"+t[0]+"</span></td>"
      +"</tr>";
  });
  var tb=document.getElementById("tb4");
  tb.innerHTML=html;
  tb.onclick=function(e){
    var row=e.target.closest("tr[data-nome]");
    if(row)sRA4(row.getAttribute("data-nome"));
  };
  var el=document.getElementById("fi4");
  if(el)el.textContent=lista.length+" regiões - "+pers+" no território da persona";
  // Renderizar matriz
  ["PRIORIDADE","EXPANDIR","CONSOLIDAR","NAO PRIORIZAR"].forEach(function(q){
    var qid={"PRIORIDADE":"q-prioridade","EXPANDIR":"q-expandir","CONSOLIDAR":"q-consolidar","NAO PRIORIZAR":"q-nao"}[q];
    var el=document.getElementById(qid);
    if(!el)return;
    var items=quad[q.replace(" ","_")]||[];
    el.innerHTML=items.slice(0,8).map(function(x){
      var ax=Math.round(x.afin/10*100),ay=Math.round((10-x.spe)/10*100);
      return "<div class=" + JSON.stringify("mpt"+(x.nome===raAt4?" sel":"")) + " style='left:"+ax+"%;top:"+ay+"%;background:#854F0B' title=" + JSON.stringify(x.nome+" SPE:"+f1(x.spe)) + " data-nome=" + JSON.stringify(x.nome) + "></div>";
    }).join("");
    el.querySelectorAll(".mpt").forEach(function(d){
      d.onclick=function(){sRA4(this.getAttribute("data-nome"));};
    });
  });
}

function sRA4(n){raAt4=n;rT4();rF4(n);}

function rF4(n){
  var d=D[n];
  var fv=document.getElementById("ficha-vazio");
  var fc=document.getElementById("ficha4");
  if(!d){if(fv)fv.style.display="block";if(fc)fc.style.display="none";return;}
  if(fv)fv.style.display="none";
  if(fc)fc.style.display="block";
  var key=pCargo+"|"+pPerfil;
  var ipd=d.spe[key]||{spe:0,afin:0,conv:0,massa:0,logist:0};
  var t=tg(ipd.spe,ipd.afin);
  var narr=(d.narrativa||"Sem análise disponível.").replace(/[#]+\u0020*/g,"").replace(/[*][*]/g,"");
  fc.innerHTML="<div class='ficha-ra-nome'>"+n+"</div>"
    +"<div class='ficha-tag'><span class='ftag' style='background:"+t[2]+";color:"+t[1]+"'>"+t[0]+"</span></div>"
    +"<div class='ficha-kpis'>"
      +"<div class='fkpi'><div class='fkpi-val' style='color:#854F0B'>"+f1(ipd.spe)+"</div><div class='fkpi-lbl'>SPE</div></div>"
      +"<div class='fkpi'><div class='fkpi-val' style='color:#534AB7'>"+f1(ipd.afin)+"</div><div class='fkpi-lbl'>Afinidade</div></div>"
      +"<div class='fkpi'><div class='fkpi-val' style='color:#185FA5'>"+f1(ipd.conv)+"</div><div class='fkpi-lbl'>Conversão</div></div>"
      +"<div class='fkpi'><div class='fkpi-val' style='color:#0F6E56'>"+f1(ipd.massa)+"</div><div class='fkpi-lbl'>Volume</div></div>"
      +"<div class='fkpi'><div class='fkpi-val' style='color:#B45309'>"+f1(ipd.logist)+"</div><div class='fkpi-lbl'>Logística</div></div>"
    +"</div>"
    +"<div class='ficha-narr'>"+narr+"</div>";
}

// ── DIAGNÓSTICO (wizard) ──────────────────────────────────────────────────────
var diagTipo = null;
var diagPaso = 1;
var diagOrigem = null;        // candidato 2022 (objeto A5_CANDS)
var diagCargoDest = null;     // string cargo destino 2026
var diagRef = null;           // candidato referência destino (objeto A5_CANDS)

var DIAG_TIPO_LABEL = {
  reposicionamento: "Reposicionamento (mandato em outro cargo)",
};
var DIAG_CARGO_LBL = {
  GOVERNADOR:"Governador", SENADOR:"Senador",
  DEPUTADO_FEDERAL:"Dep. Federal", DEPUTADO_DISTRITAL:"Dep. Distrital"
};
var DIAG_CAMPO_LBL = {
  progressista:"Progressista", moderado:"Moderado",
  liberal_conservador:"Liberal/Cons.", outros:"Outros"
};

function diagSelTipo(tipo) {
  diagTipo = tipo;
  document.querySelectorAll(".diag-type-card.available").forEach(function(c){
    c.classList.remove("selected");
  });
  var card = document.getElementById("diag-card-"+tipo);
  if(card) card.classList.add("selected");
  var btn = document.getElementById("diag-btn-next1");
  if(btn) btn.disabled = false;
  var hint = document.getElementById("diag-p1-hint");
  if(hint) hint.textContent = "Tipo selecionado: " + (DIAG_TIPO_LABEL[tipo] || tipo);
  var lbl2 = document.getElementById("diag-tipo-lbl");
  var lbl3 = document.getElementById("diag-tipo-lbl-3");
  var t = DIAG_TIPO_LABEL[tipo] || tipo;
  if(lbl2) lbl2.textContent = "Tipo: " + t;
  if(lbl3) lbl3.textContent = t;
}

function diagAvancar(n) {
  if(n < 1 || n > 2) return;
  if(n > 1 && !diagTipo) return;
  diagPaso = n;
  for(var i=1; i<=2; i++) {
    var pg = document.getElementById("diag-p"+i);
    if(pg) pg.classList.toggle("active", i === n);
    var st = document.getElementById("diag-st-"+i);
    if(st) {
      st.classList.remove("on","done");
      if(i < n) st.classList.add("done");
      else if(i === n) st.classList.add("on");
    }
  }
  if(n === 2) diagAtualizaPainel();
}

function _diagSlug(s){
  return (s||"").toLowerCase()
    .normalize("NFD").replace(/[̀-ͯ]/g,"")
    .replace(/[^a-z0-9]+/g,"_").replace(/^_+|_+$/g,"");
}

// Mostra o painel de geração quando origem + cargo + ref estão setados.
function diagAtualizaPainel() {
  var painel = document.getElementById("diag-painel");
  var empty  = document.getElementById("diag-empty");
  var sum    = document.getElementById("diag-cfg-summary");
  var stt    = document.getElementById("diag-gerar-status");

  var pronto = !!(diagTipo && diagOrigem && diagCargoDest && diagRef);
  if(painel) painel.style.display = pronto ? "block" : "none";
  if(empty)  empty.style.display  = pronto ? "none"  : "block";
  if(stt)    stt.innerHTML = "";
  if(!pronto) return;

  if(sum){
    sum.innerHTML =
      '<div><strong>Tipo:</strong> '+(DIAG_TIPO_LABEL[diagTipo]||diagTipo)+'</div>'
      +'<div style="margin-top:4px"><strong>Candidato origem:</strong> '+diagOrigem.nome+'</div>'
      +'<div style="font-size:11px;color:var(--muted);margin-left:4px">'+(DIAG_CARGO_LBL[diagOrigem.cargo]||diagOrigem.cargo)+' · '+(DIAG_CAMPO_LBL[diagOrigem.campo]||diagOrigem.campo)+' · '+(diagOrigem.partido||"?")+' · '+(diagOrigem.total||0).toLocaleString("pt-BR")+' votos</div>'
      +'<div style="margin-top:4px"><strong>Cargo destino (2026):</strong> '+(DIAG_CARGO_LBL[diagCargoDest]||diagCargoDest)+'</div>'
      +'<div style="margin-top:4px"><strong>Referência destino:</strong> '+diagRef.nome+(diagRef.eleito?' <span style="font-size:9px;padding:1px 5px;border-radius:8px;background:#E1F5EE;color:#085041">eleito</span>':'')+'</div>'
      +'<div style="font-size:11px;color:var(--muted);margin-left:4px">'+(DIAG_CAMPO_LBL[diagRef.campo]||diagRef.campo)+' · '+(diagRef.partido||"?")+' · '+(diagRef.total||0).toLocaleString("pt-BR")+' votos</div>';
  }
}

function diagGerarRelatorio() {
  if(!(diagTipo && diagOrigem && diagCargoDest && diagRef)) return;

  // Detecta se está rodando via servidor local (http) ou file://
  if(location.protocol !== "http:" && location.protocol !== "https:"){
    var stt0 = document.getElementById("diag-gerar-status");
    if(stt0) stt0.innerHTML = '<span style="color:#791F1F">⚠ Servidor não detectado.</span><br>'
      +'<span style="color:var(--muted)">No terminal, rode <code style="background:var(--s2);padding:1px 5px;border-radius:3px;font-family:Menlo,monospace">python3 servidor_diag.py</code> e abra <code style="background:var(--s2);padding:1px 5px;border-radius:3px;font-family:Menlo,monospace">http://127.0.0.1:8765/</code>.</span>';
    return;
  }

  var btn = document.getElementById("diag-btn-gerar");
  var stt = document.getElementById("diag-gerar-status");
  var cfg = {
    tipo: diagTipo,
    origem:     {nome: diagOrigem.nome, cargo: diagOrigem.cargo},
    destino:    diagCargoDest,
    referencia: {nome: diagRef.nome,    cargo: diagRef.cargo}
  };

  if(btn) { btn.disabled = true; btn.innerHTML = "⏳ Gerando..."; }
  if(stt) stt.innerHTML = '<span style="color:var(--muted)">Processando dados, renderizando imagens e montando o Word...</span>';

  fetch("/api/gerar", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(cfg)
  }).then(function(resp){
    if(!resp.ok){
      return resp.json().then(function(e){
        throw new Error(e.erro || ("HTTP "+resp.status));
      }).catch(function(){ throw new Error("HTTP "+resp.status); });
    }
    var disp = resp.headers.get("Content-Disposition") || "";
    var m = disp.match(/filename="?([^"]+)"?/);
    var fname = m ? m[1] : ("relatorio_diag_"+_diagSlug(diagOrigem.nome)+".docx");
    return resp.blob().then(function(blob){ return {blob:blob, fname:fname}; });
  }).then(function(r){
    var url = URL.createObjectURL(r.blob);
    var a = document.createElement("a");
    a.href = url; a.download = r.fname;
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    setTimeout(function(){ URL.revokeObjectURL(url); }, 1500);
    if(stt) stt.innerHTML = '<span style="color:#085041">✓ <strong>'+r.fname+'</strong> baixado.</span>';
  }).catch(function(err){
    if(stt) stt.innerHTML = '<span style="color:#791F1F">⚠ Falha: '+(err.message||err)+'</span>';
  }).finally(function(){
    if(btn) { btn.disabled = false; btn.innerHTML = "📄 Gerar e baixar relatório"; }
  });
}

// ── Configurador: CANDIDATO ORIGEM ───────────────────────────────────────────
function diagOrigBuscar(q) {
  var box = document.getElementById("diag-orig-results");
  if(!q || q.length<2){ box.style.display="none"; return; }
  var qu = q.toUpperCase();
  var hits = A5_CANDS.filter(function(c){
    return (c.nome||"").toUpperCase().indexOf(qu) >= 0;
  }).slice(0,40);
  if(!hits.length){ box.innerHTML='<div class="diag-search-item" style="color:var(--muted)">Nenhum candidato encontrado.</div>'; box.style.display="block"; return; }
  box.innerHTML = hits.map(function(c, i){
    var cargoLbl = DIAG_CARGO_LBL[c.cargo] || c.cargo;
    var idx = A5_CANDS.indexOf(c);
    return '<div class="diag-search-item" onclick="diagOrigSel('+idx+')">'
      +'<span><strong>'+c.nome+'</strong> <span class="diag-search-item-meta">· '+cargoLbl+' · '+(c.partido||"?")+(c.eleito?" · eleito":"")+'</span></span>'
      +'<span class="diag-search-item-meta">'+(c.total||0).toLocaleString("pt-BR")+'</span>'
      +'</div>';
  }).join("");
  box.style.display="block";
}
function diagOrigSel(idx) {
  diagOrigem = A5_CANDS[idx];
  document.getElementById("diag-orig-results").style.display="none";
  document.getElementById("diag-orig-input").value="";
  document.getElementById("diag-orig-wrap").style.display="none";
  var chip = document.getElementById("diag-orig-chip");
  chip.style.display="inline-flex";
  document.getElementById("diag-orig-nome").textContent = diagOrigem.nome;
  document.getElementById("diag-orig-sub").textContent =
    "· " + (DIAG_CARGO_LBL[diagOrigem.cargo]||diagOrigem.cargo)
    + " · " + (DIAG_CAMPO_LBL[diagOrigem.campo]||diagOrigem.campo)
    + " · " + (diagOrigem.partido||"?")
    + " · " + (diagOrigem.total||0).toLocaleString("pt-BR") + " votos";
  // Atualiza botões de cargo destino: desabilita o cargo origem
  document.querySelectorAll("#diag-dest-buttons .cargo-btn").forEach(function(b){
    if(b.getAttribute("data-val") === diagOrigem.cargo){
      b.setAttribute("disabled","disabled");
      b.classList.remove("on");
      if(diagCargoDest === diagOrigem.cargo){ diagCargoDest = null; }
    } else {
      b.removeAttribute("disabled");
    }
  });
  diagAtualizaPainel();
}
function diagOrigClear() {
  diagOrigem = null;
  document.getElementById("diag-orig-chip").style.display="none";
  document.getElementById("diag-orig-wrap").style.display="";
  document.querySelectorAll("#diag-dest-buttons .cargo-btn").forEach(function(b){
    b.removeAttribute("disabled");
  });
  diagAtualizaPainel();
}

// ── Configurador: CARGO DESTINO ──────────────────────────────────────────────
function diagDestSel(btn) {
  if(btn.hasAttribute("disabled")) return;
  diagCargoDest = btn.getAttribute("data-val");
  document.querySelectorAll("#diag-dest-buttons .cargo-btn").forEach(function(b){ b.classList.remove("on"); });
  btn.classList.add("on");
  // Habilita campo de referência
  var refInp = document.getElementById("diag-ref-input");
  refInp.disabled = false;
  refInp.placeholder = "Buscar candidato " + (DIAG_CARGO_LBL[diagCargoDest]||diagCargoDest) + " 2022...";
  // Se referência atual é de outro cargo, limpa
  if(diagRef && diagRef.cargo !== diagCargoDest){ diagRefClear(); }
  diagAtualizaPainel();
}

// ── Configurador: REFERÊNCIA DESTINO ─────────────────────────────────────────
function diagRefBuscar(q) {
  var box = document.getElementById("diag-ref-results");
  if(!diagCargoDest){ box.style.display="none"; return; }
  if(!q || q.length<2){ box.style.display="none"; return; }
  var qu = q.toUpperCase();
  var hits = A5_CANDS.filter(function(c){
    return c.cargo === diagCargoDest && (c.nome||"").toUpperCase().indexOf(qu) >= 0;
  }).slice(0,40);
  if(!hits.length){ box.innerHTML='<div class="diag-search-item" style="color:var(--muted)">Nenhum candidato encontrado para o cargo selecionado.</div>'; box.style.display="block"; return; }
  box.innerHTML = hits.map(function(c){
    var idx = A5_CANDS.indexOf(c);
    return '<div class="diag-search-item" onclick="diagRefSel('+idx+')">'
      +'<span><strong>'+c.nome+'</strong> <span class="diag-search-item-meta">· '+(DIAG_CAMPO_LBL[c.campo]||c.campo)+' · '+(c.partido||"?")+(c.eleito?" · eleito":"")+'</span></span>'
      +'<span class="diag-search-item-meta">'+(c.total||0).toLocaleString("pt-BR")+'</span>'
      +'</div>';
  }).join("");
  box.style.display="block";
}
function diagRefSel(idx) {
  diagRef = A5_CANDS[idx];
  document.getElementById("diag-ref-results").style.display="none";
  document.getElementById("diag-ref-input").value="";
  document.getElementById("diag-ref-wrap").style.display="none";
  var chip = document.getElementById("diag-ref-chip");
  chip.style.display="inline-flex";
  document.getElementById("diag-ref-nome").textContent = diagRef.nome;
  document.getElementById("diag-ref-sub").textContent =
    "· " + (DIAG_CAMPO_LBL[diagRef.campo]||diagRef.campo)
    + " · " + (diagRef.partido||"?")
    + " · " + (diagRef.total||0).toLocaleString("pt-BR") + " votos"
    + (diagRef.eleito ? " · eleito" : "");
  diagAtualizaPainel();
}
function diagRefClear() {
  diagRef = null;
  document.getElementById("diag-ref-chip").style.display="none";
  document.getElementById("diag-ref-wrap").style.display="";
  diagAtualizaPainel();
}


// INICIALIZAÇÃO
irSec("populacao");
estInit();

var cmpCandB = null;
var cmpFiltroPad = null;  // null = mostrar todas; "SOBREPOE"/"AGREGA_A"/"AGREGA_B"/"ABERTO" = filtra

function cmpToggleFiltro(pad){
  cmpFiltroPad = (cmpFiltroPad === pad) ? null : pad;
  cmpRenderTabela();
  // Atualiza outline visual dos cards
  ["SOBREPOE","AGREGA_B","AGREGA_A","ABERTO"].forEach(function(p){
    var el = document.getElementById("cmp-card-"+p);
    if(el){
      el.style.outline = (cmpFiltroPad === p) ? "2px solid var(--amber)" : "none";
      el.style.outlineOffset = "2px";
    }
  });
}

// candAtivoCmp: o candidato A da comparação (referência atual quando o modal está aberto)
var candAtivoCmp = null;
function abrirAliancas(cand){
  if(!cand) return;
  candAtivoCmp = cand;
  cmpCandB = null;
  cmpFiltroPad = null;
  // Limpa caches da renderização anterior (evita labels stale ao trocar A)
  cmpDeltasCache = null;
  cmpNomesCache = {nA:"A", nB:"B"};
  var _tbody = document.getElementById("cmp-tbody");
  var _thead = document.getElementById("cmp-thead");
  var _quad  = document.getElementById("cmp-quad-cards");
  var _vere  = document.getElementById("cmp-veredito");
  if(_tbody) _tbody.innerHTML = "";
  if(_thead) _thead.innerHTML = "";
  if(_quad)  _quad.innerHTML  = "";
  if(_vere)  _vere.innerHTML  = "";
  // Reset visual do candidato B (caso tenha sido aberto antes)
  var _bTag = document.getElementById("cmp-b-tag");
  if(_bTag){ _bTag.style.display = "none"; _bTag.innerHTML = ""; }
  document.getElementById("cmp-b-search").style.display = "";
  var _totA = (cand.total||0).toLocaleString("pt-BR");
  document.getElementById("cmp-a-nome").innerHTML = "<span style='color:var(--muted);font-weight:400;margin-right:5px'>"+_totA+" votos ·</span>"+cand.nome;
  var CC3={progressista:"#A32D2D",moderado:"#0F6E56",liberal_conservador:"#854F0B",outros:"#6B7280"};
  var CN3={progressista:"Progressista",moderado:"Moderado",liberal_conservador:"Liberal/Cons.",outros:"Outros"};
  var _bp="font-size:9px;padding:2px 7px;border-radius:10px;";
  var Sbg={progressista:_bp+"background:#FCEBEB;color:#791F1F",moderado:_bp+"background:#E1F5EE;color:#085041",
            liberal_conservador:_bp+"background:#FAEEDA;color:#633806",outros:_bp+"background:#F1EFE8;color:#444"};
  document.getElementById("cmp-a-dot").style.background = CC3[cand.campo]||"#888";
  document.getElementById("cmp-a-badge").style.cssText = Sbg[cand.campo]||_bp;
  document.getElementById("cmp-a-badge").textContent = CN3[cand.campo]||"";
  document.getElementById("cmp-b-search").value = "";
  document.getElementById("cmp-b-results").style.display = "none";
  document.getElementById("cmp-content").style.display = "none";
  document.getElementById("cmp-pick-hint").style.display = "block";
  document.getElementById("cmp-corr").textContent = "";
  var _cl2={GOVERNADOR:"Governador",SENADOR:"Senador",DEPUTADO_FEDERAL:"Dep. Federal",DEPUTADO_DISTRITAL:"Dep. Distrital"};
  var _subEl=document.getElementById("cmp-a-sub");
  if(_subEl) _subEl.innerHTML="<strong style='color:var(--txt);font-weight:600'>"+(_cl2[cand.cargo]||cand.cargo)+"</strong> · "+cand.partido;
  document.getElementById("cmp-overlay").style.display = "flex";
  document.body.style.overflow = "hidden";
  setTimeout(function(){ document.getElementById("cmp-b-search").focus(); }, 100);
}

function cmpFechar() {
  document.getElementById("cmp-overlay").style.display = "none";
  document.body.style.overflow = "";
  var bTag = document.getElementById("cmp-b-tag");
  if(bTag) bTag.style.display = "none";
  document.getElementById("cmp-b-search").style.display = "";
  document.getElementById("cmp-b-search").value = "";
}

function cmpBuscar(q) {
  if(!candAtivoCmp) return;
  var res = document.getElementById("cmp-b-results");
  q = (q||"").toLowerCase().trim();
  var lista = A5_CANDS.filter(function(c){
    return c.nome !== candAtivoCmp.nome
      && (q.length < 2 || c.nome.toLowerCase().indexOf(q) >= 0 || c.partido.toLowerCase().indexOf(q) >= 0);
  }).slice(0, 12);
  if(!lista.length){ res.style.display="none"; return; }
  var CC3={progressista:"#A32D2D",moderado:"#0F6E56",liberal_conservador:"#854F0B",outros:"#6B7280"};
  // Usar DOM API para evitar escaping de aspas
  var _cl3={GOVERNADOR:"Governador",SENADOR:"Senador",DEPUTADO_FEDERAL:"Dep. Federal",DEPUTADO_DISTRITAL:"Dep. Distrital"};
  res.innerHTML = "";
  lista.forEach(function(c){
    var tot = c.total >= 1000 ? Math.round(c.total/1000)+"k" : (c.total||0).toLocaleString("pt-BR");
    var item = document.createElement("div");
    item.style.cssText = "padding:8px 14px;cursor:pointer;display:flex;align-items:center;gap:8px;border-bottom:0.5px solid var(--bd)";
    item.dataset.nome = c.nome;
    item.className = "cmp-b-item";
    var bar = document.createElement("div");
    bar.style.cssText = "width:3px;height:14px;border-radius:1px;background:"+(CC3[c.campo]||"#888")+";flex-shrink:0";
    var info = document.createElement("div");
    var nome_div = document.createElement("div");
    nome_div.style.cssText = "font-size:12px;font-weight:500";
    nome_div.textContent = c.nome;
    var sub_div = document.createElement("div");
    sub_div.style.cssText = "font-size:10px;color:var(--muted)";
    sub_div.textContent = (_cl3[c.cargo]||c.cargo) + " · " + c.partido + " · " + tot + " votos";
    info.appendChild(nome_div);
    info.appendChild(sub_div);
    item.appendChild(bar);
    item.appendChild(info);
    item.addEventListener("click", function(){
      cmpSelecionarB(this.dataset.nome);
    });
    res.appendChild(item);
  });
  res.style.display = "block";
}

function cmpSelecionarB(nome) {
  cmpCandB = A5_CANDS.find(function(c){ return c.nome === nome; });
  if(!cmpCandB) return;
  document.getElementById("cmp-b-results").style.display = "none";
  // Atualizar visual do header com candidato B
  var CC3={progressista:"#A32D2D",moderado:"#0F6E56",liberal_conservador:"#854F0B",outros:"#6B7280"};
  var Sbg={progressista:"background:#FCEBEB;color:#791F1F",moderado:"background:#E1F5EE;color:#085041",
           liberal_conservador:"background:#FAEEDA;color:#633806",outros:"background:#F1EFE8;color:#444"};
  var CN3={progressista:"Progressista",moderado:"Moderado",liberal_conservador:"Liberal/Cons.",outros:"Outros"};
  var cl2={GOVERNADOR:"Governador",SENADOR:"Senador",DEPUTADO_FEDERAL:"Dep. Federal",DEPUTADO_DISTRITAL:"Dep. Distrital"};
  var srch = document.getElementById("cmp-b-search");
  srch.style.display = "none";
  // Inserir tag do candidato B no lugar do input
  var bTag = document.getElementById("cmp-b-tag");
  if(!bTag){
    bTag = document.createElement("div");
    bTag.id = "cmp-b-tag";
    bTag.style.cssText = "display:flex;align-items:center;gap:6px";
    srch.parentNode.insertBefore(bTag, srch);
  }
  bTag.onclick = null;
  bTag.style.cursor = "default";
  bTag.title = "";
  bTag.innerHTML = "";
  var _SbgL={progressista:"background:#FCEBEB;color:#791F1F",moderado:"background:#E1F5EE;color:#085041",liberal_conservador:"background:#FAEEDA;color:#633806",outros:"background:#F1EFE8;color:#444"};
  var _d2=document.createElement("span"); _d2.style.cssText="font-size:14px;font-weight:700;line-height:1;color:"+(CC3[cmpCandB.campo]||"#888")+";flex-shrink:0;width:14px;text-align:center"; _d2.textContent="✶";
  var _n2=document.createElement("span"); _n2.style.cssText="font-size:13px;font-weight:500";
  var _totB=(cmpCandB.total||0).toLocaleString("pt-BR");
  _n2.innerHTML="<span style='color:var(--muted);font-weight:400;margin-right:5px'>"+_totB+" votos ·</span>"+cmpCandB.nome;
  var _b2=document.createElement("span"); _b2.style.cssText="font-size:9px;padding:2px 7px;border-radius:10px;"+(_SbgL[cmpCandB.campo]||"background:#F1EFE8;color:#444"); _b2.textContent=CN3[cmpCandB.campo]||cmpCandB.campo;
  var _s2=document.createElement("span"); _s2.style.cssText="font-size:11px;color:var(--muted)"; _s2.innerHTML="<strong style='color:var(--txt);font-weight:600'>"+(cl2[cmpCandB.cargo]||"")+"</strong> · "+cmpCandB.partido;
  var _e2=document.createElement("span"); _e2.textContent="×"; _e2.title="Limpar e escolher outro"; _e2.style.cssText="font-size:18px;line-height:1;color:var(--muted);cursor:pointer;padding:0 4px;margin-left:2px;border-radius:4px;font-weight:400";
  _e2.onmouseenter=function(){ this.style.color="var(--txt)"; this.style.background="var(--s2)"; };
  _e2.onmouseleave=function(){ this.style.color="var(--muted)"; this.style.background="transparent"; };
  _e2.onclick=function(ev){
    ev.stopPropagation();
    cmpCandB = null;
    document.getElementById("cmp-b-tag").style.display="none";
    document.getElementById("cmp-content").style.display="none";
    document.getElementById("cmp-pick-hint").style.display="block";
    srch.style.display="";
    srch.value="";
    srch.focus();
  };
  [_d2,_n2,_b2,_s2,_e2].forEach(function(el){bTag.appendChild(el);});
  bTag.style.display = "flex";
  // Esconder placeholder e mostrar conteúdo da comparação
  document.getElementById("cmp-pick-hint").style.display = "none";
  document.getElementById("cmp-content").style.display = "block";
  cmpRenderizar(candAtivoCmp, cmpCandB);
}

function pearson(xs, ys) {
  var n = xs.length; if(n < 2) return 0;
  var mx = xs.reduce(function(s,v){return s+v;},0)/n;
  var my = ys.reduce(function(s,v){return s+v;},0)/n;
  var num=0, dx=0, dy=0;
  for(var i=0;i<n;i++){
    num += (xs[i]-mx)*(ys[i]-my);
    dx  += (xs[i]-mx)*(xs[i]-mx);
    dy  += (ys[i]-my)*(ys[i]-my);
  }
  return (dx*dy > 0) ? num/Math.sqrt(dx*dy) : 0;
}

function cmpRenderizar(cA, cB) {
  // Reset sort/filtro ao trocar de candidato B
  cmpSortCol = "delta"; cmpSortAsc = false;
  var fOld = document.getElementById("cmp-filtro-ra");
  if(fOld) fOld.value = "";
  var CC3={progressista:"#A32D2D",moderado:"#0F6E56",liberal_conservador:"#854F0B",outros:"#6B7280"};
  var corA = CC3[cA.campo]||"#888";
  var corB = CC3[cB.campo]||"#185FA5";
  var rasA = cA.ras||{}, rasB = cB.ras||{};
  var RAs = Object.keys(rasA).filter(function(r){ return rasB[r]; });
  var mesmoCampo=(cA.campo===cB.campo);
  var mesmoCargo=(cA.cargo===cB.cargo);
  // Métrica base: share interno (% do total do candidato). Mesma escala pra qualquer cargo.
  var totA=cA.total||1, totB=cB.total||1;
  var ppA = RAs.map(function(r){ return (rasA[r].v||0)/totA*100; });
  var ppB = RAs.map(function(r){ return (rasB[r].v||0)/totB*100; });
  function fpt(v){ return v.toFixed(1).replace(".",","); }
  var nA=cA.nome.split(" ")[0], nB=cB.nome.split(" ")[0];

  // Métricas
  var r = pearson(ppA, ppB);
  var deltas_vals = RAs.map(function(_,i){ return ppA[i]-ppB[i]; });
  var mean_d = deltas_vals.reduce(function(s,v){return s+v;},0)/(deltas_vals.length||1);
  var std_d  = Math.sqrt(deltas_vals.reduce(function(s,v){return s+(v-mean_d)*(v-mean_d);},0)/(deltas_vals.length||1));
  var pct_a_lidera = Math.round(deltas_vals.filter(function(v){return v>0;}).length/(deltas_vals.length||1)*100);
  var pctB = 100 - pct_a_lidera;
  var isMaioria=(cA.cargo==="GOVERNADOR"||cA.cargo==="SENADOR");
  var limUnif=isMaioria?3:5, limEsp=isMaioria?8:12;
  var dispLabel=std_d<limUnif?"baixa":std_d<limEsp?"moderada":"alta";

  // Padrão por RA — classificação por força (Reduto+Base forte = "forte"; resto = "não forte")
  // Quatro quadrantes:
  //   SOBREPOE: ambos fortes  → mesmo cargo: canibaliza · cross-cargo: chapa forte
  //   AGREGA_B: A forte, B não → A traz a base pra aliança
  //   AGREGA_A: B forte, A não → B traz a base pra aliança
  //   ABERTO:   nenhum forte   → terreno aberto, aliança não resolve aqui
  function _isForte(s){ return s==="REDUTO" || s==="BASE FORTE"; }
  // Performance em pp (delta percentual sobre o esperado pelo tamanho da RA)
  function _perfPp(r){ return (r && r.idx != null) ? (r.idx - 1) * 100 : null; }
  var deltas = RAs.map(function(r2,i){
    var sA=(rasA[r2]||{}).s||"", sB=(rasB[r2]||{}).s||"";
    var fA=_isForte(sA), fB=_isForte(sB);
    var pad = fA&&fB ? "SOBREPOE" : (fA && !fB ? "AGREGA_B" : (!fA && fB ? "AGREGA_A" : "ABERTO"));
    var perfA = _perfPp(rasA[r2]);
    var perfB = _perfPp(rasB[r2]);
    var dPerf = (perfA != null && perfB != null) ? (perfA - perfB) : 0;
    return {ra:r2, ppA:ppA[i], ppB:ppB[i],
            perfA:perfA, perfB:perfB, delta:dPerf,
            vA:(rasA[r2].v||0), vB:(rasB[r2].v||0),
            sA:sA, sB:sB, padrao:pad};
  }).sort(function(a,b){ return b.delta-a.delta; });

  // Contagem por quadrante
  var qCnt = {SOBREPOE:0, AGREGA_B:0, AGREGA_A:0, ABERTO:0};
  deltas.forEach(function(d){ qCnt[d.padrao]++; });
  var qTot = deltas.length || 1;

  // Verificar se há votos suficientes para análise
  var totalA = cA.total||0, totalB = cB.total||0;
  var minVotos = isMaioria ? 10000 : 500;
  var semDados = totalA < minVotos || totalB < minVotos;
  var maxPp = Math.max.apply(null, ppA.concat(ppB).map(Math.abs));

  // ============== VEREDITO + KPI CARDS DE QUADRANTES ==============
  // Lógica: cargo+campo determinam o tipo de aliança possível; quadrantes mostram a geografia.
  var nSob = qCnt.SOBREPOE, nAggB = qCnt.AGREGA_B, nAggA = qCnt.AGREGA_A, nAb = qCnt.ABERTO;
  var nFortesA = nSob + nAggB; // RAs onde A é forte
  var nFortesB = nSob + nAggA; // RAs onde B é forte
  var pctSob = qTot ? Math.round(nSob/qTot*100) : 0;
  var totalFortes = nSob + nAggA + nAggB;

  // Veredito descritivo (sem julgamento político — só leitura territorial)
  var veredito = "";
  if(semDados || maxPp < 0.5){
    veredito = "<strong>Volume insuficiente</strong> · "+nA+": "+totalA.toLocaleString("pt-BR")+" votos · "+nB+": "+totalB.toLocaleString("pt-BR")+" votos. Sem expressão eleitoral suficiente para análise territorial confiável.";
  } else if(totalFortes === 0){
    veredito = "<strong>Sem regiões fortes</strong> · em nenhuma das 33 RAs algum dos dois alcançou Performance ≥ +15% (Reduto ou Base forte). A leitura territorial deste cruzamento é limitada.";
  } else if(mesmoCargo && mesmoCampo){
    if(nSob > (nAggA+nAggB)){
      veredito = "<strong>Mesmo cargo, mesmo campo · bases sobrepostas</strong> · "+nSob+" RAs com Performance ≥ +15% nos dois vs "+(nAggA+nAggB)+" complementares. Disputam o mesmo voto nas mesmas regiões — voto não migra entre candidatos do mesmo cargo+campo.";
    } else if(nAggA + nAggB > 0){
      veredito = "<strong>Mesmo cargo, mesmo campo · geografia complementar</strong> · "+nAggB+" RAs onde só "+nA+" é forte, "+nAggA+" onde só "+nB+", "+nSob+" sobrepostas. Cada candidato concentra força em RAs distintas; voto não migra entre eles, mas cobrem territórios diferentes do campo.";
    } else {
      veredito = "<strong>Mesmo cargo, mesmo campo · bases coincidentes</strong> · "+nSob+" RAs sobrepostas, sem complementaridade. Bases idênticas no mesmo cargo+campo.";
    }
  } else if(mesmoCargo && !mesmoCampo){
    veredito = "<strong>Mesmo cargo, campos distintos · públicos não-substituíveis</strong> · "+nSob+" RAs de sobreposição. Cada eleitor escolhe um, voto não migra. As sobreposições refletem densidade eleitoral comum, não disputa pelo mesmo voto.";
  } else if(!mesmoCargo && mesmoCampo){
    if(nSob > (nAggA+nAggB)){
      veredito = "<strong>Cargos diferentes, mesmo campo · bases coincidentes</strong> · "+nSob+" RAs com ambos ≥ +15%. Reforço territorial sem disputa direta — a transferência depende da disposição do eleitor a votar nos dois cargos.";
    } else {
      veredito = "<strong>Cargos diferentes, mesmo campo · bases complementares</strong> · "+nSob+" RAs coincidentes, "+nAggB+" só com "+nA+" forte, "+nAggA+" só com "+nB+" forte. Cada um cobre território onde o outro não chega.";
    }
  } else {
    // !mesmoCargo && !mesmoCampo
    if(nSob > 0){
      veredito = "<strong>Cargos e campos distintos · sobreposição parcial</strong> · "+nSob+" RAs onde ambos ≥ +15%. Concorrência por densidade eleitoral comum, sem disputa direta de voto.";
    } else {
      veredito = "<strong>Cargos e campos distintos · territórios distintos</strong> · 0 sobreposição forte. "+nA+" forte em "+nAggB+" RAs, "+nB+" em "+nAggA+". Os redutos não coincidem — leitura territorial baixa para análise de aliança.";
    }
  }
  document.getElementById("cmp-veredito").innerHTML = veredito;

  // KPI cards (clicáveis — filtram a tabela abaixo)
  function _qpct(n){ return qTot ? Math.round(n/qTot*100)+"%" : "0%"; }
  var kpiBase = "background:var(--s1);border:0.5px solid var(--bd2);border-radius:8px;padding:10px 12px;display:flex;flex-direction:column;gap:3px;min-width:0;cursor:pointer;transition:background .12s";
  var kpiNum = "font-size:22px;font-weight:600;line-height:1";
  var kpiLbl = "font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.5px";
  var kpiSub = "font-size:9px;color:var(--muted);line-height:1.3;margin-top:2px";
  function _kpiHtml(id, pad, label, n, color, sub){
    return "<div id='cmp-card-"+id+"' onclick='cmpToggleFiltro(&quot;"+pad+"&quot;)' title='Clique para filtrar a tabela' style='"+kpiBase+";border-left:3px solid "+color+"'>"
      +"<div style='"+kpiLbl+"'>"+label+"</div>"
      +"<div style='"+kpiNum+";color:"+color+"'>"+n+" <span style='font-size:11px;font-weight:400;color:var(--muted)'>RAs · "+_qpct(n)+"</span></div>"
      +"<div style='"+kpiSub+"'>"+sub+"</div>"
    +"</div>";
  }
  document.getElementById("cmp-quad-cards").innerHTML =
    _kpiHtml("SOBREPOE","SOBREPOE","Sobreposição", nSob, "#B45309", "Ambos com Performance ≥ +15%")
    + _kpiHtml("AGREGA_B","AGREGA_B", nA+" agrega", nAggB, corA, nA+" forte, "+nB+" abaixo")
    + _kpiHtml("AGREGA_A","AGREGA_A", nB+" agrega", nAggA, corB, nB+" forte, "+nA+" abaixo")
    + _kpiHtml("ABERTO","ABERTO","Terreno aberto", nAb, "#6B7280", "Nenhum com Performance ≥ +15%");
  // Reaplicar outline do filtro ativo (caso esteja)
  ["SOBREPOE","AGREGA_B","AGREGA_A","ABERTO"].forEach(function(p){
    var el = document.getElementById("cmp-card-"+p);
    if(el){
      el.style.outline = (cmpFiltroPad === p) ? "2px solid var(--amber)" : "none";
      el.style.outlineOffset = "2px";
    }
  });

  // Tabela — header com sort + filtro inline (mesmo padrão de Candidatos/Estratégia)
  var thB = "padding:6px 10px;font-size:10px;letter-spacing:1px;text-transform:uppercase;color:var(--muted);font-weight:700;background:var(--s1);border-bottom:0.5px solid var(--bd2);position:sticky;top:0;z-index:4;white-space:nowrap;cursor:pointer;user-select:none";
  var cargoLbl3={GOVERNADOR:"Governador",SENADOR:"Senador",DEPUTADO_FEDERAL:"Dep. Federal",DEPUTADO_DISTRITAL:"Dep. Distrital"};
  var lblCargoA = cargoLbl3[cA.cargo]||cA.cargo;
  var lblCargoB = cargoLbl3[cB.cargo]||cB.cargo;
  var subVotosA = "<div style='font-size:8px;font-weight:500;color:var(--muted);text-transform:none;letter-spacing:0;margin-top:1px'>"+lblCargoA+"</div>";
  var subVotosB = "<div style='font-size:8px;font-weight:500;color:var(--muted);text-transform:none;letter-spacing:0;margin-top:1px'>"+lblCargoB+"</div>";
  var ttPerf = "<span class='tt' style='text-transform:none;letter-spacing:0;font-weight:400;color:var(--muted);font-size:10px;margin-left:3px'><span class='tt-icon'>?</span><span class='tt-box'>Performance: quanto a RA entrega de votos ao candidato comparado ao esperado pelo tamanho do território. +30% ou mais = Reduto · +15% a +30% = Base forte · −15% a +15% = Esperado · −15% a −30% = Base fraca · ≤ −30% = Ausência. Comparável entre candidatos com volumes muito diferentes.</span></span>";
  var ttDelta = "<span class='tt' style='text-transform:none;letter-spacing:0;font-weight:400;color:var(--muted);font-size:10px;margin-left:3px'><span class='tt-icon'>?</span><span class='tt-box'>Diferença em pp entre as Performances. Positivo: a RA performa mais para "+nA+". Negativo: performa mais para "+nB+".</span></span>";
  var ttPad = "<span class='tt' style='text-transform:none;letter-spacing:0;font-weight:400;color:var(--muted);font-size:10px;margin-left:3px'><span class='tt-icon'>?</span><span class='tt-box'>Classificação da RA pela Performance ≥ +15% (Reduto/Base forte) de cada candidato. Sobreposição: ambos fortes. "+nA+" agrega: só "+nA+" é forte. "+nB+" agrega: só "+nB+" é forte. Aberto: nenhum dos dois é forte.</span></span>";
  document.getElementById("cmp-thead").innerHTML =
    "<tr>"
    +"<th onclick='cmpSrt(&quot;ra&quot;)' style='"+thB+"text-align:left;left:0;z-index:20;min-width:160px'>Região <span class='sa' id='cmp-s-ra'></span><input class='th-filter' id='cmp-filtro-ra' placeholder='filtrar...' oninput='cmpFiltrarRA()' onclick='event.stopPropagation()'></th>"
    +"<th onclick='cmpSrt(&quot;padrao&quot;)' style='"+thB+"text-align:left;min-width:130px'>Padrão"+ttPad+" <span class='sa' id='cmp-s-padrao'></span></th>"
    +"<th onclick='cmpSrt(&quot;vA&quot;)' style='"+thB+"text-align:right'>Votos "+nA+" <span class='sa' id='cmp-s-vA'></span>"+subVotosA+"</th>"
    +"<th onclick='cmpSrt(&quot;perfA&quot;)' style='"+thB+"text-align:right'>Performance "+nA+ttPerf+" <span class='sa' id='cmp-s-perfA'></span></th>"
    +"<th onclick='cmpSrt(&quot;vB&quot;)' style='"+thB+"text-align:right'>Votos "+nB+" <span class='sa' id='cmp-s-vB'></span>"+subVotosB+"</th>"
    +"<th onclick='cmpSrt(&quot;perfB&quot;)' style='"+thB+"text-align:right'>Performance "+nB+ttPerf+" <span class='sa' id='cmp-s-perfB'></span></th>"
    +"<th onclick='cmpSrt(&quot;delta&quot;)' style='"+thB+"text-align:right'>Δ Performance"+ttDelta+" <span class='sa' id='cmp-s-delta'></span></th>"
    +"</tr>";

  // Cache pra renderizações subsequentes (filtro/sort)
  cmpDeltasCache = deltas;
  cmpCorACache = corA;
  cmpCorBCache = corB;
  cmpNomesCache = {nA: nA, nB: nB};
  cmpRenderTabela();
}

var cmpSortCol = "padrao", cmpSortAsc = false;
var cmpDeltasCache = null, cmpCorACache = "#888", cmpCorBCache = "#185FA5";
var cmpNomesCache = {nA:"A", nB:"B"};

function cmpSrt(col){
  if(cmpSortCol===col) cmpSortAsc = !cmpSortAsc;
  else { cmpSortCol = col; cmpSortAsc = (col==="ra"); }
  cmpRenderTabela();
}

function cmpFiltrarRA(){ cmpRenderTabela(); }

function cmpRenderTabela(){
  var deltas = cmpDeltasCache;
  if(!deltas) return;
  var corA = cmpCorACache, corB = cmpCorBCache;
  var nA = cmpNomesCache.nA, nB = cmpNomesCache.nB;
  function fpt2(v){ return v.toFixed(1).replace(".",","); }

  // Filtro inline (busca por RA + filtro por padrão dos cards)
  var fIn = document.getElementById("cmp-filtro-ra");
  var qRA = (fIn && fIn.value || "").trim().toLowerCase();
  var lista = deltas.slice();
  if(cmpFiltroPad){ lista = lista.filter(function(d){ return d.padrao === cmpFiltroPad; }); }
  if(qRA) lista = lista.filter(function(d){ return d.ra.toLowerCase().indexOf(qRA) >= 0; });

  // Sort
  var col = cmpSortCol, asc = cmpSortAsc ? 1 : -1;
  // Ordem natural pra padrão: SOBREPOE > AGREGA_B > AGREGA_A > ABERTO
  var padOrd = {"SOBREPOE":4, "AGREGA_B":3, "AGREGA_A":2, "ABERTO":1};
  lista.sort(function(a,b){
    var va, vb;
    if(col==="ra"){ return a.ra.localeCompare(b.ra,"pt-BR") * asc; }
    if(col==="padrao"){
      var diff = (padOrd[a.padrao]||0) - (padOrd[b.padrao]||0);
      if(diff !== 0) return diff * asc;
      return (b.delta - a.delta);  // tiebreak por delta decrescente
    }
    if(col==="vA"){ va=a.vA; vb=b.vA; }
    else if(col==="vB"){ va=a.vB; vb=b.vB; }
    else if(col==="perfA"){ va=(a.perfA!=null?a.perfA:-9999); vb=(b.perfA!=null?b.perfA:-9999); }
    else if(col==="perfB"){ va=(a.perfB!=null?a.perfB:-9999); vb=(b.perfB!=null?b.perfB:-9999); }
    else { va=a.delta; vb=b.delta; }
    return (va-vb) * asc;
  });

  // Atualizar setas
  var arrows = ["ra","padrao","vA","perfA","vB","perfB","delta"];
  arrows.forEach(function(c){
    var el = document.getElementById("cmp-s-"+c);
    if(el) el.textContent = (cmpSortCol===c) ? (cmpSortAsc?"▲":"▼") : "";
  });

  // Badges de padrão
  var padLbl = {
    "SOBREPOE":   {txt:"Sobreposição", bg:"#FEF3C7", color:"#B45309"},
    "AGREGA_B":   {txt:nA+" agrega",   bg:"#FEE7E0", color:corA},
    "AGREGA_A":   {txt:nB+" agrega",   bg:"#FEE7E0", color:corB},
    "ABERTO":     {txt:"Aberto",       bg:"#F1EFE8", color:"#6B7280"}
  };

  var tbody = lista.map(function(d){
    var dStr = d.delta > 0 ? "+"+fpt2(d.delta)+"pp" : fpt2(d.delta)+"pp";
    var dCol = d.delta > 0.5 ? corA : d.delta < -0.5 ? corB : "var(--muted)";
    var td = "padding:7px 10px;font-size:12px;border-bottom:0.5px solid var(--bd2);";
    var p = padLbl[d.padrao] || padLbl.ABERTO;
    var padBg = (d.padrao==="AGREGA_B") ? "background:"+p.color+"22" : (d.padrao==="AGREGA_A") ? "background:"+p.color+"22" : "background:"+p.bg;
    var padBadge = "<span style='display:inline-block;font-size:10px;padding:2px 8px;border-radius:10px;font-weight:500;"+padBg+";color:"+p.color+"'>"+p.txt+"</span>";
    function _perfTxt(p){
      if(p==null) return "<span style='color:var(--muted)'>—</span>";
      var sign = p >= 0 ? "+" : "";
      var col = p >= 15 ? "#085041" : p <= -15 ? "#791F1F" : "var(--muted)";
      return "<span style='color:"+col+";font-weight:500'>"+sign+fpt2(p)+"%</span>";
    }
    return "<tr>"
      +"<td style='"+td+"font-weight:500'>"+d.ra+"</td>"
      +"<td style='"+td+"'>"+padBadge+"</td>"
      +"<td style='"+td+"text-align:right'>"+d.vA.toLocaleString("pt-BR")+"</td>"
      +"<td style='"+td+"text-align:right'>"+_perfTxt(d.perfA)+"</td>"
      +"<td style='"+td+"text-align:right'>"+d.vB.toLocaleString("pt-BR")+"</td>"
      +"<td style='"+td+"text-align:right'>"+_perfTxt(d.perfB)+"</td>"
      +"<td style='"+td+"text-align:right;color:"+dCol+";font-weight:500'>"+dStr+"</td>"
      +"</tr>";
  }).join("");
  document.getElementById("cmp-tbody").innerHTML = tbody;
}

function candRenderStats(cargo) {
  var el=document.getElementById("cand-stats-bar");
  if(!el) return;
  var cands=A5_CANDS.filter(function(c){return cargo==="all"||c.cargo===cargo;});
  var totalV=cands.reduce(function(s,c){return s+(c.total||0);},0);
  var sorted=cands.slice().sort(function(a,b){return (b.total||0)-(a.total||0);});
  var top5V=sorted.slice(0,5).reduce(function(s,c){return s+(c.total||0);},0);
  var pulv=totalV>0?Math.round(top5V/totalV*100):0;
  var vagas={DEPUTADO_FEDERAL:8,DEPUTADO_DISTRITAL:24}[cargo];
  var qe=vagas&&totalV>0?Math.floor(totalV/vagas):null;
  var orfaos=vagas?sorted.slice(vagas).reduce(function(s,c){return s+(c.total||0);},0):null;
  function fK(v){return v>=1000?Math.round(v/1000)+"k":v.toLocaleString("pt-BR");}
  var s2=qe
    ?"<div class='cand-stat-card'><div class='cand-stat-lbl'>Quociente eleitoral</div><div class='cand-stat-val'>"+qe.toLocaleString("pt-BR")+"</div><div class='cand-stat-sub'>votos · "+vagas+" vagas</div></div>"
    :"<div class='cand-stat-card'><div class='cand-stat-lbl'>Sistema</div><div class='cand-stat-val' style='font-size:13px;margin-top:3px'>Maioria simples</div><div class='cand-stat-sub'>o mais votado vence</div></div>";
  var s3=orfaos!=null
    ?"<div class='cand-stat-card'><div class='cand-stat-lbl'>Votos órfãos</div><div class='cand-stat-val' style='color:#854F0B'>"+fK(orfaos)+"</div><div class='cand-stat-sub'>de não-eleitos neste cargo</div></div>"
    :"";
  el.innerHTML=
    "<div class='cand-stat-card'><div class='cand-stat-lbl'>Candidatos</div><div class='cand-stat-val'>"+cands.length+"</div><div class='cand-stat-sub'>disputaram no DF</div></div>"
    +s2+s3
    +"<div class='cand-stat-card'><div class='cand-stat-lbl'>Pulverização</div><div class='cand-stat-val'>"+pulv+"%</div><div class='cand-stat-sub'>concentrado no top 5</div></div>";
}

"""

if __name__ == "__main__":
    main()
