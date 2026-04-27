# Rascunho — Conteúdo do modal "Sobre o Estrategos"

Drafts user-facing das abas do modal de metodologia, para substituir o conteúdo
atual de `index.html` (que descreve o SPE composto aposentado em abr/2026).

**Estrutura:** 5 abas, espelhando a lógica do produto.
**Tom:** sóbrio mas didático, parágrafos curtos, um exemplo concreto por aba.

**Estado:**
- Abas 1, 2, 3 — **aprovadas**, prontas para injeção no HTML.
- Abas 4, 5 — **a escrever**.
- Após escrever as 5: substituir conteúdo do modal em `index.html` e reativar
  o link "Sobre o Estrategos" comentado em `index.html` (commit `769ad8f`).

---

## Aba 1 — Visão geral *(aprovada)*

**O que é Estrategos**

Estrategos é uma ferramenta de inteligência eleitoral aplicada ao Distrito Federal. Cruza dados socioeconômicos da PDAD/IPEDF com resultados eleitorais do TSE para gerar uma leitura territorial estratégica das 33 Regiões Administrativas, organizada por cargo e por campo político.

A pergunta central que ele responde é prática: **onde cada candidato performa acima ou abaixo do que seu tamanho relativo no território sugeriria — e o que isso significa estrategicamente para uma campanha em 2026.**

**Para que serve**

O painel organiza o território para apoiar decisões táticas — onde concentrar recursos, onde defender, onde conquistar, onde não atirar. Cada métrica pode ser reconstruída a partir das fontes públicas: nada é caixa-preta.

**O que ele não faz**

- **Não prevê resultados eleitorais.** Projeções existem, mas são cenários condicionais sobre uma referência escolhida — não predição estatística.
- **Não captura comportamento individual.** A unidade mínima é a RA. Nenhuma leitura sobre eleitores específicos decorre dos dados.
- **Não substitui pesquisa qualitativa.** Mostra onde e quanto, não responde por quê.
- **Não pondera os campos políticos por mérito ideológico.** Progressista, Moderado, Liberal/Conservador e Outros são classificações descritivas.

**Princípios**

A metodologia segue três princípios firmes: **auditabilidade** (cada número é reconstrutível das fontes públicas), **atomicidade** (cada métrica mede uma coisa só, com escala interpretável — sem índices compostos com pesos arbitrários) e **separação dado/interpretação** (o painel mostra o dado; a leitura editorial é apresentada como tal).

---

## Aba 2 — As bases *(aprovada)*

**As fontes**

Estrategos cruza duas fontes oficiais públicas.

**PDAD 2021 (IPEDF)** — pesquisa socioeconômica do governo do DF, realizada em 2021 com cerca de 83 mil moradores entrevistados em todas as 33 RAs. Entrega renda per capita, classe social, escolaridade, ocupação (servidor federal, distrital, privado), origem migratória e indicadores de vulnerabilidade. Dados representativos por RA.

**TSE 2022** — Tribunal Superior Eleitoral, dois conjuntos. O cadastro eleitoral traz o eleitorado registrado por zona, com perfil etário, gênero e escolaridade. O arquivo de votação por seção do 1º turno de 2022 permite calcular votos por candidato em cada RA.

**A unidade: a Região Administrativa**

Toda análise opera no nível da RA — pequena o bastante para preservar identidade política local, grande o bastante para evitar ruído amostral. As 33 RAs do DF coincidem com a divisão administrativa oficial e a desagregação direta da PDAD.

**Cobertura eleitoral parcial**

O TSE não opera com RAs — opera com zonas eleitorais. A correspondência foi construída por mapeamento de locais de votação. **28 das 33 RAs** têm cobertura eleitoral direta. As outras cinco — Park Way, SIA, Fercal, Sol Nascente/Pôr do Sol e Arniqueira — não têm zona própria; seus eleitores votam em zonas das RAs vizinhas e os votos não são desagregáveis com precisão. Essas RAs continuam nas leituras socioeconômicas (PDAD funciona normalmente) mas são filtradas das tabelas eleitorais, com nota de rodapé explicando.

A escolha por **filtrar em vez de estimar** é deliberada: estimativas por vizinhança ou regressão introduziriam incerteza sem ganho real de informação.

---

## Aba 3 — Como ler o painel *(aprovada)*

**A leitura central: Performance**

O indicador-chave do produto é a **Performance** — quanto cada região entrega de voto a um candidato comparado ao que seria esperado pelo seu tamanho relativo no eleitorado do DF.

**Exemplo concreto.** Plano Piloto concentra cerca de 9% do eleitorado do DF. Se um candidato recebe 18% dos seus votos de lá, está com **o dobro** do esperado pela proporção — Performance +100%. Plano Piloto é um reduto desse candidato.

A Performance é apresentada como `+X%` (acima do esperado) ou `−X%` (abaixo). Verde para positivo, vermelho para negativo, neutro na banda central.

**As cinco faixas**

| Faixa | Performance | Significa |
|---|---|---|
| **Reduto** | ≥ +30% | Muito acima do esperado |
| **Base forte** | +15% a +30% | Acima do esperado |
| **Esperado** | −15% a +15% | Proporcional ao tamanho |
| **Base fraca** | −15% a −30% | Abaixo do esperado |
| **Ausência** | ≤ −30% | Muito abaixo do esperado |

A Performance compara o candidato **consigo mesmo** ao longo das RAs — não compara entre candidatos.

**Perfil de votação**

A diferença entre a melhor e a pior Performance do candidato (o spread) classifica o tipo de campanha:

- **Distribuído** — performance parecida em todo lugar (cobertura ampla, típico de Governador).
- **Híbrido** — forte em algumas RAs, presença razoável nas demais (típico de Federal).
- **Concentrado** — hiperperformance em poucas RAs, ausência clara em outras (típico de Distrital).

**Força do campo**

Mesma escala da Performance, aplicada ao **campo político** do candidato na RA. Permite separar "candidato forte" de "campo forte" — o candidato pode performar porque o bloco dele inteiro vai bem ali, ou apesar de o bloco ir mal.

**Status — as cinco zonas estratégicas**

Cruzando Performance com Força do campo:

- **Reduto consolidado** — ambos fortes. Território a defender com prioridade.
- **Voto pessoal** — só o candidato é forte. Sucesso atípico, vulnerável.
- **Esperado** — território neutro.
- **Espaço a conquistar** — só o campo é forte. Oportunidade clara de captura.
- **Sem espaço pelo campo** — nenhum forte. Território hostil.

**Comparar com…**

Compara dois candidatos pela classificação conjunta de cada RA:

- **Sobreposição** — ambos fortes. Bases coincidem.
- **A agrega / B agrega** — só um é forte. Esse traz sua base para a aliança.
- **Aberto** — nenhum é forte. Território não amarrado.

---

## Aba 4 — Cenários e projeção *(a escrever)*

*Pendente. Cobrirá: modelo de multiplicação direta sobre referência (substituiu
o índice SPE composto aposentado), três cenários como bandas qualitativas,
patamar de eleição por cargo (Gov ~700k · Sen ~550k · Federal ~30k · Distrital
~18k), modo Reposicionamento quando referência é cargo distinto. Tom
prospectivo: deixar claro o que é arquitetura/desenho vs. estado vigente.*

---

## Aba 5 — O DF estrutural *(a escrever)*

*Pendente. Cobrirá: paradoxo da classe alta progressista no DF (inversão do
padrão nacional), vetor dual servidor federal + classe AB privada,
servidor distrital como fiel da majoritária, dualidade Eixo central × Periferia
como lente interpretativa. Tom: insight de produto, não método estatístico.*
