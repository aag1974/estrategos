"""
FASE 3 — Análise Exploratória, PCA, Clusters e IPE
====================================================
Entrada:  outputs_fase2/tabela_mestre_ra.csv
          outputs_fase3c/votos_campo_ra.csv  (ou outputs_fase3b/)
Saídas:
  outputs_fase3/correlacoes.csv       → correlações entre variáveis
  outputs_fase3/pca_componentes.csv   → cargas dos componentes principais
  outputs_fase3/clusters_ra.csv       → cluster de cada RA
  outputs_fase3/ipe_completo.csv      → IPE por RA × cargo × perfil político
  outputs_fase3/narrativas_ra.csv     → narrativa estratégica automática por RA

Dependências: pip install pandas numpy scikit-learn matplotlib seaborn
"""

from pathlib import Path
import warnings
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer

warnings.filterwarnings("ignore")

DIR_IN   = Path("outputs_fase2")
DIR_OUT  = Path("outputs_fase3")
DIR_F3B  = Path("outputs_fase3b")
DIR_F3C  = Path("outputs_fase3c")
DIR_OUT.mkdir(exist_ok=True)

# ─────────────────────────────────────────────────────────────
# VARIÁVEIS SOCIOECONÔMICAS PARA PCA
# ─────────────────────────────────────────────────────────────

VARS_PCA = [
    "DOM_renda_pc_media",
    "DOM_pct_classe_AB",
    "DOM_pct_classe_DE",
    "DOM_pct_inseg_alimentar",
    "DOM_pct_alugado",
    "MOR_pct_servidor_total",
    "MOR_pct_servidor_fed",
    "MOR_pct_privado",
    "MOR_pct_conta_propria",
    "MOR_pct_beneficio_social",
    "MOR_pct_nativo_df",
    "MOR_pct_superior",
    "MOR_pct_sem_fund",
    "MOR_pct_plano_saude",
    "MOR_pct_jovem_1624",
    "MOR_pct_idoso_60mais",
    "MOR_renda_ind_media",
]

# ─────────────────────────────────────────────────────────────
# PESOS DO IPE POR CARGO
# ─────────────────────────────────────────────────────────────
#
# Afinidade:  alinhamento histórico do campo naquele cargo naquela RA
#             (blend de voto real + perfil estrutural PDAD)
# Conversão:  potencial não realizado — onde o perfil PDAD sugere
#             mais do que o eleitor historicamente entregou
# Massa:      volume eleitoral bruto do cargo naquela RA
# Logística:  eficiência de campanha (custo por voto)
#
# Governador: precisa de cobertura ampla → conversão e massa
# Senador:    majoritário com 2 vagas → conversão crítica
# Dep. Federal: DF todo, disputa acirrada → mais massa
# Dep. Distrital: concentração local → afinidade e logística

PESOS_CARGO = {
    "GOVERNADOR": {
        "w_afinidade": 0.25, "w_conversao": 0.35,
        "w_massa":     0.30, "w_logistica": 0.10,
        "col_votos":   "TSE_GOVERNADOR_total_votos",
        "cargo_norm":  "GOVERNADOR",
    },
    "SENADOR": {
        "w_afinidade": 0.20, "w_conversao": 0.40,
        "w_massa":     0.35, "w_logistica": 0.05,
        "col_votos":   "TSE_SENADOR_total_votos",
        "cargo_norm":  "SENADOR",
    },
    "DEPUTADO_FEDERAL": {
        "w_afinidade": 0.30, "w_conversao": 0.25,
        "w_massa":     0.35, "w_logistica": 0.10,
        "col_votos":   "TSE_DEPUTADO_FEDERAL_total_votos",
        "cargo_norm":  "DEPUTADO_FEDERAL",
    },
    "DEPUTADO_DISTRITAL": {
        "w_afinidade": 0.35, "w_conversao": 0.20,
        "w_massa":     0.25, "w_logistica": 0.20,
        "col_votos":   "TSE_DEPUTADO_DISTRITAL_total_votos",
        "cargo_norm":  "DEPUTADO_DISTRITAL",
    },
}

# ─────────────────────────────────────────────────────────────
# PERFIS — DIMENSÃO ESTRUTURAL (PDAD)
# Predisposição sociológica — proxy quando não há voto real
# ─────────────────────────────────────────────────────────────
#
# Calibrado pelas correlações PDAD × voto por campo no DF 2022.
# No DF o voto progressista é de escolaridade alta e funcionalismo,
# moderado domina nas satélites de baixa renda, liberal/cons. na
# alta renda e empreendedores.

PERFIS = {
    "progressista": {
        "descricao": "Candidatura progressista / campo popular",
        "variaveis": {
            "MOR_pct_superior":         +0.30,  # r=+0.63
            "MOR_pct_plano_saude":      +0.25,  # r=+0.70
            "MOR_pct_ocupado":          +0.20,  # r=+0.67
            "MOR_pct_nativo_df":        +0.15,
            "MOR_pct_servidor_total":   +0.10,
        },
    },
    "moderado": {
        "descricao": "Candidatura de centro / institucional",
        "variaveis": {
            "MOR_pct_beneficio_social":  +0.30,
            "DOM_pct_classe_DE":         +0.25,
            "MOR_pct_migrante":          +0.20,
            "MOR_pct_desocupado":        +0.15,
            "MOR_pct_jovem_1624":        +0.10,
        },
    },
    "liberal_conservador": {
        "descricao": "Candidatura liberal / conservadora",
        "variaveis": {
            "DOM_pct_classe_AB":         +0.30,
            "MOR_pct_nativo_df":         +0.25,
            "MOR_pct_conta_propria":     +0.20,
            "MOR_pct_plano_saude":       +0.15,
            "MOR_pct_superior":          +0.10,
        },
    },
}

# Mapa de nomes de campo para normalização
CAMPO_NORM_MAP = {
    "progressista":       "progressista",
    "moderado":           "moderado",
    "liberal_conservador":"liberal_conservador",
    "liberal conservador":"liberal_conservador",
    "liberal/conservador":"liberal_conservador",
    "outros":             "outros",
}


# ─────────────────────────────────────────────────────────────
# ETAPA 1 — CARREGAR DADOS
# ─────────────────────────────────────────────────────────────

def carregar_dados():
    df = pd.read_csv(DIR_IN / "tabela_mestre_ra.csv", encoding="utf-8")
    df = df[df["RA_COD"].notna() & df["RA_NOME"].notna()].copy()
    df["RA_COD"] = df["RA_COD"].astype(int)
    print(f"   {len(df)} RAs carregadas | {len(df.columns)} colunas")
    return df


def carregar_votos_campo():
    """
    Carrega votos reais por cargo × campo × RA.
    Retorna DataFrame com colunas: RA_NOME, DS_CARGO, CAMPO, PCT
    ou None se arquivo não encontrado.
    """
    candidatos = [
        DIR_F3C / "votos_campo_ra.csv",
        DIR_F3B / "votos_campo_politico_ra.csv",
        DIR_F3B / "votos_campo_ra.csv",
    ]
    for p in candidatos:
        if p.exists():
            df = pd.read_csv(p)
            # Normalizar cargo
            if "DS_CARGO" in df.columns:
                df["_cargo_norm"] = (
                    df["DS_CARGO"].str.upper().str.strip()
                    .str.replace(" ", "_", regex=False)
                    .str.replace("-", "_", regex=False)
                )
            elif "CARGO" in df.columns:
                df["_cargo_norm"] = (
                    df["CARGO"].str.upper().str.strip()
                    .str.replace(" ", "_", regex=False)
                )
            # Normalizar campo
            campo_col = "CAMPO" if "CAMPO" in df.columns else "PERFIL"
            df["_campo_norm"] = (
                df[campo_col].str.lower().str.strip()
                .str.replace(" ", "_", regex=False)
                .str.replace("/", "_", regex=False)
                .str.replace("-", "_", regex=False)
                .map(lambda x: CAMPO_NORM_MAP.get(x, x))
            )
            print(f"   Votos por campo carregados: {p.name} ({len(df)} linhas)")
            return df
    print("   ⚠ votos_campo_ra.csv não encontrado — afinidade usará só PDAD")
    return None


# ─────────────────────────────────────────────────────────────
# ETAPA 2 — CORRELAÇÕES
# ─────────────────────────────────────────────────────────────

def calcular_correlacoes(df):
    cols_votos = [c for c in df.columns if "total_votos" in c]
    cols_pdad  = [c for c in VARS_PCA if c in df.columns]
    cols_alvo  = cols_votos if cols_votos else cols_pdad[:5]

    rows = []
    for var_pdad in cols_pdad:
        for var_alvo in cols_alvo:
            x = pd.to_numeric(df[var_pdad], errors="coerce")
            y = pd.to_numeric(df[var_alvo], errors="coerce")
            mask = x.notna() & y.notna()
            if mask.sum() >= 5:
                rows.append({
                    "VAR_PDAD":   var_pdad,
                    "VAR_ALVO":   var_alvo,
                    "CORRELACAO": round(x[mask].corr(y[mask]), 4),
                    "N":          int(mask.sum()),
                })

    df_corr = pd.DataFrame(rows).sort_values("CORRELACAO", key=abs, ascending=False)
    df_corr.to_csv(DIR_OUT / "correlacoes.csv", index=False)
    print(f"   ✓ {len(df_corr)} pares de correlação calculados")
    print("\n   TOP 10 correlações mais fortes (|r|):")
    for _, row in df_corr.head(10).iterrows():
        sinal = "↑" if row["CORRELACAO"] > 0 else "↓"
        print(f"     {sinal} {row['VAR_PDAD']:<35} × {row['VAR_ALVO']:<35} r={row['CORRELACAO']:+.3f}")
    return df_corr


# ─────────────────────────────────────────────────────────────
# ETAPA 3 — PCA
# ─────────────────────────────────────────────────────────────

def executar_pca(df):
    cols   = [c for c in VARS_PCA if c in df.columns]
    X      = df[cols].copy()
    imputer = SimpleImputer(strategy="median")
    X_imp  = imputer.fit_transform(X)
    scaler = StandardScaler()
    X_std  = scaler.fit_transform(X_imp)
    pca    = PCA(n_components=min(6, len(cols)))
    scores = pca.fit_transform(X_std)

    var_exp = pca.explained_variance_ratio_
    print(f"\n   Variância explicada por componente:")
    acum = 0
    for i, v in enumerate(var_exp):
        acum += v
        print(f"     PC{i+1}: {v*100:.1f}%  (acumulado: {acum*100:.1f}%)")

    df_cargas = pd.DataFrame(
        pca.components_.T, index=cols,
        columns=[f"PC{i+1}" for i in range(pca.n_components_)]
    ).round(4)
    df_cargas.index.name = "VARIAVEL"
    df_cargas["COMUNALIDADE"] = (df_cargas**2).sum(axis=1).round(4)
    df_cargas.to_csv(DIR_OUT / "pca_componentes.csv")

    df_scores = pd.DataFrame(scores, columns=[f"PC{i+1}" for i in range(pca.n_components_)])
    df_scores.insert(0, "RA_COD",  df["RA_COD"].values)
    df_scores.insert(1, "RA_NOME", df["RA_NOME"].values)

    print("\n   Interpretação dos PCs (variáveis com maior carga |≥0.3|):")
    for pc in df_cargas.columns[:-1]:
        top = df_cargas[pc].abs().nlargest(4)
        descr = " | ".join([f"{v} ({df_cargas.loc[v, pc]:+.2f})" for v in top.index])
        print(f"     {pc}: {descr}")

    return df_scores, df_cargas, pca, scaler, imputer, cols


# ─────────────────────────────────────────────────────────────
# ETAPA 4 — CLUSTERIZAÇÃO
# ─────────────────────────────────────────────────────────────

def clusterizar(df, df_scores):
    X_pca = df_scores[[f"PC{i+1}" for i in range(min(3, len(df_scores.columns)-2))]].values
    km    = KMeans(n_clusters=4, random_state=42, n_init=20)
    labels = km.fit_predict(X_pca)

    df_cl = df_scores[["RA_COD", "RA_NOME"]].copy()
    df_cl["CLUSTER"] = labels

    df_merged = df_cl.merge(
        df[["RA_COD"] + [c for c in VARS_PCA if c in df.columns]], on="RA_COD"
    )
    renda_por_cluster = df_merged.groupby("CLUSTER")["DOM_renda_pc_media"].median()
    ordem = renda_por_cluster.sort_values(ascending=False).index.tolist()

    nomes = [
        "Brasília Central",
        "RAs Consolidadas",
        "RAs em Dinamização",
        "RAs em Movimento",
    ]
    mapa_nomes = {cluster: nomes[i] for i, cluster in enumerate(ordem)}
    df_cl["CLUSTER_NOME"] = df_cl["CLUSTER"].map(mapa_nomes)

    print(f"\n   Composição dos clusters:")
    for nome in nomes:
        grupo = df_cl[df_cl["CLUSTER_NOME"] == nome]
        if len(grupo) > 0:
            ras = ", ".join(grupo["RA_NOME"].tolist())
            print(f"     [{nome}]\n       {ras}")

    df_cl.to_csv(DIR_OUT / "clusters_ra.csv", index=False)
    return df_cl


# ─────────────────────────────────────────────────────────────
# ETAPA 5 — CONSTRUÇÃO DO IPE / SPE
# ─────────────────────────────────────────────────────────────

def normalizar_0_10(series: pd.Series) -> pd.Series:
    mn, mx = series.min(), series.max()
    if mx == mn:
        return pd.Series(5.0, index=series.index)
    return (series - mn) / (mx - mn) * 10


def score_pdad_perfil(df, perfil_config) -> pd.Series:
    """
    Score estrutural PDAD: predisposição sociológica (0–10).
    Independente de cargo — captura o perfil demográfico da RA.
    """
    score      = pd.Series(0.0, index=df.index)
    total_peso = sum(abs(p) for p in perfil_config["variaveis"].values())
    for var, peso in perfil_config["variaveis"].items():
        if var in df.columns:
            col = pd.to_numeric(df[var], errors="coerce")
            col = col.fillna(col.median())
            score += (col / 100) * (peso / total_peso) * 10
    return normalizar_0_10(score)


def score_voto_real(df, df_campo, cargo_norm, campo_norm) -> pd.Series | None:
    """
    Score baseado no voto real histórico (cargo × campo × RA).
    Retorna None se dados não disponíveis.
    """
    if df_campo is None:
        return None
    sub = df_campo[
        (df_campo["_cargo_norm"] == cargo_norm) &
        (df_campo["_campo_norm"] == campo_norm)
    ]
    if sub.empty:
        return None
    pct_map = sub.set_index("RA_NOME")["PCT"].to_dict()
    pct     = df["RA_NOME"].map(pct_map).fillna(0.0)
    return normalizar_0_10(pct)


def calcular_afinidade(df, perfil_config, df_campo, cargo_norm, campo_norm,
                        peso_real=0.65, peso_pdad=0.35) -> pd.Series:
    """
    Afinidade = blend de comportamento histórico + predisposição estrutural.

    - peso_real (65%): o que o eleitor desta RA realmente fez nas urnas
      para este cargo×campo → captura fidelidade e tendência
    - peso_pdad (35%): o que o perfil socioeconômico sugere
      → captura potencial latente e estabilidade estrutural

    Varia por cargo×campo×RA porque o eleitorado vota diferente
    para Dep. Distrital vs Governador.
    """
    s_pdad = score_pdad_perfil(df, perfil_config)
    s_real = score_voto_real(df, df_campo, cargo_norm, campo_norm)

    if s_real is not None:
        blend = normalizar_0_10(peso_real * s_real + peso_pdad * s_pdad)
        return blend
    else:
        return s_pdad


def calcular_conversao(df, s_pdad_norm, s_real_norm, s_massa) -> pd.Series:
    """
    Conversão = pool de votos ainda não capturados × predisposição estrutural.

    Fórmula: (10 - score_real) * score_pdad / 10
    - (10 - score_real): quanto do eleitorado deste cargo×RA ainda NÃO vota
      no campo — este é o pool conversível
    - * score_pdad / 10: peso pela predisposição estrutural — só faz sentido
      tentar converter onde há base sociológica favorável

    Resultado: alto onde há muitos eleitores potenciais E estrutura favorável;
    zero onde o campo já capturou todos ou onde não há base estrutural.

    RAs sem zona eleitoral própria (massa=0) recebem conversão=0,
    pois o score_real=0 nestas RAs é ausência de dado, não oportunidade.

    Se não há dados de voto real: fallback para zona de conversão
    (afinidade entre 3 e 7 = máximo potencial de persuasão).
    """
    if s_real_norm is not None:
        pool = (10 - s_real_norm) * s_pdad_norm / 10
        # Zerar RAs sem massa (sem zona eleitoral) — SCORE_REAL=0 ali é
        # ausência de dado, não oportunidade de conversão
        pool = pool.where(s_massa > 0, other=0.0)
        return normalizar_0_10(pool)
    else:
        zona = 10 - (s_pdad_norm - 5).abs() * 2
        zona = zona.clip(0, 10)
        return normalizar_0_10(zona * s_massa)


def calcular_massa(df, col_votos_cargo=None) -> pd.Series:
    """
    Massa eleitoral: volume de votos do cargo nesta RA,
    descontado por proxy de abstenção.
    Varia por cargo (Dep. Distrital tem padrão diferente de Governador).
    """
    def col_or_zero(nome):
        if nome in df.columns:
            return pd.to_numeric(df[nome], errors="coerce").fillna(0)
        return pd.Series(0.0, index=df.index)

    proxy_abs = (
        col_or_zero("MOR_pct_jovem_1624") * 0.4 +
        col_or_zero("DOM_pct_classe_DE")  * 0.6
    ) / 100

    if col_votos_cargo and col_votos_cargo in df.columns:
        votos = pd.to_numeric(df[col_votos_cargo], errors="coerce").fillna(0)
    else:
        col_gov = next((c for c in df.columns if "GOVERNADOR_total_votos" in c), None)
        votos   = pd.to_numeric(df[col_gov], errors="coerce").fillna(0) if col_gov else col_or_zero("EL_total_aptos")

    RA_SEM_ZONA = {"Park Way", "SIA", "Fercal", "Sol Nascente/Pôr do Sol", "Arniqueira"}
    if "RA_NOME" in df.columns:
        mask = df["RA_NOME"].isin(RA_SEM_ZONA) & (votos == 0)
        votos = votos.copy()
        votos[mask] = 0

    return normalizar_0_10(votos * (1 - proxy_abs * 0.3))


def calcular_logistica(df) -> pd.Series:
    """
    Logística: eficiência de custo por voto.
    RAs menores têm custo/voto mais baixo — escala log para spread uniforme.
    RAs sem zona eleitoral própria recebem logística=0 (dado ausente).
    Fixo por RA — infra não muda entre cargos.
    """
    RA_SEM_ZONA = {"Park Way", "SIA", "Fercal", "Sol Nascente/Pôr do Sol", "Arniqueira"}
    sem_zona_mask = (
        df["RA_NOME"].isin(RA_SEM_ZONA)
        if "RA_NOME" in df.columns
        else pd.Series(False, index=df.index)
    )

    if "EL_total_aptos" in df.columns:
        tot = pd.to_numeric(df["EL_total_aptos"], errors="coerce").fillna(0)
    elif "DOM_total_estimado" in df.columns:
        tot = pd.to_numeric(df["DOM_total_estimado"], errors="coerce").fillna(0)
    else:
        tot = pd.Series(0.0, index=df.index)

    tot = tot.copy()
    tot[sem_zona_mask] = 0
    median_val = tot[tot > 0].median() if (tot > 0).any() else 1.0
    tot = tot.replace(0, np.nan).fillna(median_val)

    log_score = np.log(1 / tot)
    result = normalizar_0_10(log_score)
    result[sem_zona_mask] = 0.0
    return result


def calcular_ipe(df, df_clusters, df_campo):
    """
    SPE completo: 4 cargos × 3 campos × 33 RAs.

    Cada combinação tem:
    - Afinidade: blend voto real (65%) + PDAD estrutural (35%)
    - Conversão: gap entre potencial e resultado histórico × massa
    - Massa: volume eleitoral do cargo nessa RA
    - Logística: eficiência de custo (fixo por RA)
    - IPE: combinação ponderada pelos pesos do cargo
    """
    df_ipe = df[["RA_COD", "RA_NOME"]].copy()
    df_ipe = df_ipe.merge(df_clusters[["RA_COD", "CLUSTER_NOME"]], on="RA_COD", how="left")

    s_logistica = calcular_logistica(df)
    resultados  = []

    for cargo, pesos in PESOS_CARGO.items():
        cargo_norm    = pesos["cargo_norm"]
        col_votos     = pesos.get("col_votos")
        s_massa       = calcular_massa(df, col_votos)

        for perfil_nome, perfil_cfg in PERFIS.items():
            # Score estrutural PDAD (independente de cargo)
            s_pdad = score_pdad_perfil(df, perfil_cfg)

            # Score de voto real (cargo×campo×RA)
            s_real = score_voto_real(df, df_campo, cargo_norm, perfil_nome)

            # Afinidade = blend comportamento real + predisposição estrutural
            s_afin = calcular_afinidade(df, perfil_cfg, df_campo, cargo_norm, perfil_nome)

            # Conversão = potencial não realizado
            s_conv = calcular_conversao(df, s_pdad, s_real, s_massa)

            # IPE ponderado
            ipe_raw = (
                pesos["w_afinidade"] * s_afin   +
                pesos["w_conversao"] * s_conv   +
                pesos["w_massa"]     * s_massa  +
                pesos["w_logistica"] * s_logistica
            )
            ipe = normalizar_0_10(ipe_raw)

            for i, (_, row) in enumerate(df_ipe.iterrows()):
                resultados.append({
                    "RA_COD":           row["RA_COD"],
                    "RA_NOME":          row["RA_NOME"],
                    "CLUSTER":          row["CLUSTER_NOME"],
                    "CARGO":            cargo,
                    "PERFIL":           perfil_nome,
                    "PERFIL_DESC":      perfil_cfg["descricao"],
                    "IPE":              round(ipe.iloc[i], 2),
                    "SCORE_AFINIDADE":  round(s_afin.iloc[i],      2),
                    "SCORE_CONVERSAO":  round(s_conv.iloc[i],       2),
                    "SCORE_MASSA":      round(s_massa.iloc[i],      2),
                    "SCORE_LOGISTICA":  round(s_logistica.iloc[i],  2),
                    # Debug: componentes separados
                    "SCORE_PDAD":       round(s_pdad.iloc[i],       2),
                    "SCORE_REAL":       round(s_real.iloc[i], 2) if s_real is not None else None,
                })

    df_ipe_full = pd.DataFrame(resultados)
    df_ipe_full.to_csv(DIR_OUT / "ipe_completo.csv", index=False)

    # Verificar variação por cargo para uma RA de exemplo
    exemplo = df_ipe_full[
        (df_ipe_full["RA_NOME"] == "Brasília (Plano Piloto)") &
        (df_ipe_full["PERFIL"]  == "progressista")
    ][["CARGO","IPE","SCORE_AFINIDADE","SCORE_CONVERSAO","SCORE_MASSA"]].to_string(index=False)
    print(f"\n   Exemplo — Brasília/Plano Piloto × progressista:\n{exemplo}")

    print(f"\n   ✓ IPE calculado: {len(df_ipe_full)} combinações (RA × cargo × perfil)")
    return df_ipe_full


# ─────────────────────────────────────────────────────────────
# ETAPA 6 — NARRATIVAS ESTRATÉGICAS
# ─────────────────────────────────────────────────────────────

def gerar_narrativa(row_ra, row_ipe_gov_prog, row_ipe_gov_mod, row_ipe_gov_lib):
    ra       = row_ra["RA_NOME"]
    renda    = row_ra.get("DOM_renda_pc_media", 0) or 0
    servidor = row_ra.get("MOR_pct_servidor_total", 0) or 0
    beneficio= row_ra.get("MOR_pct_beneficio_social", 0) or 0
    nativo   = row_ra.get("MOR_pct_nativo_df", 0) or 0

    linhas = [f"{ra}"]  # sem ## — o dashboard já formata o título

    if renda > 5000:
        linhas.append(f"RA de alta renda (R${renda:,.0f} per capita). "
                      f"Eleitorado exigente, sofisticado, responde a propostas técnicas.")
    elif renda > 2000:
        linhas.append(f"RA de renda média (R${renda:,.0f} per capita). "
                      f"Eleitorado volátil — campo estratégico de conversão.")
    else:
        linhas.append(f"RA de baixa renda (R${renda:,.0f} per capita). "
                      f"Alto volume eleitoral, sensível a agenda social e de serviços.")

    if servidor > 20:
        linhas.append(f"Funcionalismo público expressivo ({servidor:.0f}% dos moradores). "
                      f"Agenda: estabilidade, carreira pública, gestão eficiente.")
    elif servidor > 12:
        linhas.append(f"Funcionalismo moderado ({servidor:.0f}%). "
                      f"Relevante mas não dominante na formação de opinião.")

    if beneficio > 22:
        linhas.append(f"Alta dependência de benefício social ({beneficio:.0f}%). "
                      f"Agenda: manutenção e ampliação de programas sociais.")
    elif beneficio < 12:
        linhas.append(f"Baixa dependência de benefício ({beneficio:.0f}%). "
                      f"Eleitorado mais autônomo — agenda econômica e serviços.")

    if nativo > 55:
        linhas.append(f"Maioria nativa do DF ({nativo:.0f}%). "
                      f"Identidade distrital forte — valorizar pertencimento e história local.")
    else:
        linhas.append(f"Maioria migrante ({100-nativo:.0f}% nascidos fora do DF). "
                      f"Agenda de integração, moradia, mobilidade urbana.")

    if row_ipe_gov_prog and row_ipe_gov_prog > 7:
        linhas.append(f"→ PRIORIDADE ALTA (progressista, SPE={row_ipe_gov_prog:.1f}): "
                      f"concentrar recursos aqui.")
    elif row_ipe_gov_mod and row_ipe_gov_mod > 7:
        linhas.append(f"→ PRIORIDADE ALTA (moderado, SPE={row_ipe_gov_mod:.1f}): "
                      f"terreno fértil para candidatura institucional.")
    elif row_ipe_gov_lib and row_ipe_gov_lib > 7:
        linhas.append(f"→ PRIORIDADE ALTA (liberal/conservador, SPE={row_ipe_gov_lib:.1f}).")
    else:
        linhas.append("→ PRIORIDADE SECUNDÁRIA: investimento moderado, monitoramento.")

    return " ".join(linhas)


def gerar_narrativas(df, df_ipe):
    rows    = []
    ipe_gov = df_ipe[df_ipe["CARGO"] == "GOVERNADOR"]

    for _, row_ra in df.iterrows():
        ra_cod = row_ra["RA_COD"]
        def get_ipe(perfil):
            sub = ipe_gov[(ipe_gov["RA_COD"] == ra_cod) & (ipe_gov["PERFIL"] == perfil)]
            return sub["IPE"].iloc[0] if len(sub) > 0 else None

        narrativa = gerar_narrativa(
            row_ra, get_ipe("progressista"),
            get_ipe("moderado"), get_ipe("liberal_conservador"),
        )
        rows.append({"RA_COD": ra_cod, "RA_NOME": row_ra["RA_NOME"], "NARRATIVA": narrativa})

    df_narr = pd.DataFrame(rows)
    df_narr.to_csv(DIR_OUT / "narrativas_ra.csv", index=False)
    print(f"   ✓ Narrativas geradas para {len(df_narr)} RAs")
    return df_narr


def imprimir_ranking_ipe(df_ipe, cargo="GOVERNADOR", perfil="moderado"):
    sub = (df_ipe[(df_ipe["CARGO"] == cargo) & (df_ipe["PERFIL"] == perfil)]
           .sort_values("IPE", ascending=False).reset_index(drop=True))
    print(f"\n{'═'*80}")
    print(f"  RANKING SPE — {cargo} | {perfil.upper()}")
    print(f"{'─'*80}")
    print(f"  {'#':>3}  {'RA':<28}  {'SPE':>5}  {'AFIN':>5}  {'CONV':>5}  {'MASSA':>5}  {'LOG':>5}")
    print(f"{'─'*80}")
    for i, row in sub.iterrows():
        print(f"  {i+1:>3}  {row['RA_NOME']:<28}  {row['IPE']:>5.1f}  "
              f"{row['SCORE_AFINIDADE']:>5.1f}  {row['SCORE_CONVERSAO']:>5.1f}  "
              f"{row['SCORE_MASSA']:>5.1f}  {row['SCORE_LOGISTICA']:>5.1f}")
    print(f"{'═'*80}")


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

def main():
    print("="*72)
    print("  FASE 3 — Análise Exploratória, PCA, Clusters e SPE")
    print("="*72)

    print("\n[1/6] Carregando tabela mestre...")
    df = carregar_dados()

    print("\n[1b] Carregando votos por campo×cargo×RA...")
    df_campo = carregar_votos_campo()

    print("\n[2/6] Calculando correlações...")
    calcular_correlacoes(df)

    print("\n[3/6] Executando PCA...")
    df_scores, df_cargas, pca, scaler, imputer, cols = executar_pca(df)

    print("\n[4/6] Clusterizando RAs (K-Means, k=4)...")
    df_clusters = clusterizar(df, df_scores)

    print("\n[5/6] Calculando SPE (4 cargos × 3 perfis × 33 RAs)...")
    df_ipe = calcular_ipe(df, df_clusters, df_campo)

    print("\n[6/6] Gerando narrativas estratégicas...")
    gerar_narrativas(df, df_ipe)

    for cargo in ["GOVERNADOR", "DEPUTADO_DISTRITAL"]:
        for perfil in ["progressista", "moderado", "liberal_conservador"]:
            imprimir_ranking_ipe(df_ipe, cargo, perfil)

    print(f"""
┌─────────────────────────────────────────────────────────────────────┐
│  ARQUIVOS GERADOS em ./outputs_fase3/                               │
│                                                                     │
│  correlacoes.csv      → correlação PDAD × votos por RA             │
│  pca_componentes.csv  → cargas dos componentes principais           │
│  clusters_ra.csv      → cluster e perfil de cada RA                │
│  ipe_completo.csv     → SPE por RA × cargo × campo político        │
│  narrativas_ra.csv    → texto estratégico automático por RA         │
│                                                                     │
│  GRUPOS COMPORTAMENTAIS (K-Means, 4 clusters):                     │
│  Brasília Central | RAs Consolidadas                                │
│  RAs em Dinamização | RAs em Movimento                              │
│                                                                     │
│  SPE — 4 DIMENSÕES:                                                 │
│  Afinidade = 65% voto real + 35% perfil PDAD (varia por cargo)     │
│  Conversão = gap potencial vs histórico × massa (varia por cargo)  │
│  Massa     = volume eleitoral do cargo na RA                        │
│  Logística = eficiência de custo por voto (fixo por RA)            │
│                                                                     │
│  PRÓXIMO PASSO → fase4_v2.py → python3 injeta_geopolitica.py       │
└─────────────────────────────────────────────────────────────────────┘
""")


if __name__ == "__main__":
    main()
