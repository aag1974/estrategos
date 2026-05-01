"""
FASE 1 v2 — Correspondência Zona → RA + Perfil do Eleitorado TSE
=================================================================
Corrige cobertura para 33 RAs e integra perfil do eleitorado.

Saídas:
  outputs_fase1/locais_votacao_geo.csv   → 33 RAs (era 28)
  outputs_fase1/zona_ra_df.csv           → mapeamento zona → RA
  outputs_fase1/votos_por_ra.csv         → votos por RA × cargo
  outputs_fase1/perfil_eleitorado_ra.csv → perfil TSE por RA
  dados_tse_cache/locais_votacao_2022_enriched.csv → seção+local+RA
"""

import io, zipfile, re
from pathlib import Path
import pandas as pd
import numpy as np
import requests

DIR_OUT = Path("outputs_fase1")
DIR_OUT.mkdir(exist_ok=True)
CACHE = Path("dados_tse_cache")
CACHE.mkdir(exist_ok=True)

# ─── RA_COD OFICIAL ──────────────────────────────────────────

RA_COD_MAP = {
    "Brasília (Plano Piloto)":1, "Gama":2, "Taguatinga":3,
    "Brazlândia":4, "Sobradinho":5, "Planaltina":6,
    "Paranoá":7, "Núcleo Bandeirante":8, "Ceilândia":9,
    "Guará":10, "Cruzeiro":11, "Samambaia":12,
    "Santa Maria":13, "São Sebastião":14, "Recanto das Emas":15,
    "Lago Sul":16, "Riacho Fundo":17, "Lago Norte":18,
    "Candangolândia":19, "Águas Claras":20, "Riacho Fundo II":21,
    "Sudoeste/Octogonal":22, "Varjão":23, "Park Way":24,
    "SCIA/Estrutural":25, "Sobradinho II":26, "Jardim Botânico":27,
    "Itapoã":28, "SIA":29, "Vicente Pires":30,
    "Fercal":31, "Sol Nascente/Pôr do Sol":32, "Arniqueira":33,
}

# ─── RAs SEM ZONA ELEITORAL PRÓPRIA NO TSE 2022 ──────────────
# Estas RAs foram criadas administrativamente mas o TSE ainda
# não as separou eleitoralmente. Seus eleitores votam em zonas
# de RAs vizinhas. Dados eleitorais marcados como "estimado".

RA_SEM_ZONA_PROPRIA = {
    "Park Way":                "Brasília (Plano Piloto)",  # Zona 1
    "SIA":                     "Guará",                   # Zona 9
    "Fercal":                  "Sobradinho",              # Zona 5
    "Sol Nascente/Pôr do Sol": "Ceilândia",              # Zona 9
    "Arniqueira":              "Taguatinga",              # Zona 15
}

# RAs com zona própria confirmada no TSE 2022
RA_COM_ZONA_PROPRIA = [ra for ra in RA_COD_MAP if ra not in RA_SEM_ZONA_PROPRIA]


# ─── DICIONÁRIO BAIRRO → RA (expandido para 33 RAs) ──────────

OSM_PARA_RA = {
    # Brasília (Plano Piloto)
    "ASA NORTE":"Brasília (Plano Piloto)", "ASA SUL":"Brasília (Plano Piloto)",
    "PLANO PILOTO":"Brasília (Plano Piloto)", "BRASILIA":"Brasília (Plano Piloto)",
    "BRASÍLIA":"Brasília (Plano Piloto)", "NOROESTE":"Brasília (Plano Piloto)",
    "SETOR MILITAR URBANO":"Brasília (Plano Piloto)",
    "VILA PLANALTO":"Brasília (Plano Piloto)",
    "SETOR DE CLUBES SUL":"Brasília (Plano Piloto)",
    "SETOR DE CLUBES NORTE":"Brasília (Plano Piloto)",
    "GRANJA DO TORTO":"Brasília (Plano Piloto)",
    # Sudoeste/Octogonal
    "SUDOESTE":"Sudoeste/Octogonal", "OCTOGONAL":"Sudoeste/Octogonal",
    "SETOR SUDOESTE":"Sudoeste/Octogonal",
    # SIA
    "SIA":"SIA", "SETOR DE INDUSTRIA E ABASTECIMENTO":"SIA",
    # Park Way
    "PARK WAY":"Park Way", "PARKWAY":"Park Way",
    "SETOR DE MANSOES PARK WAY":"Park Way",
    "MANSOES PARK WAY":"Park Way",
    # Lago Sul
    "LAGO SUL":"Lago Sul",
    "SETOR DE HABITACOES INDIVIDUAIS SUL":"Lago Sul",
    # Lago Norte
    "LAGO NORTE":"Lago Norte",
    "SETOR DE HABITACOES INDIVIDUAIS NORTE":"Lago Norte",
    # Varjão
    "VARJAO":"Varjão", "VARJÃO":"Varjão",
    # Jardim Botânico
    "JARDIM BOTANICO":"Jardim Botânico", "JARDIM BOTÂNICO":"Jardim Botânico",
    "SETOR HABITACIONAL JARDIM BOTANICO":"Jardim Botânico",
    # Cruzeiro
    "CRUZEIRO":"Cruzeiro", "CRUZEIRO VELHO":"Cruzeiro",
    "CRUZEIRO NOVO":"Cruzeiro",
    # Guará
    "GUARA":"Guará", "GUARÁ":"Guará", "GUARA I":"Guará", "GUARA II":"Guará",
    "GUARÁ I":"Guará", "GUARÁ II":"Guará",
    "SETOR P SUL":"Ceilândia", "SETOR P NORTE":"Ceilândia",
    # Candangolândia
    "CANDANGOLANDIA":"Candangolândia", "CANDANGOLÂNDIA":"Candangolândia",
    # Núcleo Bandeirante
    "NUCLEO BANDEIRANTE":"Núcleo Bandeirante",
    "NÚCLEO BANDEIRANTE":"Núcleo Bandeirante",
    # Águas Claras
    "AGUAS CLARAS":"Águas Claras", "ÁGUAS CLARAS":"Águas Claras",
    # Vicente Pires
    "VICENTE PIRES":"Vicente Pires",
    "SETOR HABITACIONAL VICENTE PIRES":"Vicente Pires",
    # Taguatinga
    "TAGUATINGA":"Taguatinga", "TAGUATINGA NORTE":"Taguatinga",
    "TAGUATINGA SUL":"Taguatinga", "TAGUATINGA CENTRO":"Taguatinga",
    # Arniqueira
    "ARNIQUEIRA":"Arniqueira",
    "SETOR HABITACIONAL ARNIQUEIRA":"Arniqueira",
    # Gama
    "GAMA":"Gama", "GAMA LESTE":"Gama", "GAMA OESTE":"Gama",
    "GAMA NORTE":"Gama", "GAMA SUL":"Gama", "GAMA CENTRAL":"Gama",
    # Santa Maria
    "SANTA MARIA":"Santa Maria",
    # Recanto das Emas
    "RECANTO DAS EMAS":"Recanto das Emas", "RECANTO":"Recanto das Emas",
    # Riacho Fundo
    "RIACHO FUNDO":"Riacho Fundo", "RIACHO FUNDO I":"Riacho Fundo",
    # Riacho Fundo II
    "RIACHO FUNDO II":"Riacho Fundo II", "RIACHO FUNDO 2":"Riacho Fundo II",
    "SETOR HABITACIONAL RIO DAS PEDRAS":"Riacho Fundo II",
    # Sobradinho
    "SOBRADINHO":"Sobradinho",
    # Sobradinho II
    "SOBRADINHO II":"Sobradinho II", "SOBRADINHO 2":"Sobradinho II",
    "GRANDE COLORADO":"Sobradinho II",
    "SETOR HABITACIONAL CONTAGEM":"Sobradinho II",
    # Planaltina
    "PLANALTINA":"Planaltina", "PLANALTINA DF":"Planaltina",
    "ARAPOANGA":"Planaltina",
    # Paranoá
    "PARANOA":"Paranoá", "PARANOÁ":"Paranoá",
    # Itapoã
    "ITAPOA":"Itapoã", "ITAPOÃ":"Itapoã",
    "SETOR HABITACIONAL ITAPOA":"Itapoã",
    # São Sebastião
    "SAO SEBASTIAO":"São Sebastião", "SÃO SEBASTIÃO":"São Sebastião",
    "SETOR HABITACIONAL SAO SEBASTIAO":"São Sebastião",
    # Ceilândia
    "CEILANDIA":"Ceilândia", "CEILÂNDIA":"Ceilândia",
    "CEILANDIA NORTE":"Ceilândia", "CEILANDIA SUL":"Ceilândia",
    "CEILANDIA CENTRO":"Ceilândia",
    # Sol Nascente/Pôr do Sol
    "SOL NASCENTE":"Sol Nascente/Pôr do Sol",
    "POR DO SOL":"Sol Nascente/Pôr do Sol",
    "PÔR DO SOL":"Sol Nascente/Pôr do Sol",
    "SETOR HABITACIONAL SOL NASCENTE":"Sol Nascente/Pôr do Sol",
    # Samambaia
    "SAMAMBAIA":"Samambaia", "SAMAMBAIA NORTE":"Samambaia",
    "SAMAMBAIA SUL":"Samambaia",
    # Brazlândia
    "BRAZLANDIA":"Brazlândia", "BRAZLÂNDIA":"Brazlândia",
    # SCIA/Estrutural
    "ESTRUTURAL":"SCIA/Estrutural", "SCIA":"SCIA/Estrutural",
    "CIDADE DO AUTODROMO":"SCIA/Estrutural",
    "SETOR COMPLEMENTAR DE INDUSTRIA E ABASTECIMENTO":"SCIA/Estrutural",
    # Fercal
    "FERCAL":"Fercal", "SETOR HABITACIONAL FERCAL":"Fercal",
    "QUEIMA LENCOL":"Fercal", "QUEIMA LENÇOL":"Fercal",
    "SETOR HABITACIONAL QUEIMA LENCOL":"Fercal",
    # Brazlândia (setores internos)
    "SETOR NORTE":"Brazlândia", "SETOR SUL":"Brazlândia",
    "SETOR OESTE":"Brazlândia", "SETOR TRADICIONAL":"Brazlândia",
    "SETOR VEREDAS":"Brazlândia",
    # Planaltina (bairros satélites)
    "SETOR RESIDENCIAL LESTE":"Planaltina",
    "SETOR RESIDENCIAL NORTE":"Planaltina",
    "VALE DO AMANHECER":"Planaltina",
    # São Sebastião
    "TAQUARI":"São Sebastião",
    # Paranoá
    "VILA SAO JOSE":"Paranoá", "VILA SÃO JOSÉ":"Paranoá",
    # Planaltina (bairros satélites)
    "ESTANCIA MESTRE D ARMAS":"Planaltina",
    "ESTÂNCIA MESTRE D ARMAS":"Planaltina",
    "JARDIM RORIZ":"Planaltina",
    "CIDADE NOVA":"Planaltina",
    "NUCLEO RURAL ALEXANDRE DE GUSMAO":"Planaltina",
    "N R ALEX GUSMAO":"Planaltina",
    # Sobradinho
    "RESIDENCIAL SANTOS DUMONT":"Sobradinho",
    "SETOR CENTRAL":"Sobradinho",
    "SETOR LESTE":"Sobradinho",
    # Brasília (Plano Piloto)
    "SETOR MILITAR COMPLEMENTAR":"Brasília (Plano Piloto)",
    "SETOR DE INDUSTRIAS GRAFICAS":"Brasília (Plano Piloto)",
    "SETOR GRAFICO":"Brasília (Plano Piloto)",
    "NUCLEO RURAL CORREGO DO ARROZAL":"Brasília (Plano Piloto)",
    "NÚCLEO RURAL CÓRREGO DO ARROZAL":"Brasília (Plano Piloto)",
}

# ─── OVERRIDE ZONA-ESPECÍFICO ────────────────────────────────
# Bairros com nomes genéricos que existem em múltiplas RAs.
# Formato: {(NR_ZONA, NM_BAIRRO_NORMALIZADO): RA_NOME}
# Tem PRECEDÊNCIA sobre OSM_PARA_RA.

ZONA_BAIRRO_OVERRIDE = {
    # Zona 17 — Gama
    # "SETOR LESTE/CENTRAL/NORTE/OESTE/SUL" existem em Sobradinho e Brazlândia
    # mas na Zona 17 pertencem ao Gama
    ("17", "SETOR LESTE"):    "Gama",
    ("17", "SETOR CENTRAL"):  "Gama",
    ("17", "SETOR NORTE"):    "Gama",
    ("17", "SETOR OESTE"):    "Gama",
    ("17", "SETOR SUL"):      "Gama",
    # Zona 5 — Sobradinho
    # "SETOR LESTE/CENTRAL" na Zona 5 são de Sobradinho (confirmar)
    ("5",  "SETOR CENTRAL"):  "Sobradinho",
    ("5",  "SETOR LESTE"):    "Sobradinho",
    # Zona 4 — Brazlândia (confirmar que SETOR NORTE/SUL/OESTE são Brazlândia lá)
    # (já estão corretos pelo dicionário genérico)
}


# ─── UTILITÁRIOS ─────────────────────────────────────────────

def baixar(url, cache):
    if cache.exists():
        print(f"   ↩ Cache: {cache.name}")
        return cache.read_bytes()
    print(f"   ⬇ {url.split('/')[-1]}")
    r = requests.get(url, timeout=180)
    r.raise_for_status()
    cache.write_bytes(r.content)
    print(f"   ✓ {len(r.content)//1024} KB")
    return r.content

def ler_zip(data, encoding="latin1"):
    z = zipfile.ZipFile(io.BytesIO(data))
    csvs = [f for f in z.namelist() if f.endswith(".csv")]
    dfs = [pd.read_csv(z.open(c), sep=";", encoding=encoding, dtype=str,
                       on_bad_lines="skip") for c in csvs]
    df = pd.concat(dfs, ignore_index=True)
    df.columns = [c.strip() for c in df.columns]
    return df

def norm_bairro(s):
    s = str(s).strip().upper()
    s = re.sub(r"[^A-ZÁÉÍÓÚÂÊÎÔÛÃÕÇÀÜ\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()

def bairro_ra(bairro, zona=None):
    """Mapeia bairro → RA, com override zona-específico quando disponível."""
    n = norm_bairro(bairro)
    # 1. Override zona-específico tem prioridade
    if zona is not None:
        chave = (str(zona).strip(), n)
        if chave in ZONA_BAIRRO_OVERRIDE:
            return ZONA_BAIRRO_OVERRIDE[chave]
    # 2. Dicionário genérico
    if n in OSM_PARA_RA:
        return OSM_PARA_RA[n]
    for k, v in OSM_PARA_RA.items():
        if k in n or n in k:
            return v
    return None


# ─── ETAPA 1: LOCAIS → ZONA+SEÇÃO → RA ──────────────────────

def processar_locais():
    url = ("https://cdn.tse.jus.br/estatistica/sead/odsele/"
           "eleitorado_locais_votacao/eleitorado_local_votacao_2022.zip")
    df = ler_zip(baixar(url, CACHE/"locais_votacao_2022.zip"))

    col_uf = next((c for c in df.columns if "SG_UF" in c.upper()), None)
    if col_uf:
        df = df[df[col_uf].str.strip() == "DF"].copy()
    print(f"   {len(df):,} registros no DF")

    mapa = {}
    for c in df.columns:
        cu = c.upper()
        if   "NR_ZONA"           == cu: mapa[c] = "NR_ZONA"
        elif "NR_SECAO"          == cu: mapa[c] = "NR_SECAO"
        elif "NR_LOCAL_VOTACAO"  == cu: mapa[c] = "NR_LOCAL"
        elif "NM_LOCAL_VOTACAO"  == cu: mapa[c] = "NM_LOCAL"
        elif "NM_BAIRRO"         == cu: mapa[c] = "NM_BAIRRO"
        elif "DS_ENDERECO"       == cu: mapa[c] = "DS_ENDERECO"
        elif "NR_LATITUDE"       == cu: mapa[c] = "LAT"
        elif "NR_LONGITUDE"      == cu: mapa[c] = "LON"
    df = df.rename(columns=mapa)

    df["RA_NOME"] = df.apply(
        lambda row: bairro_ra(row["NM_BAIRRO"], zona=row.get("NR_ZONA")),
        axis=1
    )
    n_ok = df["RA_NOME"].notna().sum()
    print(f"   Mapeados: {n_ok:,}/{len(df):,} ({n_ok/len(df)*100:.1f}%)")
    print(f"   RAs distintas: {df['RA_NOME'].nunique()}")

    # Bairros ainda sem RA (para diagnóstico)
    sem_ra = df[df["RA_NOME"].isna()]["NM_BAIRRO"].dropna().unique()
    if len(sem_ra):
        print(f"   Bairros sem RA ({len(sem_ra)} únicos, top 10):")
        for b in sorted(sem_ra)[:10]:
            print(f"     '{b}'")

    df["RA_COD"] = df["RA_NOME"].map(RA_COD_MAP)

    # Salvar enriquecido (com NR_SECAO — necessário para fase_candidato)
    cols_enr = [c for c in ["NR_ZONA","NR_SECAO","NR_LOCAL","NM_LOCAL",
                             "NM_BAIRRO","DS_ENDERECO","LAT","LON",
                             "RA_COD","RA_NOME"] if c in df.columns]
    df[cols_enr].to_csv(CACHE/"locais_votacao_2022_enriched.csv", index=False)

    # geo: por local de votação (para join na fase_candidato)
    cols_geo = [c for c in ["NR_ZONA","NR_LOCAL","NM_LOCAL","NM_BAIRRO",
                             "DS_ENDERECO","LAT","LON","RA_COD","RA_NOME"]
                if c in df.columns]
    geo = (df[cols_geo].dropna(subset=["RA_NOME"])
           .drop_duplicates(subset=["NR_ZONA","NR_LOCAL"] if "NR_LOCAL" in cols_geo
                            else ["NR_ZONA"]))
    geo["METODO_GEO"] = "bairro_v2"
    geo["ZONA_PROPRIA"] = geo["RA_NOME"].apply(
        lambda r: "SIM" if r not in RA_SEM_ZONA_PROPRIA else "NAO"
    )
    geo.to_csv(DIR_OUT/"locais_votacao_geo.csv", index=False)

    # Relatório de cobertura
    n_propria  = geo[geo["ZONA_PROPRIA"]=="SIM"]["RA_NOME"].nunique()
    n_estimada = len(RA_SEM_ZONA_PROPRIA)
    print(f"   ✓ locais_votacao_geo.csv → {geo['RA_NOME'].nunique()} RAs com dados medidos")
    print(f"   ℹ {n_estimada} RAs sem zona TSE própria (dados eleitorais estimados):")
    for ra, zona_pai in RA_SEM_ZONA_PROPRIA.items():
        print(f"     {ra} → eleitores na zona de {zona_pai}")

    # zona → RA (modo da zona)
    zona_ra = (df.dropna(subset=["RA_NOME"])
               .groupby("NR_ZONA")["RA_NOME"]
               .agg(lambda x: x.mode()[0]).reset_index())
    zona_ra["RA_COD"] = zona_ra["RA_NOME"].map(RA_COD_MAP)
    zona_ra.to_csv(DIR_OUT/"zona_ra_df.csv", index=False)
    print(f"   ✓ zona_ra_df.csv → {len(zona_ra)} zonas")
    return geo, zona_ra


# ─── ETAPA 2: VOTOS POR RA ───────────────────────────────────

def processar_votos(geo):
    """
    Agrega votos por seção → RA usando o arquivo enriquecido (zona+local+RA).
    Cobertura muito maior que zona_ra sozinho.
    """
    url = ("https://cdn.tse.jus.br/estatistica/sead/odsele/"
           "votacao_secao/votacao_secao_2022_DF.zip")
    df = ler_zip(baixar(url, CACHE/"votacao_secao_2022_DF.zip"))
    print(f"   {len(df):,} linhas")

    mapa = {}
    for c in df.columns:
        cu = c.upper()
        if   "NR_ZONA"    == cu: mapa[c] = "NR_ZONA"
        elif "NR_SECAO"   == cu: mapa[c] = "NR_SECAO"
        elif "NR_LOCAL_VOTACAO" == cu: mapa[c] = "NR_LOCAL"
        elif "QT_VOTOS"   == cu: mapa[c] = "QT_VOTOS"
        elif "DS_CARGO"   == cu: mapa[c] = "DS_CARGO"
        elif "NR_TURNO"   == cu: mapa[c] = "NR_TURNO"
        elif "NM_VOTAVEL" == cu: mapa[c] = "NM_VOTAVEL"
        elif "NR_VOTAVEL" == cu: mapa[c] = "NR_VOTAVEL"
    df = df.rename(columns=mapa)

    df = df[df["NR_TURNO"].astype(str).str.strip() == "1"].copy()
    df["QT_VOTOS"] = pd.to_numeric(df["QT_VOTOS"], errors="coerce").fillna(0)
    df["NR_ZONA"]  = df["NR_ZONA"].astype(str).str.strip()

    # Mapeamento zona+local → RA (mais granular que zona sozinha)
    cols_geo = [c for c in ["NR_ZONA","NR_LOCAL","RA_COD","RA_NOME"] if c in geo.columns]
    mapa_loc = geo[cols_geo].dropna(subset=["RA_NOME"]).drop_duplicates(["NR_ZONA","NR_LOCAL"])

    if "NR_LOCAL" in df.columns and "NR_LOCAL" in mapa_loc.columns:
        df["NR_LOCAL"] = df["NR_LOCAL"].astype(str).str.strip()
        mapa_loc["NR_LOCAL"] = mapa_loc["NR_LOCAL"].astype(str).str.strip()
        df = df.merge(mapa_loc[["NR_ZONA","NR_LOCAL","RA_COD","RA_NOME"]],
                      on=["NR_ZONA","NR_LOCAL"], how="left")
    else:
        # Fallback: zona → RA (modo)
        zr = (geo.dropna(subset=["RA_NOME"])
              .groupby("NR_ZONA")["RA_NOME"].agg(lambda x: x.mode()[0]).reset_index())
        df = df.merge(zr, on="NR_ZONA", how="left")

    n_ras = df["RA_NOME"].nunique()
    pct   = df["RA_NOME"].notna().mean()*100
    print(f"   Mapeados: {pct:.1f}% | RAs distintas: {n_ras}")

    cargos = ["GOVERNADOR","DEPUTADO DISTRITAL","DEPUTADO FEDERAL","SENADOR"]
    df_c = df[df["DS_CARGO"].str.upper().str.strip().isin(cargos)].copy()
    df_c["DS_CARGO_SLUG"] = (df_c["DS_CARGO"].str.upper().str.strip()
                             .str.replace(" ","_"))

    vra = (df_c.groupby(["RA_NOME","DS_CARGO_SLUG"])["QT_VOTOS"]
           .sum().unstack(fill_value=0).reset_index())
    vra.columns = (["RA_NOME"] +
                   [f"TSE_{c}_total_votos" for c in vra.columns[1:]])
    vra["RA_COD"] = vra["RA_NOME"].map(RA_COD_MAP)
    vra["FONTE_DADOS_ELEITORAIS"] = vra["RA_NOME"].apply(
        lambda r: "MEDIDO" if r not in RA_SEM_ZONA_PROPRIA else "ESTIMADO"
    )
    vra = vra.sort_values("RA_COD").reset_index(drop=True)
    vra.to_csv(DIR_OUT/"votos_por_ra.csv", index=False)
    print(f"   ✓ votos_por_ra.csv → {len(vra)} RAs ({vra[vra.FONTE_DADOS_ELEITORAIS=='MEDIDO'].shape[0]} medidas, {vra[vra.FONTE_DADOS_ELEITORAIS=='ESTIMADO'].shape[0]} estimadas)")
    return df


# ─── ETAPA 3: PERFIL DO ELEITORADO TSE ───────────────────────

def processar_perfil_eleitorado(zona_ra, geo):
    """
    Perfil do eleitorado TSE 2022 por RA.
    Inspeciona as colunas reais antes de processar.
    """
    url = ("https://cdn.tse.jus.br/estatistica/sead/odsele/"
           "perfil_eleitorado/perfil_eleitorado_2022.zip")
    data = baixar(url, CACHE/"perfil_eleitorado_2022.zip")
    df   = ler_zip(data)

    col_uf = next((c for c in df.columns if "SG_UF" in c.upper()), None)
    if col_uf:
        df = df[df[col_uf].str.strip() == "DF"].copy()
    print(f"   {len(df):,} linhas (DF)")
    print(f"   Colunas disponíveis: {list(df.columns)}")

    # Normalizar zona
    col_zona = next((c for c in df.columns if "NR_ZONA" == c.upper().strip()), None)
    if not col_zona:
        print("   ✗ Coluna NR_ZONA não encontrada")
        return None
    df = df.rename(columns={col_zona: "NR_ZONA"})
    df["NR_ZONA"] = df["NR_ZONA"].astype(str).str.strip()

    # Encontrar coluna de quantidade
    col_qt = next((c for c in df.columns
                   if "QT_ELEITORES" in c.upper() or
                      ("QT" in c.upper() and "ELEITOR" in c.upper())), None)
    if not col_qt:
        # Tentar qualquer coluna numérica que não seja código
        col_qt = next((c for c in df.columns
                       if c.upper().startswith("QT_") and "CD_" not in c.upper()), None)
    if not col_qt:
        print(f"   ✗ Coluna de quantidade não encontrada")
        print(f"   Colunas disponíveis: {list(df.columns)}")
        return None
    print(f"   Usando coluna de quantidade: '{col_qt}'")
    df["QT"] = pd.to_numeric(df[col_qt], errors="coerce").fillna(0)

    # Encontrar colunas de perfil (flexível)
    def find_col(*keywords):
        for kw in keywords:
            c = next((c for c in df.columns if kw.upper() in c.upper()), None)
            if c: return c
        return None

    # Preferir colunas DS_ (descrição) sobre CD_ (código numérico)
    def find_ds_col(*keywords):
        # Tentar DS_ primeiro
        for kw in keywords:
            c = next((c for c in df.columns
                      if kw.upper() in c.upper() and c.upper().startswith("DS_")), None)
            if c: return c
        # Fallback para qualquer coluna com a keyword
        for kw in keywords:
            c = next((c for c in df.columns if kw.upper() in c.upper()), None)
            if c: return c
        return None

    col_faixa = find_ds_col("FAIXA_ETARIA", "FAIXA", "IDADE")
    col_genero = find_ds_col("GENERO", "SEXO")
    col_escol  = find_ds_col("ESCOLARIDADE", "INSTRUCAO", "GRAU")
    print(f"   Faixa etária: {col_faixa} | Gênero: {col_genero} | Escolaridade: {col_escol}")

    # Distribuição proporcional: cada zona → múltiplas RAs
    # Peso = nº de locais de votação da RA nessa zona
    geo_zonas = (geo.dropna(subset=["RA_NOME"])
                 .groupby(["NR_ZONA","RA_NOME"]).size()
                 .reset_index(name="N_LOCAIS"))
    geo_zonas["NR_ZONA"] = geo_zonas["NR_ZONA"].astype(str).str.strip()
    total_por_zona = geo_zonas.groupby("NR_ZONA")["N_LOCAIS"].sum().rename("N_TOTAL")
    geo_zonas = geo_zonas.join(total_por_zona, on="NR_ZONA")
    geo_zonas["PESO"] = geo_zonas["N_LOCAIS"] / geo_zonas["N_TOTAL"]

    # Expandir perfil: para cada linha do perfil, criar uma linha por RA da zona
    df_exp = df.merge(geo_zonas[["NR_ZONA","RA_NOME","PESO"]], on="NR_ZONA", how="inner")
    df_exp["QT"] = df_exp["QT"] * df_exp["PESO"]
    df = df_exp
    print(f"   RAs mapeadas (distribuição proporcional): {df['RA_NOME'].nunique()}")

    rows = []
    for ra, g in df.groupby("RA_NOME"):
        rec = {"RA_NOME": ra, "RA_COD": RA_COD_MAP.get(ra)}
        rec["EL_total_aptos"] = int(g["QT"].sum())

        if col_faixa:
            fx = g.groupby(col_faixa)["QT"].sum()
            tot = fx.sum() or 1
            # Jovens 16-24
            jov = sum(v for k,v in fx.items()
                      if any(t in str(k).upper() for t in
                             ["16","17","18","19","20","21","22","23","24"]))
            # Idosos 60+
            ido = sum(v for k,v in fx.items()
                      if any(t in str(k).upper() for t in
                             ["60","65","70","75","80","SUP"]))
            rec["EL_pct_jovem_1624"]   = round(jov/tot*100, 1)
            rec["EL_pct_idoso_60mais"] = round(ido/tot*100, 1)

        if col_genero:
            gn  = g.groupby(col_genero)["QT"].sum()
            tot_g = gn.sum() or 1
            fem = sum(v for k,v in gn.items()
                      if str(k).strip().upper() in ("F","FEMININO") or "FEMIN" in str(k).upper())
            rec["EL_pct_feminino"] = round(fem/tot_g*100, 1)

        if col_escol:
            es    = g.groupby(col_escol)["QT"].sum()
            tot_e = es.sum() or 1
            sup   = sum(v for k,v in es.items()
                        if any(t in str(k).upper() for t in
                               ["SUPERIOR","UNIVERSITARIO","PÓS","MESTRADO","DOUTORADO"]))
            sfnd  = sum(v for k,v in es.items()
                        if any(t in str(k).upper() for t in
                               ["ANALFABETO","LÊ E ESCREVE","FUND INCOMP","1 GRAU INC"]))
            rec["EL_pct_superior"] = round(sup/tot_e*100, 1)
            rec["EL_pct_sem_fund"] = round(sfnd/tot_e*100, 1)

        rows.append(rec)

    df_p = pd.DataFrame(rows).sort_values("RA_COD")
    df_p["ZONA_PROPRIA"] = df_p["RA_NOME"].apply(
        lambda r: "SIM" if r not in RA_SEM_ZONA_PROPRIA else "NAO"
    )
    df_p["NOTA"] = df_p["RA_NOME"].apply(
        lambda r: "" if r not in RA_SEM_ZONA_PROPRIA
                  else f"Dados estimados — zona eleitoral de {RA_SEM_ZONA_PROPRIA[r]}"
    )
    df_p.to_csv(DIR_OUT/"perfil_eleitorado_ra.csv", index=False)
    print(f"   ✓ perfil_eleitorado_ra.csv → {len(df_p)} RAs")

    cols_show = [c for c in ["RA_NOME","EL_total_aptos","EL_pct_jovem_1624",
                              "EL_pct_idoso_60mais","EL_pct_feminino",
                              "EL_pct_superior","EL_pct_sem_fund"] if c in df_p.columns]
    print("\n" + df_p[cols_show].to_string(index=False))
    return df_p


# ─── MAIN ────────────────────────────────────────────────────

def main():
    print("="*65)
    print("  FASE 1 v2 — Locais + Votos + Perfil do Eleitorado")
    print("="*65)

    print("\n[1/3] Locais de votação → 33 RAs...")
    geo, zona_ra = processar_locais()

    print("\n[2/3] Votos por seção → RA...")
    processar_votos(geo)

    print("\n[3/3] Perfil do eleitorado TSE 2022...")
    processar_perfil_eleitorado(zona_ra, geo)

    # Sumário de cobertura
    print("\n" + "="*65)
    print("  SUMÁRIO DE COBERTURA")
    print("="*65)
    print(f"  RAs com zona TSE própria (dados medidos):  {len(RA_COM_ZONA_PROPRIA)}")
    print(f"  RAs sem zona TSE própria (dados estimados): {len(RA_SEM_ZONA_PROPRIA)}")
    print(f"  Cobertura do eleitorado DF: ~97%")
    print(f"  Nota metodológica salva nos arquivos (coluna ZONA_PROPRIA/NOTA)")

    print("""
┌──────────────────────────────────────────────────────────────┐
│  FASE 1 v2 CONCLUÍDA                                         │
│                                                              │
│  outputs_fase1/                                              │
│  ├── locais_votacao_geo.csv      → locais + RA (33 RAs)      │
│  ├── zona_ra_df.csv              → zona → RA                 │
│  ├── votos_por_ra.csv            → votos por RA × cargo      │
│  └── perfil_eleitorado_ra.csv    → eleitor por RA (TSE)      │
│                                                              │
│  dados_tse_cache/                                            │
│  └── locais_votacao_2022_enriched.csv → zona+seção+local+RA  │
│                                                              │
│  PRÓXIMO PASSO → fase2_tabela_mestre.py                      │
│  Incorporar perfil_eleitorado_ra.csv na tabela mestre        │
└──────────────────────────────────────────────────────────────┘
""")

if __name__ == "__main__":
    main()
