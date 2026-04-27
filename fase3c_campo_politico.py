"""
FASE 3c — Classificação Política por NR_VOTAVEL
================================================
Estratégia:
  - Proporcional (Dep. Distrital, Dep. Federal):
    2 primeiros dígitos do NR_VOTAVEL = número do partido
  - Majoritário (Governador, Senador):
    1º tenta nome em CANDIDATOS_MAJORITARIOS
    2º fallback: número do partido via NR_VOTAVEL
"""

from pathlib import Path
import pandas as pd

DIR_F1  = Path("outputs_fase1")
DIR_F2  = Path("outputs_fase2")
DIR_F3  = Path("outputs_fase3")
DIR_OUT = Path("outputs_fase3c")
DIR_OUT.mkdir(exist_ok=True)
CACHE   = Path("dados_tse_cache")

NUMERO_PARTIDO_CAMPO = {
    # Progressista
    13: "progressista",   # PT
    12: "progressista",   # PDT
    40: "progressista",   # PSB
    50: "progressista",   # PSOL
    65: "progressista",   # PC do B
    18: "progressista",   # REDE
    43: "progressista",   # PV
    70: "progressista",   # AVANTE
    36: "progressista",   # AGIR
    # Moderado
    15: "moderado",       # MDB
    45: "moderado",       # PSDB
    23: "moderado",       # CIDADANIA
    55: "moderado",       # PSD
    20: "moderado",       # PODE
    51: "moderado",       # PATRIOTA
    33: "moderado",       # PMN
    27: "moderado",       # DC
    35: "moderado",       # PMB
    # Liberal / Conservador
    22: "liberal_conservador",   # PL
    11: "liberal_conservador",   # PP
    10: "liberal_conservador",   # REPUBLICANOS
    44: "liberal_conservador",   # UNIAO BRASIL
    30: "liberal_conservador",   # NOVO
    14: "liberal_conservador",   # PTB
    25: "liberal_conservador",   # DEM
    28: "liberal_conservador",   # PRTB
    17: "liberal_conservador",   # PSL (antigo)
}

# Apenas como primeiro fallback para nomes conhecidos
# Para o resto, usa partido via NR_VOTAVEL
CANDIDATOS_MAJORITARIOS = {
    # GOVERNADOR DF 2022
    "LEANDRO GRASS":    "progressista",
    "GRASS":            "progressista",
    "IBANEIS ROCHA":    "moderado",
    "IBANEIS":          "moderado",
    "ROGERIO ROSSO":    "moderado",
    "IZALCI LUCAS":     "liberal_conservador",
    "IZALCI":           "liberal_conservador",
    "FLAVIA ARRUDA":    "liberal_conservador",
    "PAULO OCTAVIO":    "liberal_conservador",
    "RODRIGO DELMASSO": "moderado",
    "JOSE RENATO":      "liberal_conservador",
    # SENADOR DF 2022
    "DAMARES ALVES":    "liberal_conservador",
    "DAMARES":          "liberal_conservador",
    "LEILA BARROS":     "progressista",
    "LEILA":            "progressista",
    "PROF ISRAEL":      "progressista",
    "ISRAEL":           "progressista",
    "CARLOS VIANA":     "liberal_conservador",
    "FAGUNDES":         "liberal_conservador",
}


def classificar_campo(nr_votavel: str, nm_votavel: str, ds_cargo: str) -> str:
    cargo = str(ds_cargo).upper().strip()
    nm    = str(nm_votavel).upper().strip()

    if nm in ("BRANCO", "NULO", "#NULO#", "#BRANCO#"):
        return "invalido"

    if cargo in ("GOVERNADOR", "SENADOR"):
        # 1. Tentar match por nome
        for chave, campo in CANDIDATOS_MAJORITARIOS.items():
            if chave in nm:
                return campo
        # 2. Fallback: partido via NR_VOTAVEL
        try:
            nr = str(nr_votavel).strip()
            if len(nr) >= 2:
                num_partido = int(nr[:2])
                campo = NUMERO_PARTIDO_CAMPO.get(num_partido)
                if campo:
                    return campo
        except (ValueError, TypeError):
            pass
        return "outros"

    # Proporcional
    try:
        nr = str(nr_votavel).strip()
        if len(nr) >= 2:
            num_partido = int(nr[:2])
            return NUMERO_PARTIDO_CAMPO.get(num_partido, "outros")
    except (ValueError, TypeError):
        pass
    return "outros"


def processar():
    cache_path = CACHE / "votacao_secao_2022_DF.csv"
    if not cache_path.exists():
        print("Arquivo votacao_secao_2022_DF.csv nao encontrado.")
        return None

    print("   Lendo votos por secao...")
    df = pd.read_csv(cache_path, sep=";", encoding="latin1", dtype=str)
    df.columns = [c.strip() for c in df.columns]

    col_map = {}
    for c in df.columns:
        cu = c.upper()
        if "NR_ZONA" == cu:      col_map[c] = "NR_ZONA"
        elif "NR_SECAO" == cu:   col_map[c] = "NR_SECAO"
        elif "NR_TURNO" == cu:   col_map[c] = "NR_TURNO"
        elif "DS_CARGO" == cu:   col_map[c] = "DS_CARGO"
        elif "NM_VOTAVEL" == cu: col_map[c] = "NM_VOTAVEL"
        elif "NR_VOTAVEL" == cu: col_map[c] = "NR_VOTAVEL"
        elif "QT_VOTOS" == cu:   col_map[c] = "QT_VOTOS"

    df = df.rename(columns=col_map)
    df["QT_VOTOS"] = pd.to_numeric(df["QT_VOTOS"], errors="coerce").fillna(0)
    df["NR_ZONA"]  = pd.to_numeric(df["NR_ZONA"],  errors="coerce").astype("Int64")
    df["NR_TURNO"] = df["NR_TURNO"].astype(str).str.strip()
    df = df[df["NR_TURNO"] == "1"].copy()

    # Mostrar DS_CARGO unicos para diagnostico
    print("   Cargos encontrados no CSV:")
    for c in sorted(df["DS_CARGO"].str.upper().str.strip().unique()):
        print(f"     {c}")

    print("   Classificando por campo politico...")
    df["CAMPO"] = df.apply(
        lambda r: classificar_campo(
            r.get("NR_VOTAVEL", ""),
            r.get("NM_VOTAVEL", ""),
            r.get("DS_CARGO", ""),
        ), axis=1
    )

    dist = df.groupby("CAMPO")["QT_VOTOS"].sum()
    total = dist.sum()
    print(f"\n   Distribuicao dos votos por campo (1o turno):")
    for campo, votos in dist.sort_values(ascending=False).items():
        print(f"     {campo:<25} {votos:>10,.0f}  ({votos/total*100:.1f}%)")

    return df


def agregar_por_ra(df_votos):
    geo      = pd.read_csv(DIR_F1 / "locais_votacao_geo.csv")
    secao_ra = pd.read_csv(CACHE / "locais_votacao_2022.csv",
                           sep=";", encoding="latin1", dtype=str)
    secao_ra.columns = [c.strip() for c in secao_ra.columns]

    col_uf = next((c for c in secao_ra.columns if "SG_UF" in c.upper()), None)
    if col_uf:
        secao_ra = secao_ra[secao_ra[col_uf].str.strip() == "DF"].copy()

    mapa = {}
    for c in secao_ra.columns:
        cu = c.upper()
        if "NR_ZONA" == cu:           mapa[c] = "NR_ZONA"
        elif "NR_SECAO" == cu:        mapa[c] = "NR_SECAO"
        elif "NM_LOCAL_VOTACAO" == cu: mapa[c] = "NM_LOCAL"
        elif "NM_BAIRRO" == cu:       mapa[c] = "NM_BAIRRO"
    secao_ra = secao_ra.rename(columns=mapa)
    secao_ra["NR_ZONA"]  = pd.to_numeric(secao_ra["NR_ZONA"],  errors="coerce").astype("Int64")
    secao_ra["NR_SECAO"] = secao_ra["NR_SECAO"].astype(str).str.strip()

    id_cols   = [c for c in ["NM_LOCAL","NM_BAIRRO"] if c in secao_ra.columns]
    merge_key = id_cols + ["NR_ZONA"]
    secao_geo = secao_ra.merge(
        geo[merge_key + ["RA_COD","RA_NOME"]].drop_duplicates(subset=merge_key),
        on=merge_key, how="left"
    )

    df_full = df_votos.merge(
        secao_geo[["NR_ZONA","NR_SECAO","RA_COD","RA_NOME"]].drop_duplicates(),
        on=["NR_ZONA","NR_SECAO"], how="left"
    )

    # Normalizar DS_CARGO para chave consistente no CSV de saida
    cargo_norm = {
        "GOVERNADOR":         "GOVERNADOR",
        "SENADOR":            "SENADOR",
        "DEPUTADO FEDERAL":   "DEPUTADO_FEDERAL",
        "DEPUTADO DISTRITAL": "DEPUTADO_DISTRITAL",
        "1O SENADOR":         "SENADOR",
        "1 SENADOR":          "SENADOR",
    }
    df_full["DS_CARGO_NORM"] = (df_full["DS_CARGO"].str.upper().str.strip()
                                .map(cargo_norm))
    df_full = df_full[df_full["DS_CARGO_NORM"].notna()].copy()

    # Excluir invalidos do calculo de %
    df_valido = df_full[df_full["CAMPO"] != "invalido"].copy()

    df_agg = (df_valido.groupby(["RA_COD","RA_NOME","DS_CARGO_NORM","CAMPO"])["QT_VOTOS"]
              .sum().reset_index())
    total_ra = (df_agg.groupby(["RA_COD","DS_CARGO_NORM"])["QT_VOTOS"]
                .sum().reset_index().rename(columns={"QT_VOTOS":"TOTAL"}))
    df_agg = df_agg.merge(total_ra, on=["RA_COD","DS_CARGO_NORM"])
    df_agg["PCT"] = (df_agg["QT_VOTOS"] / df_agg["TOTAL"] * 100).round(2)
    df_agg = df_agg.rename(columns={"DS_CARGO_NORM": "DS_CARGO"})

    return df_agg


def correlacoes_finais(df_mestre, df_agg):
    campos     = ["progressista","moderado","liberal_conservador"]
    cargos_map = {
        "GOVERNADOR":         "GOV",
        "DEPUTADO_DISTRITAL": "DEPDIST",
        "DEPUTADO_FEDERAL":   "DEPFED",
        "SENADOR":            "SEN",
    }
    pivot_rows = []
    for ra_cod, grupo in df_agg.groupby("RA_COD"):
        rec = {"RA_COD": ra_cod}
        for _, row in grupo.iterrows():
            slug  = cargos_map.get(row["DS_CARGO"], "")
            campo = row["CAMPO"]
            if campo in campos and slug:
                rec[f"PCT_{slug}_{campo}"] = row["PCT"]
        pivot_rows.append(rec)

    df_pivot = pd.DataFrame(pivot_rows)
    df_pivot["RA_COD"] = pd.to_numeric(df_pivot["RA_COD"], errors="coerce").astype("Int64")
    df_mestre["RA_COD"] = pd.to_numeric(df_mestre["RA_COD"], errors="coerce").astype("Int64")
    df_m = df_mestre.merge(df_pivot, on="RA_COD", how="inner")

    vars_pdad  = [c for c in df_mestre.columns if c.startswith(("MOR_","DOM_","EL_"))]
    vars_campo = [c for c in df_pivot.columns if c.startswith("PCT_")]

    rows = []
    for vp in vars_pdad:
        for vc in vars_campo:
            x = pd.to_numeric(df_m[vp], errors="coerce")
            y = pd.to_numeric(df_m[vc], errors="coerce")
            mask = x.notna() & y.notna()
            if mask.sum() < 5:
                continue
            # Ignorar colunas sem variancia (std=0 causa divisao por zero)
            if x[mask].std() == 0 or y[mask].std() == 0:
                continue
            r = round(x[mask].corr(y[mask]), 4)
            if pd.notna(r):
                rows.append({"VAR_PDAD": vp, "VAR_CAMPO": vc, "r": r, "N": int(mask.sum())})

    df_corr = (pd.DataFrame(rows)
               .sort_values("r", key=abs, ascending=False))
    df_corr.to_csv(DIR_OUT / "correlacoes_finais.csv", index=False)
    print(f"\n   TOP 15 correlacoes PDAD x campo politico:")
    for _, row in df_corr.head(15).iterrows():
        s = "+" if row["r"] > 0 else "-"
        print(f"     {s} {row['VAR_PDAD']:<38} {row['VAR_CAMPO']:<35} r={row['r']:+.3f}")

    return df_corr


def main():
    print("="*60)
    print("  FASE 3c — Classificacao Politica")
    print("="*60)

    print("\n[1/3] Classificando votos...")
    df_votos = processar()
    if df_votos is None:
        return

    print("\n[2/3] Agregando por RA...")
    df_agg = agregar_por_ra(df_votos)
    df_agg.to_csv(DIR_OUT / "votos_campo_ra.csv", index=False)
    print(f"   votos_campo_ra.csv salvo: {len(df_agg)} linhas")

    # Resumo GOVERNADOR
    gov = df_agg[df_agg["DS_CARGO"] == "GOVERNADOR"]
    if not gov.empty:
        print(f"\n   GOVERNADOR — amostra:")
        pivot = gov.pivot_table(index="RA_NOME", columns="CAMPO",
                                values="PCT", aggfunc="sum").fillna(0).round(1)
        print(pivot.to_string())

    print("\n[3/3] Calculando correlacoes...")
    df_mestre = pd.read_csv(DIR_F2 / "tabela_mestre_ra.csv")
    df_mestre = df_mestre[df_mestre["RA_COD"].notna()].copy()
    correlacoes_finais(df_mestre, df_agg)
    print("\nConcluido.")


if __name__ == "__main__":
    main()
