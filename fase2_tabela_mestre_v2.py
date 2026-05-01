"""
FASE 2 v2 — Tabela Mestre por Região Administrativa (DF)
=========================================================
CORRIGIDO: variáveis mapeadas pelo dicionário oficial PDAD 2021

Variáveis PDAD 2021 corretas (moradores):
  E04      → Sexo: 1=Masculino, 2=Feminino
  E14      → Nasceu no DF: 1=Sim, 2=Não
  escolaridade → Nível de instrução (variável derivada PDAD):
                  1=Sem instrução, 2=Fund. incompleto, 3=Fund. completo,
                  4=Médio incompleto, 5=Médio completo,
                  6=Superior incompleto, 7=Superior completo, 8=Sem classificação
  I01      → Procurou trabalho nos últimos 30 dias: 1=Sim
  I05      → Trabalhou nos últimos 30 dias: 1=Sim, 2=Não
  I12      → Posição na ocupação:
                  1=Setor público, 2=Militar, 3=Setor privado (excl. doméstico),
                  4=Doméstico, 5=Estágio, 6=Aprendiz, 7=Cooperativa,
                  8=Conta própria/Autônomo, 9=Empregador, 10=Negócio familiar,
                  11=Profissional liberal, 12=Serviço militar obrigatório,
                  13=Sem remuneração, 14=Religioso remunerado
  I13      → Área de ocupação (setor público): 1=Federal, 2=Estadual/Distrital, 3=Municipal
  I17      → Possui CTPS assinada: 1=Sim
  G04      → Possui plano de saúde: 1=Sim
  I22_1    → Valor recebido de benefícios sociais (Bolsa Família, BPC/LOAS):
                  0=não recebeu, >0=recebeu
  renda_ind → Soma dos rendimentos individuais (variável derivada PDAD)
  peso_mor  → Peso amostral do morador (atenção: minúsculas na PDAD 2021)

Variáveis PDAD 2021 corretas (domicílios):
  criterio_brasil → 1=A, 2=B1, 3=B2, 4=C1, 5=C2, 6=D-E
  inseg_alimentar → 1=sem insegurança, 2=leve, 3=moderada, 4=grave
  renda_domiciliar_pc → Renda per capita domiciliar (R$)
  PESO_DOM  → Peso amostral do domicílio (maiúsculas na PDAD 2021)
"""

from pathlib import Path
import numpy as np
import pandas as pd

DIR_PDAD   = Path("PDAD2021")
DIR_FASE1  = Path("outputs_fase1")
DIR_OUTPUT = Path("outputs_fase2")
DIR_OUTPUT.mkdir(exist_ok=True)

ENC = "latin1"
SEP = ";"
MISSING = [99999, 88888, 9999, 888, 999, 77777]

RA_NOMES = {
    1:"Brasília (Plano Piloto)", 2:"Gama", 3:"Taguatinga", 4:"Brazlândia",
    5:"Sobradinho", 6:"Planaltina", 7:"Paranoá", 8:"Núcleo Bandeirante",
    9:"Ceilândia", 10:"Guará", 11:"Cruzeiro", 12:"Samambaia",
    13:"Santa Maria", 14:"São Sebastião", 15:"Recanto das Emas",
    16:"Lago Sul", 17:"Riacho Fundo", 18:"Lago Norte",
    19:"Candangolândia", 20:"Águas Claras", 21:"Riacho Fundo II",
    22:"Sudoeste/Octogonal", 23:"Varjão", 24:"Park Way",
    25:"SCIA/Estrutural", 26:"Sobradinho II", 27:"Jardim Botânico",
    28:"Itapoã", 29:"SIA", 30:"Vicente Pires",
    31:"Fercal", 32:"Sol Nascente/Pôr do Sol", 33:"Arniqueira",
}


def limpar(col):
    col = pd.to_numeric(col, errors="coerce")
    col = col.replace(MISSING, np.nan)
    return col


def pct_pond(condicao, pesos):
    """% ponderada de True na condição."""
    mask = condicao.notna() & pesos.notna()
    if mask.sum() == 0:
        return np.nan
    return np.average(condicao[mask].astype(float), weights=pesos[mask]) * 100


def media_pond(serie, pesos):
    """Média ponderada ignorando NaN."""
    mask = serie.notna() & pesos.notna()
    if mask.sum() == 0:
        return np.nan
    return np.average(serie[mask], weights=pesos[mask])


# ─────────────────────────────────────────────────────────────
# ETAPA 1 — DOMICÍLIOS
# ─────────────────────────────────────────────────────────────

def processar_domicilios():
    path = DIR_PDAD / "PDAD_2021_Domicilios.csv"
    print(f"   Lendo {path.name}...")
    df = pd.read_csv(path, sep=SEP, encoding=ENC, dtype=str, low_memory=False)
    df.columns = [c.strip() for c in df.columns]

    # Detectar peso (pode ser peso_dom minúsculas ou PESO_DOM maiúsculas)
    peso_dom_col = "peso_dom" if "peso_dom" in df.columns else "PESO_DOM"
    tot_dom_col  = "tot_dom"  if "tot_dom"  in df.columns else "TOT_DOM"

    for col in ["renda_domiciliar", "renda_domiciliar_pc", "criterio_brasil",
                "inseg_alimentar", peso_dom_col]:
        if col in df.columns:
            df[col] = limpar(df[col])

    df["A01ra"] = pd.to_numeric(df["A01ra"], errors="coerce").astype("Int64")
    print(f"   {len(df):,} domicílios | peso: {peso_dom_col}")

    resultados = []
    for ra, grupo in df.groupby("A01ra"):
        peso = grupo[peso_dom_col].fillna(1) if peso_dom_col in grupo.columns else pd.Series(1, index=grupo.index)
        rec  = {"RA_COD": int(ra)}

        # Renda per capita domiciliar
        if "renda_domiciliar_pc" in grupo.columns:
            rec["DOM_renda_pc_media"] = media_pond(grupo["renda_domiciliar_pc"], peso)

        # Critério Brasil ABEP:
        # 1=A, 2=B1, 3=B2 → classe A/B
        # 4=C1, 5=C2       → classe C
        # 6=D-E             → classe D/E
        if "criterio_brasil" in grupo.columns:
            cb = grupo["criterio_brasil"]
            # cb==7 = sem classificação — excluir como MISSING
            cb_valido = cb[cb.isin([1,2,3,4,5,6])]
            peso_cb = peso[cb.isin([1,2,3,4,5,6])]
            rec["DOM_pct_classe_AB"] = pct_pond(cb_valido.isin([1, 2, 3]), peso_cb)
            rec["DOM_pct_classe_C"]  = pct_pond(cb_valido.isin([4, 5]),    peso_cb)
            rec["DOM_pct_classe_DE"] = pct_pond(cb_valido == 6,            peso_cb)

        # Insegurança alimentar: 2=leve, 3=moderada, 4=grave
        if "inseg_alimentar" in grupo.columns:
            rec["DOM_pct_inseg_alimentar"] = pct_pond(
                grupo["inseg_alimentar"].isin([2, 3, 4]), peso
            )

        resultados.append(rec)

    df_ra = pd.DataFrame(resultados).sort_values("RA_COD").reset_index(drop=True)
    print(f"   ✓ {len(df_ra)} RAs — domicílios")
    return df_ra


# ─────────────────────────────────────────────────────────────
# ETAPA 2 — MORADORES (variáveis corrigidas)
# ─────────────────────────────────────────────────────────────

def processar_moradores():
    path = DIR_PDAD / "PDAD_2021_Moradores.csv"
    print(f"   Lendo {path.name}...")
    df = pd.read_csv(path, sep=SEP, encoding=ENC, dtype=str, low_memory=False)
    df.columns = [c.strip() for c in df.columns]

    # Detectar nome do peso (pode ser PESO_MOR ou peso_mor)
    peso_col = "peso_mor" if "peso_mor" in df.columns else "PESO_MOR"

    cols_num = ["idade", "E04", "E14", "escolaridade",
                "I01", "I05", "I12", "I13", "I17",
                "G04", "I22_1", "renda_ind", peso_col]
    for col in cols_num:
        if col in df.columns:
            df[col] = limpar(df[col])

    df["A01ra"] = pd.to_numeric(df["A01ra"], errors="coerce").astype("Int64")
    df[peso_col] = df[peso_col].fillna(1)

    # Faixa eleitoral (16+) para perfil etário
    df_el = df[df["idade"] >= 16].copy()
    print(f"   {len(df):,} moradores | {len(df_el):,} em idade eleitoral (16+)")

    resultados = []
    for ra, grupo in df.groupby("A01ra"):
        peso = grupo[peso_col]
        g_el = df_el[df_el["A01ra"] == ra]
        peso_el = g_el[peso_col] if len(g_el) > 0 else pd.Series(dtype=float)

        rec = {"RA_COD": int(ra)}

        # ── Escolaridade ─────────────────────────────────────────────────
        # Denominador: moradores 16+ (igual ao TSE) para comparabilidade do gap
        # 6=superior incompleto, 7=superior completo (excluímos 8=sem classif.)
        # 1=sem instrução, 2=fundamental incompleto
        if "escolaridade" in grupo.columns and len(g_el) > 0:
            esc_el = g_el["escolaridade"] if "escolaridade" in g_el.columns else pd.Series(dtype=float)
            peso_esc = g_el[peso_col] if peso_col in g_el.columns else pd.Series(1, index=g_el.index)
            if len(esc_el) > 0:
                rec["MOR_escolaridade_media"] = media_pond(esc_el, peso_esc)
                rec["MOR_pct_superior"]  = pct_pond(esc_el.isin([6, 7]), peso_esc)
                rec["MOR_pct_sem_fund"]  = pct_pond(esc_el.isin([1, 2]), peso_esc)

        # ── Sexo (E04: 1=Masculino, 2=Feminino) ────────────────────────
        if "E04" in grupo.columns:
            rec["MOR_pct_feminino"] = pct_pond(grupo["E04"] == 2, peso)

        # ── Naturalidade (E14: 1=Nasceu no DF, 2=Não) ──────────────────
        if "E14" in grupo.columns:
            rec["MOR_pct_nativo_df"] = pct_pond(grupo["E14"] == 1, peso)
            rec["MOR_pct_migrante"]  = pct_pond(grupo["E14"] == 2, peso)

        # ── Perfil etário — POPULAÇÃO (denominador: todos os moradores) ────
        if "idade" in grupo.columns:
            rec["MOR_pct_jovem_pop"]  = pct_pond(grupo["idade"].between(16, 24), peso)
            rec["MOR_pct_idoso_pop"]  = pct_pond(grupo["idade"] >= 60,           peso)
            rec["MOR_pct_crianca"]    = pct_pond(grupo["idade"] < 16,            peso)

        # ── Perfil etário — ELEITORADO PDAD (denominador: 16+ moradores) ─────
        if len(g_el) > 0 and "idade" in g_el.columns:
            rec["EL_pct_jovem_1624"] = pct_pond(g_el["idade"].between(16, 24), peso_el)
            rec["EL_pct_idoso_60+"]  = pct_pond(g_el["idade"] >= 60,           peso_el)

        # ── Ocupação ────────────────────────────────────────────────────
        # I05: trabalhou nos últimos 30 dias (1=Sim, 2=Não)
        # I01: procurou trabalho nos últimos 30 dias (1=Sim, 2=Não)
        if "I05" in grupo.columns:
            rec["MOR_pct_ocupado"]   = pct_pond(grupo["I05"] == 1, peso)
            # Desocupado = não trabalhou E procurou emprego
            if "I01" in grupo.columns:
                desoc = (grupo["I05"] == 2) & (grupo["I01"] == 1)
                rec["MOR_pct_desocupado"] = pct_pond(desoc, peso)

        # ── Posição na ocupação (I12) ────────────────────────────────────
        # Usa apenas quem trabalhou (I05==1) como numerador,
        # mas total de moradores como denominador
        if "I12" in grupo.columns:
            i12 = grupo["I12"]

            # Setor público + militares (I12 = 1 ou 2)
            rec["MOR_pct_servidor_total"] = pct_pond(i12.isin([1, 2]), peso)

            # Servidor federal (I12==1 AND I13==1)
            if "I13" in grupo.columns:
                fed  = (i12 == 1) & (grupo["I13"] == 1)
                dist = (i12 == 1) & (grupo["I13"] == 2)
                rec["MOR_pct_servidor_fed"]  = pct_pond(fed,  peso)
                rec["MOR_pct_servidor_dist"] = pct_pond(dist, peso)

            # Setor privado (I12==3, exclui doméstico)
            rec["MOR_pct_privado"] = pct_pond(i12 == 3, peso)

            # Conta própria / autônomo (I12==8)
            rec["MOR_pct_conta_propria"] = pct_pond(i12 == 8, peso)

        # ── Plano de saúde (G04: 1=Sim) ────────────────────────────────
        if "G04" in grupo.columns:
            rec["MOR_pct_plano_saude"] = pct_pond(grupo["G04"] == 1, peso)

        # ── Benefícios sociais (I22_1: Bolsa Família, BPC/LOAS) ─────────
        # I22_1 = valor em R$ recebido no mês passado; 0 = não recebeu
        if "I22_1" in grupo.columns:
            rec["MOR_pct_beneficio_social"] = pct_pond(grupo["I22_1"] > 0, peso)

        # ── Renda individual (renda_ind = soma de todos os rendimentos) ──
        if "renda_ind" in grupo.columns:
            renda = grupo["renda_ind"].replace(0, np.nan)
            rec["MOR_renda_ind_media"] = media_pond(renda, peso)

        resultados.append(rec)

    df_ra = pd.DataFrame(resultados).sort_values("RA_COD").reset_index(drop=True)
    print(f"   ✓ {len(df_ra)} RAs — moradores")
    return df_ra


# ─────────────────────────────────────────────────────────────
# ETAPA 3 — PERFIL DO ELEITORADO TSE (Fase 1)
# ─────────────────────────────────────────────────────────────

def processar_perfil_tse():
    path = DIR_FASE1 / "perfil_eleitorado_ra.csv"
    if not path.exists():
        print("   ⚠ perfil_eleitorado_ra.csv não encontrado")
        return pd.DataFrame()
    print(f"   Lendo {path.name}...")
    df = pd.read_csv(path, dtype=str)
    df.columns = [c.strip() for c in df.columns]
    for col in [c for c in df.columns if c.startswith("EL_")]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    if "RA_NOME" in df.columns and "RA_COD" not in df.columns:
        inv = {v: k for k, v in RA_NOMES.items()}
        df["RA_COD"] = df["RA_NOME"].map(inv)
    df["RA_COD"] = pd.to_numeric(df["RA_COD"], errors="coerce").astype("Int64")
    print(f"   ✓ {len(df)} RAs — TSE")
    return df


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────


# ─────────────────────────────────────────────────────────────
# ETAPA 4 — VOTOS POR RA (Fase 1) — totais por cargo para abstenção
# ─────────────────────────────────────────────────────────────

def processar_votos() -> pd.DataFrame:
    path = DIR_FASE1 / "votos_por_ra.csv"
    if not path.exists():
        print("   ⚠ votos_por_ra.csv não encontrado — abstenção não calculada")
        return pd.DataFrame()
    print(f"   Lendo {path.name}...")
    df = pd.read_csv(path, dtype=str)
    df.columns = [c.strip() for c in df.columns]

    # Detectar colunas de total_votos por cargo
    cols_tv = [c for c in df.columns if "total_votos" in c.lower()]
    if not cols_tv:
        print("   ⚠ Nenhuma coluna total_votos encontrada")
        return pd.DataFrame()

    # Chave de merge
    if "RA_NOME" in df.columns and "RA_COD" not in df.columns:
        inv = {v: k for k, v in RA_NOMES.items()}
        df["RA_COD"] = df["RA_NOME"].map(inv)
    df["RA_COD"] = pd.to_numeric(df["RA_COD"], errors="coerce").astype("Int64")

    for c in cols_tv:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # Manter só RA_COD + colunas de total_votos
    df = df[["RA_COD"] + cols_tv].drop_duplicates(subset=["RA_COD"]).dropna(subset=["RA_COD"])
    print(f"   ✓ {len(df)} RAs · cargos: {', '.join(c.replace('TSE_','').replace('_total_votos','') for c in cols_tv)}")
    return df


def main():
    import time
    t0 = time.time()

    print()
    print("  FASE 2 v2 — Tabela Mestre DF (variáveis corrigidas)")
    print("  " + "─" * 50)

    print("\n  [1/4] Domicílios PDAD 2021...")
    df_dom = processar_domicilios()

    print("\n  [2/4] Moradores PDAD 2021...")
    df_mor = processar_moradores()

    print("\n  [3/4] Perfil eleitorado TSE...")
    df_tse = processar_perfil_tse()

    print("\n  [4/5] Votos por RA (totais por cargo)...")
    df_votos = processar_votos()

    print("\n  [5/5] Consolidando tabela mestre...")
    df = df_dom.merge(df_mor, on="RA_COD", how="outer")
    df["RA_NOME"] = df["RA_COD"].map(RA_NOMES)
    if len(df_tse) > 0:
        if "RA_NOME" in df_tse.columns:
            df_tse = df_tse.rename(columns={"RA_NOME": "RA_NOME_TSE"})
        df = df.merge(df_tse, on="RA_COD", how="left")
    if len(df_votos) > 0:
        df = df.merge(df_votos, on="RA_COD", how="left")

    # Calcular abstenção — preferir taxa direta do comparecimento (mais precisa)
    abs_ref_path = DIR_FASE1 / "abstencao_zona_ra.csv"
    if abs_ref_path.exists():
        df_abs_ref = pd.read_csv(abs_ref_path)
        # Usar taxa direta do arquivo de comparecimento para todos os cargos
        if "RA_NOME" in df_abs_ref.columns and "ABSTENCAO_GOVERNADOR" in df_abs_ref.columns:
            df = df.merge(df_abs_ref[["RA_NOME","ABSTENCAO_GOVERNADOR"]],
                         on="RA_NOME", how="left", suffixes=("","_ref"))
            if "ABSTENCAO_GOVERNADOR_ref" in df.columns:
                df["ABSTENCAO_GOVERNADOR"] = df["ABSTENCAO_GOVERNADOR_ref"]
                df = df.drop(columns=["ABSTENCAO_GOVERNADOR_ref"])
            print(f"   ✓ Abstenção por zona (comparecimento): {df['ABSTENCAO_GOVERNADOR'].notna().sum()} RAs")
        else:
            df_abs_ref = None
    else:
        df_abs_ref = None
        print("   ⚠ abstencao_zona_ra.csv não encontrado — usando cálculo por subtração")

    # Fallback: subtração aptos-votos (só para RAs sem dado direto)
    if "EL_total_aptos" in df.columns:
        for col in [c for c in df.columns if "total_votos" in c]:
            cargo = col.replace("TSE_", "").replace("_total_votos", "")
            abs_col = f"ABSTENCAO_{cargo}"
            if abs_col in df.columns and df[abs_col].notna().sum() > 0:
                continue  # já temos dado direto
            aptos = df["EL_total_aptos"]
            votos = df[col]
            mask = (aptos > 0) & (votos > 0) & (votos <= aptos)
            df[abs_col] = np.nan
            df.loc[mask, abs_col] = ((aptos - votos) / aptos * 100).round(1)[mask]

    df = df.sort_values("RA_COD").reset_index(drop=True)

    out = DIR_OUTPUT / "tabela_mestre_ra.csv"
    df.to_csv(out, index=False)

    elapsed = time.time() - t0
    print(f"\n  ✅ {len(df)} RAs · {len(df.columns)} indicadores")
    print(f"  ✅ Salvo em {out}")
    print(f"  ✅ Concluído em {elapsed:.1f}s")
    print()

    # ── Sanity check ──────────────────────────────────────────
    print("  SANITY CHECK — valores esperados:")
    print("  (Lago Sul deve ter MAIOR renda, MENOR benefício social)")
    print("  (SCIA/Estrutural deve ter MENOR renda, MAIOR benefício)")
    print()

    checks = [
        ("DOM_renda_pc_media",      "Renda P/C",       "Lago Sul > SCIA"),
        ("MOR_pct_plano_saude",     "Plano saúde",     "Lago Sul > Ceilândia"),
        ("MOR_pct_beneficio_social","Bolsa Família",   "SCIA > Lago Sul"),
        ("MOR_pct_nativo_df",       "Nativo DF",       "Brasília > Ceilândia"),
        ("MOR_pct_superior",        "Superior",        "Lago Sul > SCIA"),
    ]

    if "RA_NOME" not in df.columns:
        df["RA_NOME"] = df["RA_COD"].map(RA_NOMES)
    ra_ref = {r["RA_NOME"]: r for _, r in df.iterrows()}

    for col, label, expectativa in checks:
        if col not in df.columns:
            print(f"  ⚠ {label}: coluna não encontrada")
            continue
        lago  = ra_ref.get("Lago Sul", {}).get(col, None)
        scia  = ra_ref.get("SCIA/Estrutural", {}).get(col, None)
        ceil  = ra_ref.get("Ceilândia", {}).get(col, None)
        bsb   = ra_ref.get("Brasília (Plano Piloto)", {}).get(col, None)

        val_str = []
        if lago  is not None and not pd.isna(lago):  val_str.append(f"Lago Sul={lago:.1f}")
        if scia  is not None and not pd.isna(scia):  val_str.append(f"SCIA={scia:.1f}")
        if ceil  is not None and not pd.isna(ceil):  val_str.append(f"Ceilândia={ceil:.1f}")
        if bsb   is not None and not pd.isna(bsb):   val_str.append(f"Brasília={bsb:.1f}")

        print(f"  {label:<22}: {', '.join(val_str)} [{expectativa}]")
    print()


if __name__ == "__main__":
    main()
