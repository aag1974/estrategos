# Metodologia · Estrategos

Documento técnico de referência sobre o método analítico subjacente ao painel **Estrategos** — solução de Inteligência Política da Opinião Informação Estratégica, aplicada às eleições do Distrito Federal em 2026.

Escrito como **fonte da verdade técnica**, defensável diante de um par crítico (acadêmico ou outro consultor). Cada camada explicita o **que é**, **por que essa escolha** foi feita (e não outra), as **premissas embutidas** e as **limitações conhecidas**.

Atualizado em **abr/2026**.

---

## Sumário

1. [Resumo executivo](#1-resumo-executivo)
2. [Premissas e escopo](#2-premissas-e-escopo)
3. [Camada 1 — Fontes e unidade de análise](#3-camada-1--fontes-e-unidade-de-análise)
4. [Camada 2 — Métrica central: sobre-índice](#4-camada-2--métrica-central-sobre-índice)
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
- **Não captura comportamento individual.** A unidade mínima é a RA. Voto secreto e o caráter ecológico do dado agregado impedem inferência sobre eleitores específicos (falácia ecológica).
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

*[a escrever]*

---

## 4. Camada 2 — Métrica central: sobre-índice

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
