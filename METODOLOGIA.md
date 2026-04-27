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

O indicador central é o **sobre-índice** — apresentado como **Performance** na interface — que mede o quanto cada RA entrega de votos a um candidato em relação ao que seria proporcional ao tamanho do seu eleitorado. Sobre essa métrica simples e auditável se constroem todas as derivações: tipologia de candidato, força do campo, zonas estratégicas, análises de aliança e reposicionamento.

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

*[a escrever]*

---

## 5. Camada 3 — Métricas derivadas

*[a escrever]*

---

## 6. Camada 4 — Cruzamentos estratégicos

*[a escrever]*

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
