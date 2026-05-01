"""
classificacao_base.py — classificação territorial unificada de candidatos
==========================================================================
Helper compartilhado por extrair_votos_candidato_ra.py, fase4_v2.py e
qualquer outro consumidor que precise rotular RAs em 5 categorias para
um candidato:

  REDUTO       (sobre-índice ≥ +30%)
  BASE FORTE   (+15% ≤ sobre-índice < +30%)
  CAMPO MEDIO  (−15% < sobre-índice < +15%)
  BASE FRACA   (−30% < sobre-índice ≤ −15%)
  AUSENCIA     (sobre-índice ≤ −30%)
  SEM DADOS    (sem voto na RA ou aptos inexistentes)

Métrica: índice de sobrerrepresentação
  idx = (votos_cand_RA / total_cand) / (aptos_RA / total_aptos_DF)

Forma de exibição preferida: delta = (idx − 1) × 100, em "+X% / −X%".

Fonte de aptos por RA: outputs_fase1/perfil_eleitorado_ra.csv (col EL_total_aptos).
Cobertura: 28 RAs com zona TSE própria. As 5 RAs sem zona (Park Way, SIA,
Fercal, Sol Nascente, Arniqueira) também não aparecem nos votos por seção,
então o conjunto bate.
"""

from pathlib import Path
import pandas as pd

CAMINHO_APTOS = Path("outputs_fase1") / "perfil_eleitorado_ra.csv"

LBL_REDUTO   = "REDUTO"
LBL_FORTE    = "BASE FORTE"
LBL_MEDIA    = "CAMPO MEDIO"
LBL_FRACA    = "BASE FRACA"
LBL_AUSENCIA = "AUSENCIA"
LBL_VAZIO    = "SEM DADOS"

# Cortes em delta percentual (idx − 1).
# Ex.: idx = 1.30  →  delta = +30%  →  REDUTO
DELTA_REDUTO   = 0.30   # idx ≥ 1.30  →  reduto
DELTA_FORTE    = 0.15   # 1.15 ≤ idx < 1.30  →  base forte
DELTA_FRACA    = -0.15  # -0.30 < idx − 1 ≤ -0.15  →  base fraca (idx em 0.70..0.85)
DELTA_AUSENCIA = -0.30  # idx ≤ 0.70  →  ausência


def carregar_aptos_por_ra(caminho: Path = CAMINHO_APTOS):
    """
    Retorna (aptos_por_ra: dict[str, int], total_aptos_df: int).
    """
    df = pd.read_csv(caminho)
    aptos = {str(r["RA_NOME"]).strip(): int(r["EL_total_aptos"]) for _, r in df.iterrows()}
    return aptos, sum(aptos.values())


def _status_por_delta(delta: float) -> str:
    if delta >= DELTA_REDUTO:    return LBL_REDUTO
    if delta >= DELTA_FORTE:     return LBL_FORTE
    if delta <= DELTA_AUSENCIA:  return LBL_AUSENCIA
    if delta <= DELTA_FRACA:     return LBL_FRACA
    return LBL_MEDIA


def classificar_ras(ras_votos, total_cand, aptos_por_ra, total_aptos_df):
    """
    Classifica as RAs de um candidato por índice de sobrerrepresentação,
    em cinco categorias usando cortes absolutos em delta (idx − 1):

      ≥ +30%     → REDUTO
      +15..+30%  → BASE FORTE
      -15..+15%  → CAMPO MEDIO
      -30..-15%  → BASE FRACA
      ≤ -30%     → AUSENCIA

    Args:
      ras_votos: lista de tuplas (ra_nome, votos_int).
      total_cand: total de votos do candidato no DF.
      aptos_por_ra: dict {ra_nome: aptos_int}.
      total_aptos_df: soma dos aptos.

    Retorna lista paralela de dicts {"idx": float|None, "status": str}, na
    mesma ordem de ras_votos.

    Casos de borda:
      - total_cand <= 0          → todos SEM DADOS
      - votos == 0               → SEM DADOS
      - aptos da RA ausente/<= 0 → SEM DADOS
    """
    if total_cand is None or total_cand <= 0:
        return [{"idx": None, "status": LBL_VAZIO} for _ in ras_votos]

    out = []
    for ra, votos in ras_votos:
        apt = aptos_por_ra.get(str(ra).strip()) if aptos_por_ra else None
        if not votos or votos <= 0 or not apt or apt <= 0 or total_aptos_df <= 0:
            out.append({"idx": None, "status": LBL_VAZIO})
            continue
        share_voto = votos / total_cand
        share_apt  = apt / total_aptos_df
        if share_apt <= 0:
            out.append({"idx": None, "status": LBL_VAZIO})
            continue
        idx = share_voto / share_apt
        delta = idx - 1.0
        out.append({"idx": round(idx, 3), "status": _status_por_delta(delta)})
    return out


# Texto canônico da explicação — usar nas duas seções (Contexto > Candidatos
# e Geopolítica > Candidato) para garantir consistência editorial.
TOOLTIP_INDICE = (
    "Mostra se a região entrega mais ou menos votos do que esperado pelo "
    "tamanho dela. Plano Piloto tem cerca de 9% do eleitorado do DF — se o "
    "candidato fosse perfeitamente proporcional, deveria ter 9% dos votos "
    "dele lá. +30% ou mais = reduto; entre +15% e +30% = base forte; "
    "−15% a +15% = no esperado; entre −15% e −30% = base fraca; ≤ −30% = "
    "ausência. A classificação compara o candidato com ele mesmo, não "
    "entre candidatos."
)
