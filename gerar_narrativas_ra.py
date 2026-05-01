"""
gerar_narrativas_ra.py — Gera narrativas ELI5 para cada RA do DF.

Lê os dados da PDAD 2021 + TSE 2022 que o pipeline já carrega
(via gerar_estrategos.carregar / montar_dados) e produz uma narrativa
parametrizada por RA, em tom conversacional e sem prescrição.

Saída:
  outputs_fase3/narrativas_ra.csv

Uso:
  python3 gerar_narrativas_ra.py [--preview]

  --preview  imprime amostras sem sobrescrever o CSV
"""

from pathlib import Path
import csv, sys

from gerar_estrategos import carregar, montar_dados

OUT_PATH = Path("outputs_fase3/narrativas_ra.csv")
RA_SEM_ZONA = {"Park Way", "SIA", "Fercal", "Sol Nascente/Pôr do Sol", "Arniqueira"}

# RA_NOME → RA_COD (sequência canônica)
RA_COD = {
    "Brasília (Plano Piloto)": 1, "Gama": 2, "Taguatinga": 3, "Brazlândia": 4,
    "Sobradinho": 5, "Planaltina": 6, "Paranoá": 7, "Núcleo Bandeirante": 8,
    "Ceilândia": 9, "Guará": 10, "Cruzeiro": 11, "Samambaia": 12,
    "Santa Maria": 13, "São Sebastião": 14, "Recanto das Emas": 15,
    "Lago Sul": 16, "Riacho Fundo": 17, "Lago Norte": 18, "Candangolândia": 19,
    "Águas Claras": 20, "Riacho Fundo II": 21, "Sudoeste/Octogonal": 22,
    "Varjão": 23, "Park Way": 24, "SCIA/Estrutural": 25, "Sobradinho II": 26,
    "Jardim Botânico": 27, "Itapoã": 28, "SIA": 29,
    "Vicente Pires": 30, "Fercal": 31, "Sol Nascente/Pôr do Sol": 32, "Arniqueira": 33,
}


# ── Formatadores ──────────────────────────────────────────────────────────────

def f_pct(v):
    if v is None: return "—"
    return f"{round(v)}%"

def f_renda(v):
    if v is None or v == 0: return "—"
    return f"R$ {v/1000:.1f} mil".replace(".", ",")

def f_volume(v):
    if v is None or v == 0: return "—"
    if v >= 1_000_000: return f"{v/1_000_000:.1f} milhões".replace(".", ",")
    if v >= 1_000: return f"{round(v/1000)} mil"
    return str(round(v))


# ── Helpers de classificação ──────────────────────────────────────────────────

def perfil_renda(renda):
    if renda is None: return "renda não informada"
    if renda >= 5500: return "renda alta"
    if renda >= 3500: return "renda média-alta"
    if renda >= 2200: return "renda média"
    if renda >= 1500: return "renda média-baixa"
    return "renda baixa"

def perfil_classe(d):
    pct_ab = d.get("pct_ab") or 0
    pct_de = d.get("pct_de") or 0
    if pct_ab >= 40:
        return f"forte presença de classe A/B ({f_pct(pct_ab)})"
    if pct_de >= 45:
        return f"predominância de classe D/E ({f_pct(pct_de)})"
    if pct_ab >= 20:
        return f"presença significativa de classe A/B ({f_pct(pct_ab)})"
    if pct_de >= 30:
        return f"presença relevante de classe D/E ({f_pct(pct_de)})"
    return "perfil de classes médias mistas"

def perfil_ocupacao(d):
    pct_serv_fed = d.get("pct_serv_fed") or 0
    pct_serv = d.get("pct_serv") or 0
    pct_conta = d.get("pct_conta") or 0
    if pct_serv_fed >= 15:
        return f"cerca de {f_pct(pct_serv_fed)} dos moradores no serviço público federal"
    if pct_serv >= 25:
        return f"cerca de {f_pct(pct_serv)} no funcionalismo público (federal e distrital somados)"
    if pct_serv >= 15:
        return f"presença relevante de funcionalismo público ({f_pct(pct_serv)})"
    if pct_conta >= 25:
        return f"forte presença de trabalhadores por conta própria ({f_pct(pct_conta)})"
    return None


# ── Construção das frases ─────────────────────────────────────────────────────

def frase_perfil(ra_nome, d):
    pr = perfil_renda(d.get("renda_pc"))
    pc = perfil_classe(d)
    po = perfil_ocupacao(d)
    renda_s = f_renda(d.get("renda_pc"))
    base = f"{ra_nome} reúne moradores de **{pr}** ({renda_s} per capita), com {pc}"
    if po:
        return f"{base} e {po}."
    return f"{base}."

def frase_eleitorado(d):
    aptos = d.get("el_aptos") or 0
    if aptos == 0:
        return ""
    if aptos >= 200_000:
        vol = "grande"
    elif aptos >= 100_000:
        vol = "robusto"
    elif aptos >= 50_000:
        vol = "médio-grande"
    elif aptos >= 30_000:
        vol = "médio"
    else:
        vol = "pequeno"
    pct_super = d.get("el_super") or 0
    pct_sem = d.get("el_sem_fund") or 0
    if pct_super >= 50:
        esc = f", com **maioria de eleitores com ensino superior** ({f_pct(pct_super)})"
    elif pct_super >= 30:
        esc = f", com cerca de {f_pct(pct_super)} de eleitores com ensino superior"
    elif pct_sem >= 25:
        esc = f", com escolaridade média mais baixa ({f_pct(pct_sem)} sem ensino fundamental)"
    else:
        esc = ""
    return f"O eleitorado é **{vol}** ({f_volume(aptos)} aptos){esc}."

def frase_voto(d):
    votos = d.get("votos") or {}
    gov = votos.get("GOVERNADOR") or {}
    campos = {}
    for k, v in gov.items():
        pct = (v or {}).get("pct") if isinstance(v, dict) else None
        if pct is not None:
            campos[k] = pct
    if not campos:
        return ""
    nome_lbl = {"progressista": "progressista",
                "moderado": "moderado",
                "liberal_conservador": "liberal-conservador"}
    ordenados = sorted(campos.items(), key=lambda kv: -kv[1])
    dom_k, dom_v = ordenados[0]
    seg_v = ordenados[1][1] if len(ordenados) > 1 else 0
    margem = dom_v - seg_v
    dom_lbl = nome_lbl.get(dom_k, dom_k)
    if margem >= 25:
        return (f"Em 2022, na disputa para Governador, o campo **{dom_lbl}** dominou "
                f"com folga ({f_pct(dom_v)} dos votos válidos).")
    if margem >= 12:
        return (f"Em 2022, o campo **{dom_lbl}** liderou a disputa para Governador "
                f"com {f_pct(dom_v)} dos votos válidos.")
    if margem > 0:
        return (f"Em 2022, o voto para Governador se dividiu — campo **{dom_lbl}** "
                f"levemente à frente ({f_pct(dom_v)}, contra {f_pct(seg_v)} do segundo).")
    return ""

def frase_particularidade(d):
    pct_mig = d.get("pct_migrante") or 0
    pct_nat = d.get("pct_nativo") or 0
    pct_ben = d.get("pct_beneficio") or 0
    pct_inseg = d.get("pct_inseg") or 0
    if pct_mig >= 65:
        return (f"É uma das RAs com maior **proporção de migrantes** — "
                f"{f_pct(pct_mig)} dos moradores nasceram fora do DF.")
    if pct_nat >= 70:
        return (f"Tem **identidade local forte** — {f_pct(pct_nat)} dos moradores "
                f"nasceram no próprio DF.")
    if pct_ben >= 25:
        return (f"**Forte dependência de benefícios sociais** — {f_pct(pct_ben)} "
                f"dos domicílios recebem auxílio (Bolsa Família, BPC ou LOAS).")
    if pct_inseg >= 40:
        return (f"**Insegurança alimentar elevada** atinge {f_pct(pct_inseg)} dos domicílios.")
    return ""


# ── Gerador principal ─────────────────────────────────────────────────────────

def gerar_narrativa(ra_nome, d):
    """
    Gera a parte ESTRUTURAL da narrativa (perfil + eleitorado + particularidade).
    A frase de voto é dinâmica e gerada em JS conforme o cargo selecionado
    no toolbar — ver geoAbrirPanel() em injeta_geopolitica.py.
    """
    eh_sem_zona = ra_nome in RA_SEM_ZONA
    partes = [frase_perfil(ra_nome, d)]
    if eh_sem_zona:
        partes.append(
            "Esta RA **não tem zona eleitoral própria** no TSE 2022 — os números "
            "eleitorais são estimativas a partir das zonas vizinhas e devem ser "
            "lidos com essa ressalva."
        )
    else:
        f_el = frase_eleitorado(d)
        if f_el: partes.append(f_el)
    f_p = frase_particularidade(d)
    if f_p: partes.append(f_p)
    return " ".join(partes)


def main():
    preview = "--preview" in sys.argv

    print("\n  gerar_narrativas_ra.py")
    print("  " + "─" * 40)
    print("  [1/3] Carregando dados...")
    df_ipe, df_mestre, df_narr, df_campo, df_cand = carregar()
    dados = montar_dados(df_ipe, df_mestre, df_narr, df_campo, df_cand)
    print(f"        {len(dados)} RAs carregadas")

    print("  [2/3] Gerando narrativas ELI5...")
    out = []
    for ra_nome, d in dados.items():
        cod = RA_COD.get(ra_nome, 0)
        narr = gerar_narrativa(ra_nome, d)
        out.append((cod, ra_nome, narr))
    out.sort(key=lambda r: r[0])

    if preview:
        print("\n  Amostras (modo --preview, sem salvar):\n")
        amostras = ["Brasília (Plano Piloto)", "Taguatinga", "Ceilândia", "Park Way",
                    "Lago Sul", "Brazlândia"]
        for a in amostras:
            cand = next((r for r in out if r[1] == a), None)
            if cand:
                print(f"  ─── {cand[1]} ───")
                # quebra em ~95 col
                for line in [cand[2][i:i+95] for i in range(0, len(cand[2]), 95)]:
                    print(f"  {line}")
                print()
        print("  (use sem --preview para sobrescrever o CSV)")
        return

    print("  [3/3] Salvando CSV...")
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["RA_COD", "RA_NOME", "NARRATIVA"])
        for cod, nome, narr in out:
            w.writerow([cod, nome, narr])
    print(f"        ✓ {OUT_PATH} ({len(out)} narrativas)")
    print()


if __name__ == "__main__":
    main()
