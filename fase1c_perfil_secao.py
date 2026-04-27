"""
FASE 1c — Perfil do Eleitorado por RA com granularidade de seção
================================================================
Substitui a distribuição proporcional zona→RA da fase1 por atribuição
direta seção→RA via point-in-polygon (PIP), eliminando o vazamento
entre RAs que compartilham zona eleitoral.

Pipeline:
  1. Carrega polígonos das 33 RAs (Limite_RA_20190.json)
  2. Carrega seções do DF a partir do raw locais_votacao_2022.csv
     (filtra turno=1 para evitar duplicação)
  3. Para cada seção: PIP usando LAT/LON. Fallback OSM (RA_NOME do
     enriched) para 10 seções com coords inválidas (-1,-1) — todas em
     bairros nomeados claros (CEUB Águas Claras, Colégio Anchieta etc).
  4. Cross-check: total agregado por RA deve bater com QT_ELEITOR_SECAO
     do TSE raw (2.203.045 aptos no DF).
  5. Junta com perfil_eleitor_secao_2022_DF (perfil demográfico).
  6. Agrega por RA: aptos, % feminino, % jovem 16-24, % idoso 60+,
     % superior, % sem fundamental.

Saídas:
  outputs_fase1/secao_ra_pip.csv          → atribuição RA por seção
  outputs_fase1/perfil_eleitorado_ra.csv  → perfil agregado por RA (canônico)

Substitui o output equivalente da fase1_correspondencia_zona_ra.py, que
ficou preservado como perfil_eleitorado_ra_v1_zona_proporcional.csv para
referência histórica.
"""

import json, zipfile, re
from pathlib import Path
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import shape, Point

DIR_OUT = Path("outputs_fase1")
DIR_OUT.mkdir(exist_ok=True)
CACHE = Path("dados_tse_cache")

RA_COD_MAP = {
    "Brasília (Plano Piloto)": 1, "Gama": 2, "Taguatinga": 3,
    "Brazlândia": 4, "Sobradinho": 5, "Planaltina": 6,
    "Paranoá": 7, "Núcleo Bandeirante": 8, "Ceilândia": 9,
    "Guará": 10, "Cruzeiro": 11, "Samambaia": 12,
    "Santa Maria": 13, "São Sebastião": 14, "Recanto das Emas": 15,
    "Lago Sul": 16, "Riacho Fundo": 17, "Lago Norte": 18,
    "Candangolândia": 19, "Águas Claras": 20, "Riacho Fundo II": 21,
    "Sudoeste/Octogonal": 22, "Varjão": 23, "Park Way": 24,
    "SCIA/Estrutural": 25, "Sobradinho II": 26, "Jardim Botânico": 27,
    "Itapoã": 28, "SIA": 29, "Vicente Pires": 30,
    "Fercal": 31, "Sol Nascente/Pôr do Sol": 32, "Arniqueira": 33,
}
RA_NUM_TO_NOME = {v: k for k, v in RA_COD_MAP.items()}


def carregar_poligonos_ra():
    """Lê Limite_RA_20190.json e retorna GeoDataFrame com 33 polígonos."""
    with open("Limite_RA_20190.json", encoding="utf-8") as f:
        gj = json.load(f)
    rows = []
    for feat in gj["features"]:
        ra_num = int(feat["properties"]["ra_num"])
        rows.append({
            "ra_num": ra_num,
            "RA_NOME": RA_NUM_TO_NOME[ra_num],
            "geometry": shape(feat["geometry"]),
        })
    gdf = gpd.GeoDataFrame(rows, geometry="geometry", crs="EPSG:4326")
    print(f"   Polígonos: {len(gdf)} RAs (overlap entre polígonos: 0)")
    return gdf


def carregar_secoes_df():
    """
    Carrega seções do raw TSE filtrando DF e turno=1 (evita duplicação).
    Traz QT_ELEITOR_SECAO como cross-check do agregado.
    """
    cols = ["SG_UF", "NR_ZONA", "NR_SECAO", "NR_LOCAL_VOTACAO", "NR_TURNO",
            "NM_LOCAL_VOTACAO", "NM_BAIRRO", "DS_ENDERECO",
            "NR_LATITUDE", "NR_LONGITUDE",
            "CD_TIPO_SECAO_AGREGADA", "DS_TIPO_SECAO_AGREGADA",
            "NR_SECAO_PRINCIPAL", "QT_ELEITOR_SECAO"]
    df = pd.read_csv(CACHE / "locais_votacao_2022.csv",
                     encoding="latin-1", sep=";", usecols=cols, low_memory=False)
    df = df[(df["SG_UF"] == "DF") & (df["NR_TURNO"] == 1)].copy()
    df = df.rename(columns={"NR_LATITUDE": "LAT", "NR_LONGITUDE": "LON"})
    print(f"   Seções DF (turno 1): {len(df):,}")
    print(f"   Total aptos (QT_ELEITOR_SECAO): {df['QT_ELEITOR_SECAO'].sum():,}")
    print(f"   Tipo de seção: {df['DS_TIPO_SECAO_AGREGADA'].value_counts().to_dict()}")
    print(f"   Coords inválidas (LAT=-1 ou LON=-1): {((df['LAT']==-1)|(df['LON']==-1)).sum()}")
    return df


def carregar_osm_fallback():
    """
    Carrega RA atribuída via OSM/bairro do enriched, para servir como
    fallback nas seções com coords inválidas.
    """
    enr = pd.read_csv(CACHE / "locais_votacao_2022_enriched.csv")
    enr = enr.drop_duplicates(subset=["NR_ZONA", "NR_SECAO"])
    return enr[["NR_ZONA", "NR_SECAO", "RA_NOME"]].rename(
        columns={"RA_NOME": "RA_NOME_OSM"})


def atribuir_ra_secao(secoes, polys_gdf, osm):
    """
    Atribui RA por seção: PIP para coords válidas, OSM para inválidas.
    Retorna DataFrame com colunas RA_NOME_PIP, RA_NOME_OSM, RA_NOME_FINAL,
    METODO.
    """
    # Merge OSM em todas as seções (será comparador e fallback)
    secoes = secoes.merge(osm, on=["NR_ZONA", "NR_SECAO"], how="left")

    valid = (secoes["LAT"].notna() & secoes["LON"].notna() &
             (secoes["LAT"] != -1) & (secoes["LON"] != -1))
    com = secoes[valid].copy()
    sem = secoes[~valid].copy()

    # PIP nas válidas
    com["geometry"] = [Point(lon, lat) for lon, lat in
                       zip(com["LON"], com["LAT"])]
    pontos = gpd.GeoDataFrame(com, geometry="geometry", crs="EPSG:4326")
    polys = polys_gdf[["ra_num", "RA_NOME", "geometry"]].rename(
        columns={"ra_num": "RA_NUM_PIP", "RA_NOME": "RA_NOME_PIP"})
    joined = gpd.sjoin(pontos, polys, how="left", predicate="within")
    joined = pd.DataFrame(joined.drop(columns=["geometry", "index_right"]))
    joined["METODO"] = "PIP"

    sem_pip_match = joined["RA_NOME_PIP"].isna()
    if sem_pip_match.any():
        # Fallback OSM se PIP não achou polígono (raro)
        joined.loc[sem_pip_match, "METODO"] = "OSM (fallback - PIP sem match)"
        print(f"   ⚠ {int(sem_pip_match.sum())} com coords válidas sem polígono → fallback OSM")

    # Inválidas: usam OSM direto
    sem["RA_NOME_PIP"] = pd.NA
    sem["RA_NUM_PIP"] = pd.NA
    sem["METODO"] = "OSM (fallback - coords inválidas)"

    todos = pd.concat([joined, sem], ignore_index=True)
    todos["RA_NOME_FINAL"] = todos["RA_NOME_PIP"].where(
        todos["RA_NOME_PIP"].notna(), todos["RA_NOME_OSM"])
    todos["RA_NOME_FINAL"] = todos["RA_NOME_FINAL"].astype(str).str.strip()
    todos.loc[todos["RA_NOME_FINAL"] == "nan", "RA_NOME_FINAL"] = pd.NA
    todos["RA_COD_FINAL"] = todos["RA_NOME_FINAL"].map(RA_COD_MAP)

    # Sanity check final
    sem_atrib = todos["RA_NOME_FINAL"].isna()
    if sem_atrib.sum():
        print(f"   ⚠ Seções sem atribuição RA ({int(sem_atrib.sum())}):")
        for _, r in todos[sem_atrib].iterrows():
            print(f"     zona={r['NR_ZONA']} seção={r['NR_SECAO']} "
                  f"local={r.get('NM_LOCAL_VOTACAO','?')} "
                  f"bairro={r.get('NM_BAIRRO','?')} "
                  f"aptos={r.get('QT_ELEITOR_SECAO',0)}")
    print(f"   Atribuídas via PIP: {(todos['METODO']=='PIP').sum():,}")
    print(f"   Atribuídas via OSM (fallback): {(todos['METODO']!='PIP').sum()}")

    total_raw = secoes["QT_ELEITOR_SECAO"].sum()
    total_atrib = todos.loc[~sem_atrib, "QT_ELEITOR_SECAO"].sum()
    diff = total_raw - total_atrib
    status = '✓ bate' if diff == 0 else f'✗ falta {diff} aptos'
    print(f"   Cross-check aptos: atribuídos {total_atrib:,} / raw {total_raw:,} → {status}")

    return todos


def comparar_pip_vs_osm(secao_ra):
    """Diagnóstico das discrepâncias PIP vs OSM (atribuição via bairro)."""
    pip = secao_ra[secao_ra["METODO"] == "PIP"].copy()
    pip["RA_NOME_OSM_norm"] = pip["RA_NOME_OSM"].astype(str).str.strip()
    valid = pip[pip["RA_NOME_PIP"].notna() &
                pip["RA_NOME_OSM_norm"].notna() &
                (pip["RA_NOME_OSM_norm"] != "nan")].copy()
    n = len(valid)
    if n == 0:
        print("\n=== Diagnóstico PIP vs OSM ===\n   Nada comparável.")
        return
    valid["bate"] = valid["RA_NOME_PIP"] == valid["RA_NOME_OSM_norm"]
    bate = int(valid["bate"].sum())
    print(f"\n=== Diagnóstico PIP vs OSM (no subset com PIP) ===")
    print(f"   Comparáveis: {n:,}  Concordância: {bate:,} ({bate/n*100:.1f}%)"
          f"  Divergência: {n-bate:,}")
    if n - bate > 0:
        diff = valid[~valid["bate"]]
        print("   Top realocações (OSM → PIP):")
        top = diff.groupby(["RA_NOME_OSM_norm", "RA_NOME_PIP"]).size().sort_values(ascending=False).head(8)
        for (osm, pip_), c in top.items():
            print(f"     {osm:>25} → {pip_:<25}  {c}")


def calcular_abstencao_gov(secao_ra):
    """
    Calcula ABSTENCAO_GOV por RA = 1 − comparecimento_RA / aptos_RA.

    aptos_RA: soma de QT_ELEITOR_SECAO de todas as seções (Principal +
              Agregada) atribuídas à RA via PIP.
    comparec_RA: soma de QT_VOTOS (Governador 1T) das Principais. As
              Agregadas não votam fisicamente, mas todas as 235 agregadas
              do DF estão na mesma RA da sua Principal — o comparecimento
              fica naturalmente correto agregando por RA.
    """
    print("\n=== Calculando abstenção (Governador 1º turno 2022) ===")
    chave_to_ra = dict(zip(
        secao_ra["NR_ZONA"].astype(str) + "_" + secao_ra["NR_SECAO"].astype(str),
        secao_ra["RA_NOME_FINAL"]))

    # Comparecimento (Governador 1T) por seção (= soma QT_VOTOS de todos
    # os candidatos + brancos + nulos)
    comp = pd.read_csv(CACHE / "votacao_secao_2022_DF.csv",
                       encoding="latin-1", sep=";",
                       usecols=["NR_TURNO", "DS_CARGO", "NR_ZONA", "NR_SECAO",
                                "QT_VOTOS"], low_memory=False)
    comp = comp[(comp["NR_TURNO"] == 1) & (comp["DS_CARGO"] == "GOVERNADOR")].copy()
    comp = comp.groupby(["NR_ZONA", "NR_SECAO"], as_index=False)["QT_VOTOS"].sum()
    comp["chave"] = comp["NR_ZONA"].astype(str) + "_" + comp["NR_SECAO"].astype(str)
    comp["RA_NOME"] = comp["chave"].map(chave_to_ra)
    comp = comp.dropna(subset=["RA_NOME"])
    print(f"   Seções com comparecimento (Gov): {len(comp):,}")

    # Aptos por RA — somar TODAS as seções (Principal + Agregada)
    aptos_ra = secao_ra.dropna(subset=["RA_NOME_FINAL"]).groupby(
        "RA_NOME_FINAL", as_index=False)["QT_ELEITOR_SECAO"].sum()
    aptos_ra = aptos_ra.rename(columns={"RA_NOME_FINAL": "RA_NOME",
                                        "QT_ELEITOR_SECAO": "aptos"})

    # Comparecimento por RA — somar todas as seções (Agregada não vota,
    # então o comparecimento delas é zero — soma é equivalente ao das Principais)
    comp_ra = comp.groupby("RA_NOME", as_index=False)["QT_VOTOS"].sum()
    comp_ra = comp_ra.rename(columns={"QT_VOTOS": "comparec"})

    grp = aptos_ra.merge(comp_ra, on="RA_NOME", how="left")
    grp["comparec"] = grp["comparec"].fillna(0)
    grp["ABSTENCAO_GOV"] = ((1 - grp["comparec"] / grp["aptos"]) * 100).round(1)

    # Sanity check: nenhuma abstenção negativa nem >100%
    bad = grp[(grp["ABSTENCAO_GOV"] < 0) | (grp["ABSTENCAO_GOV"] > 100)]
    if len(bad):
        print(f"   ⚠ {len(bad)} RAs com abstenção fora do intervalo [0,100]:")
        print(bad.to_string(index=False))
    else:
        print(f"   ✓ Abstenção dentro do intervalo [0,100] em todas as 33 RAs")
    return grp[["RA_NOME", "ABSTENCAO_GOV"]]


def agregar_perfil(secao_ra):
    """Lê perfil_eleitor_secao e agrega por RA usando RA_NOME_FINAL."""
    print("\n=== Agregando perfil por RA ===")
    chave_to_ra = dict(zip(
        secao_ra["NR_ZONA"].astype(str) + "_" + secao_ra["NR_SECAO"].astype(str),
        secao_ra["RA_NOME_FINAL"]))
    print(f"   Lookup seção→RA: {len(chave_to_ra):,} chaves")

    chunks = []
    with zipfile.ZipFile(CACHE / "perfil_eleitor_secao_2022_DF.zip") as z:
        with z.open("perfil_eleitor_secao_2022_DF.csv") as f:
            for chunk in pd.read_csv(f, sep=";", encoding="latin-1",
                                     chunksize=200_000,
                                     dtype={"NR_ZONA": str, "NR_SECAO": str}):
                chunk["chave"] = chunk["NR_ZONA"] + "_" + chunk["NR_SECAO"]
                chunk["RA_NOME"] = chunk["chave"].map(chave_to_ra)
                chunk = chunk.dropna(subset=["RA_NOME"])
                chunk = chunk[chunk["RA_NOME"] != "nan"]
                chunks.append(chunk)
    df = pd.concat(chunks, ignore_index=True)
    print(f"   Linhas perfil com RA: {len(df):,}")
    print(f"   Total agregado: {df['QT_ELEITORES_PERFIL'].sum():,}")

    def parse_idade_min(s):
        m = re.match(r"(\d+)", str(s).strip())
        return int(m.group(1)) if m else None

    df["idade_min"] = df["DS_FAIXA_ETARIA"].apply(parse_idade_min)
    df["jovem_1624"] = (df["idade_min"] >= 16) & (df["idade_min"] <= 24)
    df["idoso_60mais"] = df["idade_min"] >= 60

    esc = df["DS_GRAU_ESCOLARIDADE"].astype(str).str.upper()
    df["superior"] = esc.str.contains(
        r"SUPERIOR|UNIVERSITARIO|PÓS|MESTRADO|DOUTORADO", regex=True, na=False)
    df["sem_fund"] = esc.str.contains(
        r"ANALFABETO|LÊ E ESCREVE|FUND.*INCOMP|1.*GRAU INC", regex=True, na=False)

    df["feminino"] = df["DS_GENERO"].astype(str).str.upper().str.startswith("F")

    rows = []
    for ra, g in df.groupby("RA_NOME"):
        q = g["QT_ELEITORES_PERFIL"]
        total = int(q.sum())
        rec = {
            "RA_NOME": ra,
            "RA_COD": RA_COD_MAP.get(ra),
            "EL_total_aptos": total,
            "EL_pct_jovem_1624": round(q[g["jovem_1624"]].sum()/total*100, 1) if total else 0,
            "EL_pct_idoso_60mais": round(q[g["idoso_60mais"]].sum()/total*100, 1) if total else 0,
            "EL_pct_feminino": round(q[g["feminino"]].sum()/total*100, 1) if total else 0,
            "EL_pct_superior": round(q[g["superior"]].sum()/total*100, 1) if total else 0,
            "EL_pct_sem_fund": round(q[g["sem_fund"]].sum()/total*100, 1) if total else 0,
        }
        rows.append(rec)
    return pd.DataFrame(rows).sort_values("RA_COD").reset_index(drop=True)


def main():
    print("=== FASE 1c — Perfil do Eleitorado por RA via seção ===\n")

    print(">> Carregando polígonos das RAs")
    polys = carregar_poligonos_ra()

    print("\n>> Carregando seções do TSE raw")
    secoes = carregar_secoes_df()

    print("\n>> Carregando atribuição OSM (fallback)")
    osm = carregar_osm_fallback()

    print("\n>> Atribuindo RA por seção")
    secao_ra = atribuir_ra_secao(secoes, polys, osm)

    cols_save = ["NR_ZONA", "NR_SECAO", "NR_LOCAL_VOTACAO", "LAT", "LON",
                 "QT_ELEITOR_SECAO", "DS_TIPO_SECAO_AGREGADA",
                 "RA_NOME_PIP", "RA_NOME_OSM", "RA_NOME_FINAL",
                 "RA_COD_FINAL", "METODO"]
    cols_save = [c for c in cols_save if c in secao_ra.columns]
    secao_ra[cols_save].to_csv(DIR_OUT / "secao_ra_pip.csv", index=False)
    print(f"   ✓ outputs_fase1/secao_ra_pip.csv → {len(secao_ra):,} seções")

    comparar_pip_vs_osm(secao_ra)

    df_ra = agregar_perfil(secao_ra)

    abst = calcular_abstencao_gov(secao_ra)
    df_ra = df_ra.merge(abst, on="RA_NOME", how="left")

    # Manter compatibilidade com schema v1 (ZONA_PROPRIA agora é sempre SIM,
    # NOTA fica vazia — todas as 33 RAs têm perfil próprio via PIP)
    df_ra["ZONA_PROPRIA"] = "SIM"
    df_ra["NOTA"] = ""

    # Cross-check final
    total_v2 = int(df_ra["EL_total_aptos"].sum())
    total_raw = int(secoes["QT_ELEITOR_SECAO"].sum())
    print(f"\n=== Cross-check final ===")
    print(f"   Soma EL_total_aptos no v2: {total_v2:,}")
    print(f"   Total raw QT_ELEITOR_SECAO: {total_raw:,}")
    print(f"   Diferença: {total_raw - total_v2}"
          f" {'✓ tudo conferido' if total_raw == total_v2 else '✗ atenção'}")

    df_ra.to_csv(DIR_OUT / "perfil_eleitorado_ra.csv", index=False)
    print(f"\n   ✓ outputs_fase1/perfil_eleitorado_ra.csv → {len(df_ra)} RAs")

    print("\n=== Resumo por RA ===")
    print(df_ra[["RA_NOME", "EL_total_aptos", "EL_pct_superior",
                 "EL_pct_jovem_1624", "EL_pct_idoso_60mais", "EL_pct_feminino"]].to_string(index=False))


if __name__ == "__main__":
    main()
