"""
extrair_votos_candidato_ra.py — v3
====================================
Extrai votos de TODOS os candidatos por RA usando a mesma
lógica do montar_candidatos() do fase4_v2.py.

Inputs (já na sua máquina da fase 1):
  dados_tse_cache/votacao_secao_2022_DF.csv
  dados_tse_cache/locais_votacao_2022_enriched.csv

Saída:
  outputs_fase3c/votos_candidato_ra.csv

Uso:
  python3 extrair_votos_candidato_ra.py
"""

from pathlib import Path
import numpy as np
import pandas as pd

from classificacao_base import (
    carregar_aptos_por_ra,
    classificar_ras,
)

CACHE   = Path("dados_tse_cache")
DIR_OUT = Path("outputs_fase3c")
DIR_OUT.mkdir(exist_ok=True)

# ── Constantes — idênticas ao fase4_v2.py ────────────────────

CARGOS_VALIDOS = {
    "GOVERNADOR", "SENADOR",
    "DEPUTADO FEDERAL", "DEPUTADO DISTRITAL",
}

CARGO_NORM = {
    "GOVERNADOR":         "GOVERNADOR",
    "SENADOR":            "SENADOR",
    "DEPUTADO FEDERAL":   "DEPUTADO_FEDERAL",
    "DEPUTADO DISTRITAL": "DEPUTADO_DISTRITAL",
}

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

NUMERO_PARTIDO = {
    10:"Rep.",11:"PP",12:"PDT",13:"PT",14:"PTB",15:"MDB",
    16:"PSTU",17:"PSL",18:"REDE",20:"PSC",21:"Podemos",22:"PL",
    23:"Cidadania",25:"UB",27:"DC",28:"PRTB",30:"NOVO",
    33:"PMN",36:"Agir",40:"PSB",43:"PV",44:"União",45:"PSDB",
    50:"PSOL",51:"Patriota",55:"PSD",65:"PC do B",70:"Avante",
    77:"Solidariedade",
}

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

MIN_VOTOS = 50


def campo_de(nr, cargo, nome):
    cargo_n = CARGO_NORM.get(cargo, cargo)
    if "DEPUTADO" in cargo_n:
        try:
            prefixo = int(str(nr).strip()[:2])
            return NUMERO_CAMPO.get(prefixo, "outros")
        except:
            return "outros"
    else:
        nome_u = str(nome).upper().strip()
        for k, v in NOME_CAMPO_MAJOR.items():
            if k in nome_u:
                return v
        try:
            prefixo = int(str(nr).strip()[:2])
            return NUMERO_CAMPO.get(prefixo, "outros")
        except:
            return "outros"


def partido_de(nr, sg_partido=None):
    if sg_partido and str(sg_partido).strip() not in ["", "nan", "?"]:
        return str(sg_partido).strip()
    try:
        return NUMERO_PARTIDO.get(int(str(nr).strip()[:2]), "?")
    except:
        return "?"


def main():
    print()
    print("  extrair_votos_candidato_ra.py v3")
    print("  " + "─" * 40)

    # ── 1. Mapa seção → RA ───────────────────────────────────
    print("\n[1/3] Carregando mapa seção → RA...")
    locais_path = CACHE / "locais_votacao_2022_enriched.csv"
    if not locais_path.exists():
        locais_path = CACHE / "locais_votacao_2022.csv"
    if not locais_path.exists():
        locais_path = Path("outputs_fase1") / "locais_votacao_geo.csv"

    df_loc = pd.read_csv(locais_path, dtype=str,
                         usecols=lambda c: c in ["NR_ZONA","NR_SECAO","RA_NOME"])
    df_loc = df_loc.dropna(subset=["RA_NOME"])
    for col in ["NR_ZONA","NR_SECAO","RA_NOME"]:
        if col in df_loc.columns:
            df_loc[col] = df_loc[col].astype(str).str.strip()

    secao_ra = {
        (r["NR_ZONA"], r["NR_SECAO"]): r["RA_NOME"]
        for _, r in df_loc.iterrows()
    }
    # Override: seções "órfãs" no enriched (sem coordenada → não geocodificadas)
    # mas com votos no CSV bruto. Sem isso, perdemos votos no agregado por RA.
    # Detectado em 2026-04-29: 136 votos da CPP-SIA somem (Kicis perde 11).
    SECOES_OVERRIDE = {
        ("9", "2022"): "SIA",  # CPP - Centro de Progressão Penitenciária (Trecho 4 SIA)
    }
    for k, ra in SECOES_OVERRIDE.items():
        if k not in secao_ra:
            secao_ra[k] = ra
    print(f"   {len(secao_ra):,} seções mapeadas → {df_loc['RA_NOME'].nunique()} RAs (+{len(SECOES_OVERRIDE)} override)")

    # ── 2. Votação por seção ─────────────────────────────────
    print("\n[2/3] Lendo votação por seção (pode demorar)...")
    votos_path = CACHE / "votacao_secao_2022_DF.csv"
    if not votos_path.exists():
        print(f"   ERRO: {votos_path} não encontrado.")
        return

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
    df["QT_VOTOS"]  = pd.to_numeric(df["QT_VOTOS"], errors="coerce").fillna(0)
    df["NR_ZONA"]   = df["NR_ZONA"].astype(str).str.strip()
    df["NR_SECAO"]  = df["NR_SECAO"].astype(str).str.strip()
    df["NR_VOTAVEL"]= df["NR_VOTAVEL"].astype(str).str.strip()

    # Excluir nulos de votação (95-99)
    df = df[~df["NR_VOTAVEL"].isin(["95","96","97","98","99"])].copy()

    # Excluir votos de legenda (NR ≤ 2 dígitos em proporcionais)
    _nr_len = df["NR_VOTAVEL"].str.len()
    df = df[~(df["DS_CARGO"].isin(["DEPUTADO DISTRITAL","DEPUTADO FEDERAL"]) &
              (_nr_len <= 2))].copy()

    print(f"   {len(df):,} votos nominais válidos")

    # Mapear seção → RA
    df["RA_NOME"] = df.apply(
        lambda r: secao_ra.get((r["NR_ZONA"], r["NR_SECAO"])), axis=1
    )
    df = df.dropna(subset=["RA_NOME"])
    print(f"   {len(df):,} votos com RA mapeada ({df['RA_NOME'].nunique()} RAs)")

    # Campo e partido
    df["CAMPO"] = df.apply(
        lambda r: campo_de(r["NR_VOTAVEL"], r["DS_CARGO"], r.get("NM_VOTAVEL", "")), axis=1
    )
    df["PARTIDO"] = df.apply(
        lambda r: partido_de(r["NR_VOTAVEL"], r.get("SG_PARTIDO")), axis=1
    )

    # ── 3. Agregar ────────────────────────────────────────────
    print("\n[3/3] Agregando por candidato × RA...")

    total_cand    = df.groupby(["NM_VOTAVEL","DS_CARGO"])["QT_VOTOS"].sum()
    total_cargo_ra= df.groupby(["DS_CARGO","RA_NOME"])["QT_VOTOS"].sum().to_dict()
    total_campo_ra= df.groupby(["DS_CARGO","RA_NOME","CAMPO"])["QT_VOTOS"].sum().to_dict()

    grp = df.groupby(["NM_VOTAVEL","DS_CARGO","RA_NOME","CAMPO","PARTIDO"])["QT_VOTOS"].sum().reset_index()

    rows = []
    for _, r in grp.iterrows():
        nome   = str(r["NM_VOTAVEL"]).strip()
        cargo  = r["DS_CARGO"]
        ra     = r["RA_NOME"]
        campo  = r["CAMPO"]
        partido= r["PARTIDO"]
        votos  = int(r["QT_VOTOS"])
        total_c= int(total_cand.get((r["NM_VOTAVEL"], r["DS_CARGO"]), 0))

        if total_c < MIN_VOTOS:
            continue

        vt_cargo = int(total_cargo_ra.get((cargo, ra), 1) or 1)
        vt_campo = int(total_campo_ra.get((cargo, ra, campo), 1) or 1)

        rows.append({
            "NM_CANDIDATO": nome,
            "DS_CARGO":     CARGO_NORM.get(cargo, cargo),
            "CAMPO":        campo,
            "SG_PARTIDO":   partido,
            "RA_NOME":      ra,
            "QT_VOTOS_RA":  votos,
            "PCT_DO_CARGO": round(votos / vt_cargo * 100, 2),
            "PCT_DO_CAMPO": round(votos / vt_campo * 100, 2),
            "TOTAL_CAND":   total_c,
        })

    df_out = pd.DataFrame(rows)

    # Índice de sobrerrepresentação + status (helper compartilhado com fase4_v2.py)
    aptos_por_ra, total_aptos_df = carregar_aptos_por_ra()

    def add_status(grp):
        ras_votos = [(r["RA_NOME"], int(r["QT_VOTOS_RA"])) for _, r in grp.iterrows()]
        total_c = int(grp["TOTAL_CAND"].iloc[0]) if len(grp) else 0
        out = classificar_ras(ras_votos, total_c, aptos_por_ra, total_aptos_df)
        grp = grp.copy()
        grp["INDICE_SOBRE"] = [o["idx"] for o in out]
        grp["STATUS_BASE"]  = [o["status"] for o in out]
        return grp

    df_out = (df_out.groupby(["NM_CANDIDATO","DS_CARGO"], group_keys=False)
                    .apply(add_status)
                    .reset_index(drop=True))

    df_out = df_out.sort_values(
        ["DS_CARGO","TOTAL_CAND","RA_NOME"],
        ascending=[True, False, True]
    ).reset_index(drop=True)

    out = DIR_OUT / "votos_candidato_ra.csv"
    df_out.to_csv(out, index=False)

    n_cands = df_out["NM_CANDIDATO"].nunique()
    n_ras   = df_out["RA_NOME"].nunique()
    print(f"\n   ✓ {out}")
    print(f"   {len(df_out):,} linhas | {n_cands} candidatos | {n_ras} RAs")
    print()
    print("   Distribuição por cargo:")
    for cargo, grp in df_out.groupby("DS_CARGO"):
        nc = grp["NM_CANDIDATO"].nunique()
        print(f"     {cargo:<30} {nc:>3} candidatos")

    print(f"""
  ✅ Arquivo gerado: outputs_fase3c/votos_candidato_ra.csv
     Traga este arquivo de volta para o Claude.
""")


if __name__ == "__main__":
    main()
