# Metodologia · Estrategos

Documento técnico de referência sobre o método analítico subjacente ao painel **Estrategos** — solução de Inteligência Política da Opinião Informação Estratégica, aplicada às eleições do Distrito Federal em 2026.

Escrito como **fonte da verdade técnica**, defensável diante de um par crítico (acadêmico ou outro consultor). Cada camada explicita o **que é**, **por que essa escolha** foi feita (e não outra), as **premissas embutidas** e as **limitações conhecidas**.

Atualizado em **abr/2026**.

---

## Sumário

1. [Resumo executivo](#1-resumo-executivo)
2. [Premissas e escopo](#2-premissas-e-escopo)
3. [Camada 1 — Fontes e unidade de análise](#3-camada-1--fontes-e-unidade-de-análise)
4. [Camada 2 — Métrica central (Performance · sobre-índice)](#4-camada-2--métrica-central-performance--sobre-índice)
5. [Camada 3 — Métricas derivadas](#5-camada-3--métricas-derivadas)
6. [Camada 4 — Cruzamentos estratégicos](#6-camada-4--cruzamentos-estratégicos)
7. [Camada 5 — Achados estruturais do DF](#7-camada-5--achados-estruturais-do-df)
8. [Camada 6 — Projeção 2026](#8-camada-6--projeção-2026)
9. [Limitações conhecidas e decisões pendentes](#9-limitações-conhecidas-e-decisões-pendentes)
10. [Glossário técnico](#10-glossário-técnico)

---

## 1. Resumo executivo

Estrategos é um sistema de inteligência eleitoral aplicada ao Distrito Federal. Cruza dados socioeconômicos (PDAD 2021/IPEDF) com resultados de votação (TSE 2022) para gerar uma leitura territorial estratégica das 33 Regiões Administrativas (RAs) do DF, organizada por cargo (Governador, Senador, Deputado Federal, Deputado Distrital) e por campo político (Progressista, Moderado, Liberal/Conservador, Outros).

O indicador central é o **sobre-índice** — apresentado como **Performance** na interface — que mede o quanto cada RA entrega de votos a um candidato em relação ao que seria proporcional ao tamanho do seu eleitorado. Sobre essa métrica simples e auditável se constroem todas as derivações: perfil de votação do candidato, força do campo, zonas estratégicas, análises de aliança e reposicionamento.

A escolha de uma **métrica atomizada** — em vez de um índice composto com pesos arbitrários, modelo que foi explicitamente aposentado em abr/2026 — é deliberada: cada número é defensável, reconstrutível a partir de fontes públicas, e o usuário pode auditar cada passo. O produto **organiza o território para apoiar decisões táticas; não prevê resultados eleitorais**.

---

## 2. Premissas e escopo

### 2.1 O que Estrategos faz

- Descreve o comportamento eleitoral por território no DF em 2022, com profundidade por cargo e por campo.
- Classifica o desempenho de candidatos individuais e do campo político em cada RA usando uma métrica única (sobre-índice).
- Cruza essas leituras para gerar zonas estratégicas — onde consolidar, onde conquistar, onde não atirar.
- Coloca achados estruturais do DF (correlações renda × ideologia, papel do servidor público) ao alcance imediato do consultor.

### 2.2 O que Estrategos não faz

- **Não prevê resultados de 2026.** Projeções existem (Camada 6), mas são cenários condicionais sobre uma referência escolhida — não predição estatística com intervalo de confiança.
- **Não captura comportamento individual.** A unidade mínima é a RA. O dado é agregado, não individual — não permite inferir como um eleitor específico vota a partir do que a sua RA vota.
- **Não substitui pesquisa qualitativa.** Descreve onde e quanto cada campo/candidato performa; não responde *por que* um eleitor vota como vota.
- **Não pondera campos políticos por mérito ideológico.** A classificação Progressista / Moderado / Liberal-Conservador / Outros é descritiva (baseada em filiação partidária e padrão de voto histórico), não normativa.

### 2.3 Princípios metodológicos

1. **Auditabilidade.** Cada número apresentado deve ser reconstrutível pelo usuário a partir das fontes públicas (PDAD e TSE). Sem caixas-pretas, sem coeficientes calibrados internamente sem documentação.
2. **Atomicidade.** Métricas compostas com pesos arbitrários foram explicitamente rejeitadas (ver decisão de abr/2026 sobre a aposentadoria do índice SPE composto, que combinava Afinidade × Conversão × Massa × Logística com pesos editoriais). Cada indicador exposto mede uma coisa só, com escala interpretável.
3. **Separação dado/interpretação.** O painel apresenta o dado bruto e suas derivações. A interpretação editorial (achados, leituras, recomendações) é apresentada como tal — em blocos visualmente distintos — para que o usuário possa concordar ou discordar conscientemente.
4. **Conservadorismo na inferência.** Quando o dado não existe ou é frágil (5 RAs sem zona eleitoral TSE, por exemplo), a opção é declarar a ausência, não estimar com técnicas que escondam a incerteza.

### 2.4 Universo coberto

| Dimensão | Cobertura |
|---|---|
| Geografia | Distrito Federal — 33 Regiões Administrativas (28 com zona TSE direta · 5 sem) |
| Eleições de referência | TSE 2022 (cadastro eleitoral · votação por seção). Infraestrutura para TSE 2018 e PDAD 2018 disponível, uso pontual. |
| Cargos | Governador · Senador · Deputado Federal · Deputado Distrital |
| Campos políticos | Progressista · Moderado · Liberal/Conservador · Outros (residual) |
| Horizonte de aplicação | Eleições do DF em 2026 |

---

## 3. Camada 1 — Fontes e unidade de análise

### 3.1 As fontes

#### PDAD 2021 (IPEDF)

A **Pesquisa Distrital por Amostra de Domicílios** é o levantamento socioeconômico oficial do Distrito Federal, conduzido pelo Instituto de Pesquisa e Estatística do DF (IPEDF, ex-CODEPLAN). A edição 2021 entrevistou cerca de 83 mil moradores em todas as 33 RAs do DF, com expansão amostral por RA.

**O que entrega:** renda per capita, classe social (A/B/C/D/E pelo critério Brasil), escolaridade (sem fundamental · com fundamental · superior), ocupação (funcionalismo público distrital · funcionalismo federal · setor privado · informal), origem (DF · outras UFs), faixa etária e indicadores de vulnerabilidade (insegurança alimentar, dependência de benefícios sociais).

**Por que escolhida:** é a única fonte com **granularidade direta por RA** para variáveis socioeconômicas. O Censo IBGE 2022 cobre o DF, mas sua malha territorial não coincide com as RAs e a desagregação exige reagrupamento de setores censitários — perdendo precisão e introduzindo passos de transformação adicionais.

#### TSE 2022

Cadastro eleitoral e resultados da eleição geral de 2022, distribuídos publicamente pelo Tribunal Superior Eleitoral. São dois recortes complementares:

**Cadastro:** total de eleitores aptos por zona eleitoral, com decomposição por gênero, faixa etária e escolaridade declarada.

**Votação:** votos por candidato, por seção eleitoral, em cada um dos quatro cargos disputados (Governador, Senador, Deputado Federal, Deputado Distrital), incluindo brancos, nulos e abstenção.

**Por que escolhida:** é a última eleição geral antes do alvo (2026), com os mesmos cargos em disputa, e seu nível de granularidade (seção eleitoral) é mais fino do que precisamos — permite agregar à RA com pouca perda. Eleições municipais (2024) ficam fora do escopo: cargos diferentes (vereador, prefeito) não se aplicam ao DF, que não tem municípios.

**Períodos secundários:** TSE 2018 e PDAD 2018 estão disponíveis no pipeline e foram usados pontualmente para validar séries temporais (estabilidade de correlações, deslocamentos de campo entre 2018 e 2022). Não compõem a base de produção atual — entram como controle quando uma decisão metodológica depende de saber se um achado é estrutural ou conjuntural.

### 3.2 A unidade de análise: a Região Administrativa

Toda a análise é construída tendo a **Região Administrativa do DF como unidade mínima**. Essa escolha tem três justificativas complementares:

1. **Granularidade adequada.** A seção eleitoral (algumas dezenas a poucas centenas de eleitores) introduz ruído amostral; o DF inteiro perde território. A RA fica no ponto onde o dado é estável e o significado político é interpretável.
2. **Coincidência com o tecido administrativo do DF.** Cada RA tem administração regional, orçamento próprio, identidade local reconhecida pelos moradores. Uma análise por RA fala a mesma língua que o consultor e o cliente já falam.
3. **Coerência com a fonte socioeconômica.** A PDAD é desagregada exatamente por RA. Trabalhar nessa unidade evita reagrupamentos arbitrários e mantém a auditabilidade.

#### Correspondência zona TSE ↔ RA

O TSE não opera com RAs — opera com **zonas eleitorais**. As zonas do DF foram desenhadas em outro momento histórico, e a correspondência com as RAs atuais não é 1-para-1: algumas zonas atendem mais de uma RA, e algumas RAs novas (criadas após o desenho original das zonas) não têm zona própria.

O pipeline (Fase 1) constrói uma tabela de correspondência zona ↔ RA com base na localização dos locais de votação e na atribuição majoritária dos eleitores. O resultado:

- **28 RAs com cobertura direta**: a totalidade dos votos de uma ou mais zonas é atribuída à RA com baixa ambiguidade.
- **5 RAs sem zona própria**: Park Way, SIA, Fercal, Sol Nascente/Pôr do Sol e Arniqueira. Seus eleitores estão registrados em zonas das RAs vizinhas (Arniqueira em Águas Claras, Sol Nascente em Ceilândia, etc.) e não há como desagregar votos com precisão.

#### Tratamento das 5 RAs sem zona TSE

A decisão atual é **filtrar essas 5 RAs das tabelas eleitorais e indicadores derivados**, mantendo-as nas tabelas socioeconômicas (onde a PDAD funciona normalmente). Cada tabela afetada traz uma nota de rodapé canônica explicando a ausência.

**Alternativas consideradas e rejeitadas:**

| Alternativa | Problema |
|---|---|
| Atribuir votos da RA-mãe proporcionalmente ao eleitorado | Pressupõe que o comportamento eleitoral da RA filha é idêntico ao da mãe — contradiz justamente o que a análise quer descobrir |
| Estimar via regressão multivariada (PDAD da RA filha → voto esperado) | Modelo introduz incerteza que o painel não tem como comunicar; resultado parece tão sólido quanto dado real, mas não é |
| Atribuir votos por vizinhança geográfica | Park Way (vizinha de Núcleo Bandeirante) e SIA (vizinha de Guará) têm perfis socioeconômicos muito distintos das vizinhas; vizinhança não é proxy de comportamento |

A escolha por **filtrar e declarar a ausência** é coerente com o princípio de conservadorismo na inferência (§2.3). Um toggle "incluir estimativas" foi cogitado mas permanece pendente — exigiria documentação clara do método e da incerteza, e não é prioritário no momento.

### 3.3 Cargos e campos políticos

#### Os quatro cargos

Estrategos cobre os quatro cargos disputados no DF: **Governador**, **Senador**, **Deputado Federal** e **Deputado Distrital**. Os dois primeiros são majoritários; os dois últimos, proporcionais. As lógicas de eleição são diferentes (maioria simples vs. quociente eleitoral), e o produto trata cada cargo separadamente — uma RA pode ser reduto de um candidato para Distrital e ausência para o mesmo candidato em Federal.

#### A classificação em campos políticos

Os candidatos são classificados em **quatro campos**, com base na filiação partidária e no padrão histórico de coalizões:

| Campo | Critério | Partidos típicos no DF (2022) |
|---|---|---|
| **Progressista** | Esquerda e centro-esquerda | PT, PSOL, PCdoB, PV, Rede, PSB |
| **Moderado** | Centro pragmático, "centrão" | PSD, MDB, União Brasil, PSDB, Cidadania, Solidariedade |
| **Liberal/Conservador** | Direita e centro-direita | PL, Republicanos, PP, Novo, PRTB |
| **Outros** | Residual (siglas pequenas, perfis ambíguos) | — |

A classificação é **descritiva, não normativa** (§2.2). Não pondera mérito ideológico nem captura toda a variabilidade interna de cada partido. Casos limítrofes — candidato cujo padrão de voto e alianças destoam claramente da sigla — recebem ajuste manual quando a evidência é forte. Esses ajustes ficam documentados no código de classificação (`classificacao_base.py`).

**Por que "Outros" e não "Centro":** "Centro" colidiria conceitualmente com "Moderado" (que já cobre o centro pragmático). "Outros" é honesto sobre o que é — uma categoria residual para o que não cabe nos três blocos principais.

### 3.4 Premissas embutidas

Toda análise depende de premissas. As principais nesta camada:

1. **Eleitorado de 2022 é proxy razoável do eleitorado de 2026.** Quatro anos é tempo curto para mudança estrutural significativa na composição eleitoral. Mudanças marginais (entrada de jovens, mortalidade, mobilidade interestadual) não invalidam a leitura territorial. Mudanças bruscas (anexações, redivisões administrativas) seriam exceção e exigiriam reavaliação caso a caso.
2. **Residência declarada na PDAD coincide com domicílio eleitoral na zona correspondente.** Em geral verdadeiro no DF. Uma exceção potencialmente relevante são servidores federais que mantêm título de eleitor na UF de origem — esse grupo apareceria nos dados socioeconômicos da RA mas não nos eleitorais. Em RAs com forte concentração de servidores federais migrados (Lago Norte, Plano Piloto), o eleitorado pode estar parcialmente subestimado em relação à população residente; não dispomos de dado para cravar a magnitude desse efeito.
3. **Filiação partidária é proxy razoável de campo político no DF em 2022.** A política nacional pós-2018 amplificou a polarização e tornou as siglas mais coesas dentro de cada bloco. Casos de divergência interna (candidato progressista em sigla de centro, p. ex.) são tratados manualmente quando relevantes.

### 3.5 Limitações conhecidas

1. **As 5 RAs sem zona TSE perdem cobertura eleitoral.** Já discutido em §3.2.
2. **Granularidade fixa na RA, não abaixo.** Algumas RAs grandes (Ceilândia, Plano Piloto, Taguatinga) abrigam realidades socioeconômicas internas muito heterogêneas. A análise por RA mascara essa heterogeneidade. Subdivisão por bairro (NUCB, Águas Lindas, Sobradinho I × II, etc.) é tecnicamente possível na PDAD mas não no TSE — e a falta de simetria invalida o cruzamento. Mantemos a RA como teto comum.
3. **Classificação "Outros" perde resolução.** Quando um candidato relevante cai em "Outros" por filiação a sigla pequena, sua leitura individual fica preservada (Camada 2 atua sobre o candidato, não sobre o campo), mas ele desaparece dos cruzamentos por campo (Camada 4). Isso é aceito como custo.
4. **Sem dado pós-2022.** Eleições municipais 2024 não se aplicam ao DF. Pesquisas qualitativas, dados de redes sociais, mobilidade urbana, séries econômicas pós-2022 — nada disso entra. O painel é uma fotografia de 2022 lida pela ótica de 2026; se houver ruptura estrutural entre os dois períodos (crise econômica grande, evento político maior), a leitura precisa ser ajustada qualitativamente fora do painel.
5. **Inferência limitada ao território, não ao eleitor individual.** As correlações entre variáveis socioeconômicas e voto que aparecem no painel são por RA — não por pessoa. "RAs com mais classe AB votam mais progressista" **não significa** "eleitores AB votam progressista": pode ser outro perfil de morador (servidor público, por exemplo) puxando a média. A interpretação individual exige pesquisa de outro tipo (survey, grupo focal). Os blocos didáticos do painel sinalizam essa fronteira onde a leitura territorial aparece.

---

## 4. Camada 2 — Métrica central (Performance · sobre-índice)

### 4.1 Definição formal

A métrica central de Estrategos é o **sobre-índice** — chamado **Performance** na interface. Para um candidato C numa RA R:

```
sobre-índice(C, R) = (votos_RA / total_cand) / (aptos_RA / aptos_DF)
```

Onde:
- `votos_RA` = votos do candidato C na RA R
- `total_cand` = votos totais do candidato C em todo o DF
- `aptos_RA` = eleitores aptos na RA R (cadastro TSE)
- `aptos_DF` = eleitores aptos no DF inteiro

O numerador é a **fração dos votos do candidato** que vieram daquela RA. O denominador é a **fração do eleitorado total** que mora na RA. A razão entre os dois mede se a RA entregou mais (ou menos) votos do que entregaria se o candidato performasse de modo perfeitamente proporcional ao tamanho do território.

#### Apresentação

O ratio bruto é convertido em delta percentual antes de ser exibido:

```
Performance = (sobre-índice − 1) × 100
```

Assim:
- ratio 1,00 → **0%** (RA proporcional)
- ratio 1,50 → **+50%** (RA entrega 50% acima do esperado)
- ratio 0,70 → **−30%** (RA entrega 30% abaixo do esperado)

A interface sempre exibe o delta (`+50%` / `−30%`), nunca o ratio (`1,5×`). O ratio existe internamente no pipeline e nas memórias técnicas, mas é traduzido na saída — `+X%` é mais imediatamente interpretável para quem não está acostumado a razões.

#### Exemplo concreto

Plano Piloto concentra cerca de **9% do eleitorado do DF**. Se um candidato tem performance perfeitamente proporcional, esperaríamos que ~9% dos seus votos viessem dali. Suponha um candidato com 100 mil votos no DF e 18 mil em Plano Piloto:

- share de votos do candidato em PP: 18.000 / 100.000 = **18%**
- share de aptos PP no DF: **9%**
- sobre-índice: 18% / 9% = **2,0**
- Performance: **+100%**

Plano Piloto entregou o dobro do que seu tamanho sugeria — é um reduto desse candidato.

### 4.2 Por que essa escolha (vs. alternativas)

A pergunta que a métrica central precisa responder é: *onde o candidato performa acima ou abaixo do que seu tamanho relativo no território sugeriria?* Quatro alternativas foram consideradas e rejeitadas:

| Alternativa | Por que rejeitada |
|---|---|
| **Voto absoluto na RA** | Não considera tamanho. Um candidato com 100 mil votos em Ceilândia (RA grande) pode estar performando abaixo do esperado; 5 mil em Park Way pode ser reduto. Voto bruto confunde escala com força. |
| **% do voto do cargo na RA** (penetração local) | Mede outra coisa — fatia de mercado naquele território, não força do candidato relativa a si próprio. Útil como indicador secundário (ver Camada 3), não como métrica central. |
| **Z-score (desvio em sigmas)** | Sensível à dispersão do próprio candidato. Um z-score de +1 significa coisas diferentes para um candidato concentrado vs. distribuído. O sobre-índice é absoluto: +30% sempre quer dizer "30% acima da proporção esperada", independente da forma da distribuição. |
| **Diferença bruta entre shares (em pp)** | Insensível à magnitude. Uma RA com 1% do eleitorado tem teto matemático de +99pp; uma RA com 10% tem teto de +90pp. Não comparável entre RAs de tamanhos distintos. |

A escolha pelo sobre-índice não é arbitrária: é a única transformação simples que torna RAs de tamanhos diferentes diretamente comparáveis e cuja escala (`+30%`, `−15%`) tem leitura imediata.

### 4.3 Aptos como denominador (vs. comparecimento)

O denominador `aptos_RA / aptos_DF` usa o **eleitorado registrado** (cadastro TSE), não o **comparecimento** (eleitores que efetivamente votaram). Essa escolha tem consequência metodológica relevante.

**Por que aptos:**

1. Aptos é estável entre eleições — corresponde ao tamanho potencial do mercado eleitoral da RA. Comparecimento varia por eleição e por mobilização local, e usá-lo no denominador embaralharia "candidato cresceu por captura" com "eleição teve menos abstenção".
2. A abstenção, no nosso modelo, é uma **variável independente** (pode indicar oportunidade de mobilização). Misturá-la no denominador da métrica central esconde o que ela tem a dizer.
3. A pergunta "como o candidato performa em relação ao tamanho do território" é mais bem respondida usando o tamanho potencial (aptos) do que o tamanho efetivo (comparecimento).

**Implicação aceita:** Performance pode estar levemente inflada em RAs com baixa abstenção e deflada em RAs com alta abstenção. Isso é assumido como custo da escolha. A abstenção entra na análise pelo lado do **diagnóstico territorial** (variável visível em outras camadas), não como ruído escondido na métrica central.

### 4.4 Os cinco cortes (±15% / ±30%)

A Performance é classificada em cinco faixas descritivas:

| Faixa | Performance | Leitura |
|---|---|---|
| **Reduto** | ≥ +30% | RA entrega substancialmente acima do esperado |
| **Base forte** | +15% a +30% | RA entrega acima do esperado |
| **Esperado** | −15% a +15% | RA trata o candidato como genérico (proporcional) |
| **Base fraca** | −15% a −30% | RA entrega abaixo do esperado |
| **Ausência** | ≤ −30% | RA entrega substancialmente abaixo do esperado |

#### Por que esses cortes

A escolha é **editorial, não estatística**. Os cortes ±15% e ±30% foram fixados com base em observação empírica sobre os candidatos do TSE 2022:

- ±15% delimita a faixa onde a maior parte das RAs cai para um candidato "típico" do cargo. Dentro dessa banda, a variação é ruidosa o suficiente para não merecer leitura editorial.
- ±30% marca o limite onde o desvio é qualitativamente diferente — a RA tem comportamento próprio em relação ao candidato, não apenas variação de fundo.

#### Por que cinco faixas (e não três)

Três faixas (forte / esperado / fraco) perderiam a distinção narrativa entre **Reduto** (uma RA que carrega votos desproporcionalmente) e **Base forte** (uma RA aliada mas sem ser o coração da campanha). Essa distinção importa para decisão tática — onde concentrar recursos vs. onde apenas defender.

#### Por que simétrico

Cortes simétricos (mesmo módulo nos dois lados) refletem a natureza linear da métrica. A perda de "30% abaixo" e o ganho de "30% acima" são tratados como equivalentes em magnitude — ainda que estrategicamente representem situações distintas (uma é sinal de vulnerabilidade, a outra de força).

#### Termos descartados para a faixa central

"Médio", "Média", "No esperado", "Intermediário", "Estável", "Neutro" (este último colidiria com "Outros" do campo político), "Proporcional", "Padrão". O canônico é **Esperado** — neutro o bastante, descritivo o bastante, sem peso valorativo.

### 4.5 Threshold mínimo (proteção contra microRAs)

Performance é uma razão. Em RAs muito pequenas (poucos aptos) e/ou candidatos com poucos votos na RA, o numerador e o denominador ficam instáveis — pequenas variações absolutas geram deltas percentuais enormes que não significam nada estratégico.

Para fins de ranking e cards de "regiões principais", aplicamos um **threshold mínimo**:

```
votos_RA ≥ max(30, 1% × total_cand)
```

RAs abaixo desse limite têm sua Performance calculada e exibida na tabela completa, mas ficam **fora** dos rankings curados (top 3 redutos, top 3 ausências) e dos blocos editoriais. Isso evita que o painel destaque, p. ex., "principal reduto: SIA com +480%" quando a base é 12 votos numa RA com 800 aptos.

### 4.6 Premissas embutidas

1. **Aptos é o denominador correto.** Discutido em §4.3.
2. **A linearidade do delta é interpretável.** +30% e −30% são tratados como simétricos em magnitude. Estrategicamente são situações diferentes (força vs. vulnerabilidade), mas a métrica não pondera isso — quem pondera é a leitura editorial.
3. **A Performance compara o candidato consigo mesmo.** Indicador é interno ao candidato, não entre candidatos. Falar "candidato A tem mais reduto que candidato B" porque A tem mais RAs em ≥+30% é leitura possível mas tangencial — o desenho da métrica é para responder *onde* o candidato performa, não *quanto* ele performa em comparação.

### 4.7 Limitações conhecidas

1. **Cortes editoriais não calibrados estatisticamente.** Os ±15% e ±30% são empíricos no sentido de "olhamos a distribuição e fixamos onde fazia sentido", não "fizemos teste de sensibilidade formal". Existe a hipótese de que o corte ideal varie por cargo (Distrital tende a maior dispersão; Governador a menor) — não foi testada. Pendência registrada no backlog.
2. **Sensibilidade à abstenção.** Como discutido em §4.3, RAs com abstenção atípica deslocam a métrica. Aceito como custo.
3. **Threshold mínimo é heurístico.** O `max(30, 1%)` foi calibrado por observação, não por análise formal de variância. Funciona bem para os candidatos do TSE 2022; pode precisar ajuste para outras eleições ou outros tipos de candidato.
4. **Ratio indefinido em casos extremos.** Quando `aptos_RA = 0` (não ocorre no DF, mas teórico) ou `votos_RA = 0` (Performance = −100% ou ratio zero), o pipeline trata com regras numéricas explícitas no código.
5. **Performance é descritiva, não causal.** Diz onde a RA está acima ou abaixo do esperado. Não diz por quê. A explicação fica para a Camada 5 (achados estruturais) e para a leitura editorial caso a caso.

---

## 5. Camada 3 — Métricas derivadas

A Performance é a métrica central, mas sozinha não responde todas as perguntas estratégicas. Cinco métricas derivadas complementam a leitura — quatro descrevem **a RA ou o candidato**, e uma é uma transformação que classifica o **tipo de campanha**.

### 5.1 Spread e perfil de votação

#### Spread

```
spread(C) = max(Performance) − min(Performance) do candidato C
```

Em pontos percentuais. Mede a **amplitude** da Performance do candidato — quanto a sua RA mais favorável difere da menos favorável.

#### Perfil de votação (Distribuído / Híbrido / Concentrado)

A partir do spread, o candidato é classificado em um de três perfis:

| Perfil | Spread | Leitura | Cargo típico |
|---|---|---|---|
| **Distribuído** | < 100pp | Candidato performa parecido em todo o DF; cobertura ampla | Governador (Ibaneis-tipo) |
| **Híbrido** | 100–200pp | Forte em algumas regiões mas mantém presença razoável nas demais | Federal (Kicis-tipo) |
| **Concentrado** | > 200pp | Hiperperformance em poucas RAs; ausência clara em outras | Distrital (Manzoni-tipo) |

#### Por que essa métrica

O perfil de votação diagnostica **o tipo de campanha** que o candidato faz — antes mesmo de olhar onde ele é forte. Isso tem implicação estratégica direta:

- Um candidato **Distribuído** já cobre território; o desafio é defender a base e mobilizar.
- Um **Híbrido** tem alicerce em poucas RAs e precisa decidir entre consolidar ou expandir.
- Um **Concentrado** depende de hiperperformance num conjunto pequeno; a estratégia é afunilar, não diluir.

#### Por que cortes em 100pp e 200pp

Como em §4.4, os cortes são **editoriais empíricos** — fixados pela observação dos candidatos do TSE 2022. Refletem diferenças naturais entre cargos: Governador exige distribuição (quem ganha em maioria simples não pode ter ausência grande), Distrital aceita hiperconcentração (a aritmética do quociente eleitoral premia bases compactas).

#### Limitações

- **Sensível a outliers.** Spread se baseia em dois pontos (max e min). Uma única RA atípica pode jogar o perfil. Alternativa considerada: desvio padrão da Performance — mais robusto, mas menos interpretável editorialmente. A escolha pelo spread privilegia a leitura ("qual é o range?") sobre o rigor estatístico.
- **Cortes não validados estatisticamente.** Mesma limitação dos cortes da Performance. Pode haver cargo onde 150pp seja a fronteira mais informativa.

### 5.2 Domínio do campo

```
domínio(campo, RA, cargo) = votos_campo_RA / votos_totais_cargo_RA
```

Em pontos percentuais. Mede a **fatia de mercado bruta** do campo político na RA — qual fração dos votos válidos daquele cargo na RA foi para algum candidato do campo.

#### Por que essa métrica (e por que separada da Performance)

Performance e Domínio respondem perguntas diferentes:

- **Performance** mede **força relativa** ao tamanho do território. Uma RA pequena com Performance +50% pode contribuir com poucos votos absolutos.
- **Domínio** mede **peso absoluto na disputa local**. Uma RA grande com domínio 40% para um campo é um território onde quase metade dos votos do cargo vai para esse campo, independentemente do tamanho.

Exemplo: um candidato pode ter Performance +50% em Park Way (reduto pessoal numa RA pequena) e Performance +20% em Plano Piloto (RA grande). Em volume absoluto de votos, Plano Piloto contribui muito mais — Domínio captura isso.

A leitura conjunta das duas métricas evita o erro de tratar reduto pequeno e território estratégico como equivalentes.

#### Aplicação por candidato

A mesma lógica de Domínio se aplica ao candidato individual: `votos_cand_RA / votos_totais_cargo_RA`, exibido como "% do cargo" na interface. Mede penetração local.

### 5.3 Margem 1º–2º

```
margem(RA, cargo) = % do 1º colocado − % do 2º colocado (em pp)
```

Mede a **competitividade da RA naquele cargo**. Quanto menor a margem, mais disputada — uma decisão eleitoral pequena pode virar a RA. Quanto maior, mais cativa.

#### Por que essa métrica

A margem é o indicador mais direto de onde uma campanha tem **leverage** territorial. Investir em uma RA com margem de 50pp é jogar contra a corrente; em uma com margem de 5pp, qualquer mobilização adicional pode mudar o resultado local.

A margem é calculada **na RA × cargo**, não no DF inteiro. Uma RA pode ser disputadíssima para Governador e cativa para Deputado Distrital, ou vice-versa.

#### Faixas de leitura

A margem é exibida como número contínuo na interface, sem cortes categóricos fixados. Como guia editorial provisório:

- **< 10pp** — competição alta
- **10–30pp** — competição moderada
- **> 30pp** — competição baixa

Os rótulos categóricos para a Margem ainda estão sendo definidos no produto e podem ser revisados.

### 5.4 Peso eleitoral da RA

```
peso(RA, cargo) = votos_totais_cargo_RA / votos_totais_cargo_DF
```

Em pontos percentuais. Mede a **importância da RA na decisão eleitoral** daquele cargo.

#### Por que separada de "share de aptos"

Peso eleitoral usa **votos efetivos**, não eleitorado registrado. A diferença reflete a abstenção: uma RA com 9% dos aptos do DF mas só 6% dos votos válidos para Governador tem peso 6%, não 9%. Para decisão estratégica de campanha, o que importa é onde a eleição **efetivamente** é decidida — peso eleitoral é o indicador correto.

(O share de aptos, lembrando, é o que entra no denominador da Performance — porque a Performance mede potencial relativo, não decisão efetiva.)

#### Aplicação

Cruzando peso × margem, identifica-se o que poderia se chamar de **"onde a eleição é decidida"**: RAs grandes (alto peso) e disputadas (margem pequena). Esse cruzamento foi a fundação da antiga "Visão Cargo" do produto e hoje vive como duas colunas adjacentes na tabela de Campo político.

### 5.5 Força do campo

A Força do campo é a **Performance aplicada ao campo político**, não ao candidato individual. Para um campo P (Progressista, Moderado, Liberal/Conservador) numa RA R e cargo Q:

```
força_campo(P, R, Q) = (votos_P_R_Q / total_P_Q) / (aptos_R / aptos_DF)
```

Mesmo formato e mesma escala da Performance — exibida como `+X%` / `−X%`. Usa os **mesmos cortes ±15% / ±30%** para classificar a RA em forte / esperado / fraca para o campo.

#### Por que essa métrica

A Força do campo separa **"candidato forte"** de **"campo forte"**. Um candidato pode ter Performance +50% numa RA por dois motivos:

1. O campo dele inteiro vai bem ali — o candidato surfa essa onda.
2. O candidato especificamente performa, mesmo que o campo seja médio.

Saber qual dos dois está acontecendo muda totalmente a leitura estratégica. O cruzamento Performance × Força do campo gera as **cinco zonas estratégicas** descritas em Camada 4 (Reduto consolidado, Voto pessoal, Esperado, Espaço a conquistar, Sem espaço pelo campo).

#### Limitações

- **"Outros" como campo é especialmente frágil.** Por construção, "Outros" agrega candidatos heterogêneos de siglas pequenas. A força do campo "Outros" tende a ter pouco significado estratégico e raramente entra na leitura.
- **Soma das forças dos quatro campos pode ser toda negativa.** Em RAs com alta abstenção, o numerador agregado de cada campo é proporcionalmente menor que o denominador (aptos), e os quatro idx podem ficar simultaneamente negativos. Isso não é erro — é reflexo direto do baixo comparecimento da RA. Tratamento atual: candidato a tooltip explicativo na interface; o leitor que entende a métrica reconhece o sinal.

### 5.6 Resumo das relações

```
Performance      → onde o candidato está acima/abaixo do tamanho do território
Spread/perfil      → que tipo de campanha o candidato faz (Distribuído, Híbrido, Concentrado)
Domínio          → fatia de mercado bruta (% do cargo)
Margem           → competitividade local
Peso eleitoral   → onde a eleição é decidida
Força do campo   → onda em que o candidato surfa (ou não)
```

Performance e Força do campo compartilham a mesma forma matemática — diferem apenas no agregado (candidato individual vs. soma do campo). Domínio e Peso são fatias absolutas (do cargo na RA, da RA no cargo). Margem é a única que olha para a estrutura competitiva da RA, não para o candidato.

A leitura estratégica de Estrategos depende da combinação dessas métricas — nenhuma sozinha responde tudo.

---

## 6. Camada 4 — Cruzamentos estratégicos

Camadas 2 e 3 descrevem cada RA isoladamente. Camada 4 é o salto da **descrição** para a **orientação tática** — cruza duas métricas para responder *o que fazer naquela RA*. Três cruzamentos compõem o núcleo estratégico de Estrategos:

1. **Estratégia** — Performance × Força do campo (5 zonas)
2. **Reposicionamento** — candidato origem × candidato referência (5 zonas)
3. **Aliança eleitoral** — candidato A × candidato B (4 quadrantes)

Estratégia e Aliança usam **±15% como ponto de corte** — o mesmo limite que separa "Base forte" de "Esperado" na escala da Performance. Reposicionamento usa um corte mais permissivo (Performance ≥ 0%, ratio ≥ 1,0); a justificativa está em §6.2.

### 6.1 Estratégia: Performance × Força do campo (5 zonas)

A pergunta que responde: *o candidato é forte na RA por mérito próprio, ou porque o campo dele é forte ali? E onde o campo dele tem espaço que ele ainda não ocupou?*

| Zona | Performance | Força do campo | Leitura tática |
|---|---|---|---|
| **Reduto consolidado** | ≥ +15% | ≥ +15% | Candidato e campo fortes — território a defender com prioridade |
| **Voto pessoal** | ≥ +15% | < +15% | Sucesso individual em terreno neutro/hostil — vulnerável, depende do candidato |
| **Esperado** | −15% a +15% | qualquer | Território neutro — baixa prioridade tática |
| **Espaço a conquistar** | < −15% | ≥ +15% | Campo já ganhou ali, candidato não — oportunidade clara de captura |
| **Sem espaço pelo campo** | < −15% | < +15% | Território hostil estrutural — não atirar |

#### Como ler cada zona

- **Reduto consolidado** combina força pessoal e força do campo — base afetiva e ideológica caminham juntas. É a zona de defesa prioritária, onde queda significa perda dupla (de voto pessoal e de identidade do campo).
- **Voto pessoal** sinaliza captura atípica. O candidato performa onde o campo dele não ganha — bom indicador de capacidade pessoal, mas alerta de fragilidade: o voto pode evaporar se o candidato sair de cena ou se a campanha perder tração.
- **Esperado** ocupa a banda central. O candidato performa próximo ao tamanho da RA, e o campo também. Não há informação tática diferencial — investir aqui rende proporcional ao esforço, sem alavancagem.
- **Espaço a conquistar** é a zona de oportunidade mais informativa. O campo do candidato já mostrou que ganha ali (Força do campo ≥ +15%), mas o candidato específico não converteu — há demanda latente que outro candidato do bloco capturou e ele não.
- **Sem espaço pelo campo** é território hostil em duas camadas: nem o candidato, nem o bloco dele performam ali. Investir contra o vento custa caro e rende pouco; a recomendação é ignorar.

### 6.2 Reposicionamento: origem × referência (5 zonas)

Aplica-se quando um candidato muda de cargo (Distrital → Federal, p. ex.) e quer entender quanto pode herdar de uma **referência** — outro candidato do mesmo campo que disputou o cargo destino numa eleição anterior.

O cruzamento é entre a **Performance do candidato no cargo origem** (em 2022) e a **Performance da referência no cargo destino** (também em 2022, ou ciclo histórico relevante). As cinco zonas:

| Zona | Origem forte? | Referência forte? | Volume na RA |
|---|---|---|---|
| **Base compartilhada** | sim (Performance ≥ 0%) | sim (Performance ≥ 0%) | — |
| **Voto pessoal** | sim | não | — |
| **Espaço a conquistar** | não | sim | — |
| **Terreno aberto** | não | não | aptos ≥ mediana |
| **Volume baixo** | não | não | aptos < mediana |

A última distinção (Terreno aberto vs. Volume baixo) usa a **mediana dos aptos entre as RAs em análise** como tiebreaker. RAs sem força de origem nem de referência se dividem em duas: as que ainda têm eleitorado relevante (terreno disputável onde a campanha pode investir do zero) e as pequenas demais para justificar prioridade.

#### Por que o corte aqui é Performance ≥ 0% (e não ≥ +15%)

Reposicionamento já cruza **duas dimensões** (origem e referência). Exigir Performance ≥ +15% em ambas tornaria a zona "Base compartilhada" muito restrita — pouquíssimas RAs satisfariam o duplo critério, e o diagnóstico perderia poder informativo. O corte em 0% é pragmático: pega RAs onde o candidato e a referência performaram **acima da proporção esperada pelo tamanho do território**, mesmo que apenas marginalmente. Isso preserva uma leitura mais ampla e útil para a decisão de mudança de cargo, ao custo de aceitar uma fronteira mais frouxa.

#### Vocabulário compartilhado com Estratégia

Duas zonas têm o mesmo nome em Estratégia e em Reposicionamento, com mesmo significado conceitual: **Voto pessoal** (força individual em território onde o agregado é fraco) e **Espaço a conquistar** (agregado favorável que o foco da análise não capturou). A consistência de vocabulário entre os dois cruzamentos é deliberada — ajuda o usuário a transferir intuição de um contexto ao outro.

#### Limitação central

O Reposicionamento depende da **escolha da referência**. Uma referência mal escolhida (candidato que não é análogo, ou cuja eleição teve dinâmica atípica) compromete todo o diagnóstico. A escolha é editorial e deve ser justificada caso a caso — não é detectada automaticamente pelo painel.

### 6.3 Aliança eleitoral: quadrantes (Comparar com…)

Aplica-se quando se compara dois candidatos para avaliar viabilidade de aliança — onde os dois se sobrepõem, onde um agrega o outro, onde há terreno aberto.

O cruzamento é entre **Performance do candidato A** e **Performance do candidato B** na mesma RA × cargo (ou cargos compatíveis, em caso de aliança cross-cargo / dobradinha). Considera-se "forte" qualquer Performance ≥ +15% (Reduto + Base forte). Os quatro quadrantes:

| Padrão | A forte? | B forte? | Leitura |
|---|---|---|---|
| **Sobreposição** | sim | sim | Ambos têm reduto ali — sobreposição de bases, eficiência baixa |
| **A agrega** | sim | não | A traz sua base; aliança soma território |
| **B agrega** | não | sim | B traz sua base; aliança soma território |
| **Aberto** | não | não | Território não amarrado por nenhum — campo neutro de captura conjunta |

#### Por que quadrantes e não correlação

A primeira versão dessa análise usou correlação de Pearson (r) entre as Performances dos dois candidatos como métrica de complementaridade. **Foi rejeitada para o DF.** Razões:

1. **N pequeno.** Apenas 28 RAs com cobertura TSE. Coeficientes de correlação com N tão baixo são estatisticamente instáveis — pequenas variações em uma RA mudam r significativamente.
2. **Outliers dominam.** Plano Piloto e Ceilândia (RAs grandes e atípicas) tendem a determinar o sinal e a magnitude do r. A correlação acaba descrevendo essas duas RAs, não o comportamento conjunto dos candidatos.
3. **Perda da leitura territorial.** Um r = 0,3 não diz onde a aliança agrega. Quadrantes preservam essa leitura — quem olha vê *quais RAs* caem em "A agrega", não só "há agregação fraca em média".

A escolha por quadrantes categóricos é coerente com o princípio de auditabilidade (§2.3): cada RA fica visível em uma zona específica, e a interpretação é local, não agregada num número que esconde a heterogeneidade.

#### Aplicação cross-cargo

A análise de aliança suporta dobradinhas (Federal × Distrital, Senador × Federal, etc.) do mesmo campo. O cruzamento usa a Performance de cada candidato em seu cargo respectivo na mesma RA. A leitura é a mesma — quadrantes idênticos —, com a ressalva de que cargos diferentes têm dinâmicas diferentes (proporcional vs. majoritário) e a sobreposição de redutos pode significar coisas distintas.

### 6.4 Os cortes nos cruzamentos

**Estratégia e Aliança usam ±15% como fronteira entre forte e fraco** — o mesmo limite que separa Base forte de Esperado na escala da Performance. Manter o corte estável entre esses dois cruzamentos é deliberado: o usuário aprende uma fronteira (+15%) e ela mantém significado consistente nesses contextos.

**Reposicionamento, por outro lado, usa Performance ≥ 0% como corte de "forte"** — justificado em §6.2 pela natureza do duplo cruzamento (origem × referência), que ficaria restritivo demais com o limite ±15%.

A inconsistência é assumida e tem custo cognitivo: "forte" significa coisas levemente diferentes em contextos distintos do produto. A alternativa — alinhar Reposicionamento ao ±15% também — está em aberto como decisão a revisitar; nesta versão, a leitura mais ampla foi privilegiada sobre a uniformidade absoluta do vocabulário.

### 6.5 Limitações conhecidas

1. **Cruzamentos são descritivos.** Mostram o estado atual do território conforme uma fotografia eleitoral. Não predizem se a configuração se mantém em 2026.
2. **Efeito de fronteira.** Uma RA com Performance +14,9% e outra com +15,1% caem em zonas diferentes. A leitura discreta esconde a continuidade do dado. Esse custo é aceito em nome da clareza categórica; a tabela completa com o número contínuo permanece visível.
3. **Reposicionamento depende da referência.** Discutido em §6.2.
4. **Aliança ignora dimensões não-territoriais.** Lealdade política, alinhamento ideológico, capacidade real de transferência de voto, química pessoal entre candidatos — nada disso entra. O cruzamento responde apenas onde há sobreposição/complementaridade *territorial*. A decisão final exige leitura política externa.
5. **"Outros" como campo é frágil em todos os cruzamentos.** Já discutido em §5.5; vale lembrar que análises envolvendo Força do campo ou Aliança onde um dos candidatos cai em "Outros" devem ser lidas com cautela.

---

## 7. Camada 5 — Achados estruturais do DF

*[a escrever]*

---

## 8. Camada 6 — Projeção 2026

*[a escrever]*

---

## 9. Limitações conhecidas e decisões pendentes

*[a escrever]*

---

## 10. Glossário técnico

*[a escrever]*
