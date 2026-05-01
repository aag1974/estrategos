"""
FASE 0 — Análise histórica TSE 2018 × 2022
===========================================
Objetivo: estudar a transferência de base eleitoral entre ciclos e cargos.
Entrada:  dados_tse_cache/ (arquivos 2018 e 2022 já baixados)
Saída:    outputs_fase0/
            candidatos_2018.csv        → votos por RA em 2018
            candidatos_2022.csv        → votos por RA em 2022
            trajetorias.csv            → pares 2018→2022 com índice de penetração
            padroes_transferencia.csv  → coeficientes médios por tipo de trajetória
            relatorio_exploratório.txt → análise em texto

Downloads necessários (rodar uma vez):
  cd dados_tse_cache
  curl -L -O https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_secao/votacao_secao_2018_DF.zip
  curl -L -O https://cdn.tse.jus.br/estatistica/sead/odsele/eleitorado_locais_votacao/eleitorado_local_votacao_2018.zip
"""

from pathlib import Path
import pandas as pd
import numpy as np

CACHE    = Path("dados_tse_cache")
DIR_OUT  = Path("outputs_fase0")
DIR_OUT.mkdir(exist_ok=True)

# Mapa zona → RA já construído na fase1
LOCAIS_PATH = CACHE / "locais_votacao_2022_enriched.csv"

CARGOS_VALIDOS = {
    "GOVERNADOR", "GOVERNADOR DO ESTADO",
    "SENADOR", "SENADOR DA REPÚBLICA",
    "DEPUTADO FEDERAL",
    "DEPUTADO DISTRITAL", "DEPUTADO ESTADUAL",
}

CARGO_NORM = {
    "GOVERNADOR DO ESTADO": "GOVERNADOR",
    "SENADOR DA REPÚBLICA": "SENADOR",
    "DEPUTADO ESTADUAL":    "DEPUTADO DISTRITAL",
}

# Peso do cargo na hierarquia de escala (para calcular direção de migração)
CARGO_ESCALA = {
    "DEPUTADO DISTRITAL": 1,
    "DEPUTADO FEDERAL":   2,
    "SENADOR":            3,
    "GOVERNADOR":         4,
}

NUMERO_CAMPO = {
    10: "moderado", 11: "moderado", 12: "moderado", 15: "moderado",
    20: "moderado", 22: "moderado", 23: "moderado",
    13: "progressista", 14: "progressista", 16: "progressista",
    17: "progressista", 65: "progressista",
    11: "moderado",
    25: "liberal_conservador", 17: "progressista",
    30: "liberal_conservador", 31: "liberal_conservador",
    36: "liberal_conservador",
}

# ──────────────────────────────────────────────────────────────
# ETAPA 1 — Carregar mapa seção → RA
# ──────────────────────────────────────────────────────────────

def carregar_mapa_secao_ra():
    print("  Carregando mapa seção → RA...", end="", flush=True)
    df = pd.read_csv(LOCAIS_PATH, dtype=str,
                     usecols=["NR_ZONA", "NR_SECAO", "RA_NOME"])
    df = df.dropna(subset=["RA_NOME"])
    mapa = {
        (r["NR_ZONA"].strip(), r["NR_SECAO"].strip()): r["RA_NOME"].strip()
        for _, r in df.iterrows()
    }
    print(f" {len(mapa):,} seções")
    return mapa

# ──────────────────────────────────────────────────────────────
# ETAPA 2 — Extrair candidatos de um ano
# ──────────────────────────────────────────────────────────────

def extrair_candidatos(ano: int, secao_ra: dict) -> pd.DataFrame:
    """
    Lê votacao_secao_{ano}_DF.zip e retorna DataFrame com:
    NM_VOTAVEL, NR_VOTAVEL, CARGO, PARTIDO, RA_NOME, QT_VOTOS
    """
    zip_path = CACHE / f"votacao_secao_{ano}_DF.zip"
    csv_path = CACHE / f"votacao_secao_{ano}_DF.csv"

    print(f"\n  [{ano}] Lendo votação por seção...", end="", flush=True)

    if csv_path.exists():
        df = pd.read_csv(csv_path, sep=";", encoding="latin1", dtype=str)
    elif zip_path.exists():
        import zipfile, io
        with zipfile.ZipFile(zip_path) as z:
            name = next(n for n in z.namelist() if n.endswith(".csv"))
            with z.open(name) as f:
                df = pd.read_csv(f, sep=";", encoding="latin1", dtype=str)
    else:
        print(f"\n  ERRO: arquivo {zip_path} não encontrado.")
        print(f"  Execute: curl -L -O https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_secao/votacao_secao_{ano}_DF.zip")
        return pd.DataFrame()

    df.columns = [c.strip() for c in df.columns]

    # Inspecionar colunas disponíveis
    print(f"\n  [{ano}] Colunas disponíveis: {list(df.columns)}")

    # Normalizar colunas (nomes variam entre anos)
    col_map = {}
    for c in df.columns:
        cu = c.upper()
        if   cu == "NR_VOTAVEL":                    col_map[c] = "NR_VOTAVEL"
        elif cu == "NM_VOTAVEL":                    col_map[c] = "NM_VOTAVEL"
        elif cu == "QT_VOTOS":                      col_map[c] = "QT_VOTOS"
        elif cu == "NR_TURNO":                      col_map[c] = "NR_TURNO"
        elif cu == "DS_CARGO":                      col_map[c] = "DS_CARGO"
        elif cu == "NR_ZONA":                       col_map[c] = "NR_ZONA"
        elif cu == "NR_SECAO":                      col_map[c] = "NR_SECAO"
        elif cu in ("SG_PARTIDO", "SG_LEGENDA",
                    "NM_PARTIDO", "DS_PARTIDO"):    col_map[c] = "SG_PARTIDO"
        elif "NM_TIPO_ELEICAO" in cu:               col_map[c] = "NM_TIPO_ELEICAO"
    df = df.rename(columns=col_map)

    # Garantir coluna de partido
    if "SG_PARTIDO" not in df.columns:
        print(f"  [{ano}] AVISO: coluna de partido não encontrada — usando '?'")
        df["SG_PARTIDO"] = "?"

    print(f" {len(df):,} linhas", end="", flush=True)

    # Filtrar 1º turno
    df = df[df["NR_TURNO"].astype(str).str.strip() == "1"].copy()

    # Normalizar cargo
    df["DS_CARGO"] = df["DS_CARGO"].str.upper().str.strip()
    df["DS_CARGO"] = df["DS_CARGO"].replace(CARGO_NORM)
    df = df[df["DS_CARGO"].isin(CARGOS_VALIDOS | set(CARGO_NORM.keys()))].copy()
    df["DS_CARGO"] = df["DS_CARGO"].replace(CARGO_NORM)

    # Votos numéricos
    df["QT_VOTOS"] = pd.to_numeric(df["QT_VOTOS"], errors="coerce").fillna(0)

    # Remover brancos/nulos
    df = df[~df["NR_VOTAVEL"].astype(str).str.strip().isin(
        ["95", "96", "97", "98", "99"]
    )].copy()

    df["NR_ZONA"]  = df["NR_ZONA"].astype(str).str.strip()
    df["NR_SECAO"] = df["NR_SECAO"].astype(str).str.strip()

    # Mapear RA
    df["RA_NOME"] = df.apply(
        lambda r: secao_ra.get((r["NR_ZONA"], r["NR_SECAO"])), axis=1
    )
    df = df.dropna(subset=["RA_NOME"])

    print(f" · {df['NM_VOTAVEL'].nunique():,} candidatos · {df['RA_NOME'].nunique()} RAs")

    # SG_PARTIDO pode não existir em todos os anos
    if "SG_PARTIDO" not in df.columns:
        df["SG_PARTIDO"] = "?"

    # Agregar votos por candidato × RA
    grp = df.groupby(
        ["NM_VOTAVEL", "NR_VOTAVEL", "DS_CARGO", "SG_PARTIDO", "RA_NOME"],
        as_index=False
    )["QT_VOTOS"].sum()

    # Total por candidato
    totais = grp.groupby("NM_VOTAVEL")["QT_VOTOS"].sum().rename("TOTAL_VOTOS")
    grp = grp.merge(totais, on="NM_VOTAVEL")

    # Filtrar candidatos com pelo menos 500 votos totais (elimina ruído)
    grp = grp[grp["TOTAL_VOTOS"] >= 500].copy()

    # % do total por RA
    grp["PCT_RA"] = grp["QT_VOTOS"] / grp["TOTAL_VOTOS"]

    grp["ANO"] = ano
    return grp


# ──────────────────────────────────────────────────────────────
# ETAPA 3 — Identificar trajetórias 2018 → 2022
# ──────────────────────────────────────────────────────────────

def identificar_trajetorias(df18: pd.DataFrame, df22: pd.DataFrame) -> pd.DataFrame:
    """
    Cruza candidatos pelos dois ciclos pelo nome.
    Retorna pares com cargo 2018, cargo 2022 e tipo de trajetória.
    """
    print("\n  Identificando trajetórias 2018→2022...", end="", flush=True)

    cands18 = df18[["NM_VOTAVEL", "DS_CARGO", "SG_PARTIDO", "TOTAL_VOTOS"]]\
              .drop_duplicates("NM_VOTAVEL")
    cands22 = df22[["NM_VOTAVEL", "DS_CARGO", "SG_PARTIDO", "TOTAL_VOTOS"]]\
              .drop_duplicates("NM_VOTAVEL")

    merged = cands18.merge(
        cands22, on="NM_VOTAVEL", suffixes=("_18", "_22")
    )

    def tipo_trajetoria(cargo18, cargo22):
        e18 = CARGO_ESCALA.get(cargo18, 0)
        e22 = CARGO_ESCALA.get(cargo22, 0)
        nat18 = "majoritario" if cargo18 in ("GOVERNADOR", "SENADOR") else "proporcional"
        nat22 = "majoritario" if cargo22 in ("GOVERNADOR", "SENADOR") else "proporcional"

        if cargo18 == cargo22:
            return "renovacao"
        elif e22 > e18:
            if nat18 == "proporcional" and nat22 == "majoritario":
                return "proporcional_para_majoritario"
            else:
                return "crescimento_escala"
        elif e22 < e18:
            return "reducao_escala"
        else:
            return "lateral"

    merged["TIPO_TRAJETORIA"] = merged.apply(
        lambda r: tipo_trajetoria(r["DS_CARGO_18"], r["DS_CARGO_22"]), axis=1
    )

    print(f" {len(merged):,} candidatos com trajetória identificada")

    # Contar por tipo
    print("\n  Distribuição de trajetórias:")
    for tipo, cnt in merged["TIPO_TRAJETORIA"].value_counts().items():
        print(f"    {tipo}: {cnt}")

    return merged


# ──────────────────────────────────────────────────────────────
# ETAPA 4 — Calcular índice de penetração por RA
# ──────────────────────────────────────────────────────────────

def calcular_penetracao(
    df18: pd.DataFrame,
    df22: pd.DataFrame,
    trajetorias: pd.DataFrame
) -> pd.DataFrame:
    """
    Para cada candidato com trajetória, calcula por RA:
      penetracao = PCT_RA_2022 / PCT_RA_2018

    penetracao > 1: RA ganhou peso relativo na base do candidato
    penetracao < 1: RA perdeu peso relativo
    penetracao = 1: estável

    Retorna DataFrame com índices por candidato × RA × tipo de trajetória.
    """
    print("\n  Calculando índice de penetração por RA...")

    resultados = []

    for _, traj in trajetorias.iterrows():
        nome  = traj["NM_VOTAVEL"]
        tipo  = traj["TIPO_TRAJETORIA"]
        c18   = traj["DS_CARGO_18"]
        c22   = traj["DS_CARGO_22"]

        ra18 = df18[df18["NM_VOTAVEL"] == nome][["RA_NOME", "PCT_RA"]]\
               .rename(columns={"PCT_RA": "PCT_18"})
        ra22 = df22[df22["NM_VOTAVEL"] == nome][["RA_NOME", "PCT_RA"]]\
               .rename(columns={"PCT_RA": "PCT_22"})

        ra = ra18.merge(ra22, on="RA_NOME", how="outer").fillna(0)
        ra["NOME"]           = nome
        ra["CARGO_18"]       = c18
        ra["CARGO_22"]       = c22
        ra["TIPO_TRAJETORIA"]= tipo

        # Índice de penetração: evitar divisão por zero
        ra["PENETRACAO"] = ra.apply(
            lambda r: r["PCT_22"] / r["PCT_18"] if r["PCT_18"] > 0.005 else None,
            axis=1
        )

        # Variação absoluta em pp
        ra["DELTA_PP"] = (ra["PCT_22"] - ra["PCT_18"]) * 100

        resultados.append(ra)

    df_pen = pd.concat(resultados, ignore_index=True)
    return df_pen


# ──────────────────────────────────────────────────────────────
# ETAPA 5 — Padrões de transferência por tipo de trajetória
# ──────────────────────────────────────────────────────────────

def calcular_taxa_conversao(trajetorias: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula a taxa de conversão de votos entre cargos.

    taxa_conversao = votos_2022 / votos_2018

    Responde: se um candidato teve X votos no cargo A em 2018,
    quantos votos ele teve no cargo B em 2022?

    Para usar no modelo:
      votos_estimados_2026 = votos_2022_referência × taxa_conversao_mediana[cargo18→cargo22]
    """
    print("\n  Calculando taxa de conversão de cargo...")

    resultados = []

    for _, row in trajetorias.iterrows():
        if row["TOTAL_VOTOS_18"] > 0:
            taxa = row["TOTAL_VOTOS_22"] / row["TOTAL_VOTOS_18"]
            resultados.append({
                "NOME":           row["NM_VOTAVEL"],
                "CARGO_18":       row["DS_CARGO_18"],
                "CARGO_22":       row["DS_CARGO_22"],
                "TIPO_TRAJETORIA":row["TIPO_TRAJETORIA"],
                "VOTOS_18":       row["TOTAL_VOTOS_18"],
                "VOTOS_22":       row["TOTAL_VOTOS_22"],
                "TAXA_CONVERSAO": round(taxa, 4),
            })

    df_tc = pd.DataFrame(resultados)

    # Resumo por par de cargos
    resumo = df_tc.groupby(["CARGO_18", "CARGO_22", "TIPO_TRAJETORIA"]).agg(
        n_candidatos     = ("NOME", "nunique"),
        taxa_med         = ("TAXA_CONVERSAO", "median"),
        taxa_p25         = ("TAXA_CONVERSAO", lambda x: x.quantile(0.25)),
        taxa_p75         = ("TAXA_CONVERSAO", lambda x: x.quantile(0.75)),
        taxa_min         = ("TAXA_CONVERSAO", "min"),
        taxa_max         = ("TAXA_CONVERSAO", "max"),
        votos_18_med     = ("VOTOS_18", "median"),
        votos_22_med     = ("VOTOS_22", "median"),
    ).reset_index()

    print("\n  Taxa de conversão por par de cargos:")
    print(f"  {'Cargo 18':<22} {'Cargo 22':<22} {'N':>4} {'Mediana':>9} {'P25':>8} {'P75':>8}")
    print("  " + "─" * 78)
    for _, r in resumo.iterrows():
        print(f"  {r['CARGO_18']:<22} {r['CARGO_22']:<22} {int(r['n_candidatos']):>4} "
              f"{r['taxa_med']:>8.1%} {r['taxa_p25']:>7.1%} {r['taxa_p75']:>7.1%}")

    return df_tc, resumo


def calcular_padroes(df_pen: pd.DataFrame) -> pd.DataFrame:
    """
    Agrupa por tipo de trajetória × RA e calcula:
    - penetração mediana (mais robusta que média)
    - % de candidatos que mantiveram penetração > 0.7 na RA
    - % que cresceram (penetração > 1.2)
    """
    print("\n  Calculando padrões por tipo de trajetória...")

    df_valid = df_pen.dropna(subset=["PENETRACAO"]).copy()

    padroes = df_valid.groupby(
        ["TIPO_TRAJETORIA", "CARGO_18", "CARGO_22", "RA_NOME"]
    ).agg(
        n_candidatos   = ("NOME", "nunique"),
        penetracao_med = ("PENETRACAO", "median"),
        penetracao_p25 = ("PENETRACAO", lambda x: x.quantile(0.25)),
        penetracao_p75 = ("PENETRACAO", lambda x: x.quantile(0.75)),
        pct_manteve    = ("PENETRACAO", lambda x: (x >= 0.7).mean()),
        pct_cresceu    = ("PENETRACAO", lambda x: (x >= 1.2).mean()),
        delta_pp_med   = ("DELTA_PP",   "median"),
    ).reset_index()

    print("\n  Padrões globais por tipo de trajetória:")
    resumo = df_valid.groupby("TIPO_TRAJETORIA").agg(
        n_pares       = ("NOME", "nunique"),
        pen_mediana   = ("PENETRACAO", "median"),
        delta_pp_med  = ("DELTA_PP", "median"),
    )
    print(resumo.to_string())

    return padroes


# ──────────────────────────────────────────────────────────────
# ETAPA 6 — Relatório exploratório
# ──────────────────────────────────────────────────────────────

def gerar_relatorio(
    trajetorias: pd.DataFrame,
    df_pen: pd.DataFrame,
    padroes: pd.DataFrame,
    df_tc: pd.DataFrame,
    resumo_tc: pd.DataFrame,
) -> str:
    linhas = [
        "ANÁLISE HISTÓRICA TSE 2018 × 2022 — DF",
        "=" * 50,
        "",
        f"Total de candidatos com trajetória identificada: {trajetorias['NM_VOTAVEL'].nunique()}",
        "",
        "DISTRIBUIÇÃO POR TIPO DE TRAJETÓRIA:",
    ]

    for tipo, cnt in trajetorias["TIPO_TRAJETORIA"].value_counts().items():
        linhas.append(f"  {tipo}: {cnt} candidatos")

    linhas += ["", "PADRÕES DE PENETRAÇÃO POR TRAJETÓRIA:", ""]

    for tipo in trajetorias["TIPO_TRAJETORIA"].unique():
        subset = df_pen[
            (df_pen["TIPO_TRAJETORIA"] == tipo) &
            df_pen["PENETRACAO"].notna()
        ]
        if subset.empty:
            continue

        pen_med = subset["PENETRACAO"].median()
        delta_med = subset["DELTA_PP"].median()
        manteve = (subset["PENETRACAO"] >= 0.7).mean() * 100
        cresceu = (subset["PENETRACAO"] >= 1.2).mean() * 100

        # Cargos neste tipo
        c18 = trajetorias[trajetorias["TIPO_TRAJETORIA"]==tipo]["DS_CARGO_18"].unique()
        c22 = trajetorias[trajetorias["TIPO_TRAJETORIA"]==tipo]["DS_CARGO_22"].unique()

        linhas += [
            f"  [{tipo}]",
            f"  Cargos: {', '.join(c18)} → {', '.join(c22)}",
            f"  Penetração mediana: {pen_med:.2f}  (1.0 = estável, <1 = perdeu peso, >1 = ganhou)",
            f"  Delta pp mediano: {delta_med:+.1f}pp",
            f"  % RAs que mantiveram penetração ≥ 0.7: {manteve:.0f}%",
            f"  % RAs com crescimento ≥ 1.2: {cresceu:.0f}%",
            "",
        ]

        # Top RAs com maior crescimento
        top_ra = (
            subset.groupby("RA_NOME")["PENETRACAO"].median()
            .sort_values(ascending=False).head(5)
        )
        linhas.append("  RAs com maior penetração mediana:")
        for ra, pen in top_ra.items():
            linhas.append(f"    {ra}: {pen:.2f}")
        linhas.append("")

    linhas += [
        "TAXAS DE CONVERSÃO POR PAR DE CARGOS:",
        "",
        "  (votos_estimados_2026 = votos_referência_2022 × taxa_mediana)",
        "",
    ]
    for _, r in resumo_tc.iterrows():
        linhas.append(
            f"  {r['CARGO_18']} → {r['CARGO_22']}: "
            f"mediana {r['taxa_med']:.1%}  "
            f"(P25={r['taxa_p25']:.1%}, P75={r['taxa_p75']:.1%}, N={int(r['n_candidatos'])})"
        )
    linhas.append("")

    linhas += [
        "FÓRMULA DO MODELO DE ESTRATÉGIA:",
        "",
        "  Passo 1 — Volume total estimado:",
        "    votos_total = votos_candidato_referência_2022 × taxa_conversao_mediana[cargo22→cargo2026]",
        "",
        "  Passo 2 — Distribuição por RA:",
        "    votos_RA = votos_total × pct_RA_2022 × coef_penetracao_RA[trajetoria]",
        "",
        "  Passo 3 — Rota mínima:",
        "    Ordenar RAs por potencial (base consolidada primeiro, expansão depois)",
        "    Acumular até atingir o quociente eleitoral estimado",
        "",
        "  Para candidatos sem histórico:",
        "    Substituir passo 1 e 2 por SPE_base (PDAD × pesos por cargo e campo)",
        "    Sem coeficiente de trajetória — coef = 1.0 para todas as RAs",
    ]

    return "\n".join(linhas)


# ──────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────

def main():
    print("\n  FASE 0 — Análise histórica TSE 2018 × 2022")
    print("  " + "─" * 42)

    if not LOCAIS_PATH.exists():
        print(f"\n  ERRO: {LOCAIS_PATH} não encontrado.")
        print("  Execute a fase1 primeiro para gerar o mapa de seções.")
        return

    secao_ra = carregar_mapa_secao_ra()

    # Extrair candidatos dos dois ciclos
    df18 = extrair_candidatos(2018, secao_ra)
    df22 = extrair_candidatos(2022, secao_ra)

    if df18.empty or df22.empty:
        print("\n  Não foi possível continuar sem os dados de ambos os anos.")
        return

    # Salvar candidatos por ano
    df18.to_csv(DIR_OUT / "candidatos_2018.csv", index=False)
    df22.to_csv(DIR_OUT / "candidatos_2022.csv", index=False)
    print(f"\n  Salvos: candidatos_2018.csv · candidatos_2022.csv")

    # Trajetórias
    trajetorias = identificar_trajetorias(df18, df22)
    trajetorias.to_csv(DIR_OUT / "trajetorias.csv", index=False)

    # Índice de penetração
    df_pen = calcular_penetracao(df18, df22, trajetorias)
    df_pen.to_csv(DIR_OUT / "penetracao_por_ra.csv", index=False)

    # Taxa de conversão de cargo
    df_tc, resumo_tc = calcular_taxa_conversao(trajetorias)
    df_tc.to_csv(DIR_OUT / "taxa_conversao_candidatos.csv", index=False)
    resumo_tc.to_csv(DIR_OUT / "taxa_conversao_resumo.csv", index=False)

    # Padrões de penetração por RA
    padroes = calcular_padroes(df_pen)
    padroes.to_csv(DIR_OUT / "padroes_transferencia.csv", index=False)

    # Relatório
    relatorio = gerar_relatorio(trajetorias, df_pen, padroes, df_tc, resumo_tc)
    relatorio_path = DIR_OUT / "relatorio_exploratorio.txt"
    relatorio_path.write_text(relatorio, encoding="utf-8")

    print(f"\n  Relatório: {relatorio_path}")
    print("\n" + relatorio)

    print(f"\n  ✅ Concluído — outputs em {DIR_OUT}/")


if __name__ == "__main__":
    main()
