# Estrategos · Spec narrativo

Documento de referência produzido em abr/2026 a partir da revisão de storytelling do dashboard. Substitui o roteiro anterior em "3 ondas". Fonte da verdade para o trabalho de produto e para o template do relatório Word.

---

## Sumário

1. [Decisões arquiteturais](#1-decisões-arquiteturais)
2. [Padrões transversais](#2-padrões-transversais)
3. [Spec por seção do dashboard](#3-spec-por-seção-do-dashboard)
   - 3.1 [Capa & "Sobre o SPE"](#31-capa--sobre-o-spe)
   - 3.2 [Território](#32-território-população--eleitorado)
   - 3.3 [Contexto](#33-contexto-campo-político--candidatos)
   - 3.4 [Estratégia](#34-estratégia-projeções)
   - 3.5 [Geopolítica](#35-geopolítica-território--candidato)
4. [Spec do relatório Word](#4-spec-do-relatório-word)
5. [Pendências em aberto](#5-pendências-em-aberto)
6. [Glossário](#6-glossário)

---

## 1. Decisões arquiteturais

| # | Decisão | Status |
|---|---|---|
| 1 | Aposentar o índice SPE composto. Métricas atomizadas substituem em todos os fluxos. | ✅ confirmada |
| 2 | Adotar a métrica de **sobre/sub-representação** como indicador central da Visão Candidato (formato `+X% / −X%`). | ✅ implementada |
| 3 | Cortes do sobre-índice: **±15%** (forte/fraca) e **±30%** (reduto/ausência). 5 categorias, não 3. | ⏳ a aplicar |
| 4 | Estrutura de 3 visões — **Campo · Cargo · Candidato** — cada uma com indicador próprio. | ⏳ implementação parcial |
| 5 | Visão Cargo (peso × competitividade) **não vira seção própria**: absorvida em Contexto > Campo político como coluna de competitividade. | ⏳ a implementar |
| 6 | **Renomear "SPE" para Estrategos** (working assumption — user pode reverter pra Strategos sem custo). | ✅ confirmada |
| 7 | Caso Reposicionamento (Manzoni-tipo) entra como **modo automático** dentro da Estratégia (ativa quando referência selecionada está em cargo distinto do candidato), não como gate de árvore. | ⏳ a implementar |
| 8 | Árvore de decisão de perfil de candidato (Estreante c/ ref · Estreante s/ ref · Incumbente · Reposicionado) **não entra no dashboard** — vira gerador de templates do relatório Word. | ✅ confirmada |
| 9 | Geopolítica mantém status de seção própria; **drawer lateral** complementa as outras seções para visualização contextual de RA. | ✅ confirmada |
| 10 | Função "exportar mapa" (PNG/SVG) é requisito do produto pela exigência do relatório Word. | ⏳ a especificar |

### Roteiro de implementação proposto

A ordem aqui é por dependência de decisão e por valor entregue, não pela rigidez das "3 ondas" anteriores.

**Bloco A — Higiene e UX (mecânico, sem decisão pendente)**
- Aplicar padrão `tt/tt-icon/tt-box` na coluna Índice (resolve task #6)
- Remover coluna SPE de Contexto > Candidatos, Geopolítica > Candidato e Estratégia
- Trocar formato do índice de ratio (`1.6×`) para delta (`+60%`)
- Aplicar 5 categorias (±15% / ±30%) no resumo territorial
- Reescrever achados desatualizados

**Bloco B — Visão Campo enriquecida**
- ✅ Adicionar coluna sobre-índice ao lado de domínio em Contexto > Campo político
- ✅ Adicionar coluna margem 1º-2º (Visão Cargo absorvida)
- ⏳ Visualizar r=0,93 com micro-gráfico DF×Brasil
- ❌ ~~Cruzamento PDAD × campo via filtro/coluna "perfil compatível"~~ — **adiado para Bloco E**. Razão: as âncoras simples (escolaridade, classe, servidor) não distinguem progressista de liberal no DF. Lago Norte é forte para os dois extremos ideológicos — o que difere "voto ideológico" de "voto local", não a direção. Ferramenta provavelmente vai morar como "perfil do eleitor-tipo do campo" no fluxo de estreantes sem referência (Estratégia).

**Bloco C — Visão Candidato enriquecida**
- Badge tipologia (capilar/campo/nicho) baseada em spread reduto-ausência
- Top 3 RAs no perfil
- Spike chart do spread no header do perfil
- Persistir candidato selecionado entre seções

**Bloco D — Geopolítica enriquecida**
- Adicionar variáveis de sobre-índice e margem ao mapa do Território
- Adicionar variável `idx` ao mapa do Candidato
- Pills cargo/campo reagem no mapa quando aplicável
- 5 caixas no painel direito
- Migrar Diagnóstico 4 quadrantes pra Estratégia

**Bloco E — Estratégia reconstruída**
- Novo modelo de projeção (multiplicação direta + toggles opcionais β/γ)
- Cenários calibrados pelos percentis empíricos
- Bloco didático narrativo na meta
- Modo Reposicionamento auto-ativado (5 categorias de RA)

**Bloco F — Capa, About e templates Word**
- Capa de boas-vindas com 3 cards
- "Sobre o SPE" reescrito (4 abas)
- Templates do relatório Word (4 perfis)
- Função exportar mapa

**Bloco G — Drawer lateral por RA**
- Componente transversal aplicado em qualquer tabela
- Resolve a "amarração tabela ↔ mapa"

---

## 2. Padrões transversais

### Linguagem visual

- **Cores por área:** kicker amber para "Estratégia", azul para "Contexto", marrom para "Território", verde claro para "Geopolítica" (manter).
- **Cores por campo político:** progressista #534AB7 (roxo), moderado #0F6E56 (verde), liberal-conservador #854F0B (marrom).
- **Cores semânticas (sobre-índice):** verde para acima do esperado, vermelho para abaixo, neutro cinza para "no esperado".

### Formato numérico (pt-BR)

**Premissa firme:** vírgula como separador decimal, ponto como separador de milhar. Em todo lugar do produto.

- ✅ `R$ 1.234,56` · `87,3%` · `+1,6×` · `5,7`
- ❌ `R$ 1,234.56` · `87.3%` · `+1.6×` · `5.7`

Em JS, **nunca usar** `toFixed()` direto na saída visual. Usar:

```js
// Para números com decimais
v.toLocaleString('pt-BR', {minimumFractionDigits:1, maximumFractionDigits:1})

// Para inteiros (separador de milhar)
v.toLocaleString('pt-BR')
```

Em Python, usar formatação explícita pt-BR ou substituir ponto por vírgula nos floats que vão pra HTML.

### Regra de arredondamento — half-up

**Premissa firme:** sempre arredondar pelo método **half-up** (≥ 0,5 sobe). Vale para tabelas, achados, KPIs, gráficos. Em todo lugar do produto, e particularmente em texto narrativo onde inconsistência quebra confiança.

- ✅ 285.620 → **286 mil** · R$ 625,54 → **R$ 626** · 18,58× → **quase 19×** ou **18,6×**
- ❌ 285.620 → 285 mil (truncamento) · R$ 625,54 → R$ 625 (truncamento) · 18,58× → 18×

**Em texto narrativo**, escolher a versão mais impactante quando o arredondamento permitir — desde que continue honesto. *"quase 19×"* é mais marcante que *"18×"* e tecnicamente mais correto. Mas ao confrontar com tabela, o número da tabela e o do texto **precisam bater**.

Para achados de impacto (renda, eleitorado, votos), priorizar arredondamento que **maximize o contraste** real visível no dado, não o número que parece menor.

### Tooltip — padrão oficial

Padrão único e canônico do produto:

```html
<span class="tt">Título<span class="tt-icon">?</span><span class="tt-box">Texto explicativo</span></span>
```

CSS já existe em `fase4_v2.py` (linhas 593–597). Ícone `?` em círculo cinza claro, hover-triggered, fundo escuro com texto claro. **Qualquer tooltip novo usa este padrão. Sem `title=""` HTML nativo, sem ícones soltos.**

### Header de seção

Padrão `sec-kicker` + `sec-titulo` + `sec-lead` (linhas 545–547 de `fase4_v2.py`). Manter em todas as seções; lead com voz narrativa, não técnica.

### Bloco didático

Padrão `achado-lbl` + `achado-txt` (linhas 563–564). Kicker amber + corpo. **Usar 2-3 achados por seção, não só 1**, especialmente em Eleitorado, Campo político e Candidatos.

### Filtros: cargo-bar + campo-bar

Padrão de pílulas — funciona bem (Contexto, Geopolítica, Estratégia). Reusar em Visão Campo enriquecida.

### Layout 3 colunas

`[lista/ranking/KPIs] | [mapa ou conteúdo central] | [painel detalhado]`. Estrutura provada em Geopolítica e Candidatos. Replicar quando aplicável.

### Componente novo — Drawer lateral

Não existe ainda. Especificar: ao clicar em uma linha de tabela ou em uma RA do mapa, abre um drawer à direita com:
- Nome da RA + grupo (se aplicável)
- 4 KPIs principais (eleitores aptos, renda PC, campo dominante, abstenção)
- Mini-mapa centrado na RA
- Resumo dos 3 candidatos mais votados de 2022 (link pra Candidatos)
- Botão "Ver no mapa completo"

Acionável de qualquer seção. Resolve a amarração tabela↔mapa identificada na Parada 2.

### Componente novo — Badge tipologia

Para o perfil do candidato. Calculada a partir do spread reduto-ausência:

| Spread (max−min do índice) | Tipologia |
|---|---|
| < 100pp | **Capilar** (gov-tipo: distribuição ampla) |
| 100–200pp | **Campo militante** (federal-tipo: forte no campo, ainda capilar) |
| > 200pp | **Nicho** (distrital-tipo: hiperconcentrado em poucas RAs) |

Exibir como badge ao lado do "Moderado · Governador" no header do perfil.

### Componente novo — Spike chart

Mini-gráfico horizontal mostrando os índices do candidato ordenados, do reduto à ausência. ~140×30px. Visualmente comunica o spread sem precisar olhar tabela.

---

## 3. Spec por seção do dashboard

### 3.1 Capa & "Sobre o SPE"

**Hoje:** não há capa; usuário cai direto em População. "Sobre o SPE" é um link no rodapé do menu, abre modal com 5 abas (Visão geral, Bases, Candidatos, Projeções, SPE).

**Decisões:**

1. **Criar capa de boas-vindas** com 3 cards (Território/Contexto/Estratégia) + CTA "Começar pela população" + 3 links secundários (Sobre, Bases, Limitações).
2. **Modal renomeado** para "Como o SPE funciona" com 4 abas:
   - O que é o SPE (visão geral redesenhada — 3 visões, sem score composto)
   - Bases de dados (mantida, pequena reescrita)
   - As três visões (substitui aba "SPE 4 dimensões")
   - Projeções (reescrita pro novo modelo)
3. **Promover acesso** ao modal — botão visível na capa, não só linkzinho cinza no rodapé.

**Texto-âncora da nova "O que é o SPE":**

> O SPE é um sistema de inteligência eleitoral aplicada ao Distrito Federal em 2026. Ele organiza dados públicos — censo da PDAD/IPEDF e resultados do TSE — em três visões complementares que respondem a perguntas estratégicas distintas:
>
> 1. **Campo político** — onde meu bloco é dono do território, e onde tenho espaço de crescer.
> 2. **Cargo** — onde a eleição se decide, e onde se defende o que já se tem.
> 3. **Candidato** — onde uma pessoa específica performa acima ou abaixo do esperado pelo tamanho da região.
>
> Cada visão entrega indicadores próprios, auditáveis, sem pesos arbitrários. O produto não prevê resultados eleitorais — ele organiza o território para apoiar decisões táticas.

### 3.2 Território (População + Eleitorado)

**Decisões:**

1. **População — enxugar tabela** de 17 → 6-7 colunas core (Renda · Superior · Classe AB · Classe DE · Funcionalismo · Idosos · Jovens) com botão "Ver mais variáveis" expandindo as outras.
2. **População — destacar visualmente** as 3 colunas-chave (Renda, Classe AB/DE, Funcionalismo).
3. **NÃO** agrupar por PED-DF (rejeitado: agrupamento DIEESE não conecta com objetivo eleitoral).
4. **Eleitorado — somar 2 achados** além do "Ceilândia 302K":
   - "Idosos sobre-representam +Xpp na urna" (sobre-representação etária)
   - "Em RA Z, abstenção foi 25%+ — base potencial de virada"
5. **Costurar População ↔ Eleitorado** com achado-âncora explícito sobre gap morador × eleitor (ex.: "Em SCIA/Estrutural, 1% dos moradores tem superior, mas 8% do eleitorado declara ter").
6. **Amarração com mapa** via drawer lateral por linha (decisão da arquitetura, item 9).

### 3.3 Contexto (Campo político + Candidatos)

**Campo político — decisões:**

1. **Adicionar coluna Sobre-índice** ao lado do domínio (% campo). Formato `+X% / −X%`.
2. **Adicionar coluna Margem 1º-2º** (em pp) — Visão Cargo absorvida aqui.
3. **Substituir/complementar coluna "Dominante"** com a margem.
4. **Cruzamento PDAD × campo** via filtro "Perfil compatível: alta/média/baixa" ou coluna dedicada.
5. **Visualizar r=0,93** com micro-gráfico DF×Brasil (200×100px) abaixo do achado central.
6. **Δ 2018→2022** — desejável, adiável.

**Candidatos — decisões:**

1. **Remover coluna SPE** da tabela.
2. **Adicionar badge tipologia** (capilar/campo/nicho) no header do perfil.
3. **Adicionar spike chart** do spread no header do perfil.
4. **Adicionar bloco "Top 3 RAs"** antes da tabela.
5. **Reescrever achado "Como ler"** pro modelo ±15% / ±30% com 5 categorias.
6. **Auditar `candComparar()`** durante implementação — provavelmente usa SPE.
7. **Persistir seleção** com Geopolítica > Candidato.

### 3.4 Estratégia (Projeções)

**Decisões:**

1. **Novo modelo de projeção:** multiplicação direta `Votos = referência × cenário`, sem fator SPE. Toggles opcionais para:
   - Ajuste demográfico PDAD (sucessor da "Afinidade")
   - Ajuste por tendência histórica 2018→2022
2. **Cenários recalibrados:** trocar 50/75/100% editoriais pelos percentis empíricos dos candidatos do cargo×campo (ex.: pior decil/mediana/top decil dos novatos = 35/55/95). Tooltip explicando a fonte de cada cenário.
3. **Bloco "Meta mínima"** vira didático narrativo: "Você precisa de X votos pra ser eleito em [cargo]. Sua referência fez Y. Cobertura: Z%."
4. **Modo Reposicionamento auto-ativado** quando a referência está em cargo diferente do candidato. Entrega:
   - Diagnóstico de partida
   - 5 categorias de RA (reduto compartilhado / núcleo afetivo / lacuna / hostil / irrelevante)
   - Cenários (orgânico / com ponte parcial / com ponte construída)
5. **Receber Diagnóstico 4 quadrantes** migrado da Geopolítica > Candidato (mas refatorado pra usar sobre-índice × votos absolutos em vez de SPE × captura).
6. **Comparação**: diferenciar editorialmente de Candidatos. Aqui é projeção 2026; lá é retrospectiva 2022.

### 3.5 Geopolítica (Território + Candidato)

**Decisões:**

1. **Remover SPE** do dropdown e do painel.
2. **Adicionar variáveis** ao dropdown:
   - Sobre-índice por campo (par com domínio existente)
   - Margem 1º-2º (Visão Cargo visualizável)
3. **Adicionar variável `idx`** (sobre-índice do candidato) ao mapa de Geopolítica > Candidato.
4. **Reativar pills cargo/campo** no mapa quando variável é sensível. Remover a nota desculpa "Cargo e campo qualificam o painel, não esta visualização".
5. **Painel direito Candidato:** 5 caixas (Reduto/Forte/Médio/Fraca/Ausência) substituem as 3 atuais.
6. **Persistir candidato selecionado** com Contexto > Candidatos.
7. **Migrar Diagnóstico estratégico** (4 quadrantes) pra Estratégia.
8. **Função "exportar mapa"** (PNG/SVG) — requisito da entrega Word.

---

## 4. Spec do relatório Word

A árvore de decisão do candidato vira **gerador de templates**. Quatro perfis, cada um com seu próprio sumário:

### Tipo 3 — Reposicionamento (aprovado)

Modelo canônico aprovado em abr/2026. Estrutura: capa + 5 capítulos.

```
Capa — Resumo executivo (1 página)
Cap. 1 — Contexto eleitoral do DF
   1.1 Estrutura territorial (renda, concentração de eleitorado)
   1.2 Paradoxo do voto progressista no DF (achado r=+0,86)
Cap. 2 — Diagnóstico de partida
   2.1 Card do candidato em 2022 (tipologia, σ, resumo territorial)
   2.2 Maiores forças territoriais (top 3 redutos)
   2.3 Maiores fraquezas territoriais (top 3 ausências)
   2.4 Card da referência (tipologia, trajetória 2026)
Cap. 3 — Análise de captura (peça central)
   3.1 Distribuição das 28 RAs nas 5 categorias
   3.2 Detalhamento das categorias (RAs e votos)
   3.3 Matriz de priorização 2×2 (Retorno × Esforço)
Cap. 4 — Cenários e meta
   4.1 Quociente eleitoral e meta
   4.2 Três cenários (Substituto orgânico / Ponte parcial / Ponte construída)
   4.3 A pergunta-chave
Cap. 5 — Plano de ação
   5.1 Reduto compartilhado (prioridade imediata)
   5.2 Lacuna e Núcleo afetivo (esforço médio)
   5.3 Hostil grande (decisão estratégica)
   5.4 Periferia irrelevante
   5.5 Síntese executiva
```

**Visualizações exportadas para o Word:**
- 1.1 Mapa do DF colorido por renda
- 1.2 Scatter % servidor federal × % voto progressista
- 2 Mapa do candidato colorido por Performance
- 3.1 Mapa do DF colorido pelas 5 categorias
- 3.2 Matriz 2×2 Retorno × Esforço
- 4 Gráfico horizontal cobertura da meta

**Princípios editoriais:**
- Tom sóbrio (sem coloquialismos como "bombou")
- Conceitos explicados apenas na primeira aparição (Performance, Voto, 5 categorias)
- Conceitos universais do DF (RA, eleitor vs morador, geografia básica) não são explicados
- Texto inteiramente parametrizável a partir de números + vocabulário do produto (sem caracterização editorial subjetiva)

### Decisões arquiteturais sobre Estratégia ↔ Word (abr/2026)

**Estratégia (renomeada para "Diagnóstico") = módulo gerador de relatório Word.** Decisão tomada em revisão ao Bloco E:

- A "Estratégia" do dashboard se funde com o gerador de Word num único módulo de wizard.
- Workflow: Exploração (Território/Contexto/Geopolítica) → Diagnóstico (configurar + ver análise + gerar Word).
- Wizard em **3 passos**:
  1. Quem é o candidato (escolha do tipo)
  2. A análise (conteúdo customizado por tipo, pré-visualizado em HTML)
  3. Relatório (preview do Word + download .docx)

**4 tipos de candidato (cards visíveis no Passo 1, sem detecção automática):**

1. **Estreante com referência** — primeira candidatura, identifica candidato 2022 análogo
2. **Estreante sem referência** — primeira candidatura, sem análogo claro (análise estrutural via PDAD)
3. **Reposicionamento** — já tem mandato em outro cargo, muda de cargo em 2026
4. **Reeleição** — disputa o mesmo cargo+campo de 2022

Cada tipo gera um template Word próprio. Bloco F (templates Word) absorvido neste novo Bloco E.

### Capítulo recorrente — A geografia política do DF (todos os templates)

**Inserir como Cap. 2** em todos os 4 templates (não como apêndice).

Esse capítulo é o **coração editorial do produto** — onde a leitura "DF é único" se concretiza. Sustentado por: scatter servidor federal × prog federal (gerado por `gerar_scatter_servidor_prog()`), tabela de correlações por cargo, exemplos concretos de RAs.

**Decisão arquitetural (abr/2026):** os achados e o scatter **vivem no Word, não no dashboard**. A tela ficou apenas com o "Como ler esta tabela" + a tabela funcional. Razão: na tela, achados editoriais empurram a tabela pra baixo do viewport e quebram o uso exploratório. No Word, ganham o espaço narrativo que merecem.

```
Cap. 2 — Como o DF vota: a geografia política

2.1 O paradoxo: classe alta vota progressista
    "No DF, o voto progressista cresce com renda e classe alta — o
    inverso do padrão nacional. A correlação entre % Classe A/B na
    RA e voto progressista chega a r = +0,86 para Dep. Federal."

2.2 O vetor dual
    "Mas o vetor é dual: servidor federal puxa por identidade
    ideológica de carreira pública (r = +0,83 para Federal e Senador);
    classe AB privada altamente escolarizada — Lago Sul, Águas Claras,
    Jardim Botânico — sustenta o efeito mesmo onde servidor não está
    concentrado. O eleitor 'rico' do DF é dois eleitores, e ambos votam
    progressista, contrariando o que renda alta significa em outras
    capitais."
    
    [INSERIR scatter: servidor federal × voto progressista (Federal),
     28 RAs, regressão visível, cor por classe AB]

2.3 O cargo importa
    "O voto do servidor não é monolítico — depende do cargo em disputa.
    Servidor federal vota progressista em Federal e Senador (r ≈ +0,83),
    mas em Distrital sua influência cai (r = +0,43). Servidor distrital
    faz o caminho inverso: depende da máquina local e tende ao campo
    governista — em Governador, r = +0,61 com liberal/conservador; em
    Senador, r = +0,60 com moderado. A própria disputa majoritária local
    cobra moderação — governos progressistas anteriores acabaram
    operando pelo centro."

2.4 Por que isso importa pra sua campanha
    Implicação tática para o cargo/campo do candidato — customizado
    por template (veja seções 4 deste documento).
```

**Função `gerar_scatter_servidor_prog(ras)` em `fase4_v2.py`** retorna o SVG do scatter pronto para inserção em qualquer destino (relatório Word via render do HTML, exportação PNG, etc.). Mantida no código mesmo sem uso na tela, antecipando a geração do Word.

### Template "Estreante com referência"

```
Cap. 1 — O território onde a campanha acontece (resumido)
Cap. 2 — Como o DF vota
   2.1 Geografia ideológica (achado r=0,93)
   2.2 Onde seu campo é dono
   2.3 Onde a eleição se decide (peso × competitividade)
Cap. 3 — Sua referência [perfil completo da referência selecionada]
   3.1 Quem ela foi em 2022
   3.2 Onde ela foi forte (sobre-índice + 5 categorias)
   3.3 Tipologia dela (capilar/campo/nicho)
Cap. 4 — Sua projeção 2026
   4.1 Sua meta (quociente + faixa esperada + cobertura)
   4.2 Onde virão os votos (mapa de captura herdada)
   4.3 Faixa de incerteza (cenários calibrados)
Cap. 5 — Recomendação
```

### Template "Estreante sem referência"

```
Cap. 1 — O território (extenso — primeira leitura do DF)
Cap. 2 — Como o DF vota
Cap. 3 — Quem é seu eleitor
   3.1 Perfil PDAD do eleitor-tipo do seu campo
   3.2 Onde mora esse perfil
Cap. 4 — Sua projeção 2026 estrutural
   4.1 Sua meta
   4.2 RAs com perfil compatível com seu campo
   4.3 Faixa de incerteza
Cap. 5 — Recomendação
```

### Template "Reposicionamento" (Manzoni-tipo)

```
Cap. 1 — Resumo do território
Cap. 2 — Resumo do contexto político (foco no cargo destino)
Cap. 3 — Diagnóstico de partida
   3.1 Quem você foi no cargo origem
   3.2 Tipologia atual (capilar/campo/nicho)
   3.3 Spread e teto
Cap. 4 — Análise de captura
   4.1 As 5 categorias de RA
   4.2 Estoque herdável da referência
   4.3 Hostilidades estruturais
Cap. 5 — Cenários
   5.1 Substituto orgânico
   5.2 + Ponte parcial
   5.3 + Ponte construída
Cap. 6 — Recomendação
```

### Template "Incumbente"

```
Cap. 1 — Sua geografia atual (defendendo)
Cap. 2 — Onde você ainda tem espaço
Cap. 3 — Concorrentes do mesmo campo+cargo
Cap. 4 — Risco eleitoral (RAs decisivas onde está vulnerável)
Cap. 5 — Recomendação
```

### Mapas exportados (todos os templates)

Imagens vêm da Geopolítica:

| Capítulo | Mapa |
|---|---|
| 1.x A geografia do voto | Território colorido por renda |
| 2.1 Geografia ideológica | Território colorido por sobre-índice do campo |
| 2.3 Onde decide | Território colorido por margem |
| 3.x Perfil da referência / candidato | Candidato colorido por sobre-índice (`idx`) |
| 4.x Onde virão os votos | Mapa de captura (5 categorias para reposicionamento) |

**Requisito:** botão "Exportar mapa atual" em cada visualização da Geopolítica gera PNG/SVG nomeado.

### Capa e estrutura comum

- Capa: nome do candidato · cargo · campo · período da análise · selo do consultor
- Sumário executivo (1 página): 3-5 bullets do achado central de cada capítulo
- Glossário no final
- Apêndice metodológico

---

## 5. Pendências em aberto

**Pendência específica do Geo > Candidato (revisitar no final):**
- Reformular o painel direito: substituir tabela "Desempenho por RA" (truncada) pelo bloco "Polos do candidato" (3 redutos + 3 ausências por performance), mantendo "Top 3 RAs principais" (por voto absoluto). Adicionar link "Ver tabela completa" pra Contexto > Candidatos. Espaço vertical economiza ~50%, leitura fica mais sintética/estratégica.



1. ~~**Nome do produto**~~ — ✅ confirmado **Estrategos** (working).
2. ~~**Amarração tabela↔mapa**~~ — ✅ confirmado **drawer lateral**.
3. **Δ 2018→2022 em Campo político** — desejável, adiável.
4. **Função `candComparar()`** — auditar quando entrar em implementação.
5. ~~**Função "exportar mapa"** (Bloco D.6)~~ — descartada como botão manual no dashboard. Migrada para o **gerador Word (Bloco F)**: imagens são produzidas programaticamente como parte da geração do relatório, evitando workflow de export manual e duplicação de trabalho.
6. **Campo do "perfil compatível PDAD × campo"** — adiado para Bloco E (Estratégia). Razão: âncoras simples não distinguem progressista de liberal no DF (Lago Norte é forte para os dois).
7. **Cenários recalibrados** — depende de ter dados de 2018 com qualidade pros percentis empíricos. Verificar cobertura.
8. **Aprofundamento dos achados de Campo político** — testes empíricos sobre: (i) origem da anomalia DF (estrutural × cultural via comparação 2018×2022), (ii) teto demográfico do servidor federal, (iii) servidor distrital como fiel da balança majoritária, (iv) explicações pro paradoxo Lago Sul, (v) mensagem-tipo por perfil de cliente. Discutidos no debate, agendados para revisão posterior.
9. ~~**5 RAs sem zona TSE (predição)**~~ — ✅ **resolvido em abr/2026** via novo método de atribuição seção→RA por point-in-polygon (`fase1c_perfil_secao.py`, baseado em `perfil_eleitor_secao_2022_DF` e `Limite_RA_20190.json`). Park Way, SIA, Fercal, Sol Nascente/Pôr do Sol e Arniqueira agora têm dado eleitoral próprio agregado das suas seções reais. Cross-check com total raw TSE bate com diferença zero (2.203.045 aptos no DF).
10. **Revisão da metodologia de Estrategos** — flagada em abr/2026, ainda não feita. Mapa em 6 camadas para varrer top-down (próxima sessão escolhe por onde começar):
    1. **Fontes e unidade de análise** — PDAD 2021 × TSE 2022 (validação 2018 disponível mas pouco usada); 33 RAs com cobertura via atribuição seção→RA por PIP (resolveu o caso histórico das 5 sem zona); Cargo × Campo (4 campos incl. "Outros" residual).
    2. **Métrica central** — Sobre-índice/Performance, cortes ±15%/±30%, denominador "aptos" (não comparecimento), threshold mínimo 30 votos / 1% do total.
    3. **Métricas derivadas** — Spread → tipologia (cortes 100pp/200pp); Domínio; Margem 1º-2º; Peso eleitoral; Força do campo; Idx do Campo (pode ser todo negativo).
    4. **Cruzamentos estratégicos** — Estratégia (Performance × Força do campo, 5 zonas); Reposicionamento (origem × referência, 5 zonas com Volume baixo separado por mediana); Aliança (quadrantes categóricos, substituiu r/σ).
    5. **Achados estruturais do DF** — Eixo central × Periferia; classe alta progressista (r≈+0,86); vetor dual servidor federal/AB privada; servidor distrital como fiel da majoritária.
    6. **Projeção e Word** — Quociente, cenários (orgânico / ponte parcial / ponte construída — calibração pendente); 4 templates por tipo de candidato.

    **Pontos frágeis identificados (candidatos a discussão):** ~~(i) 5 RAs sem zona TSE~~ — **resolvido** (ver item 9); (ii) Cortes ±15/±30 — empíricos ou herdados? (iii) Aptos vs. comparecimento como denominador — escolha consciente? (iv) Cruzamento PDAD × campo (item 6 acima já adiado pra Bloco E). (v) Calibração de cenários — depende de cobertura 2018. (vi) "Outros" como campo residual — entra ou não nos cruzamentos de força?

    **Estado atual do dashboard durante a revisão:** link "Sobre o Estrategos" do rodapé do menu **comentado** em `index.html` (commit `769ad8f`, abr/2026) — modal explicativo descreve metodologia que pode mudar. Reativar quando a revisão concluir. Campo político permanece visível.

11. **Revisão CSS mobile** — não começada. Dois níveis estimados:
    - **Decente** (~1 dia): nav vira drawer com hambúrguer, layouts 3-col empilham, tabelas ganham scroll horizontal, tooltips viram tap. Garante que não quebra.
    - **Bom** (~1 semana): tabelas grandes (Candidatos, Estratégia) viram cards/colapso de colunas em <768px, decisões editoriais sobre o que cortar, mapas redimensionados, comportamento de hover/tap consistente.

    Recomendação inicial: nível 1 + versão "leitura" no mobile com achados-âncora e remetendo pro desktop pras tabelas. Decisão pendente.

12. ~~**Gap escolaridade no menu Eleitorado**~~ — ✅ **resolvido em abr/2026** junto com o item 9. O gap absurdo (Lago Sul −47,8pp, SCIA +37,5pp etc.) era artefato da distribuição proporcional zona→RA: o perfil eleitoral do TSE só vem por zona, e várias RAs compartilhavam a mesma zona, recebendo todas a mesma média. Com o novo método PIP, cada RA recebe perfil próprio e o gap converge para faixa razoável (±5–13pp).

13. **Coluna "% do candidato" no menu Candidatos** — refletir sobre adicionar coluna mostrando o quanto cada RA representou no total de votos do candidato (`votos_RA / total_cand`). Hoje a tabela mostra Votos 2022, % do campo, % do cargo, Performance e Status — falta a fatia que cada RA contribuiu pro próprio candidato. É um dos componentes da fórmula da Performance, mas tem leitura própria ("de onde vieram meus votos"). Avaliar onde encaixa sem sobrecarregar a tabela.

14. **Filtro da tabela por card no Comparar candidatos** — habilitar clique nos KPI cards (Sobreposição / A agrega / B agrega / Aberto) para filtrar a tabela abaixo apenas pelas RAs daquele quadrante. Hoje os cards mostram apenas a contagem; vira atalho de leitura natural se forem clicáveis.

15. **Limpeza de `dados_tse_cache/`** — redundância de ~600MB (CSVs descompactados + ZIPs do mesmo conteúdo). Após migração para `perfil_eleitor_secao_2022_DF`, `perfil_eleitorado_2022.zip` (Brasil-todo, agregado por zona) fica obsoleto pro pipeline e pode ir pra `legado/`. Adicionar `.DS_Store` ao `.gitignore`.

---

## 6. Glossário

**Sobre/sub-índice (índice de sobrerrepresentação)**
`(votos_RA / total_cand) / (aptos_RA / aptos_DF)`. Acima de 1 = a RA entrega mais votos do que seu tamanho sugere; abaixo de 1 = entrega menos. Apresentado como `+X% / −X%`.

**Domínio do campo**
% dos votos do cargo na RA que foram para algum candidato do campo. Mede fatia de mercado bruta.

**Margem 1º-2º**
Diferença em pontos percentuais entre o vencedor e o segundo colocado em uma RA. Mede competitividade.

**Peso eleitoral da RA**
% dos votos totais do cargo no DF que vieram daquela RA. Mede importância da RA na decisão eleitoral.

**Spread**
Distância entre o sobre-índice máximo e o mínimo do candidato. Métrica derivada que classifica o tipo de campanha.

**Tipologia de candidato**
- **Capilar** (spread <100pp): distribuição ampla, joga em todo lugar (Ibaneis-tipo)
- **Campo militante** (100–200pp): forte mas distribui razoavelmente (Kicis-tipo)
- **Nicho** (>200pp): hiperconcentrado em poucas RAs (Manzoni-tipo)

**5 categorias do sobre-índice**
- **Reduto** (idx ≥ +30%): RA me ama muito mais do que o esperado
- **Base forte** (+15% a +30%): RA me ama acima do esperado
- **No esperado** (−15% a +15%): RA me trata como um candidato genérico
- **Base fraca** (−15% a −30%): RA me ama abaixo do esperado
- **Ausência** (idx ≤ −30%): RA praticamente me ignora

**5 categorias de RA no reposicionamento**
Cruzando sobre-índice atual do candidato com sobre-índice da referência:
- **Reduto compartilhado** (consolidar e absorver)
- **Núcleo afetivo** (defender)
- **Lacuna da referência** (captura oportunística)
- **Hostil grande** (não atira)
- **Periferia irrelevante** (ignora)

**Eixo central × Periferia**
Insight estrutural do DF identificado na revisão: Plano Piloto + Lagos + Sudoeste + Águas Claras + Jardim Botânico = ringue ideológico onde qualquer campo extremo se elege. Periferia (Brazlândia, Varjão, SCIA, Recanto) opera com lógica de política local não-ideológica.
