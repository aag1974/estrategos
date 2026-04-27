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
9. [Limitações conhecidas](#9-limitações-conhecidas)
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
4. **Conservadorismo na inferência.** Quando o dado não existe ou é frágil, a opção é declarar a ausência, não estimar com técnicas que escondam a incerteza.

### 2.4 Universo coberto

| Dimensão | Cobertura |
|---|---|
| Geografia | Distrito Federal — 33 Regiões Administrativas, todas com cobertura via atribuição seção→RA por point-in-polygon |
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

#### Atribuição seção → RA via point-in-polygon

O TSE não opera com RAs — opera com **zonas eleitorais**. As zonas do DF foram desenhadas em outro momento histórico, e a correspondência zona × RA não é 1-para-1: várias zonas atendem mais de uma RA, e várias RAs (criadas posteriormente) não têm zona própria.

A solução metodológica adotada (em abr/2026, substituindo um método anterior por distribuição proporcional) é **atribuir cada seção eleitoral à RA via point-in-polygon**:

1. O TSE disponibiliza coordenadas geográficas (LAT/LON) de cada local de votação. Cada seção pertence a um local.
2. O governo do DF disponibiliza polígonos georreferenciados das 33 RAs (`Limite_RA_20190.json`, sem overlap entre polígonos).
3. Para cada seção, identificamos o ponto do seu local de votação e testamos contra os polígonos das RAs. Cada seção cai em **exatamente uma** RA.
4. O **perfil eleitoral por seção** (TSE 2022, faixa etária × gênero × escolaridade) é então agregado por RA pela atribuição PIP.
5. Para 10 seções com coordenadas inválidas (`-1, -1` no cadastro do TSE — todas em locais bem identificados como CEUB Águas Claras, Colégio Anchieta etc.), usa-se atribuição de fallback pelo nome do bairro.

**Resultado:** todas as **33 RAs do DF têm dado eleitoral próprio**. As 5 RAs antes consideradas "sem zona" (Park Way, SIA, Fercal, Sol Nascente/Pôr do Sol, Arniqueira) recebem agora seu perfil real, agregado a partir das seções cujos locais de votação caem nelas — independentemente de qual zona TSE atende essas seções.

#### Cross-check de integridade

O método é validado por igualdade de totais: a soma de `EL_total_aptos` agregada por RA deve bater **exatamente** com a soma de `QT_ELEITOR_SECAO` do TSE raw (eleitorado total do DF). Verificação automática no pipeline (`fase1c_perfil_secao.py`) — qualquer divergência interrompe a geração.

Para o DF em 2022, o total é **2.203.045 eleitores**, com diferença zero entre raw e agregado.

#### Por que esse método e não distribuição proporcional

O método anterior (distribuição proporcional do perfil agregado da zona entre as RAs ponderado pelo número de locais) introduzia um viés sistemático: várias RAs recebiam o mesmo `% superior`, `% jovem` etc. — porque o perfil é da zona, não da RA. Em zonas com forte heterogeneidade interna (zona 18 cobrindo Lago Sul + São Sebastião + Jardim Botânico, p. ex.), o resultado distorcia drasticamente RAs ricas (Lago Sul aparecia com 38% de superior em vez dos 73% reais) e simétricamente RAs pobres da mesma zona (SCIA aparecia com 43% em vez de 7%).

A atribuição por seção via PIP elimina esse vazamento: cada seção carrega o perfil dos seus eleitores e é atribuída à sua RA real, sem mistura.

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

1. **Granularidade fixa na RA, não abaixo.** Algumas RAs grandes (Ceilândia, Plano Piloto, Taguatinga) abrigam realidades socioeconômicas internas muito heterogêneas. A análise por RA mascara essa heterogeneidade. Subdivisão por bairro (NUCB, Águas Lindas, Sobradinho I × II, etc.) é tecnicamente possível na PDAD mas não no TSE — e a falta de simetria invalida o cruzamento. Mantemos a RA como teto comum.
2. **Limites das RAs no JSON podem estar levemente desatualizados em fronteiras.** O método PIP herda os polígonos do `Limite_RA_20190.json` como verdade. Pequenas divergências entre o polígono e a percepção administrativa atual (ex.: Granja do Torto, Taquari como parte de Lago Norte e não Plano Piloto) podem ocorrer. As reatribuições foram inspecionadas e refletem a partição oficial mais recente disponível.
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

1. **N pequeno.** Apenas 33 RAs no DF — N baixo torna coeficientes de correlação estatisticamente instáveis: pequenas variações em uma RA mudam r significativamente.
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

Camadas 2 a 4 descrevem o estado do território. Camada 5 olha para os **padrões que se repetem** — aquilo que o DF revela quando se cruza renda, escolaridade, ocupação e voto entre as RAs. Esses achados não são conjunturais (uma eleição específica) nem individuais (um candidato): descrevem como o eleitorado distrital se organiza estruturalmente.

A leitura aqui muda de tom. Em Camadas 2-4, a unidade é o candidato ou a RA específica. Em Camada 5, a unidade é o **DF como sistema** — e o que se ganha é uma chave de interpretação que se aplica a qualquer candidato que entre depois no painel.

### 7.1 Método correlacional

A ferramenta principal é o **coeficiente de correlação de Pearson (r)** entre variáveis socioeconômicas (PDAD) e variáveis eleitorais (TSE), agregando por RA.

```
r(X, Y) = covariância(X, Y) / (σ_X × σ_Y)
```

Onde X é uma variável socioeconômica da RA (ex.: % de classe A/B, % de servidor federal, % com ensino superior) e Y é uma variável eleitoral (ex.: % de voto para o campo progressista naquele cargo). O cálculo cobre as **33 RAs do DF**, todas com perfil eleitoral próprio após a migração para atribuição seção→RA por PIP (§3.2). Coeficientes calculados com base no TSE 2022 anteriores ao recalculo podem diferir levemente — ver pendência de revisão das correlações no backlog.

#### Por que Pearson

A escolha por Pearson tem três motivações:

1. **Direto e interpretável.** Um r entre −1 e +1 com sinal explícito comunica imediatamente sentido (positivo/negativo) e força (módulo). Métricas alternativas (Spearman, informação mútua) ou são equivalentes para os pares aproximadamente lineares observados, ou perdem leitura ("informação mútua = 0,12" não diz nada para o leitor não-técnico).
2. **Coerente com o tom do produto.** Os achados precisam virar afirmações editorialmente claras ("a renda alta no DF puxa para o progressista, ao contrário do padrão nacional"). Pearson sustenta esse tipo de afirmação sem precisar de aparato técnico adicional.
3. **Compatível com visualização.** Toda correlação de Pearson tem um scatter que a representa fielmente (28 pontos, uma reta de regressão). O painel pode renderizar o scatter quando o achado for central, e o leitor verifica olho-no-olho.

#### Como interpretar a magnitude

Os cortes convencionais para |r| (em módulo):

| |r| | Leitura |
|---|---|
| **< 0,3** | Sem padrão linear claro — variáveis aproximadamente independentes |
| **0,3 – 0,6** | Padrão moderado |
| **0,6 – 0,8** | Padrão forte |
| **> 0,8** | Padrão muito forte |

O sinal indica o sentido: positivo (variam juntas) ou negativo (variam inverso).

#### Limitações conhecidas do método

- **Linearidade pressuposta.** Pearson detecta apenas dependência linear. Relações em U, em S, ou com saturação podem ter |r| baixo mesmo sendo informativas. Inspeção visual do scatter mitiga isso parcialmente.
- **Sensível a outliers.** Já discutido em §6.3 (no contexto da Aliança). Plano Piloto, Lago Sul e Ceilândia tendem a influenciar fortemente os coeficientes — em alguns casos, removê-los altera o r de modo substantivo. Quando isso acontece, o achado merece ser apresentado com a ressalva.
- **N pequeno.** Vinte e oito pontos. Intervalos de confiança de Pearson para N=28 são amplos: um r = 0,5 tem IC95% que pode ir de ~0,15 a ~0,75. Magnitudes próximas dos cortes (p.ex. r = 0,32) devem ser lidas com cautela.
- **Inferência limitada ao território.** Como em §3.5, a correlação é em nível de RA — não autoriza concluir comportamento individual do eleitor.

### 7.2 Achado 1 — Paradoxo da classe alta progressista

No DF, **renda alta vota progressista** — o oposto do padrão nacional, onde classes mais altas tendem a votar conservador.

- **r ≈ +0,93** entre % com ensino superior na RA e voto progressista (todos os cargos agregados).
- **r ≈ +0,86** entre % de classe A/B na RA e voto progressista para Deputado Federal.

As RAs que sustentam essa correlação são Lago Sul, Plano Piloto, Sudoeste/Octogonal, Águas Claras e Jardim Botânico — as mais ricas e escolarizadas do DF — e simultaneamente as que mais entregam votos para o campo progressista no cargo Federal.

Esse padrão é estrutural, não conjuntural: aparece também em 2018 (com magnitude próxima) e em ciclos anteriores. Não é efeito Lula, não é efeito Bolsonaro — é traço do DF.

### 7.3 Achado 2 — Vetor dual

O paradoxo da classe alta progressista não tem **um único** mecanismo causal — tem **dois** vetores que se sobrepõem:

1. **Servidor federal.** A presença de servidores federais na RA correlaciona fortemente com voto progressista para cargos federais (**r ≈ +0,83** para Deputado Federal e Senador). A interpretação é direta: identidade ideológica de carreira pública, defesa do Estado, alinhamento histórico com pautas trabalhistas.
2. **Classe AB privada altamente escolarizada.** Mesmo onde o servidor federal **não** está concentrado, o voto progressista persiste, sustentado por escolaridade alta e perfil cosmopolita. A hipótese qualitativa — a confirmar empiricamente — é que Lago Sul ilustra esse caso: predomínio de renda alta privada com proporção comparativamente menor de servidor federal, mas voto progressista mantido.

Os dois vetores são distintos e se reforçam. O "eleitor rico" do DF, na verdade, **são dois eleitores** — e ambos votam progressista, contrariando o que renda alta significa em outras capitais brasileiras.

A separação dos dois vetores é importante porque tem implicação tática: uma campanha progressista que se ancora apenas em pauta de servidor federal perde Lago Sul; uma que se ancora apenas em pauta cosmopolita perde Plano Piloto. A leitura conjunta de PDAD (% servidor federal, % classe A/B, % superior) por RA permite ver onde cada vetor pesa mais.

### 7.4 Achado 3 — O cargo importa: servidor distrital como fiel da majoritária

A força da correlação servidor federal × progressista **cai com o cargo**:

- Federal e Senador: **r ≈ +0,83**
- Distrital: **r ≈ +0,43**

E o **servidor distrital** faz o movimento oposto. Sua presença correlaciona positivamente com o campo governista local:

- **r ≈ +0,61** entre % servidor distrital e voto liberal/conservador para Governador.
- **r ≈ +0,60** entre % servidor distrital e voto moderado para Senador.

A leitura: o servidor distrital depende da máquina pública local e tende a votar com quem governa o DF — independentemente do campo ideológico que esse governo represente. Em ciclos com governos progressistas, o servidor distrital migra para a moderação operacional do governo. Em ciclos com governos liberais/conservadores (como 2022), ele migra para o liberal/conservador.

A implicação metodológica: a mesma variável socioeconômica (% servidor) tem **direção de correlação diferente conforme o cargo e o tipo de servidor**. Análises que tratam "servidor público" como bloco único perdem essa estrutura. Estrategos separa servidor federal de servidor distrital exatamente por isso.

### 7.5 Insight estrutural — Eixo central × Periferia

Os três achados anteriores são correlacionais. O quarto é **interpretativo**: emerge do conjunto dos dados quando se olha para a geografia política do DF como um todo.

#### O eixo central como ringue ideológico

Cinco RAs concentram a maior parte do voto ideológico do DF — em qualquer direção:

**Plano Piloto · Lago Sul · Lago Norte · Sudoeste/Octogonal · Águas Claras · Jardim Botânico**

Essas RAs são simultaneamente o coração do voto progressista (achado 1) **e** o coração do voto liberal-conservador de elite (Lago Sul é base bolsonarista; Plano Piloto é base PSOL e PT). Candidatos extremos dos dois lados — Kicis (PL) e Erika Kokay (PT), Manzoni (PL Distrital) e Fábio Felix (PSOL Distrital) — disputam **as mesmas RAs**, com Performance alta nos mesmos territórios.

A leitura: o eixo central é onde **a política ideológica acontece**. Quem se elege por extremos (de qualquer lado) sustenta a base ali.

#### A periferia como política local não-ideológica

Brazlândia, SCIA/Estrutural, Recanto das Emas, Varjão, Itapoã, Paranoá — RAs grandes em eleitorado, baixas em escolaridade e renda — não seguem o eixo ideológico. Os candidatos que performam ali não são os ideológicos do eixo central; são candidatos com **base territorial específica**: pastor com igreja consolidada, sindicalista, vereador-virou-distrital, candidato com prestação direta (cesta básica, ambulância, vale-luz, mediação com administração regional).

A correlação % superior × voto progressista, que vale +0,93 quando se olha o DF inteiro, **cai a praticamente zero** se filtrar para a periferia. Lá não há padrão ideológico — há padrão de presença local.

#### Implicação metodológica

A dualidade Eixo × Periferia é a chave que evita interpretar errado o DF. Análises que extrapolam o padrão do eixo central para o DF inteiro (do tipo "no DF, a renda alta puxa para o progressista — então campanha progressista deve focar em renda alta") **erram a estratégia** se a campanha for para a periferia. A campanha da periferia é outra coisa — territorial, individual, não-ideológica.

Estrategos não codifica essa dualidade como métrica formal (não há um indicador "isto é eixo / isto é periferia"). Mas ela atravessa a leitura de tudo: as zonas estratégicas (Camada 4), as projeções (Camada 6), e a estrutura editorial dos relatórios. Funciona como uma **lente interpretativa** sobre os dados quantitativos.

### 7.6 Premissas e limitações

1. **Achados são correlacionais, não causais.** Que renda alta correlacione com voto progressista não significa que renda alta *causa* voto progressista. O mecanismo causal pode ser escolaridade, perfil ocupacional, identidade urbana cosmopolita ou um conjunto deles — Pearson não distingue.
2. **Inferência ecológica.** Repetindo a fronteira de §3.5: as correlações são entre variáveis das RAs, não entre características de eleitores individuais. "RAs ricas votam progressista" é diferente de "eleitores ricos votam progressista".
3. **Outliers influenciam fortemente.** Lago Sul pesa muito no r de classe A/B × progressista. Plano Piloto pesa em quase tudo. Achados centrais foram verificados removendo cada outlier para garantir robustez, mas a magnitude exata dos coeficientes é sensível.
4. **N = 28 limita precisão.** Para valores absolutos próximos dos cortes convencionais, intervalos de confiança são amplos. Achados muito fortes (|r| > 0,8) são robustos a essa limitação; achados moderados (|r| ≈ 0,4–0,6) precisam ser lidos com cautela.
5. **Eixo × Periferia é interpretação, não classificação formal.** A dualidade emerge da leitura conjunta dos achados — não há uma fronteira numérica fixa que separe RAs em uma categoria ou outra. A lista citada no §7.5 é uma simplificação editorial; alguns casos (Vicente Pires, Cruzeiro, Guará) ficam ambíguos e merecem leitura caso a caso.

---

## 8. Camada 6 — Projeção 2026

Camadas 2 a 5 olham para o passado: descrevem o território conforme se expressou em 2022, com seus padrões estruturais. Camada 6 olha para frente — propõe **cenários condicionais** sobre o que pode acontecer em 2026, dada uma escolha de referência.

A diferença tonal é importante: o que vem antes é **descritivo** (dados públicos auditáveis), o que vem aqui é **prospectivo** (cenários sob premissas declaradas). Por isso a fronteira entre as camadas é dura — projeção é apresentada com sinalização clara de que é projeção, não fotografia.

### 8.1 Princípio do modelo

A pergunta que a projeção responde é simples: *dado que escolhi um candidato de 2022 como referência (porque seu perfil é análogo ao do candidato em análise), e dado um cenário sobre como esse candidato cresce ou encolhe, quantos votos ele faria em cada RA em 2026?*

A resposta, em forma:

```
Votos_2026(RA) = Votos_referência_2022(RA) × cenário_multiplicador
```

A escolha por **multiplicação direta** sobre uma referência empírica é deliberada. Substituiu, em abr/2026, um modelo composto anterior (índice SPE) que combinava Afinidade × Conversão × Massa × Logística com pesos editoriais ponderados por cargo. Esse modelo composto foi aposentado por três motivos:

1. **Pesos arbitrários.** Os coeficientes que combinavam as quatro dimensões eram fixados editorialmente, não calibrados estatisticamente. O resultado era defensável apenas por construção interna — não por evidência.
2. **Cobertura furada.** "SPE não disponível" aparecia em metade das combinações cargo × campo, porque o modelo dependia de candidatos análogos em todas as dimensões — o que raramente se materializava.
3. **Sem ação prática.** O número composto agregado escondia o que estava por trás. Um SPE 8,2 não dizia se o candidato era forte por afinidade ou por logística — e a campanha não tem como agir num agregado.

A multiplicação direta sobre uma referência conhecida é mais auditável: o consultor escolhe a referência, sabe por que, e o cenário é apenas um ajuste sobre dados reais.

### 8.2 Os cenários

A arquitetura prevê **três cenários** sobre a multiplicação base, cobrindo uma banda de "menos do que a referência" a "mais do que a referência". Os nomes específicos dos cenários e os multiplicadores numéricos estão em definição — não há ainda vocabulário canônico fixado nem calibração estatística aplicada no painel.

A versão anterior do produto, baseada no índice SPE composto (aposentado em abr/2026), usava multiplicadores editoriais de **50% / 75% / 100%** como âncoras didáticas. Esses valores **não são** os do modelo atual: eram parte de uma arquitetura que foi descartada. A nova calibração é decisão pendente — depende de dados de 2018 com qualidade suficiente para gerar percentis empíricos por cargo × campo (p.ex.: pior decil / mediana / top decil dos eleitos).

Enquanto a calibração não estiver feita, qualquer cenário apresentado no painel deve ser entendido como **âncora didática**, não como estimativa estatística.

### 8.3 Toggles opcionais (ajustes sobre a multiplicação base)

Sobre o modelo base (multiplicação direta), dois ajustes opcionais foram desenhados — para serem ativados ou não pelo consultor, conforme o caso:

**Ajuste demográfico (PDAD).**
Quando há razão para acreditar que o candidato em análise tem afinidade demográfica diferente da referência (perfil socioeconômico distinto do eleitorado-alvo), o ajuste pondera a multiplicação pelo grau de compatibilidade entre o perfil PDAD da RA e o perfil teórico do eleitor-tipo do candidato. **Status atual:** modelo conceitual definido; calibração e implementação em aberto. Substituiria a antiga "Afinidade" do SPE.

**Ajuste por tendência histórica 2018→2022.**
Quando o campo do candidato cresceu ou encolheu sistematicamente entre os dois ciclos numa RA específica, o ajuste aplica essa tendência ao multiplicador local. Captura a noção de que algumas RAs estão num movimento direcional que provavelmente continua. **Status atual:** mesmo do ajuste anterior — definido conceitualmente, calibração pendente.

Ambos os toggles são **opcionais e desligados por padrão**. O modelo base funciona sem eles; eles são refinamentos para casos específicos.

### 8.4 Patamar de eleição

A projeção por RA não responde sozinha à pergunta estratégica final: *isso é suficiente para eleger?* Para responder isso é preciso comparar o total de votos projetado com um **patamar de eleição** — o volume de votos que candidatos individuais costumam atingir para serem eleitos no cargo.

O patamar varia significativamente por cargo:

| Cargo | Tipo de eleição | Patamar aproximado |
|---|---|---|
| **Governador** | Majoritária (vaga única) | ~**700 mil** votos |
| **Senador** | Majoritária (1 a 2 vagas) | ~**550 mil** votos |
| **Deputado Federal** | Proporcional (8 vagas no DF) | ~**30 mil** votos |
| **Deputado Distrital** | Proporcional (24 vagas no DF) | ~**18 mil** votos |

Federal e Distrital têm patamares **distintos**, ainda que ambos sejam proporcionais — o quociente eleitoral é diferente porque o número de cadeiras e o tamanho do eleitorado total do cargo são diferentes. Os valores são aproximações calibradas pela observação dos eleitos de 2022, não pisos formais — eleitos podem entrar abaixo via legenda e sobras, e candidatos fortes podem ultrapassar substancialmente. Valores são recalculados a partir dos dados oficiais a cada ciclo.

A projeção apresenta o total de votos lado a lado com a faixa de patamar — a leitura "cobertura: X% do patamar" é o que conecta a leitura territorial à decisão estratégica.

### 8.5 Modo Reposicionamento

Quando a referência selecionada está em **cargo diferente** do candidato em análise (Distrital → Federal, p. ex.), a leitura prevista pela arquitetura é o **modo Reposicionamento**. Isso muda duas coisas:

1. A leitura territorial passa a usar as **cinco zonas do Reposicionamento** (Camada 4, §6.2) em vez das cinco zonas estratégicas — porque a pergunta deixa de ser "onde meu campo é forte" e passa a ser "quanto da base da referência eu posso herdar".
2. Os cenários são reformulados para refletir grau de transferência:
   - **Substituto orgânico** — herda apenas onde origem e referência se sobrepõem (Base compartilhada).
   - **Com ponte parcial** — herda também o Espaço a conquistar onde a referência foi forte.
   - **Com ponte construída** — herda parte do Terreno aberto onde há volume relevante.

A intenção arquitetural é que a ativação seja automática (detectada pela diferença de cargo entre análise e referência), sem configuração manual do usuário. O grau de implementação atual no painel está em revisão e pode ser parcial — esta seção descreve o desenho-alvo, não necessariamente o estado vigente.

### 8.6 Premissas e limitações

1. **A projeção depende inteiramente da referência.** Uma referência mal escolhida gera projeção mal calibrada. A escolha é editorial, não detectada — exige conhecimento sobre análogos perfeitos e quase-perfeitos.
2. **Multiplicadores ainda são editoriais.** A calibração estatística (percentis empíricos) é pendente. Hoje os cenários ancoram com 50%, 75%, 100% como pontos didáticos.
3. **Toggles em construção.** Os ajustes demográfico e histórico estão definidos conceitualmente mas não implementados/calibrados. O modelo base hoje é a multiplicação direta crua.
4. **Não é predição estatística.** Não há intervalos de confiança formais. Os cenários são bandas qualitativas (conservador / esperado / otimista) com calibração editorial. Quem ler precisa saber disso — a apresentação é deliberada para não dar a impressão de inferência probabilística.
5. **Não captura ruptura estrutural.** Se entre 2022 e 2026 ocorrer evento que mude estruturalmente o eleitorado (mudança radical no panorama nacional, crise local grave, candidato carismático fora do espectro mapeado), a projeção subjacente ao painel **não tem como ajustar automaticamente**. O consultor precisa fazer essa leitura externamente.
6. **Performance × patamar é leitura, não receita.** Cobertura de 80% do patamar não significa "vai perder por 20%". Significa "se o cenário se confirmar e o patamar histórico for o teto efetivo, faltam 20% pra entrar na faixa de eleitos típicos". A interpretação editorial fecha o que a aritmética abre.

---

## 9. Limitações conhecidas

Esta seção sintetiza as **limitações estruturais** que apareceram ao longo das seis camadas — fragilidades inerentes ao método que vão continuar existindo mesmo depois que decisões pendentes forem resolvidas. Não substitui a leitura das limitações específicas em cada camada; sumariza-as em categorias para facilitar a leitura crítica do produto.

Decisões em aberto (cortes a calibrar, toggles a implementar, vocabulário a alinhar) não estão aqui — vivem no backlog (ver ponteiro ao final).

### 9.1 Inferência ecológica (corte de raiz)

Toda análise é em nível de RA, não de eleitor. Correlações, Performance, Força do campo, zonas estratégicas — tudo descreve comportamento agregado territorial. Conclusões sobre eleitores individuais (*"o eleitor de classe AB do DF vota progressista"*) não decorrem dos dados — exigem outro tipo de pesquisa (survey, focal). Discutido em §3.5, §5.5 e §7.6.

### 9.2 N pequeno (33 RAs)

A análise correlacional opera com 33 pontos. Para magnitudes próximas dos cortes convencionais (|r| ≈ 0,3–0,5), os intervalos de confiança são amplos. Outliers — Plano Piloto, Lago Sul, Ceilândia — puxam fortemente os coeficientes. Achados muito fortes (|r| > 0,8) são robustos; achados moderados merecem cautela. Discutido em §6.3, §7.1 e §7.6.

### 9.3 Limites das RAs em fronteiras

A atribuição seção → RA depende dos polígonos do `Limite_RA_20190.json`. Em regiões de fronteira ou em setores que historicamente eram parte de outra RA mas foram absorvidos por reorganização administrativa (Granja do Torto, Taquari), o ponto de votação cai onde o polígono diz, não onde a percepção tradicional sugere. Pequenas divergências dessa natureza são esperadas e refletem a partição oficial vigente. Discutido em §3.2 e §3.5.

### 9.4 Linearidade e simetria dos cortes

Duas suposições embutidas no aparato quantitativo:

- **Linearidade do Pearson.** Detecta apenas dependência linear entre variáveis. Relações em U, em S ou com saturação podem ter |r| baixo sem serem informativas. Inspeção visual do scatter mitiga, mas não elimina.
- **Simetria dos cortes da Performance.** ±15% e ±30% tratam ganhar e perder na mesma magnitude como equivalentes. Estrategicamente, +30% e −30% representam situações qualitativamente distintas (força vs. vulnerabilidade); o método não pondera essa assimetria — é a leitura editorial que faz isso.

### 9.5 Método descritivo, não causal nem preditivo

- **Performance descreve onde, não por quê.** Por que uma RA é reduto de um candidato, ou por que uma RA é progressista — exige interpretação que não decorre dos números.
- **Correlações apontam padrões, não mecanismos.** Que renda alta correlacione com voto progressista não significa que renda alta cause voto progressista (§7.6).
- **Projeções são cenários condicionais.** Não há intervalos de confiança formais — são bandas qualitativas calibradas editorialmente. Quem ler precisa saber disso (§8.6).

### 9.6 Dependência de escolhas editoriais

Várias decisões metodológicas são tomadas pelo consultor, não por algoritmo:

- Classificação de cada candidato em campo político (§3.3) — com ajuste manual em casos limítrofes.
- Escolha da referência na projeção (§8.6) — uma má escolha invalida o diagnóstico inteiro.
- Cortes (±15%, ±30%, 100pp/200pp, 0% no Reposicionamento) — fixados editorialmente, não calibrados estatisticamente.
- Lista de RAs do "eixo central" e da "periferia" (§7.5) — interpretação editorial, não classificação formal.

Essas escolhas são **auditáveis** (ficam visíveis no produto e podem ser questionadas) mas não automatizadas. O método **depende do consultor**.

### 9.7 Aliança ignora dimensões não-territoriais

A análise de aliança eleitoral (§6.3) responde apenas onde há sobreposição/complementaridade *territorial*. Lealdade política, alinhamento ideológico, capacidade real de transferência de voto, química pessoal entre candidatos — nada disso entra. Decisão de aliança no mundo real exige leitura política externa que o painel não substitui.

### 9.8 Sensibilidade ao período-base (TSE 2022)

A análise toma 2022 como fotografia. Se entre 2022 e 2026 ocorrer ruptura estrutural — mudança radical no panorama nacional, crise local grave, candidato carismático fora do espectro mapeado — o método não tem como detectar nem ajustar. A leitura de ruptura precisa ser feita externamente pelo consultor, e a interpretação dos números do painel deve ser temperada por essa leitura.

### 9.9 "Outros" como campo é frágil em todos os cruzamentos

A categoria "Outros" (§3.3) é residual por construção — agrega candidatos heterogêneos de siglas pequenas. Em cruzamentos que envolvem Força do campo (Camada 4), análises de aliança ou projeções pelo lado do campo, qualquer presença de "Outros" exige cautela na leitura. Não é erro do método — é honestidade sobre o que a categoria representa.

---

**Decisões pendentes que afetam o método** — calibração estatística dos cortes, implementação dos toggles de projeção, alinhamento de vocabulário entre documentos — vivem no backlog do produto. Ver `STORYTELLING_SPEC.md` §5 "Pendências em aberto".

---

## 10. Glossário técnico

Definições compactas dos termos técnicos usados nesta metodologia. Para o vocabulário canônico de produto e UX (rótulos da interface, regras editoriais), ver `DECISOES_PROJETO.md`.

### Métricas

**Sobre-índice (Performance)**
`(votos_RA / total_cand) / (aptos_RA / aptos_DF)`. Razão entre a fração dos votos do candidato que vieram de uma RA e a fração do eleitorado do DF que mora nela. Apresentado como delta `+X% / −X%` (= ratio − 1, em percentual). Camada 2.

**Spread**
`max(Performance) − min(Performance)` para o candidato. Mede a amplitude da Performance entre RAs. Em pontos percentuais. Camada 3.

**Domínio do campo**
`votos_campo_RA / votos_totais_cargo_RA`. Fatia de mercado bruta do campo na RA × cargo. Camada 3.

**Margem 1º–2º**
Diferença em pontos percentuais entre o 1º e o 2º colocado do cargo na RA. Mede competitividade local. Camada 3.

**Peso eleitoral da RA**
`votos_totais_cargo_RA / votos_totais_cargo_DF`. Fatia da decisão eleitoral total que a RA carrega. Camada 3.

**Força do campo**
Sobre-índice aplicado ao campo (não ao candidato individual). Mesma forma matemática e mesma escala da Performance, agregando todos os candidatos do campo. Camada 3.

**Coeficiente de correlação de Pearson (r)**
Mede dependência linear entre duas variáveis. Varia de −1 a +1; sinal indica sentido, módulo indica força. Cortes convencionais de leitura: |r| < 0,3 fraca, 0,3–0,6 moderada, 0,6–0,8 forte, > 0,8 muito forte. Camada 5.

### Categorizações

**5 faixas da Performance**
Reduto (≥ +30%) · Base forte (+15 a +30%) · Esperado (−15 a +15%) · Base fraca (−15 a −30%) · Ausência (≤ −30%). Aplicam-se ao candidato individual e — com a mesma escala — à Força do campo.

**Perfil de votação**
Classificação do candidato pelo spread: **Distribuído** (< 100pp) · **Híbrido** (100–200pp) · **Concentrado** (> 200pp). Diagnostica o tipo de campanha. Camada 3.

**5 zonas estratégicas (Estratégia)**
Cruzamento Performance × Força do campo, ambos com corte ±15%:
Reduto consolidado · Voto pessoal · Esperado · Espaço a conquistar · Sem espaço pelo campo. Camada 4.

**5 zonas do Reposicionamento**
Cruzamento Performance do candidato (cargo origem) × Performance da referência (cargo destino), com corte ≥ 0%:
Base compartilhada · Voto pessoal · Espaço a conquistar · Terreno aberto · Volume baixo. Última distinção via mediana de aptos das RAs em análise. Camada 4.

**4 quadrantes da Aliança eleitoral**
Cruzamento Performance candidato A × Performance candidato B, com corte ≥ +15% (Reduto + Base forte):
Sobreposição · A agrega · B agrega · Aberto. Camada 4.

### Conceitos do produto

**Patamar de eleição**
Volume de votos típico para se eleger no cargo, calibrado pela observação dos eleitos de 2022:
Governador ~700 mil · Senador ~550 mil · Deputado Federal ~30 mil · Deputado Distrital ~18 mil. Aproximações, não pisos formais. Camada 6.

**Aliança eleitoral**
Termo guarda-chuva para arranjos entre candidatos (mesmo cargo ou cross-cargo). Distinto de "coligação" (proibida em proporcional desde 2017). Camada 4.

**Dobradinha**
Caso específico de aliança cross-cargo com candidatos do mesmo campo (Federal × Distrital, Senador × Federal etc.). Camada 4.

**Eixo central × Periferia**
Insight estrutural do DF: Plano Piloto + Lago Sul + Lago Norte + Sudoeste/Octogonal + Águas Claras + Jardim Botânico = ringue ideológico (qualquer extremo se elege ali). Periferia (Brazlândia, SCIA, Recanto, Varjão, Itapoã, Paranoá) opera com lógica de política local não-ideológica. Não é classificação formal — é lente interpretativa. Camada 5.

### Fontes e unidades

**RA — Região Administrativa**
Unidade mínima de análise de Estrategos. O DF tem 33 RAs; todas com cobertura eleitoral via atribuição seção→RA por point-in-polygon (`Limite_RA_20190.json`). Camada 1.

**Zona eleitoral**
Unidade administrativa do TSE. Não coincide 1-para-1 com a RA — a correspondência é construída por mapeamento de locais de votação na Fase 1 do pipeline. Camada 1.

**Eleitor apto**
Eleitor registrado no cadastro TSE da zona/RA. Distinto de **comparecimento** (eleitores que efetivamente votaram). A Performance usa aptos no denominador; o Peso eleitoral usa votos efetivos. Camadas 2 e 3.

**PDAD (Pesquisa Distrital por Amostra de Domicílios)**
Levantamento socioeconômico oficial do DF, conduzido pelo IPEDF (ex-CODEPLAN). Edição 2021 com cobertura censitária por RA. Camada 1.

**Cargo**
Os quatro disputados no DF: Governador, Senador, Deputado Federal, Deputado Distrital. Camada 1.

**Campo político**
Classificação descritiva em 4 categorias: Progressista, Moderado, Liberal/Conservador, Outros (residual). Baseada em filiação partidária e padrão histórico. Camada 1.

---

## 10. Glossário técnico

*[a escrever]*
