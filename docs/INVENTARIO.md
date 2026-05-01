# Inventário do projeto + arquitetura-alvo multi-UF

**Data:** 2026-05-01 · **Estado:** rascunho para revisão antes da faxina

Objetivo: classificar tudo que existe na pasta para (a) deletar/arquivar lixo e (b) saber o que vai precisar virar parametrizável quando o painel for além do DF (SP, MG, etc.).

---

## 1. Pipeline de produção atual (o que NÃO pode quebrar)

```
                     ┌── outputs_fase0/candidatos_2022.csv
fase0_historico.py ──┤
                     └── (outros CSVs de trajetórias/transferência: só auto-uso)

fase1_correspondencia_zona_ra.py ──► outputs_fase1/{locais_votacao_geo, perfil_eleitorado_ra,
                                                     zona_ra_df, votos_por_ra}.csv
fase1c_perfil_secao.py            ──► refina perfil_eleitorado_ra (versão atual)
fase1_fix_aptos.py                ──► fix em cima de perfil_eleitorado_ra
fase2_tabela_mestre_v2.py         ──► outputs_fase2/tabela_mestre_ra.csv
fase3_ipe.py                      ──► outputs_fase3/{ipe_completo, narrativas_ra, clusters_ra,
                                                     pca_componentes, correlacoes}.csv
fase3c_campo_politico.py          ──► outputs_fase3c/{votos_campo_ra, votos_candidato_ra}.csv
extrair_votos_candidato_ra.py     ──► outputs_fase3c/votos_candidato_ra.csv (versão atual; lê
                                       classificacao_base + locais_votacao_geo)
extrair_orcamento_referencia.py   ──► outputs_tse_2022_DF/orcamento_referencia.json

──────────────────── BUILD DO DASHBOARD ────────────────────
fase4_v2.py                       ──► dashboard_spe_df.html
injeta_geopolitica.py             ──► dashboard_com_geo.html  (anexa GeoJSON)
injeta_candidato.py               ──► index.html              (anexa A5_CANDS base64)

⚠️ Em 2026-04/05, `index.html` foi editado direto (filtros sem acento, PB_GASTO_POR_CAND,
   PB_SENADOR_CENARIOS, modais novos). O `JS_CODE` em `fase4_v2.py` está dessincronizado.
   Rodar `fase4_v2.main()` apaga as correções — ver `feedback_template_dessync.md`.

──────────────────── PLAYBOOK ────────────────────
gerar_playbook_dados.py  →  playbook_dados_*.json  →  playbook_template.html  →  PDF

──────────────────── HELPERS COMPARTILHADOS ────────────────────
classificacao_base.py     (importado por fase4_v2 e extrair_votos_candidato_ra)

──────────────────── DIAG (Flask) ────────────────────
servidor_diag.py  → gerar_relatorio_diag.py  → relatorio_diag_*.docx
                       (importa fase4_v2 para reaproveitar carregar/montar_dados)
gerar_narrativas_ra.py    (importa fase4_v2; gera narrativas que vão pra outputs_fase3)
```

**Helper crítico:** `classificacao_base.py` (importado por 2 scripts ativos, lê `outputs_fase1/perfil_eleitorado_ra.csv`). Mover sem cuidado quebra dashboard + playbook.

---

## 2. Classificação de scripts

### 2.1. NÚCLEO ATIVO (não mover sem refatorar imports)

| Script | Papel | Risco ao mover |
|---|---|---|
| `fase0_historico.py` | gera `candidatos_2022.csv` | alto — consumido por `fase4_v2`, `gerar_playbook_dados`, `extrair_orcamento_referencia` |
| `fase1_correspondencia_zona_ra.py` | seção→RA, zona→RA, perfil eleitorado | alto |
| `fase1c_perfil_secao.py` | refinamento atual de perfil_eleitorado_ra | alto |
| `fase1_fix_aptos.py` | corrige aptos | médio |
| `fase2_tabela_mestre_v2.py` | tabela_mestre_ra | alto (consumida por dashboard, playbook, fase3, fase3c, exportar_populacao) |
| `fase3_ipe.py` | calcula IPE | alto |
| `fase3c_campo_politico.py` | votos por campo / por candidato (versão atual) | alto |
| `extrair_votos_candidato_ra.py` | reconstrução de votos por RA com override CPP-SIA | alto |
| `extrair_orcamento_referencia.py` | lê despesas TSE | médio |
| `fase4_v2.py` | gera dashboard_spe_df.html (template) | alto + ⚠️ JS_CODE defasado |
| `injeta_geopolitica.py` | embute GeoJSON | médio |
| `injeta_candidato.py` | embute A5_CANDS | alto |
| `gerar_playbook_dados.py` | gera JSON do playbook por candidato | alto |
| `gerar_narrativas_ra.py` | importa fase4_v2 | médio |
| `gerar_relatorio_diag.py` | importa fase4_v2 | médio |
| `servidor_diag.py` | Flask + gerar_relatorio_diag | baixo (só tu usa) |
| `classificacao_base.py` | helper compartilhado | crítico |
| `exportar_populacao_xlsx.py` | export Excel da tela População (recém-criado) | baixo |

### 2.2. POSSIVELMENTE MORTO (validar antes de arquivar)

| Script | Indício | Decisão sugerida |
|---|---|---|
| `fase0b_pdad2018.py` | gera `outputs_fase0b/*` consumido só por ele mesmo | arquivar — experimento com PDAD 2018 que não foi pra produção |
| `fase3b_comparacao.py` | output `outputs_fase3b/votos_campo_politico_ra.csv` é só *fallback* opcional do `fase3_ipe` (canônico é `outputs_fase3c`) | arquivar — versão antiga do agrupamento por campo |
| `fase_candidato.py` | gera `outputs_candidato/ipe_personalizado.csv`. Consumido só por ele mesmo. Nada de produção lê | arquivar — substituído por `extrair_votos_candidato_ra.py` |

### 2.3. MORTO ÓBVIO (arquivar/deletar)

Versões antigas substituídas (já listados como "Versões antigas/debug" no `.gitignore`):
- `fase2_tabela_mestre.py` (substituído por `_v2`)
- `fase4_dashboard.py` (substituído por `fase4_v2`)
- `fase4_v2_16.py` (versão antiga do `_v2`)
- `geopolitica.py` + `geopolitica_df.html` (substituído por `injeta_geopolitica`)
- `injeta_geopolitica_0.py` (versão antiga)

Debug/exploração one-shot:
- `debug_gama.py`, `debug_join.py`, `debug_ra_faltantes.py`, `debug_ra_names.py`, `debug_sia_gama.py`
- `diagnostico_abstencao.py`, `inspecionar_pdad.py`, `valida_beneficio.py`
- `explorar_orcamento_2022.py`, `explorar_rubricas_eleitos.py`

Boilerplate de exemplo:
- `exemplo_contexto_pdf.py`, `exemplo_relatorio_pdf.py`

JS legado:
- `gerar_relatorio.js`, `gerar_relatorio_candidato.js` (e prováveis órfãos `node_modules/`, `package*.json`)

HTML legado:
- `dashboard_spe_df.html`, `dashboard_com_geo.html`, `dashboard_com_candidato.html` (intermediários do build chain — só `index.html` é o produto)
- `geopolitica_df.html`
- `relatorio_DAMARES.html`, `relatorio_ERIKA.html`, `relatorio_REGINALDO.html`, `relatorio_contexto_DF.html` (gerados pelo `geopolitica.py` morto)
- `simulador_quociente.html`

### 2.4. UTILITÁRIOS PERIFÉRICOS (manter mas avaliar)

- `gerar_credencial.py` + `credenciais.json` + `credenciais.example.json` → mecanismo de auth, manter
- `logo_opiniao.png` → branding, manter na raiz ou mover pra `assets/`
- `CNAME` → GitHub Pages, manter na raiz

---

## 3. Pontos DF-específicos hardcoded (precisarão parametrizar)

| Onde | O que é DF-específico |
|---|---|
| `fase1_correspondencia_zona_ra.py` | `RA_COD_MAP` (mapa de 33 nomes→cod), `RA_SEM_ZONA_PROPRIA`, dicionário bairro→RA |
| `fase3_ipe.py` | `GRUPOS_PED` (4 conglomerados socioeconômicos do DF) |
| `gerar_playbook_dados.py` | `GRUPOS_PED`, `SENADOR_CENARIOS` calibrado em 2018-DF, `VAGAS_CARGO` (24 distritais é DF) |
| `fase4_v2.py` | strings "DF 2026", "Distrito Federal", `RA_SEM_ZONA`, ASCII art Estrategos |
| `index.html` | nomes de RAs nas legendas, GeoJSON DF embutido |
| `Limite_RA_20190.json` | shapefile DF |
| `candidatos_2022_DF.csv` (raiz) | pré-filtro DF; pode ser removido se a gente sempre filtrar do cadastro nacional |
| `outputs_tse_2022_DF/` | nome do diretório fixa "DF" |
| `outputs_fase*/` | implícito DF |
| `dados_tse_cache/PDAD_*` | PDAD é IPEDF, exclusivo DF |
| `PDAD2021/` | exclusivo DF |

### Fonte demográfica por UF

| UF | Fonte equivalente à PDAD |
|---|---|
| DF | PDAD 2021 (IPEDF) — granularidade RA, ~50 indicadores |
| Outras | Censo 2022 IBGE (agregado por município ou setor censitário). Indicadores comparáveis: renda, escolaridade, ocupação. **Sem** classe AB/DE direta (montar via faixa de renda), **sem** Bolsa Família por região (estimar via CadÚnico), **sem** plano de saúde (vai sumir ou estimar via PNAD). |

Implicação: o esquema de variáveis da tela "População" precisa de **camadas opcionais** — núcleo comum (renda, escolaridade, idade, gênero, origem) presente em qualquer UF; e camada estendida (classe, insegurança alimentar, plano de saúde, conglomerados socioeconômicos) só onde houver fonte equivalente.

---

## 4. Dados brutos e tamanhos

| Caminho | Tamanho | Observação |
|---|---|---|
| `TSE/perfil_comparecimento_abstencao_2022/` | 4,6 GB | gitignored, manter local. Por UF na origem |
| `dados_tse_cache/` | 1,3 GB | gitignored. Mistura caches DF (votacao, locais) + PDAD 2018 |
| `perfil_comparecimento_abstencao_2022.zip` (raiz) | 192 MB | gitignored. Provavelmente duplicata do que já está em `TSE/`; **candidato a deletar** |
| `PDAD2021/` | 62 MB | gitignored. Fonte primária PDAD |
| `outputs_tse_2022_DF/` | 74 MB | parcialmente gitignored (CSVs grandes), JSONs versionados |
| `outputs_fase1/` | 25 MB | gitignored |
| `outputs_fase0/` | 4,1 MB | gitignored |
| `node_modules/` | 9 MB | gitignored. Provavelmente órfão do JS legado — confirmar e deletar |

---

## 5. Árvore-alvo proposta (multi-UF nativo)

```
geopolitica/
├── README.md
├── CNAME
├── pyproject.toml                      ← (substituir package*.json órfão)
├── docs/
│   ├── DECISOES_PROJETO.md
│   ├── METODOLOGIA.md
│   ├── SPE_PROJETO.md
│   ├── STORYTELLING_SPEC.md
│   ├── PLAYBOOK_RASCUNHO.md
│   ├── MODAL_RASCUNHO.md
│   └── INVENTARIO.md  (este aqui)
├── assets/
│   └── logo_opiniao.png
├── pipeline/                            ← scripts numerados como hoje, mas com --uf
│   ├── classificacao_base.py
│   ├── fase0_historico.py
│   ├── fase1_correspondencia_zona_ra.py    (→ "fase1_secao_para_regiao.py")
│   ├── fase1_fix_aptos.py
│   ├── fase1c_perfil_secao.py
│   ├── fase2_tabela_mestre.py              (→ renomear, sem _v2)
│   ├── fase3_ipe.py
│   ├── fase3c_campo_politico.py
│   ├── extrair_votos_candidato_ra.py       (→ "extrair_votos_candidato.py")
│   ├── extrair_orcamento_referencia.py
│   ├── gerar_playbook_dados.py
│   ├── exportar_populacao_xlsx.py
│   └── _arquivo/                       ← legados retidos só pra histórico git
├── build/                               ← geração do dashboard
│   ├── fase4_dashboard.py              (substitui fase4_v2.py — JS_CODE → arquivo)
│   ├── dashboard_template.html         (FONTE da verdade do JS, não embutido em .py)
│   ├── injeta_geopolitica.py
│   ├── injeta_candidato.py
│   └── playbook_template.html
├── diag/                                ← Flask Diag
│   ├── servidor_diag.py
│   └── gerar_relatorio_diag.py
├── data/                                ← dados brutos por UF (gitignored)
│   ├── DF/
│   │   ├── pdad/
│   │   ├── tse_cache/
│   │   ├── shapes/Limite_RA_20190.json
│   │   └── config.toml                 ← RA_COD_MAP, GRUPOS_PED, VAGAS_CARGO override, etc.
│   ├── SP/                             ← futuro
│   │   ├── censo/
│   │   ├── tse_cache/
│   │   ├── shapes/...
│   │   └── config.toml
│   └── ...
├── outputs/                             ← idem, por UF (gitignored)
│   ├── DF/{fase0,fase1,fase2,fase3,fase3c,tse,export,candidato}/
│   ├── SP/{...}/
│   └── ...
├── ufs/                                 ← módulos Python específicos de cada UF
│   ├── __init__.py
│   ├── df.py                           ← RA_COD_MAP, GRUPOS_PED, fonte demográfica = PDAD
│   ├── sp.py                           ← MUNICIPIO_COD_MAP, fonte = Censo
│   └── base.py                         ← interface comum (load_demografia, get_grupos, ...)
└── index.html                           ← deploy artifact, na raiz pra GitHub Pages
```

### Princípios da árvore

1. **`--uf DF` por padrão** em todo script: `python pipeline/fase2_tabela_mestre.py --uf DF` (default mantém retrocompat).
2. **`ufs/<uf>.py` carrega config**: dicionários DF-específicos (`RA_COD_MAP`, `GRUPOS_PED`, `VAGAS_CARGO`) saem dos scripts e viram dados de `ufs/df.py` ou de `data/<uf>/config.toml`.
3. **Camada demográfica plugável**: interface `ufs/base.py` define `carregar_demografia(uf) -> DataFrame` com schema mínimo comum; `df.py` implementa lendo PDAD, `sp.py` implementa lendo Censo. Tela "População" usa só o schema comum + flags `tem_classe_abde`, `tem_inseguranca_alimentar`, etc., para esconder colunas onde não há dado.
4. **Template do dashboard sai de dentro do `.py`**: `JS_CODE` em `fase4_v2.py` vira `build/dashboard_template.html`, lido em runtime. Acaba a dessincronização.
5. **Outputs/data segregados por UF**: zero mistura no diretório.

---

## 6. Roteiro de execução sugerido (em fases pequenas)

| # | Passo | Risco | Ganho |
|---|---|---|---|
| 1 | **Você revisa este inventário** e marca o que discorda | — | alinhamento |
| 2 | **Faxina A — arquivar mortos óbvios** (lista §2.3): mover pra `_arquivo/`, sem renomear nada | baixo | -25 arquivos da raiz |
| 3 | **Validar pipeline ainda roda** (rodar fase0..fase4_v2 + injetadores + playbook batch); commit | baixo | rede de segurança |
| 4 | **Faxina B — possíveis mortos** (§2.2): confirmar 1 a 1 antes de arquivar `fase0b`, `fase3b`, `fase_candidato` | baixo | -3 arquivos |
| 5 | **Mover docs e assets** pra `docs/` e `assets/`. Atualizar `MEMORY.md` (path absoluto do `DECISOES_PROJETO.md`). Commit | baixo | raiz limpa |
| 6 | **Refatorar `fase4_v2`: extrair JS_CODE → `dashboard_template.html`**. Resolver dívida de dessincronização | médio (precisa testar visual) | acaba a fonte de bug que vc levantou |
| 7 | **Introduzir `ufs/df.py`**: mover `RA_COD_MAP`, `GRUPOS_PED`, `VAGAS_CARGO`, `SENADOR_CENARIOS` para lá. Scripts importam `from ufs.df import ...` | médio | base pra multi-UF |
| 8 | **Renomear `outputs_fase*` → `outputs/DF/fase*`**. Ajustar paths nos scripts (constantes `DIR_F1` etc.) | médio | preparação multi-UF |
| 9 | **Renomear `dados_tse_cache/` → `data/DF/tse_cache/`** e `PDAD2021/` → `data/DF/pdad/`. Ajustar paths | médio | idem |
| 10 | **Adicionar flag `--uf` aos scripts** (default DF). Não muda comportamento ainda | baixo | hook pra futuro |
| 11 | **(Quando precisar) implementar `ufs/sp.py` etc.** consumindo Censo IBGE | alto | habilita multi-UF de fato |

Sugestão: passos 2–5 nesta sessão (faxina barata, alto retorno visual). 6–10 nas próximas, um por sessão para conseguir validar o batch de playbook depois de cada um. 11 só quando houver demanda real de outro estado.

---

## 7. Decisões pendentes pra você bater o martelo

1. **Aprova a árvore-alvo da §5?** Em particular: `pipeline/`, `build/`, `data/<uf>/`, `outputs/<uf>/`, `ufs/`. Algum nome que prefere mudar?
2. **`fase0b_pdad2018.py`, `fase3b_comparacao.py`, `fase_candidato.py`** — pode arquivar os três? (eu testei: nada de produção depende deles)
3. **`perfil_comparecimento_abstencao_2022.zip` na raiz (192 MB)** — confirma que é duplicata e pode deletar?
4. **`node_modules/` + `package*.json`** — algum uso atual ou pode deletar?
5. **`dashboard_*.html` intermediários** (spe_df, com_geo, com_candidato) — manter como caches do build ou deletar e gerar sob demanda?
6. **Onde fica `index.html`?** Raiz (GitHub Pages exige) ou subpasta com redirect?
7. **Refatorar `fase4_v2` agora ou depois da faxina simples?** Tem dívida real (template defasado), mas é a mexida mais arriscada da lista.
