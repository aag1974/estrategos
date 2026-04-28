# Decisões consolidadas — Projeto Estrategos

Registro vivo das decisões aprovadas pelo cliente sobre vocabulário, UX, métricas e features.
Antes de mexer em qualquer item já decidido aqui, consultar este documento.
Antes de inventar item novo, propor e — se aprovado — registrar.

Atualizado em **abr/2026**.

---

## 1. Branding e identidade

| Item | Decisão | Notas |
|---|---|---|
| Nome do produto | **Estrategos** | Substituiu "SPE" em todos os textos visíveis em abr/2026. "SPE" continua só como nome de variável interna no código. |
| Empresa | **Opinião Informação Estratégica** | Logo embarcada como base64 no HTML (não depende de URL externa) |
| Definição do produto | "Solução de Inteligência Política da Opinião Informação Estratégica" | Texto canônico do rodapé do print |

---

## 2. Vocabulário canônico (termos do produto)

| Termo | Significa | Não confundir com |
|---|---|---|
| **Performance** | Sobre-índice do candidato — quanto recebeu de voto comparado ao tamanho do eleitorado da RA. **+50%** = recebeu 50% mais que o esperado. | "Sobre-índice" é o nome **técnico interno** do mesmo conceito. No produto, sempre **Performance**. |
| **Patamar de eleição** | Volume de votos que candidatos individuais costumam atingir para serem eleitos. Gov ~700k · Sen ~550k · Federal/Distrital ~18k. | "Meta canônica" foi termo antigo descartado. |
| **Perfil de votação** | Como o voto se distribui pelo território: **Distribuído** / **Híbrido** / **Concentrado**. | "Tipologia" foi nome antigo descartado. "Capilar/Campo militante/Nicho" foram rótulos rejeitados. |
| **Força do campo** | Sobre-índice do campo político do candidato (Progressista/Moderado/Liberal-Cons.) na RA × cargo. Mesma escala da Performance. | NÃO usar "Performance do campo" nem "Sobre-índice do campo" — vira confusão com Performance do candidato. |
| **Votos do candidato** | Total de votos que o candidato recebeu na RA. | NÃO escrever só "Votos" — fica ambíguo (votos de quem? do candidato? da RA? do campo?). |
| **Status** | Coluna que classifica cada RA na tabela. Termo padronizado em **ambos** os módulos (Candidatos e Estratégia). | NÃO usar "Categoria" — mesmo conceito, palavra diferente vira ruído. Em Candidatos os valores são as 5 faixas de Performance (Reduto / Base forte / Esperado / Base fraca / Ausência). Em Estratégia são as 5 zonas estratégicas (Reduto consolidado / Voto pessoal / Esperado / Espaço a conquistar / Sem espaço pelo campo). |
| **Aliança eleitoral** | Termo guarda-chuva pra qualquer arranjo entre candidatos (mesmo cargo ou cross-cargo). | NÃO usar "coligação" — tem peso jurídico (proibida em proporcional desde 2017). |
| **Dobradinha** | Caso específico de aliança cross-cargo + mesmo campo (Federal × Distrital, Sen × Federal etc. do mesmo campo). | Termo coloquial brasileiro com sentido eleitoral preciso. |
| **Padrão** (na Comparar com…) | Classificação de cada RA pelo cruzamento de força dos dois candidatos: Sobreposição (ambos fortes) / A agrega / B agrega / Aberto (nenhum). | "Forte" = Reduto + Base forte (Performance ≥ +15%). |

### As 5 faixas de Performance (classificação descritiva por RA)

| Faixa | Performance | Cor |
|---|---|---|
| Reduto | ≥ +30% | verde forte (#A7F3C8 / #0B5A2E) |
| Base forte | +15% a +30% | verde claro (#E1F5EE / #085041) |
| **Esperado** | −15% a +15% | âmbar (#FEF3C7 / #B45309) |
| Base fraca | −15% a −30% | vermelho claro (#FCEBEB / #791F1F) |
| Ausência | ≤ −30% | vermelho forte (#FCA5A5 / #5A1010) |

Termos descartados para a faixa central: "Médio", "Média", "No esperado", "Intermediário", "Estável", "Neutro" (este último colidiria com "Outros" do campo político), "Proporcional", "Padrão". O canônico é **Esperado**.

### As 5 zonas estratégicas (Estratégia — cruzamento Performance × Força do campo)

| Zona | Performance | Força do campo | Cor |
|---|---|---|---|
| Reduto consolidado | ≥ +15% | ≥ +15% | #0B5A2E sobre #A7F3C8 |
| Voto pessoal | ≥ +15% | < +15% | #075985 sobre #E0F2FE |
| Esperado | −15% a +15% | qualquer | #B45309 sobre #FEF3C7 |
| Espaço a conquistar | < −15% | ≥ +15% | #9A3412 sobre #FFE4D6 |
| Sem espaço pelo campo | < −15% | < +15% | #5A1010 sobre #FCA5A5 |

### As 5 zonas do Reposicionamento (Diagnóstico — cruzamento candidato origem × candidato referência)

| Zona | Origem forte? | Referência forte? | Volume RA |
|---|---|---|---|
| Base compartilhada | sim | sim | — |
| Voto pessoal | sim | não | — |
| Espaço a conquistar | não | sim | — |
| Terreno aberto | não | não | acima da mediana |
| Volume baixo | não | não | abaixo da mediana |

Vocabulário compartilhado entre Estratégia e Diagnóstico (Voto pessoal, Espaço a conquistar) — mesmo significado conceitual.

---

## 3. Modelo de cinco campos políticos

Os candidatos são classificados em 4 campos:
- **Progressista**
- **Moderado** (inclui o "Centro" pragmático: MDB, União Brasil, PSD)
- **Liberal/Conservador**
- **Outros** (residual — partidos pequenos, perfis que não cabem nos 3 acima)

"Outros" mantém esse nome — não vira "Centro" (colide com Moderado) nem "Neutro" (perde precisão).

---

## 4. UX — regras de interface

### 4.1 Cliente final ≠ desenvolvedor
- O painel será entregue a clientes não-técnicos no futuro.
- Qualquer fluxo que exija terminal (rodar python, baixar JSON, etc.) precisa ser **opcional ou explicitamente para o consultor (Alexandre)**, não para o cliente.
- O servidor local (`servidor_diag.py`) torna o fluxo de gerar Word um clique único pro cliente.

### 4.2 Padronização visual
- Estilos seguem o template `Etapa1_Cliente_Secreto.docx`:
  - Heading 1: 16pt bold, cor #004C99 (azul)
  - Heading 2: 13pt bold, cor #747678 (cinza)
  - Heading 3: 12pt bold
  - Body: Calibri 11pt
- Captions ABNT: "Tabela N – ..." acima das tabelas; "Figura N – ..." abaixo das figuras

### 4.3 Notas de rodapé das tabelas

**Decisão revogada em abr/2026.** A regra anterior — filtrar Park Way, SIA, Fercal, Sol Nascente/Pôr do Sol e Arniqueira das tabelas eleitorais com nota de rodapé canônica — deixou de valer com a migração para o método de atribuição seção→RA por point-in-polygon (`fase1c_perfil_secao.py`). Todas as 33 RAs agora aparecem nas tabelas com dado eleitoral próprio. As notas de rodapé canônicas devem ser **removidas** das tabelas afetadas.

### 4.4 Ordem de candidatos no menu Candidatos
- Caixa de busca por nome/partido vem **antes** dos botões de filtro de cargo

### 4.5 Cards "3 regiões principais"
- Critério: ordenar por **Performance** desc (não por votos absolutos)
- Threshold mínimo: max(30 votos, 1% do total do candidato) — evita microRAs distorcerem
- Fallback: se o filtro deixar < 3, completa por votos absolutos

---

## 5. Estrutura do menu

```
TERRITÓRIO              (terracota)
  • População                        · PDAD 2021
  • Eleitorado                       · TSE 2022

CONTEXTO                (azul)
  • Campo político                   · TSE 2022
  • Candidatos                       · TSE 2022
  • Estratégia                       (Performance × Força do campo)

GEOPOLÍTICA             (verde)
  • Território
  • Candidato

RELATÓRIO               (âmbar — antigo grupo "Estratégia")
  • Projeções
  • Diagnóstico                      (em stand-by; será produto pago futuro)
```

Submenus de Geopolítica usam **`.nav-item`** (mesmo padrão dos outros), não `.nav-sub-item`.

---

## 6. Diagnóstico (em stand-by)

- Tipo Reposicionamento foi implementado (relatório Word de 6 capítulos via `gerar_relatorio_diag.py`).
- Tipos Estreante c/ref, Estreante s/ref e Reeleição **não foram implementados**.
- O módulo está em stand-by por decisão do cliente (abr/2026) — usuário expressou que pode estar fazendo "generalismo excessivo sem nexo prático" e prefere focar em painel + entrega leve antes.
- Diagnóstico será reposicionado como **produto pago futuro** ("Estratégia consultiva premium"). O painel atual gratuito e o PDF de duas páginas (em construção) serão lead magnets.

---

## 7. Geração de impressão (Geopolítica)

- Botão `🖨 Imprimir` na toolbar de Território e Candidato
- Layout A4 paisagem por padrão (cliente pode escolher retrato no diálogo)
- Cabeçalho com logo Opinião + título do módulo + data + filtros aplicados
- 3 colunas: ranking compacto · mapa · painel direito (RA selecionada / candidato)
- Rodapé: "Fontes: TSE 2022 · PDAD 2021. Instrumento gerado pelo painel **Estrategos** — solução de Inteligência Política da **Opinião Informação Estratégica**."

---

## 8. Fontes de dados (atribuição obrigatória)

| Fonte | O que entrega | Ano |
|---|---|---|
| **PDAD 2021** (IPEDF) | Perfil socioeconômico das RAs (renda, classe, ocupação, escolaridade, origem, idade) | 2021 |
| **TSE 2022** | Cadastro eleitoral (aptos, idade, gênero, escolaridade do eleitorado) e votação por seção (votos por candidato, campo, cargo, abstenção, margem) | 2022 |

Toda tabela e cabeçalho de variável traz a fonte/ano em pequeno discreto.

---

## 9. Como atualizar este documento

A cada decisão **aprovada pelo cliente**, adicionar entrada aqui no formato:

```
- [DATA] Decisão Y: contexto · alternativa rejeitada (se houver) · razão
```

Decisões em discussão **não** entram aqui — só após aprovação explícita.

Se algo neste documento estiver inconsistente com o painel, a fonte da verdade é o que está aqui (ou levanta-se a inconsistência para resolver).

---

## §X. Conglomerados socioeconômicos das RAs (4 grupos)

Classificação editorial das 33 RAs do DF em 4 grupos para uso no Playbook e dashboard. **Não é PED-DF/DIEESE oficial** — é organização própria da equipe Estrategos, fundamentada em homogeneidade socioeconômica que correlaciona com comportamento eleitoral.

| Sigla | Grupo | RAs |
|---|---|---|
| **BC** | Brasília Central | Plano Piloto, Jardim Botânico, Lago Norte, Lago Sul, Park Way, Sudoeste/Octogonal |
| **RM** | Regiões Maduras | Águas Claras, Candangolândia, Cruzeiro, Gama, Guará, Núcleo Bandeirante, Sobradinho, Sobradinho II, Taguatinga, Vicente Pires, SIA, Arniqueira |
| **RP** | Regiões Populares | Brazlândia, Ceilândia, Planaltina, Riacho Fundo, Riacho Fundo II, Samambaia, Santa Maria, São Sebastião |
| **PF** | Periferia em Formação | Fercal, Itapoã, Paranoá, Recanto das Emas, SCIA/Estrutural, Varjão, Sol Nascente/Pôr do Sol |

**Critério**: homogeneidade socioeconômica (renda + escolaridade + ocupação) que correlaciona com comportamento eleitoral (METODOLOGIA §7, r=+0,87 entre escolaridade e voto progressista).

**Fonte de verdade**: composição neste documento. `outputs_fase3/clusters_ra.csv` (k-means + PCA sobre 17 variáveis PDAD, gerado por `fase3_ipe.py`) é referência metodológica auxiliar — divergências entre k-means e a classificação editorial são esperadas e documentadas (SIA e Arniqueira foram classificadas editorialmente sobrepondo o k-means).

**Exceção editorial conhecida**: Paranoá (1957, vila operária histórica) está em PF pelo perfil socioeconômico (R$ 1.153 per capita, 9% classe AB, 15% superior) e não pela idade. Único caso onde temporalidade urbana cede pra perfil socioeconômico.
