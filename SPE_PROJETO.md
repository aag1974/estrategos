# SPE — Score Político Estratégico

**Inteligência eleitoral aplicada ao Distrito Federal — eleições 2026**

---

## 1. O que é o projeto

O SPE é uma ferramenta de consultoria política voltada para profissionais de marketing político, focada nas eleições de 2026 no Distrito Federal. Cruza dados socioeconômicos da PDAD 2021 (IPEDF) com resultados eleitorais do TSE 2022 para gerar um diagnóstico territorial das 33 Regiões Administrativas e produzir recomendações estratégicas por candidato, cargo e campo político.

O produto final é entregue como um dashboard HTML único (`dashboard_spe_df.html`), gerado por um pipeline Python em fases sequenciais.

---

## 2. As duas jornadas do produto

A arquitetura conceitual divide o produto em **passado** (diagnóstico) e **futuro** (estratégia), com o GeoPolítica como camada visual compartilhada.

### Jornada do passado — "O que aconteceu?"
Análise retrospectiva com base em dados reais de 2022. Aplica-se a quem disputou (análise de candidato) ou ao campo (se o cliente é estreante).

### Jornada do futuro — "O que fazer?"
Construção da estratégia 2026 a partir de uma persona. Atos 1 a 4 percorrendo território, eleitorado, campo político e SPE. Não depende de o candidato ter histórico.

### Distinção operacional
- **Atos 1–4**: rodam para qualquer candidato, estreante ou não. Encerram a jornada principal com o SPE e a recomendação estratégica.
- **Análise de candidato**: jornada paralela, acessível por seção própria no nav, ativada apenas quando há dados reais de 2022 para o candidato em questão.

A distinção entre "Nova candidatura" e "Reeleição/novo cargo" só é meaningful quando existe voto real de 2022 para puxar — sem isso, a análise individual perde substrato.

---

## 3. Fontes de dados

| Fonte | Conteúdo | Uso |
|---|---|---|
| **PDAD 2021** (IPEDF, antigo CODEPLAN) | 83 mil moradores entrevistados nas 33 RAs | Indicadores socioeconômicos: renda, classe, escolaridade, ocupação, benefícios |
| **PDAD 2018** (IPEDF) | Versão anterior da pesquisa | Validação histórica do modelo SPE |
| **TSE 2022** | Cadastro eleitoral + votação por seção | Eleitorado por RA, votos por candidato/campo, perfil etário/educacional |
| **TSE 2018** | Mesmo formato do TSE 2022 | Trajetórias de candidatos 2018 → 2022, taxas de conversão entre cargos |
| **GeoJSON DF** | Limites das 33 RAs | Camada visual do GeoPolítica (item ainda em aberto) |

Importante: o perfil do eleitorado vem do **cadastro eleitoral** do TSE — não dos dados de urna. É quem está apto a votar, não quem efetivamente votou.

---

## 4. As 33 Regiões Administrativas

```
1  Brasília (Plano Piloto)   12 Samambaia                23 Varjão
2  Gama                       13 Santa Maria              24 Park Way *
3  Taguatinga                 14 São Sebastião            25 SCIA/Estrutural
4  Brazlândia                 15 Recanto das Emas         26 Sobradinho II
5  Sobradinho                 16 Lago Sul                 27 Jardim Botânico
6  Planaltina                 17 Riacho Fundo             28 Itapoã
7  Paranoá                    18 Lago Norte               29 SIA *
8  Núcleo Bandeirante         19 Candangolândia           30 Vicente Pires
9  Ceilândia                  20 Águas Claras             31 Fercal *
10 Guará                      21 Riacho Fundo II          32 Sol Nascente/Pôr do Sol *
11 Cruzeiro                   22 Sudoeste/Octogonal       33 Arniqueira *
```

\* RAs sem zona TSE própria — dados eleitorais estimados via zona da RA-mãe. Cobertura do eleitorado DF: ~97%.

| RA sem zona | Zona pai (estimativa) |
|---|---|
| Park Way | Zona 1 — Brasília (Plano Piloto) |
| SIA | Zona 9 — Guará |
| Fercal | Zona 5 — Sobradinho |
| Sol Nascente/Pôr do Sol | Zona 9 — Ceilândia |
| Arniqueira | Zona 15 — Taguatinga |

---

## 5. Grupos PED-DF (DIEESE)

Agrupamento socioeconômico oficial do DF, usado para análises agregadas:

| Grupo | RAs |
|---|---|
| **Brasília Central** | Plano Piloto, Jardim Botânico, Lago Norte, Lago Sul, Park Way, Sudoeste/Octogonal |
| **Satélites Consolidadas** | Águas Claras, Candangolândia, Cruzeiro, Gama, Guará, Núcleo Bandeirante, Sobradinho, Sobradinho II, Taguatinga, Vicente Pires |
| **Satélites em Expansão** | Brazlândia, Ceilândia, Planaltina, Riacho Fundo, Riacho Fundo II, SIA, Samambaia, Santa Maria, São Sebastião, Arniqueira |
| **Fronteiras Urbanas** | Fercal, Itapoã, Paranoá, Recanto das Emas, SCIA/Estrutural, Varjão, Sol Nascente/Pôr do Sol |

---

## 6. A fórmula do SPE

O SPE combina quatro componentes ponderados por cargo:

```
SPE = w_afin × Afinidade  +  w_conv × Conversão  +  w_massa × Massa  +  w_log × Logística
```

Todos os componentes são normalizados na escala 0–10. O resultado final do SPE também.

### 6.1 Afinidade
Predisposição estrutural da RA para um campo político, medida pela combinação ponderada de variáveis PDAD. Quando há dados eleitorais reais, combina-se 60% estrutural + 40% eleitoral.

### 6.2 Conversão
Potencial de virar voto adversário ou indeciso. Atinge o máximo na **zona de indecisão** (afinidade entre 3 e 7) multiplicada por massa eleitoral. RAs já consolidadas para o campo ou claramente perdidas têm conversão baixa.

```
Conversão = (10 − |Afinidade − 5| × 2) × Massa
```

### 6.3 Massa
Volume eleitoral bruto, usando os votos do cargo específico, ajustado por proxy de abstenção:

```
proxy_abstenção = 0.4 × %jovens_16-24  +  0.6 × %classe_DE
Massa = votos × (1 − proxy_abstenção × 0.3)
```

RAs sem zona TSE própria E sem votos registrados recebem Massa = 0.

### 6.4 Logística
Eficiência de campanha — RAs menores têm custo/voto mais baixo:

```
Logística = normalizar(1 / total_domicílios)
```

### 6.5 Pesos por cargo

A lógica territorial de cada eleição define os pesos:

| Cargo | Afinidade | Conversão | Massa | Logística | Lógica |
|---|---|---|---|---|---|
| **Governador** | 0.30 | 0.30 | 0.25 | 0.15 | Equilíbrio — precisa de cobertura ampla |
| **Senador** | 0.20 | 0.40 | 0.35 | 0.05 | Majoritário, 2 vagas — conversão crítica, nenhuma RA dispensável |
| **Dep. Federal** | 0.25 | 0.30 | 0.35 | 0.10 | Disputa em todo DF — massa pesa |
| **Dep. Distrital** | 0.40 | 0.20 | 0.20 | 0.20 | Concentração — afinidade e logística maximizadas |

> Nota: existem duas calibrações dos pesos no codebase (`fase3_ipe.py` e `fase_candidato.py`) com ligeiras variações para Governador e Dep. Federal — acompanhar quando consolidar a fórmula final.

---

## 7. Os três campos políticos

### 7.1 Definição
- **Progressista** — PT, PDT, PSB, PSOL, PCdoB, REDE, PV, AVANTE, PROS
- **Moderado/Centro** — MDB, PSDB, CIDADANIA, PSD, PODEMOS, PATRIOTA, DC, PMN, PMB
- **Liberal/Conservador** — PL, PP, REPUBLICANOS, UNIÃO, NOVO, PTB, DEM, PRTB, PRD

A classificação é feita pelos dois primeiros dígitos do `NR_VOTAVEL` para cargos proporcionais, e por nome do candidato (com fallback de partido) para cargos majoritários.

### 7.2 Variáveis PDAD que predizem cada campo

**Progressista** (achado central: r = 0,93 com escolaridade)
| Variável | Peso |
|---|---|
| % Superior | +0.30 |
| % Plano de saúde | +0.25 |
| % Ocupado formal | +0.20 |
| % Nativo DF | +0.15 |
| % Servidor público | +0.10 |

**Moderado** (padrão Ibaneis/MDB nas satélites)
| Variável | Peso |
|---|---|
| % Benefício social | +0.30 |
| % Classe DE | +0.25 |
| % Migrante | +0.20 |
| % Desocupado | +0.15 |
| % Jovem 16-24 | +0.10 |

**Liberal/Conservador** (campo fragmentado, alta renda)
| Variável | Peso |
|---|---|
| % Classe AB | +0.30 |
| % Nativo DF | +0.25 |
| % Conta própria | +0.20 |
| % Plano de saúde | +0.15 |
| % Superior | +0.10 |

### 7.3 Achado central
**No DF, o voto progressista cresce com renda e escolaridade — o inverso do padrão nacional.** A correlação entre escolaridade do eleitorado e voto progressista para Deputado Federal em 2022 é r = 0,93. Regiões de alta renda (Plano Piloto, Lago Norte) votam à esquerda; periferias votam à direita ou centro.

### 7.4 Outros achados-âncora
- **Ceilândia tem 285 mil eleitores aptos** — mais do que os 7 menores territórios somados.
- **Campo moderado dominou as periferias** mas perdeu para o liberal no total do DF.
- **Campo liberal/conservador chegou a 32% no DF** em 2022 — maior fatia, mas fragmentada.
- **48% de moderado em Taguatinga** — território de disputa real.
- **Recanto das Emas: 56% no campo moderado.**

---

## 8. As seis personas

Cada persona representa um arquétipo estratégico, ancorado em campo + cargo + perfil socioeconômico.

| Persona | Campo | Cargo típico | Frase-síntese |
|---|---|---|---|
| **O Servidor Progressista** | Progressista | Dep. Federal/Distrital | *"Meu eleitor já é meu eleitor. Ele tem diploma, plano de saúde. Já vota comigo."* |
| **O Expansionista** | Progressista | Governador ou Senador | *"Eu sei que minha base não basta. Meu trabalho é convencer quem nunca votou no meu campo."* |
| **O Gestor das Satélites** | Moderado | Governador | *"Meu eleitor não quer ideologia. Ele quer asfalto, hospital e segurança."* |
| **O Deputado Territorial** | Moderado | Dep. Distrital ou Federal | *"Não preciso ganhar o DF inteiro. Preciso ser o mais votado em 2 ou 3 regiões."* |
| **O Liberal de Nicho** | Liberal/Cons. | Dep. Federal ou Distrital | *"Eu sei exatamente quem é meu eleitor. Ele tem empresa, paga plano de saúde."* |
| **O Conservador Majoritário** | Liberal/Cons. | Governador ou Senador | *"O campo tem 32% dos votos, mas ninguém uniu. Se resolver esse problema, posso vencer."* |

A persona é o **Ato 1** da jornada do futuro — define o filtro analítico de tudo que vem depois. O nome "estreante" foi descontinuado em favor de "Nova candidatura" (sem histórico) vs. "Reeleição ou novo cargo" (com histórico em 2022).

---

## 9. Diagnóstico territorial — 4 estratégias

Cada RA é classificada em uma das quatro categorias com base em **SPE** e **% de captura do campo**:

| Estratégia | SPE | Base do campo | Ação | Recursos |
|---|---|---|---|---|
| **CONSOLIDAR** | Alto | Forte | Mobilizar, não converter | 25% |
| **EXPANDIR** | Alto | Fraca | Campo de conversão crítico | 45% |
| **DEFENDER** | Médio | Forte | Não deixar sangrar | 20% |
| **MONITORAR** | Baixo | Fraca | Presença mínima | 10% |

---

## 10. Pipeline técnico

Sequência das fases, cada uma é um script Python com seus outputs em CSV.

```
fase1_correspondencia_zona_ra.py
    → outputs_fase1/
        ├── locais_votacao_geo.csv
        ├── zona_ra_df.csv
        ├── votos_por_ra.csv
        └── perfil_eleitorado_ra.csv

fase2_tabela_mestre_v2.py
    → outputs_fase2/tabela_mestre_ra.csv         (~60 indicadores × 33 RAs)

fase3_ipe.py
    → outputs_fase3/
        ├── correlacoes.csv
        ├── pca_componentes.csv
        ├── clusters_ra.csv
        ├── ipe_completo.csv                     (SPE × cargo × campo × RA)
        └── narrativas_ra.csv

fase3c_campo_politico.py
    → outputs_fase3c/votos_campo_ra.csv

fase_candidato.py
    → outputs_candidato/
        ├── ipe_personalizado.csv
        └── sumario_candidato.json

fase0_historico.py / fase0b_pdad2018.py
    → outputs_fase0/                             (validação 2018 × 2022)

fase4_v2.py
    → dashboard_spe_df.html                      (dashboard final)

injeta_geopolitica.py
    → dashboard_spe_df.html                      (com camada GeoPolítica injetada)
```

### 10.1 Auxiliares
- `fase3b_comparacao.py` — ferramenta de comparação metodológica (k-means vs. PED-DF).
- `fase0_historico.py` — extrai trajetórias de candidatos 2018 → 2022 e calcula taxas de conversão entre cargos.
- `fase0b_pdad2018.py` — valida o SPE retroativamente: calcula SPE com PDAD 2018 + TSE 2018 e compara com votos reais de 2022 (Spearman, top-5 e top-10).

---

## 11. O dashboard (dashboard_spe_df.html)

### 11.1 Estrutura do nav
```
Território
  · População       (PDAD 2021)
  · Eleitorado      (TSE 2022 — cadastro)

Contexto
  · Campo político  (votos 2022 por RA × campo × cargo)
  · Candidatos      (análise individual com performance por RA)

Estratégia
  · Projeções       (cenários conservador/moderado/otimista por RA)

Geopolítica
  · Mapa interativo (camada injetada por injeta_geopolitica.py)
```

### 11.2 Modal de metodologia
Acessado por `ⓘ Sobre o SPE` no rodapé do nav e por links contextuais em cada ato. Navegação interna com seções: intro, ato1, ato2, ato3, ato4, ato5. Fecha com `Esc` ou botão `✕`.

### 11.3 Tom dos textos
Conteúdo metodológico escrito em **tom ELI5 voltado para profissionais adultos de marketing político** — explicações claras sem jargão técnico desnecessário, mas respeitando a sofisticação do público.

### 11.4 Características técnicas
- HTML único com JS embutido
- Coluna "Região" travada no scroll horizontal (sticky)
- Tooltips ajustados para não cortar nas últimas colunas
- Dados embarcados em base64 (`__DADOS_B64__`, `__CANDS_B64__`)
- Sistema de cores por campo:
  - Progressista: `#A32D2D` / `#FCEBEB`
  - Moderado: `#0F6E56` / `#E1F5EE` (no projeções) ou `#185FA5` / `#E6F1FB` (campo)
  - Liberal/Conservador: `#854F0B` / `#FAEEDA`

---

## 12. GeoPolítica

Mapa interativo das 33 RAs (Leaflet + GeoJSON) injetado no dashboard via `injeta_geopolitica.py`.

### 12.1 Variáveis disponíveis para colorir o mapa
- **Território**: renda per capita, %AB, %DE, %superior, %sem fundamental, %funcionalismo, %benefício, %migrantes
- **Eleitorado**: aptos, %jovens, %idosos, %feminino
- **Voto por campo**: %progressista, %moderado, %liberal/conservador
- **SPE**: score por cargo + campo selecionados

### 12.2 Painel lateral
Ao clicar numa RA, abre painel com KPIs (renda, classe AB, superior, benefício), eleitorado, distribuição de votos por campo no cargo selecionado, e quadro SPE com Afinidade, Conversão, Massa.

### 12.3 Item em aberto
Confirmar fonte e formato definitivo do **GeoJSON das 33 RAs** (portal de dados abertos do GDF é o ponto de partida).

---

## 13. Validação retroativa (fase0b)

O modelo é validado fazendo o "treino 2018 / teste 2022":
1. Calcula SPE usando apenas PDAD 2018 + TSE 2018.
2. Compara o ranking gerado com os votos reais de 2022.
3. Métricas: Spearman r, top-5 e top-10 corretas, qualidade (boa > 0.5, moderada > 0.3, fraca abaixo).

Se o SPE-2018 prevê bem o ranking de 2022, o modelo é estruturalmente sólido — independente do contexto político específico.

---

## 14. Princípios de produto (decisões de design)

1. **A persona não é splash** — é o Ato 1 da jornada do futuro, no mesmo padrão visual dos outros atos.
2. **Atos 1–4 são universais** — funcionam para qualquer candidato, com ou sem histórico.
3. **Análise de candidato é jornada paralela** — não um "Ato 5" sequencial. Acessível por seção própria no nav.
4. **GeoPolítica não é uma terceira jornada** — é a interface visual que ambas projetam diferentes camadas.
5. **Sem busca por nome de candidato na jornada principal** — a análise da persona usa o campo político, não dados individuais.
6. **Dado de receita de campanha (SPCE/TSE) descartado** — sabidamente não confiável.
7. **Renomeação IPE → SPE** — Score Político Estratégico é o nome consolidado.

---

## 15. Gotchas técnicos críticos

Para evitar retrabalho ao mexer no `fase4_v2.py` ou em scripts que injetam JS no Python:

1. **`JS_CODE` usa `"""` regular, não `r"""`** — assumir raw string falha silenciosamente.
2. **Escapes Unicode `\u25bc` dentro de `"""..."""` são desescapados pelo Python** antes de chegar no JS — usar caracteres Unicode literais ou raw strings cuidadosamente.
3. **`\"` dentro de `"""..."""` vira `"` puro no JS** — quebra a sintaxe. Usar strings JS com aspas simples ou raw strings com cuidado.
4. **HTML do Ato 5 deve ser inserido dentro de `#content` E `#app`** — alvo correto: `'  </div>\n  </div>\n</div>\n<script>// __JS__</script>'`.
5. **`#content` e `.ato` precisam de `background:var(--s1)` explícito** — flex layout não propaga background de forma confiável.
6. **No `injeta_geopolitica.py`** — o marcador para inserir a geo-section antes do modal é `"  </div>\n</div>\n\n<!-- MODAL"`.

---

## 16. Estado atual e horizonte

### Concluído
- Pipeline completo (fases 1 a 4) funcionando.
- Renomeação IPE → SPE em todo o codebase.
- Componente Logística adicionado à fórmula.
- Sticky column e tooltips corrigidos.
- Modal de metodologia com 5 atos navegáveis.
- Reconcepção do "Ato 5" como jornada paralela "Análise de candidato".
- Decisões de produto: "Nova candidatura" vs. "Reeleição ou novo cargo", remoção de busca por nome.
- Validação histórica (fase0b) implementada.
- GeoPolítica funcionando (modo Território).

### Em aberto
- Confirmar GeoJSON definitivo das 33 RAs.
- Implementar a seção "Análise de candidato" como jornada distinta no dashboard.
- GeoPolítica modo Candidato (camada de votos reais, captura, gaps).
- Refinamento contínuo do pipeline rumo ao ciclo eleitoral 2026.

---

## 17. Stack e arquivos de referência

**Linguagens**: Python (pipeline) + HTML/JS embutido (dashboard).

**Bibliotecas Python**: pandas, numpy, scikit-learn (PCA, KMeans), scipy.stats, matplotlib, seaborn.

**JS no dashboard**: vanilla — sem framework. Leaflet 1.9.4 para o mapa.

**Arquivos do codebase**:
```
GEOPOLITICA/
├── fase0_historico.py             trajetórias 2018→2022
├── fase0b_pdad2018.py             validação retroativa
├── fase1_correspondencia_zona_ra.py    geocodificação seções→RAs
├── fase2_tabela_mestre_v2.py      tabela mestre PDAD+TSE
├── fase3_ipe.py                   PCA, clusters, SPE
├── fase3b_comparacao.py           comparação metodológica
├── fase3c_campo_politico.py       classificação campo por NR_VOTAVEL
├── fase_candidato.py              análise individual de candidato
├── fase4_v2.py                    geração do dashboard HTML
└── injeta_geopolitica.py          injeção do mapa no dashboard
```

---

*Documento consolidado das definições do projeto SPE — Score Político Estratégico, Brasília/DF, 2026.*
