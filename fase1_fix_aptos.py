"""
fase1_fix_aptos.py v3 — Abstenção por RA via perfil_comparecimento_abstencao_2022
==================================================================================
Usa QT_APTOS, QT_COMPARECIMENTO e QT_ABSTENCAO por zona eleitoral do DF.
Mapeia zona → RA usando pesos por locais de votação (mesmo método da fase1).
Elimina o problema de votos > aptos calculando a TAXA de abstenção diretamente
da fonte, sem depender de subtração entre arquivos de fontes diferentes.

Execute: python3 fase1_fix_aptos.py <caminho_para_perfil_comparecimento_abstencao_2022.zip>
Exemplo: python3 fase1_fix_aptos.py perfil_comparecimento_abstencao_2022.zip
"""

import sys, zipfile, io
from pathlib import Path
import pandas as pd
import numpy as np

DIR_OUT = Path("outputs_fase1")

RA_SEM_ZONA = {
    "Park Way", "SIA", "Fercal", "Sol Nascente/Pôr do Sol", "Arniqueira"
}

def main():
    # ── Arquivo de entrada ────────────────────────────────────────────────────
    zip_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("perfil_comparecimento_abstencao_2022.zip")
    if not zip_path.exists():
        print(f"ERRO: {zip_path} não encontrado.")
        print("Uso: python3 fase1_fix_aptos.py perfil_comparecimento_abstencao_2022.zip")
        return

    print("\n" + "="*65)
    print("  Fase 1 Fix v3 — Abstenção por RA (fonte única consistente)")
    print("="*65)

    # ── 1. Extrair abstenção por zona do DF ───────────────────────────────────
    print(f"\n1. Lendo {zip_path.name} em chunks...")
    z = zipfile.ZipFile(zip_path)

    # Tentar arquivo específico do DF ou BRASIL
    csv_df   = next((f for f in z.namelist() if "_DF.csv" in f), None)
    csv_br   = next((f for f in z.namelist() if "BRASIL" in f), None)
    csv_alvo = csv_df or csv_br
    if not csv_alvo:
        print("ERRO: arquivo do DF ou BRASIL não encontrado no zip.")
        return

    print(f"   Arquivo: {csv_alvo}")
    chunks = pd.read_csv(
        z.open(csv_alvo), sep=";", encoding="latin1",
        dtype=str, low_memory=False, chunksize=100_000
    )
    df_list = []
    for chunk in chunks:
        chunk.columns = [c.strip() for c in chunk.columns]
        mask = (chunk["SG_UF"].str.strip() == "DF") & (chunk["NR_TURNO"].str.strip() == "1")
        if mask.any():
            df_list.append(chunk[mask])

    if not df_list:
        print("ERRO: nenhum dado do DF encontrado.")
        return

    df = pd.concat(df_list, ignore_index=True)
    print(f"   {len(df):,} linhas DF · 1º turno | {df['NR_ZONA'].nunique()} zonas")

    for c in ["QT_APTOS", "QT_COMPARECIMENTO", "QT_ABSTENCAO"]:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    zona = df.groupby("NR_ZONA").agg(
        QT_APTOS         =("QT_APTOS","sum"),
        QT_COMPARECIMENTO=("QT_COMPARECIMENTO","sum"),
        QT_ABSTENCAO     =("QT_ABSTENCAO","sum")
    ).reset_index()
    zona["NR_ZONA"]        = zona["NR_ZONA"].astype(str).str.strip()
    zona["TAXA_ABSTENCAO"] = (zona["QT_ABSTENCAO"] / zona["QT_APTOS"] * 100).round(2)

    print(f"\n   {'Zona':<6} {'Aptos':>10} {'Abstenção':>12}")
    for _, r in zona.sort_values("NR_ZONA").iterrows():
        print(f"   {r['NR_ZONA']:<6} {int(r['QT_APTOS']):>10,} {r['TAXA_ABSTENCAO']:>11.2f}%")
    print(f"   Total: {zona['QT_APTOS'].sum():>9,.0f} | Média: {(zona['QT_ABSTENCAO'].sum()/zona['QT_APTOS'].sum()*100):.2f}%")

    # ── 2. Mapa local → RA com pesos ─────────────────────────────────────────
    geo_path = DIR_OUT / "locais_votacao_geo.csv"
    if not geo_path.exists():
        print(f"\nERRO: {geo_path} não encontrado. Execute fase1_correspondencia_zona_ra.py primeiro.")
        return

    print(f"\n2. Mapa zona → RA ({geo_path.name})...")
    geo = pd.read_csv(geo_path, dtype=str)
    geo["NR_ZONA"]  = geo["NR_ZONA"].astype(str).str.strip()
    geo = geo.dropna(subset=["RA_NOME"])

    geo_z = (geo.groupby(["NR_ZONA","RA_NOME"]).size().reset_index(name="N_LOCAIS"))
    tot_z = geo_z.groupby("NR_ZONA")["N_LOCAIS"].sum().rename("N_TOTAL")
    geo_z = geo_z.join(tot_z, on="NR_ZONA")
    geo_z["PESO"] = geo_z["N_LOCAIS"] / geo_z["N_TOTAL"]

    # Merge zona → RA com dados de abstenção
    geo_z = geo_z.merge(
        zona[["NR_ZONA","QT_APTOS","TAXA_ABSTENCAO"]],
        on="NR_ZONA", how="left"
    )

    # ── 3. Calcular abstenção e aptos por RA ──────────────────────────────────
    print("\n3. Calculando abstenção por RA (média ponderada por locais de votação)...")
    results = []
    for ra, grupo in geo_z.groupby("RA_NOME"):
        # Aptos: soma ponderada dos aptos de cada zona pela proporção do RA
        aptos_ra  = (grupo["QT_APTOS"] * grupo["PESO"]).sum()
        # Abstenção: média ponderada das taxas, ponderada pelos aptos da zona × peso
        peso_abs  = grupo["QT_APTOS"] * grupo["PESO"]
        taxa_ra   = ((grupo["TAXA_ABSTENCAO"] * peso_abs).sum() / peso_abs.sum()
                     if peso_abs.sum() > 0 else None)
        results.append({
            "RA_NOME":           ra,
            "EL_aptos_abs_src":  int(round(aptos_ra)) if aptos_ra > 0 else None,
            "ABSTENCAO_GOV":     round(taxa_ra, 1) if taxa_ra is not None else None,
        })

    df_res = pd.DataFrame(results)

    # ── 4a. Salvar CSV de referência para o fase2 ────────────────────────────
    ref_path = DIR_OUT / "abstencao_zona_ra.csv"
    df_res.rename(columns={"ABSTENCAO_GOV":"ABSTENCAO_GOVERNADOR"}).to_csv(ref_path, index=False)
    print(f"\n   ✓ abstencao_zona_ra.csv salvo em {ref_path}")
    df_res_local = df_res.copy()  # guardar antes do rename

    # ── 4b. Atualizar perfil_eleitorado_ra.csv e tabela_mestre_ra.csv ─────────
    perf_path = DIR_OUT / "perfil_eleitorado_ra.csv"
    if perf_path.exists():
        df_perf = pd.read_csv(perf_path)
        # Backup
        df_perf.to_csv(perf_path.with_suffix(".csv.bak"), index=False)
        df_perf = df_perf.merge(df_res, on="RA_NOME", how="left")
        # Atualizar aptos (usar nova fonte para RAs com zona própria)
        mask_ok = (~df_perf["RA_NOME"].isin(RA_SEM_ZONA)) & df_perf["EL_aptos_abs_src"].notna()
        df_perf.loc[mask_ok, "EL_total_aptos"] = df_perf.loc[mask_ok, "EL_aptos_abs_src"]
        df_perf = df_perf.drop(columns=["EL_aptos_abs_src"])
        df_perf.to_csv(perf_path, index=False)
        print(f"   ✓ {perf_path.name} atualizado")

    # Atualizar tabela_mestre
    mestre_path = Path("outputs_fase2/tabela_mestre_ra.csv")
    if mestre_path.exists():
        df_m = pd.read_csv(mestre_path)
        df_m.to_csv(mestre_path.with_suffix(".csv.bak"), index=False)
        # Remover coluna antiga se existir
        for c in ["ABSTENCAO_GOVERNADOR","ABSTENCAO_GOV"]:
            if c in df_m.columns:
                df_m = df_m.drop(columns=[c])
        df_m = df_m.merge(df_res_local[["RA_NOME","ABSTENCAO_GOV"]], on="RA_NOME", how="left")
        df_m = df_m.rename(columns={"ABSTENCAO_GOV": "ABSTENCAO_GOVERNADOR"})
        df_m.to_csv(mestre_path, index=False)
        print(f"   ✓ {mestre_path.name} atualizado")

    # ── 5. Relatório final ────────────────────────────────────────────────────
    print(f"\n{'RA':<30} {'Aptos':>10} {'Abstenção%':>12} {'Zona própria':>14}")
    print("-"*68)
    for _, r in df_res.sort_values("RA_NOME").iterrows():
        sem_z = "SIM" if r["RA_NOME"] in RA_SEM_ZONA else "não"
        aptos = f"{int(r['EL_aptos_abs_src']):,}" if r["EL_aptos_abs_src"] else "--"
        abs_v = f"{r['ABSTENCAO_GOV']:.1f}%" if r["ABSTENCAO_GOV"] else "--"
        print(f"{r['RA_NOME']:<30} {aptos:>10} {abs_v:>12} {sem_z:>14}")

    print(f"\n✅ Concluído — abstenção calculada via taxa direta da fonte")
    print("   Não há mais inconsistência votos > aptos (taxa independe de subtração)")
    print("\nPróximo passo: python3 fase4_v2.py (tabela mestre já atualizada)")
    print("="*65 + "\n")


if __name__ == "__main__":
    main()
