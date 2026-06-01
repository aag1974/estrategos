"""
gerar_estrategos.py — gerador unificado do dashboard Estrategos.

Lê `estrategos_template.html` (com 9 placeholders), gera os dados, substitui e
escreve `index.html`.

Substitui o build chain antigo (fase4_v2 → injeta_geopolitica → injeta_candidato).
"""
import json, base64, csv, time, secrets, unicodedata, re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
import pandas as pd
import numpy as np

from classificacao_base import carregar_aptos_por_ra, classificar_ras

# ──────────────────────────────────────────────────────────────────────────
#  Caminhos
# ──────────────────────────────────────────────────────────────────────────
TEMPLATE     = Path("estrategos_template.html")
OUTPUT       = Path("index.html")
CRED         = Path("credenciais.json")
GEOJSON_PATH = Path("Limite_RA_20190.json")
CACHE        = Path("dados_tse_cache")
DIR_F2       = Path("outputs_fase2")
DIR_F3       = Path("outputs_fase3")
DIR_F3C      = Path("outputs_fase3c")
CSV_GC       = Path("outputs_fase3c/votos_candidato_ra.csv")
PESQUISAS_JSON = Path("outputs_pesquisas/pesquisas_df.json")

MIN_VOTOS_GC = 50  # mínimo de votos pro candidato entrar em GC_DATA

# ──────────────────────────────────────────────────────────────────────────
#  Mapeamentos políticos (campo, partido, cargo)
# ──────────────────────────────────────────────────────────────────────────
NUMERO_CAMPO = {
    13: "progressista", 12: "progressista", 40: "progressista",
    50: "progressista", 65: "progressista", 18: "progressista",
    43: "progressista", 77: "progressista", 70: "progressista",
    15: "moderado",     45: "moderado",     23: "moderado",
    55: "moderado",     20: "moderado",     51: "moderado",
    22: "liberal_conservador", 11: "liberal_conservador",
    10: "liberal_conservador", 44: "liberal_conservador",
    30: "liberal_conservador", 14: "liberal_conservador",
    25: "liberal_conservador", 28: "liberal_conservador",
}

NOME_CAMPO_MAJOR = {
    "IBANEIS ROCHA":   "moderado",
    "LEANDRO GRASS":   "progressista",
    "JOSE EDMAR":      "moderado",
    "IZALCI LUCAS":    "liberal_conservador",
    "DAMARES ALVES":   "liberal_conservador",
    "ROGERIO CORREIA": "progressista",
    "LEILA BARROS":    "moderado",
    "FABIO FELIX":     "progressista",
    # Presidente 2022 (só 2º turno)
    "LULA":            "progressista",
    "BOLSONARO":       "liberal_conservador",
}

NUMERO_PARTIDO = {
    10:"Rep.",11:"PP",12:"PDT",13:"PT",14:"PTB",15:"MDB",
    16:"PSTU",17:"PSL",18:"REDE",20:"PSC",21:"Podemos",22:"PL",
    23:"Cidadania",25:"UB",27:"DC",28:"PRTB",30:"NOVO",
    33:"PMN",36:"Agir",40:"PSB",43:"PV",44:"União",45:"PSDB",
    50:"PSOL",51:"Patriota",55:"PSD",65:"PC do B",70:"Avante",
    77:"Solidariedade",
}

CARGOS_VALIDOS = {
    "GOVERNADOR", "SENADOR",
    "DEPUTADO FEDERAL", "DEPUTADO DISTRITAL",
    "PRESIDENTE",
}

CARGO_NORM = {
    "GOVERNADOR":         "GOVERNADOR",
    "SENADOR":            "SENADOR",
    "DEPUTADO FEDERAL":   "DEPUTADO_FEDERAL",
    "DEPUTADO DISTRITAL": "DEPUTADO_DISTRITAL",
    "PRESIDENTE":         "PRESIDENTE",
}

# Descontinuado em abr/2026 — todas as 33 RAs têm dado próprio (PIP).
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

# Mapeamento nome de RA no GeoJSON → nome canônico no pipeline
GEO_PARA_PIPE = {
    "Plano Piloto":              "Brasília (Plano Piloto)",
    "Sudoeste/ Octogonal":       "Sudoeste/Octogonal",
    "SCIA":                      "SCIA/Estrutural",
    "Sol Nascente/  Pôr do Sol": "Sol Nascente/Pôr do Sol",
}


# ──────────────────────────────────────────────────────────────────────────
#  Carga de dados
# ──────────────────────────────────────────────────────────────────────────
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
        if pd.isna(n):
            continue
        def v(col, dec=1):
            for c in [col, col+"_x", col+"_y"]:
                val = r.get(c)
                if val is not None and not pd.isna(val):
                    try: return round(float(val), dec)
                    except: pass
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
            "pct_jov_mor":  v("MOR_pct_jovem_pop"),
            "pct_ido_mor":  v("MOR_pct_idoso_pop"),
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
            "afin":   round(float(r.get("SCORE_AFINIDADE", r.get("AFIN_COMBO",0)) or 0), 1),
            "conv":   round(float(r.get("SCORE_CONVERSAO",  r.get("CONV", 0)) or 0), 1),
            "massa":  round(float(r.get("SCORE_MASSA",      r.get("MASSA",0)) or 0), 1),
            "logist": round(float(r.get("SCORE_LOGISTICA",  0) or 0), 1),
        }

    for _, r in df_narr.iterrows():
        n = r.get("RA_NOME")
        if n in ras: ras[n]["narrativa"] = str(r.get("NARRATIVA","")).strip()

    if df_campo is not None:
        try:
            df_campo["_cargo_norm"] = (df_campo["DS_CARGO"]
                .str.upper().str.strip()
                .str.replace(" ", "_", regex=False)
                .str.replace("-", "_", regex=False))
            df_campo["QT_VOTOS"] = pd.to_numeric(df_campo.get("QT_VOTOS", 0), errors="coerce").fillna(0)
            df_campo["_campo_norm"] = df_campo["CAMPO"].astype(str).str.lower().str.strip().str.replace(" ", "_", regex=False)

            tot_campo_df = (df_campo.groupby(["_cargo_norm","_campo_norm"])["QT_VOTOS"].sum()).to_dict()
            aptos_df = {n: (ras[n].get("el_aptos") or 0) for n in ras}
            tot_aptos = sum(v for v in aptos_df.values() if v)

            for cargo_str in ["GOVERNADOR","SENADOR","DEPUTADO_FEDERAL","DEPUTADO_DISTRITAL","PRESIDENTE"]:
                sub = df_campo[df_campo["_cargo_norm"] == cargo_str]
                if sub.empty:
                    cargo_alt = cargo_str.replace("_", " ")
                    sub = df_campo[df_campo["DS_CARGO"].str.upper().str.strip() == cargo_alt]
                for _, r in sub.iterrows():
                    n = r.get("RA_NOME")
                    if n not in ras: continue
                    cn = r.get("_campo_norm","")
                    if not cn: continue
                    p  = float(r.get("PCT", 0) or 0)
                    qt = float(r.get("QT_VOTOS", 0) or 0)
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

    # Margem 1º-2º por RA × cargo
    if df_cand is not None:
        try:
            df_cand["QT_VOTOS_RA"] = pd.to_numeric(df_cand["QT_VOTOS_RA"], errors="coerce").fillna(0)
            for n in ras:
                ras[n]["margem"] = {}
            for cargo_str in ["GOVERNADOR","SENADOR","DEPUTADO_FEDERAL","DEPUTADO_DISTRITAL","PRESIDENTE"]:
                sub = df_cand[df_cand["DS_CARGO"] == cargo_str]
                if sub.empty: continue
                tot_ra = sub.groupby("RA_NOME")["QT_VOTOS_RA"].sum().to_dict()
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
                    ras[ra_nome]["margem"][cargo_str] = {
                        "v1": int(v1), "v2": int(v2),
                        "nm1": nm1, "nm2": nm2,
                        "margem_pp": margem_pp,
                        "tot_ra": int(tot),
                    }
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


# ──────────────────────────────────────────────────────────────────────────
#  Candidatos compactos (A5_CANDS) — pipeline primário das seções de votação
# ──────────────────────────────────────────────────────────────────────────
def _nome_curto_fallback(nome):
    """Fallback quando o nome de urna não é encontrado no cadastro TSE.
    Pega primeiro + último sobrenome do nome civil (uppercase)."""
    partes = str(nome).strip().split()
    if len(partes) <= 2:
        return str(nome).strip()
    return partes[0] + " " + partes[-1]


def _carregar_mapa_nome_urna():
    """Lê outputs_tse_2022_DF/consulta_cand_DF.csv e retorna mapa
    {(NM_CANDIDATO, DS_CARGO): NM_URNA_CANDIDATO}.
    Também popula {(NM_CANDIDATO, None): NM_URNA} como fallback quando
    o cargo não bate exatamente."""
    paths = [
        Path("outputs_tse_2022_DF/consulta_cand_DF.csv"),
        CACHE / "consulta_cand_DF.csv",
    ]
    csv_path = next((p for p in paths if p.exists()), None)
    if not csv_path:
        return {}
    mapa = {}
    with open(csv_path, encoding="latin-1") as f:
        rdr = csv.reader(f, delimiter=";")
        header = [c.strip('"') for c in next(rdr)]
        try:
            i_nm   = header.index("NM_CANDIDATO")
            i_urna = header.index("NM_URNA_CANDIDATO")
            i_carg = header.index("DS_CARGO")
        except ValueError:
            return {}
        for row in rdr:
            try:
                nm   = row[i_nm].strip('"').strip()
                urna = row[i_urna].strip('"').strip()
                carg = row[i_carg].strip('"').strip().upper()
            except IndexError:
                continue
            if not nm or not urna:
                continue
            mapa[(nm, carg)] = urna
            mapa.setdefault((nm, None), urna)
    return mapa


def montar_candidatos():
    """
    Extrai candidatos 2022 com votos por RA. Saída usada para A5_CANDS.
    Fonte primária: dados_tse_cache/votacao_secao_2022_DF.csv (ROW por seção).
    Fallback:       candidatos_2022.csv (já agregado por RA).
    """
    # CSV combinado: 4 cargos DF (1T) + Presidente (2T)
    votos_path  = CACHE / "votacao_secao_2022_DF_completo.csv"
    if not votos_path.exists():
        votos_path = CACHE / "votacao_secao_2022_DF.csv"  # fallback p/ ambiente sem presidente
    locais_path = CACHE / "locais_votacao_2022_enriched.csv"

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

    print("   Lendo mapa de seções...", end="", flush=True)
    df_loc = pd.read_csv(locais_path, dtype=str, usecols=["NR_ZONA","NR_SECAO","RA_NOME"])
    df_loc = df_loc.dropna(subset=["RA_NOME"])
    secao_ra = {
        (r["NR_ZONA"].strip(), r["NR_SECAO"].strip()): r["RA_NOME"].strip()
        for _, r in df_loc.iterrows()
    }
    # Override CPP-SIA: seção 9-2022 é o presídio (Trecho 4 SIA), órfã no enriched.
    SECOES_OVERRIDE = {
        ("9", "2022"): "SIA",
    }
    for k, ra in SECOES_OVERRIDE.items():
        secao_ra.setdefault(k, ra)
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
    # Turno: 1T para todos os cargos, exceto Presidente (2T) — DF teve 2T 2022 só pra presidente
    df["DS_CARGO"] = df["DS_CARGO"].str.upper().str.strip()
    df["NR_TURNO"] = df["NR_TURNO"].astype(str).str.strip()
    df = df[df["DS_CARGO"].isin(CARGOS_VALIDOS)].copy()
    df = df[
        ((df["DS_CARGO"] != "PRESIDENTE") & (df["NR_TURNO"] == "1")) |
        ((df["DS_CARGO"] == "PRESIDENTE") & (df["NR_TURNO"] == "2"))
    ].copy()
    df["QT_VOTOS"] = pd.to_numeric(df["QT_VOTOS"], errors="coerce").fillna(0)
    df["NR_ZONA"]  = df["NR_ZONA"].astype(str).str.strip()
    df["NR_SECAO"] = df["NR_SECAO"].astype(str).str.strip()
    df = df[~df["NR_VOTAVEL"].astype(str).str.strip().isin(["95","96","97","98","99"])]
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

    total_cand     = df.groupby(["NM_VOTAVEL","DS_CARGO"])["QT_VOTOS"].sum()
    grp            = df.groupby(["NM_VOTAVEL","DS_CARGO","RA_NOME","CAMPO","PARTIDO"])["QT_VOTOS"].sum().reset_index()
    total_cargo_ra = df.groupby(["DS_CARGO","RA_NOME"])["QT_VOTOS"].sum().to_dict()
    total_campo_ra = df.groupby(["DS_CARGO","RA_NOME","CAMPO"])["QT_VOTOS"].sum().to_dict()

    # Mapa nome civil → nome de urna (cadastro TSE 2022 DF)
    nomes_urna = _carregar_mapa_nome_urna()

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
            cands[key] = {
                "nome":nome,
                "nome_urna": nomes_urna.get((nome, r["DS_CARGO"])) or nomes_urna.get((nome, None)) or _nome_curto_fallback(nome),
                "cargo":cargo,"campo":campo,"partido":part,"total":total_c,"ras":{}
            }
        vt_cargo = int(total_cargo_ra.get((r["DS_CARGO"], ra), 1) or 1)
        vt_campo = int(total_campo_ra.get((r["DS_CARGO"], ra, campo), 1) or 1)
        cands[key]["ras"][ra] = {
            "v":  votos,
            "pe": round(votos / total_c * 100, 2) if total_c else 0,
            "pc": round(votos / vt_cargo * 100, 2),
            "pp": round(votos / vt_campo * 100, 2),
        }

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
    """Fallback de montar_candidatos() a partir do candidatos_2022.csv pré-agregado."""
    df = pd.read_csv(str(csv_path))
    df["DS_CARGO"] = df["DS_CARGO"].str.upper().str.strip()
    df = df[df["DS_CARGO"].isin(CARGOS_VALIDOS)].copy()
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

    nomes_urna = _carregar_mapa_nome_urna()

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
            cands[key] = {
                "nome":nome,
                "nome_urna": nomes_urna.get((nome, r["DS_CARGO"])) or nomes_urna.get((nome, None)) or _nome_curto_fallback(nome),
                "cargo":cargo,"campo":campo,"partido":part,"total":total_c,"ras":{}
            }
        vt_cargo = int(total_cargo_ra.get((r["DS_CARGO"], ra), 1) or 1)
        vt_campo = int(total_campo_ra.get((r["DS_CARGO"], ra, campo), 1) or 1)
        cands[key]["ras"][ra] = {
            "v":  votos,
            "pe": round(votos / total_c * 100, 2) if total_c else 0,
            "pc": round(votos / vt_cargo * 100, 2),
            "pp": round(votos / vt_campo * 100, 2),
        }

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


# ──────────────────────────────────────────────────────────────────────────
#  Estatísticas dos eleitos (VOTOS_ELEITOS, METAS_CAMPO)
# ──────────────────────────────────────────────────────────────────────────
_NUMERO_CAMPO_ELEITOS = {
    10:'moderado',11:'moderado',12:'moderado',13:'progressista',
    14:'progressista',15:'moderado',16:'progressista',17:'progressista',
    20:'moderado',22:'liberal_conservador',23:'moderado',
    25:'liberal_conservador',30:'liberal_conservador',31:'moderado',
    33:'moderado',36:'moderado',40:'progressista',43:'progressista',
    44:'moderado',50:'progressista',55:'moderado',65:'progressista',
    77:'moderado',90:'moderado',
}
_VAGAS_CARGO = {'DEPUTADO DISTRITAL':24,'DEPUTADO FEDERAL':8,'GOVERNADOR':1,'SENADOR':2}
_CARGO_NORM_ELEITOS = {
    'DEPUTADO DISTRITAL':'DEPUTADO_DISTRITAL','DEPUTADO FEDERAL':'DEPUTADO_FEDERAL',
    'GOVERNADOR':'GOVERNADOR','SENADOR':'SENADOR',
}


def _df_eleitos_2022():
    """Carrega candidatos_2022.csv com flag ELEITO marcada para os top-N por cargo."""
    csv_paths = [
        CACHE / "candidatos_2022_ra.csv",
        CACHE.parent / "candidatos_2022.csv",
    ]
    csv_path = next((p for p in csv_paths if p.exists()), None)
    if csv_path is None:
        return None
    df = pd.read_csv(str(csv_path))
    df['CAMPO'] = df['NR_VOTAVEL'].apply(
        lambda x: _NUMERO_CAMPO_ELEITOS.get(int(str(x)[:2]),'outros') if str(x).isdigit() else 'outros')
    for cargo, vagas in _VAGAS_CARGO.items():
        top = (df[df['DS_CARGO']==cargo]
                 .drop_duplicates('NM_VOTAVEL')
                 .sort_values('TOTAL_VOTOS', ascending=False)
                 .head(vagas)['NM_VOTAVEL'].tolist())
        df.loc[df['DS_CARGO']==cargo, 'ELEITO'] = df['NM_VOTAVEL'].isin(top)
    return df


def calcular_votos_eleitos():
    """P25/P50/P75 dos eleitos por cargo|campo|RA."""
    df = _df_eleitos_2022()
    if df is None:
        return {}
    result = {}
    for cargo_raw, _vagas in _VAGAS_CARGO.items():
        for campo in ['moderado','progressista','liberal_conservador']:
            key = _CARGO_NORM_ELEITOS[cargo_raw] + '|' + campo
            sub = df[(df['DS_CARGO']==cargo_raw) & (df['CAMPO']==campo) & (df['ELEITO']==True)]
            n = sub['NM_VOTAVEL'].nunique()
            if n == 0: continue
            ra_stats = {}
            for ra in sub['RA_NOME'].dropna().unique():
                vals = sub[sub['RA_NOME']==ra]['QT_VOTOS'].values
                if len(vals) == 0: continue
                ra_stats[ra] = {
                    'p25': int(np.percentile(vals, 25)),
                    'p50': int(np.percentile(vals, 50)),
                    'p75': int(np.percentile(vals, 75)),
                }
            ra_stats['_n'] = n
            result[key] = ra_stats
    return result


def calcular_metas_campo():
    """Mínimo de votos para eleição por cargo|campo."""
    df = _df_eleitos_2022()
    if df is None:
        return {}
    result = {}
    for cargo_raw in _VAGAS_CARGO:
        for campo in ['moderado','progressista','liberal_conservador']:
            key = _CARGO_NORM_ELEITOS[cargo_raw] + '|' + campo
            sub = (df[(df['DS_CARGO']==cargo_raw) & (df['CAMPO']==campo) & (df['ELEITO']==True)]
                     .drop_duplicates('NM_VOTAVEL').sort_values('TOTAL_VOTOS'))
            if sub.empty: continue
            r = sub.iloc[0]
            result[key] = {'votos': int(r['TOTAL_VOTOS']),
                           'ref':   r['NM_VOTAVEL'].title(),
                           'n':     len(sub)}
    return result


# ──────────────────────────────────────────────────────────────────────────
#  GeoJSON (GEO_DATA)
# ──────────────────────────────────────────────────────────────────────────
def processar_geojson():
    with open(GEOJSON_PATH, encoding="utf-8") as f:
        geo = json.load(f)
    for feat in geo["features"]:
        geo_nome  = feat["properties"]["ra"]
        feat["properties"]["RA_PIPE"] = GEO_PARA_PIPE.get(geo_nome, geo_nome)
    return geo


# ──────────────────────────────────────────────────────────────────────────
#  Candidatos detalhados (GC_DATA) — visão Geopolítica
# ──────────────────────────────────────────────────────────────────────────
def carregar_gc():
    """
    Lê outputs_fase3c/votos_candidato_ra.csv e devolve a lista usada em GC_DATA.
    Cada item: nm, cargo, campo, partido, total, ras=[{ra, votos, pct_cargo,
    pct_campo, idx, status}], status_cnt={status: count}.
    """
    por_cand = defaultdict(lambda: {"meta": None, "ras": []})
    with open(CSV_GC, encoding="utf-8") as f:
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
        if info["meta"]["total"] < MIN_VOTOS_GC:
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


# ──────────────────────────────────────────────────────────────────────────
#  Geração final
# ──────────────────────────────────────────────────────────────────────────
def b64(obj) -> str:
    return base64.b64encode(
        json.dumps(obj, ensure_ascii=True, separators=(",", ":")).encode("utf-8")
    ).decode("ascii")


# ──────────────────────────────────────────────────────────────────────────
#  API de dados estática — arquivo único consumido por sistemas parceiros.
#  Servida pelo GitHub Pages em https://estrategos.opiniao.inf.br/api/<token>/
#  estrategos.json. O <token> é um caminho "secreto" (não é autenticação real:
#  o repo é público e o dashboard já embute a mesma base; serve só pra tirar a
#  URL da vitrine). O token fica em api_token.txt e é reusado entre builds.
# ──────────────────────────────────────────────────────────────────────────
API_BASE      = Path("api")
API_TOKEN     = Path("api_token.txt")
API_DESCRICAO = ("Estrategos — Inteligência Política da Opinião Informação "
                 "Estratégica. Diagnóstico eleitoral por Região Administrativa "
                 "do DF (ciclo 2026), cruzando PDAD 2021 (IPEDF) e TSE 2022.")


def _api_slug(nm):
    s = unicodedata.normalize("NFD", nm or "").encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return s or "candidato"


def _api_token():
    if API_TOKEN.exists():
        t = API_TOKEN.read_text(encoding="utf-8").strip()
        if t:
            return t
    t = secrets.token_hex(16)
    API_TOKEN.write_text(t + "\n", encoding="utf-8")
    return t


def gerar_api(ras, cands_detalhados, votos_eleitos, metas_campo, pesquisas, geo):
    """Grava api/<token>/estrategos.json com toda a base num arquivo único."""
    token = _api_token()

    # slug único por candidato (colisão → sufixo -2, -3, …; ordem = total desc)
    vistos = {}
    candidatos = []
    for c in cands_detalhados:
        base = _api_slug(c.get("nm"))
        slug, n = base, 2
        while slug in vistos:
            slug = f"{base}-{n}"; n += 1
        vistos[slug] = True
        candidatos.append({"slug": slug, **c})

    payload = {
        "schema":     1,
        "produto":    "Estrategos",
        "descricao":  API_DESCRICAO,
        "gerado_em":  datetime.now().isoformat(timespec="seconds"),
        "fontes":     {"socioeconomico": "PDAD 2021 (IPEDF)", "eleitoral": "TSE 2022"},
        "contagens":  {"candidatos": len(candidatos), "ras": len(ras)},
        "candidatos": candidatos,
        "ras":        ras,
        "votos_eleitos": votos_eleitos,
        "metas_campo":   metas_campo,
        "pesquisas":     pesquisas,
        "geo":           geo,
    }

    out_dir = API_BASE / token
    out_dir.mkdir(parents=True, exist_ok=True)
    destino = out_dir / "estrategos.json"
    blob = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    destino.write_text(blob, encoding="utf-8")
    return token, destino, len(blob.encode("utf-8"))


def main():
    t0 = time.time()
    print()
    print("  Estrategos — gerador unificado")
    print("  " + "─" * 38)

    # 1. RAs (D)
    print("  [1/5] Carregando dados das RAs...", end="", flush=True)
    df_ipe, df_mestre, df_narr, df_campo, df_cand = carregar()
    ras = montar_dados(df_ipe, df_mestre, df_narr, df_campo, df_cand)
    n_votos = sum(1 for r in ras.values() if r["votos"])
    print(f"\r  [1/5] RAs montadas           {len(ras)} regiões · votos em {n_votos}")

    # 2. Candidatos (A5_CANDS compacto, GC_DATA detalhado)
    print("  [2/5] Montando candidatos...", end="", flush=True)
    cands_compactos  = montar_candidatos()
    cands_detalhados = carregar_gc()
    print(f"\r  [2/5] Candidatos             A5={len(cands_compactos)} · GC={len(cands_detalhados)}")

    # 3. GeoJSON com dados acoplados em cada feature
    print("  [3/5] Processando GeoJSON...", end="", flush=True)
    geo = processar_geojson()
    for feat in geo["features"]:
        feat["properties"]["dados"] = ras.get(feat["properties"]["RA_PIPE"], {})
    n_inj = sum(1 for f in geo["features"] if f["properties"]["dados"])
    print(f"\r  [3/5] GeoJSON processado     {len(geo['features'])} features · dados em {n_inj}")

    # 4. Substituições no template
    print("  [4/5] Aplicando placeholders...", end="", flush=True)
    template = TEMPLATE.read_text(encoding="utf-8")
    creds = json.loads(CRED.read_text(encoding="utf-8")) if CRED.exists() else {}
    pesquisas = (json.loads(PESQUISAS_JSON.read_text(encoding="utf-8"))
                 if PESQUISAS_JSON.exists()
                 else {"pesquisas": [], "n_pesquisas": 0, "atualizado_em": None,
                       "uf": "DF", "fonte": ""})
    votos_eleitos = calcular_votos_eleitos()
    metas_campo   = calcular_metas_campo()

    out = (template
        .replace("__DADOS_B64__",         b64(ras))
        .replace("__PT_B64__",            b64(PERSONA_TERRITORIOS))
        .replace("__PK_B64__",            b64(PERSONA_IPE_KEY))
        .replace("__CANDS_B64__",         b64(cands_compactos))
        .replace("__VOTOS_ELEITOS_B64__", b64(votos_eleitos))
        .replace("__METAS_CAMPO_B64__",   b64(metas_campo))
        .replace("__GEO_B64__",           b64(geo))
        .replace("__CAND_B64__",          b64(cands_detalhados))
        .replace("__PESQUISAS_B64__",     b64(pesquisas))
        .replace("__ESTRATEGOS_USERS__",  json.dumps(creds, ensure_ascii=False, separators=(",", ":")))
    )

    for ph in ("__DADOS_B64__","__PT_B64__","__PK_B64__","__CANDS_B64__",
               "__VOTOS_ELEITOS_B64__","__METAS_CAMPO_B64__","__GEO_B64__",
               "__CAND_B64__","__PESQUISAS_B64__","__ESTRATEGOS_USERS__"):
        if ph in out:
            raise SystemExit(f"ERRO: placeholder {ph} não foi substituído")

    OUTPUT.write_text(out, encoding="utf-8")
    kb = len(out.encode()) // 1024
    print(f"\r  [4/5] {OUTPUT} gerado        ({kb} KB)")

    # 5. API de dados estática (arquivo único pra sistemas parceiros)
    print("  [5/5] Gerando API de dados...", end="", flush=True)
    token, destino, nbytes = gerar_api(ras, cands_detalhados, votos_eleitos,
                                       metas_campo, pesquisas, geo)
    print(f"\r  [5/5] API gerada             {destino} ({nbytes // 1024} KB)")
    print(f"        URL: https://estrategos.opiniao.inf.br/{destino.as_posix()}")

    elapsed = time.time() - t0
    print()
    print(f"  ✅ Concluído em {elapsed:.1f}s")
    print()


if __name__ == "__main__":
    main()
