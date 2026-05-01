# Rascunho — Documento de Estratégia de Campanha

PDF gerado a partir do menu **Estratégia** com base no candidato
selecionado. Não confundir com os relatórios atuais (Erika, Damares,
Reginaldo) — esse é um documento **novo**, focado em **estratégia
acionável** por zona.

**MVP:** Reeleição · Dep. Distrital · candidato com voto em 2022.

**Princípios editoriais:**
- Tom **descritivo + analítico** (mesma família dos PDFs Geopolítica)
- Cada página tem uma temática
- Cada página inclui **explicação conceitual** (didática) + **análise
  específica** do candidato
- Camada 1 = parte fixa do conteúdo (universal); Camada 2 = parte que
  varia com os números do candidato

**Padrão visual herdado:** A4 paisagem, classes do
`relatorio_ERIKA.html` (`.report`, `.hd`, `.kpi`, `.sec`, `.tbl-mini`,
`.st-badge`, etc.).

---

## Estrutura — 8 páginas

| # | Página | Propósito |
|---|---|---|
| **1** | Capa + Diagnóstico | Identificação do candidato + 4 KPIs + frase-tese |
| **2** | Conceitos centrais | Performance, Força do campo, 5 zonas, patamar — didático puro |
| **3** | Onde defender | Reduto consolidado + Voto pessoal — RAs, votos, ações |
| **4** | Onde crescer | Espaço a conquistar — RAs, estoque potencial, ações |
| **5** | Decisões periféricas | Esperado em RAs grandes + Sem espaço pelo campo |
| **6** | Quem é meu eleitor | Perfil PDAD agregado das RAs onde performa vs DF |
| **7** | Alocação + Síntese | % sugerido por zona + 4 achados-âncora |
| **8** | Apêndice — 33 RAs | Tabela completa do território como referência rápida |

---

## Página 1 — Capa + Diagnóstico

### Mockup (A4 paisagem · 277mm × 190mm útil)

```
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║  [LOGO]   ESTRATÉGIA DE CAMPANHA · DEP. DISTRITAL    27/04/2026   ║
║                                                                   ║
║           {NOME DO CANDIDATO}                                     ║
║           {Partido} · {Campo}    [Eleito]    {Total} votos        ║
║           Perfil: [{Distribuído|Híbrido|Concentrado}]             ║
║                                                                   ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║   ┌──────────────┬──────────────┬──────────────┬──────────────┐  ║
║   │ TOTAL VOTOS  │ PERFIL       │ PATAMAR      │ REDUTOS       │  ║
║   │              │              │ ELEIÇÃO      │              │  ║
║   │ {N}          │ {Tipo}       │ {±X%}        │ {N RAs}      │  ║
║   │ votos 2022   │ spread {N}pp │ vs 18k votos │ Reduto + V.P.│  ║
║   └──────────────┴──────────────┴──────────────┴──────────────┘  ║
║                                                                   ║
║   ▌ DIAGNÓSTICO                                                   ║
║   {Frase-tese 2-3 linhas, gerada da combinação                    ║
║    perfil × patamar × distribuição das zonas}                     ║
║                                                                   ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║   ▌ PÁGINAS DESTE DOCUMENTO                                       ║
║                                                                   ║
║     2. Conceitos centrais                                         ║
║        Performance · Força do campo · 5 zonas · Patamar           ║
║                                                                   ║
║     3. Onde defender (Reduto + Voto pessoal)                      ║
║     4. Onde crescer (Espaço a conquistar)                         ║
║     5. Decisões periféricas (Esperado + Sem espaço)               ║
║     6. Quem é meu eleitor (perfil PDAD)                           ║
║     7. Alocação de esforço + Síntese                              ║
║                                                                   ║
╠═══════════════════════════════════════════════════════════════════╣
║   Fontes: PDAD 2021 (IPEDF) · TSE 2022. Estrategos.               ║
╚═══════════════════════════════════════════════════════════════════╝
```

### Variáveis (Camada 2 — adapta ao candidato)

| Variável | Exemplo (Felix · PSOL · 52k votos · Concentrado · Eleito) | Cálculo |
|---|---|---|
| `nome_candidato` | "Fábio Felix Silveira" | `cand.nome` |
| `partido` | "PSOL" | `cand.partido` |
| `campo` | "Progressista" | `cand.campo` (label) |
| `eleito` | true → badge verde "Eleito" | `cand.eleito` |
| `total_votos` | "52.184" | `cand.total` (locale) |
| `perfil_votacao` | "Concentrado" + cor | calc: spread > 200pp → Concentrado |
| `spread_pp` | "327pp" | `max(perf) − min(perf)` |
| `total_kpi` | "52.184" | mesmo `total_votos` |
| `patamar_pct` | "+190%" (acima) ou "−25%" (abaixo) | `(total / 18000 − 1) × 100` |
| `n_redutos` | "9" | count(zonas in {Reduto, Voto pessoal}) |
| `frase_tese` | gerada por regras | ver §"Geração da frase-tese" |

### Geração da frase-tese (Camada 2 médio)

A frase-tese é **gerada por regras** (não LLM) a partir de:

1. `perfil_votacao` (Distribuído / Híbrido / Concentrado)
2. `patamar_pct` (acima ou abaixo do patamar)
3. `n_redutos` (quantas RAs em Reduto + Voto pessoal)
4. `n_aberto` (quantas em Sem espaço pelo campo)

**Templates de regras:**

```
SE Concentrado E acima do patamar:
  "Concentrado: {N_REDUTOS} RAs do Reduto consolidado e Voto pessoal
   carregam a maior parte da sua base. Você está {PATAMAR_PCT} acima
   do patamar de eleição, mas a amplitude do voto é estreita —
   defender essas RAs é a decisão mais importante de 2026."

SE Concentrado E abaixo do patamar:
  "Concentrado mas frágil: você performa em {N_REDUTOS} RAs mas o
   total ({TOTAL_VOTOS}) está {PATAMAR_PCT} abaixo do patamar. A
   estratégia precisa combinar defesa rígida do reduto com captura
   ativa de Espaço a conquistar."

SE Híbrido E acima do patamar:
  "Híbrido com base diversificada: {N_REDUTOS} RAs sustentam sua
   base, mas sem hiperconcentração. Margem do patamar ({PATAMAR_PCT})
   permite estratégia equilibrada — defender base e expandir em
   Espaço a conquistar."

SE Híbrido E abaixo do patamar:
  "Híbrido sem base consolidada: você cobre território mas sem
   reduto definido. {PATAMAR_PCT} abaixo do patamar — estratégia
   precisa criar reduto antes de tentar expandir."

SE Distribuído E acima do patamar:
  "Distribuído com cobertura ampla: poucas RAs em Reduto, voto
   espalhado por mais de 20 RAs. {PATAMAR_PCT} acima do patamar —
   capilaridade é seu trunfo. Defender é cobrir, não fortalecer."

SE Distribuído E abaixo do patamar:
  "Distribuído com baixa intensidade: voto espalhado mas sem
   concentração. {PATAMAR_PCT} abaixo do patamar — estratégia
   precisa escolher entre criar reduto (concentrar) ou expandir
   capilaridade. Indefinição estratégica é o maior risco."
```

6 templates cobrem as combinações principais. Edge cases (muitos
"Sem espaço pelo campo", etc.) podem ser adicionados conforme
aparecerem casos.

### Conteúdo Camada 1 (fixo na página 1)

- Logo Opinião + título "ESTRATÉGIA DE CAMPANHA · DEP. DISTRITAL"
- Data de geração
- Sumário das páginas (texto fixo, igual em todo PDF Distrital)
- Rodapé canônico ("Fontes: PDAD 2021 (IPEDF) · TSE 2022. Estrategos.")

### Conteúdo Camada 2 (varia)

- Nome do candidato + meta-dados (cargo, partido, total votos, eleito)
- 4 KPIs (4 valores numéricos diferentes por candidato)
- Frase-tese (gerada por regras a partir de 4 variáveis)

---

## Página 2 — Conceitos centrais

**Página 100% Camada 1** — texto didático, idêntico em todos os PDFs
Distritais. Explica os conceitos antes de o leitor encarar as análises.

### Mockup (A4 paisagem)

```
╔═══════════════════════════════════════════════════════════════════╗
║   [logo]   CONCEITOS CENTRAIS                                     ║
║            O vocabulário que sustenta todo o documento            ║
╠══════════════════════════════════╤════════════════════════════════╣
║ ▌ PERFORMANCE                    │ ▌ FORÇA DO CAMPO              ║
║                                  │                                ║
║ Quanto a região entrega de votos │ Mesma escala da Performance,  ║
║ ao candidato comparado ao        │ aplicada ao campo político    ║
║ esperado pelo seu tamanho        │ inteiro do candidato (todos os║
║ relativo no eleitorado do DF.    │ candidatos do mesmo bloco no  ║
║                                  │ mesmo cargo).                  ║
║ Exemplo: Plano Piloto tem 9% do  │                                ║
║ eleitorado. Se o candidato fosse │ Mostra se o campo dele é forte║
║ proporcional, deveria ter 9% dos │ ou fraco naquela região,      ║
║ votos lá. Se tem 18%, está com   │ INDEPENDENTE desse candidato  ║
║ +100% Performance.               │ específico.                    ║
║                                  │                                ║
║ Faixas:                          │ Por que separar?              ║
║ ▌ Reduto      ≥ +30%             │ Distingue "candidato forte"   ║
║ ▌ Base forte  +15% a +30%        │ de "campo forte". Performance ║
║ ▌ Esperado    −15% a +15%        │ alta + Campo fraco = voto     ║
║ ▌ Base fraca  −15% a −30%        │ pessoal. Performance baixa +  ║
║ ▌ Ausência    ≤ −30%             │ Campo forte = espaço a        ║
║                                  │ conquistar (campo já vota).   ║
╠══════════════════════════════════╧════════════════════════════════╣
║ ▌ AS 5 ZONAS ESTRATÉGICAS                                         ║
║                                                                   ║
║ Cruzamento Performance × Força do campo. Cada RA cai em uma zona. ║
║                                                                   ║
║ ┌─────────────────────────┬──────────────┬──────────────┬──────┐ ║
║ │ Zona                    │ Performance  │ Força campo  │ Cor  │ ║
║ ├─────────────────────────┼──────────────┼──────────────┼──────┤ ║
║ │ Reduto consolidado      │ ≥ +15%       │ ≥ +15%       │ ▌    │ ║
║ │ Voto pessoal            │ ≥ +15%       │ < +15%       │ ▌    │ ║
║ │ Esperado                │ −15% a +15%  │ qualquer     │ ▌    │ ║
║ │ Espaço a conquistar     │ < −15%       │ ≥ +15%       │ ▌    │ ║
║ │ Sem espaço pelo campo   │ < −15%       │ < +15%       │ ▌    │ ║
║ └─────────────────────────┴──────────────┴──────────────┴──────┘ ║
║                                                                   ║
╠═══════════════════════════════════════════════════════════════════╣
║ ▌ PATAMAR DE ELEIÇÃO                                              ║
║                                                                   ║
║ Volume de votos típico para se eleger em cada cargo no DF —       ║
║ calibrado pela observação dos eleitos em 2022.                    ║
║                                                                   ║
║   Governador  ≈ 700 mil   ·   Senador  ≈ 550 mil                  ║
║   Dep. Federal ≈ 30 mil   ·   Dep. Distrital ≈ 18 mil  ←  você    ║
║                                                                   ║
║ Não é piso formal — eleitos podem entrar abaixo via legenda e     ║
║ sobras, e candidatos fortes ultrapassam o patamar substancial-    ║
║ mente. Serve como referência: estar muito abaixo significa que    ║
║ o candidato precisa crescer; muito acima, que tem folga.          ║
╚═══════════════════════════════════════════════════════════════════╝
```

### Conteúdo (texto canônico)

#### PERFORMANCE

Mostra se uma região foi **bem ou mal pra o candidato**, comparado ao tamanho dela.

A conta é simples: cada região tem uma fatia do eleitorado do DF. Se o candidato fosse "neutro" no território, deveria pegar essa mesma fatia dos seus votos lá. Quando pega mais, é Reduto. Quando pega menos, é Ausência.

**Exemplo (do candidato selecionado):** {NOME_RA_EXEMPLO} tem {PCT_APTOS}% do eleitorado do DF. Esperaríamos que entregasse {PCT_APTOS}% dos votos do candidato. Entregou {PCT_VOTOS_CAND}% — está com **{PERFORMANCE_RA_EXEMPLO} de Performance**.

**Faixas:**

| Faixa | Performance | Leitura |
|---|---|---|
| Reduto | ≥ +30% | a região votou muito acima do esperado |
| Base forte | +15% a +30% | acima do esperado |
| Esperado | −15% a +15% | dentro do esperado pelo tamanho |
| Base fraca | −15% a −30% | abaixo do esperado |
| Ausência | ≤ −30% | muito abaixo do esperado |

#### FORÇA DO CAMPO

A Performance olha pro candidato sozinho. A Força do campo olha pro **bloco inteiro** dele (todos os candidatos progressistas, ou moderados, ou liberais/conservadores) na mesma região, no mesmo cargo.

Mesma escala. Mesma leitura. **Independente do candidato específico**.

**Pra que serve essa separação?** Pra responder uma pergunta crucial: o candidato é forte na região **por mérito próprio** ou **porque o campo dele inteiro vai bem ali**?

- Candidato forte + campo forte = **reduto consolidado** (você está em casa)
- Candidato forte + campo fraco = **voto pessoal** (você ganha apesar do bloco; voto vinculado à pessoa)
- Candidato fraco + campo forte = **espaço a conquistar** (o campo já vota ali; falta o eleitor saber que você existe)
- Candidato fraco + campo fraco = **território hostil**

#### AS 5 ZONAS ESTRATÉGICAS

Cruzamento Performance × Força do campo. Cada RA cai em **uma e só uma** zona.

| Zona | Performance | Força do campo | Significado |
|---|---|---|---|
| 🟢 **Reduto consolidado** | ≥ +15% | ≥ +15% | Você e seu campo são fortes ali. **Defenda.** |
| 🔵 **Voto pessoal** | ≥ +15% | < +15% | Só você é forte (campo é fraco). **Proteja — voto vinculado à pessoa.** |
| 🟠 **Esperado** | −15% a +15% | qualquer | Território neutro. **Investir só com motivo específico.** |
| 🟤 **Espaço a conquistar** | < −15% | ≥ +15% | Campo forte mas você não chegou. **Capture — eleitor já vota no bloco.** |
| 🔴 **Sem espaço pelo campo** | < −15% | < +15% | Hostil estrutural. **Não atira.** |

#### PATAMAR DE ELEIÇÃO

Quantos votos são suficientes pra se eleger? Não tem piso formal — depende de coligações, sobras, votos de legenda. Mas **observando os eleitos de 2022**, dá pra estimar uma referência:

| Cargo | Patamar de votos |
|---|---|
| Governador | ≈ 700 mil |
| Senador | ≈ 550 mil |
| Dep. Federal | ≈ 30 mil |
| **Dep. Distrital** | **≈ 18 mil**  ← cargo deste documento |

Estar bem acima do patamar significa folga; abaixo, alvo claro de crescimento. Mas patamar é referência, não promessa: candidatos fortes ultrapassam, eleitos podem entrar abaixo por sobras de legenda.

### Camada 2 (variáveis adaptadas ao candidato)

| Variável | Onde aparece | Cálculo |
|---|---|---|
| `NOME_RA_EXEMPLO` | bloco Performance, exemplo concreto | RA com **maior Performance positiva** entre as RAs do candidato com voto > 0. Fallback: Plano Piloto |
| `PCT_APTOS` | exemplo Performance | aptos da RA exemplo / total DF × 100 |
| `PCT_VOTOS_CAND` | exemplo Performance | votos do candidato na RA / total candidato × 100 |
| `PERFORMANCE_RA_EXEMPLO` | exemplo Performance | `+X%` formatado |

**Por que adaptar o exemplo?** O cliente lê o conceito e já vê **na própria situação dele**. Ex.:
- Felix (PSOL): "Plano Piloto tem 9% do eleitorado. Entregou 24% dos votos do Felix — está com **+167% de Performance**."
- Manzoni (PL): "Lago Sul tem 1,9% do eleitorado. Entregou 7,2% dos votos do Manzoni — está com **+289% de Performance**."

A RA do exemplo deve ser **forte** (Reduto preferencialmente) — ilustra o conceito sob a melhor luz pro candidato. Se o candidato não tiver nenhum Reduto, usa a RA com maior Performance positiva, mesmo que seja só Base forte.

---

## Página 3 — Onde defender

**Reduto consolidado + Voto pessoal.** Duas zonas que compartilham a
estratégia-mãe ("defender") mas têm ações específicas distintas.

### Mockup (A4 paisagem)

```
╔══════════════════════════════════════════════════════════════════════╗
║  [logo]  ONDE DEFENDER                                               ║
║          Reduto consolidado + Voto pessoal                           ║
╠══════════════════════════════════════════════════════════════════════╣
║  ▌ POR QUE DEFENDER                                                  ║
║                                                                      ║
║  Aqui é onde você já tem voto. Não é zona de conquista — é zona de   ║
║  proteção. O risco principal é a abstenção: o eleitor que votou em   ║
║  2022 deixar de votar em 2026 porque achou que estava garantido.     ║
║                                                                      ║
║  São duas zonas com motores diferentes:                              ║
║  • Reduto consolidado: você É forte, e o seu campo TAMBÉM. Você      ║
║    está em casa. Defenda a base.                                     ║
║  • Voto pessoal: só você é forte (o campo é fraco). O voto está      ║
║    vinculado à sua pessoa, não ao partido. Proteja a relação.        ║
╠══════════════════════════════════════════════════════════════════════╣
║  ▌ SUAS RAs DE DEFESA — {N} regiões · {VOTOS_TOTAIS} votos          ║
║                                                                      ║
║  ┌────────────────────┬──────┬──────┬────┬───────┬───────┬──────┐  ║
║  │ Região             │Aptos │Votos │ %  │ Perf. │ Campo │ Zona │  ║
║  ├────────────────────┼──────┼──────┼────┼───────┼───────┼──────┤  ║
║  │ Lago Sul           │ 41k  │1.853 │7,2 │ +289% │ +60%  │ ▌Red │  ║
║  │ Plano Piloto       │184k  │6.890 │27,0│ +223% │ +40%  │ ▌Red │  ║
║  │ Park Way           │5,9k  │  144 │0,6 │ +109% │ −12%  │ ▌V.P.│  ║
║  │ ... (todas as RAs em Reduto + Voto pessoal)                  │  ║
║  └────────────────────┴──────┴──────┴────┴───────┴───────┴──────┘  ║
║                                                                      ║
║  ▶ INSIGHT: {Frase gerada — concentração da defesa no total}        ║
║                                                                      ║
╠══════════════════════════════════════════════════════════════════════╣
║  ┌────────────────────────────────┬───────────────────────────────┐ ║
║  │ ▌ REDUTO CONSOLIDADO           │ ▌ VOTO PESSOAL                │ ║
║  │                                │                               │ ║
║  │ Estratégia: defender a base.   │ Estratégia: proteger relação. │ ║
║  │ Foco em comparecimento, não    │ O voto está vinculado a você, │ ║
║  │ em conversão.                  │ não ao partido.               │ ║
║  │                                │                               │ ║
║  │ Risco: complacência. Eleitor   │ Risco: mudança evapora o      │ ║
║  │ satisfeito vira abstenção.     │ voto. Troca de cargo, partido │ ║
║  │                                │ ou de visibilidade desfaz.    │ ║
║  │                                │                               │ ║
║  │ Ações:                         │ Ações:                        │ ║
║  │ • Agradecimento explícito      │ • Atendimento individual      │ ║
║  │ • Prestação de contas          │   visível (gabinete na rua)   │ ║
║  │ • Mobilização pré-eleição      │ • Marca pessoal sobre marca   │ ║
║  │ • Presença regular durante     │   partidária                  │ ║
║  │   o mandato                    │ • Contato com lideranças      │ ║
║  │                                │   locais                      │ ║
║  └────────────────────────────────┴───────────────────────────────┘ ║
╚══════════════════════════════════════════════════════════════════════╝
```

### Conteúdo Camada 1 (texto fixo)

#### Por que defender

Aqui é onde você já tem voto. Não é zona de conquista — é zona de proteção. O risco principal é a abstenção: o eleitor que votou em 2022 deixar de votar em 2026 porque achou que estava garantido.

#### Reduto consolidado

- **Estratégia:** defender a base. Foco em comparecimento, não em conversão.
- **Risco:** complacência. Eleitor satisfeito se torna abstenção quando se sente garantido.
- **Ações:** agradecimento explícito, prestação de contas, mobilização pré-eleição (lembrete e eventos locais), presença regular durante o mandato.

#### Voto pessoal

- **Estratégia:** proteger a relação pessoal. O voto está vinculado à você, não ao partido.
- **Risco:** mudança evapora o voto. Troca de cargo, de partido ou redução de visibilidade pode desfazer a base.
- **Ações:** atendimento individual visível (gabinete na rua, redes pessoais), marca pessoal sobre marca partidária, contato com lideranças locais que sustentam o voto.

### Conteúdo Camada 2 (analítico — varia por candidato)

#### Tabela "Suas RAs de defesa"

Listar todas as RAs do candidato em **Reduto consolidado** ou **Voto pessoal**, ordenadas por Performance descendente. Colunas:

- Região
- Aptos (em milhares ou completo)
- Votos (votos do candidato na RA)
- % dos votos (frequência relativa)
- Performance
- Força do campo
- Zona (badge: ▌Reduto consolidado / ▌Voto pessoal)

Cabeçalho da seção mostra: **"{N} regiões · {VOTOS_TOTAIS} votos"** (somatório).

#### Insight gerado por regras

Frase final, gerada da combinação:

```
SE soma_pct_dos_votos ≥ 70%:
  "Concentração alta: {N} RAs de defesa carregam {SOMA_PCT}% dos
   seus votos. Defender é a parte mais importante da estratégia."

SE soma_pct_dos_votos entre 40% e 70%:
  "Base equilibrada: {N} RAs de defesa carregam {SOMA_PCT}% dos
   seus votos. Defender importa, mas precisa caminhar junto com
   captura em Espaço a conquistar."

SE soma_pct_dos_votos < 40%:
  "Base diluída: só {SOMA_PCT}% dos seus votos vêm das RAs de
   defesa. O grosso está em Esperado — defender aqui não basta;
   a estratégia precisa criar reduto antes de defender."
```

### Variáveis (Camada 2)

| Variável | Cálculo |
|---|---|
| `RAS_DEFESA[]` | RAs em ("Reduto consolidado", "Voto pessoal") |
| `N` | count(`RAS_DEFESA`) |
| `VOTOS_TOTAIS` | sum(votos) nas `RAS_DEFESA` |
| `SOMA_PCT` | sum(pe) nas `RAS_DEFESA` (em %) |

---

## Página 4 — Onde crescer

**Espaço a conquistar.** Zona única — campo do candidato já vota ali, mas
o eleitor não escolheu ele especificamente.

### Mockup (A4 paisagem)

```
╔══════════════════════════════════════════════════════════════════════╗
║  [logo]  ONDE CRESCER                                                ║
║          Espaço a conquistar                                         ║
╠══════════════════════════════════════════════════════════════════════╣
║  ▌ POR QUE CRESCER AQUI                                              ║
║                                                                      ║
║  Aqui o seu campo já vota. O eleitor escolheu o seu bloco político — ║
║  só não escolheu você especificamente. A conversão é barata: não é   ║
║  preciso convencer o eleitor de que o bloco vale; basta fazê-lo      ║
║  saber que você é uma opção válida dentro dele.                      ║
║                                                                      ║
╠══════════════════════════════════════════════════════════════════════╣
║  ▌ SUAS RAs DE CRESCIMENTO — {N} regiões                             ║
║                                                                      ║
║  ┌────────────────┬──────┬──────┬────┬───────┬───────┬───────────┐ ║
║  │ Região         │Aptos │Votos │ %  │ Perf. │ Campo │ Estoque   │ ║
║  ├────────────────┼──────┼──────┼────┼───────┼───────┼───────────┤ ║
║  │ Recanto Emas   │ 93k  │  XYZ │0,X │ −44%  │ +21%  │ {votos}   │ ║
║  │ ...                                                              │ ║
║  └────────────────┴──────┴──────┴────┴───────┴───────┴───────────┘ ║
║                                                                      ║
║  ▶ INSIGHT: {Frase gerada — estoque potencial}                      ║
║                                                                      ║
╠══════════════════════════════════════════════════════════════════════╣
║  ▌ COMO CRESCER                                                      ║
║                                                                      ║
║  Estratégia: captura oportunística. O campo já vota, falta o eleitor ║
║  saber que existe esse candidato.                                    ║
║                                                                      ║
║  Risco: canibalização interna do bloco. Disputar voto com o "dono    ║
║  atual" daquela RA pode dar atrito sem ganho líquido.                ║
║                                                                      ║
║  Ações:                                                              ║
║  • Awareness — panfleto, sonoro, redes com mensagem do campo         ║
║  • Endosso de lideranças do mesmo bloco na RA                        ║
║  • Eventos conjuntos com candidatos do bloco que têm reduto ali      ║
║  • Mensagem identitária do campo (não pessoal)                       ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

### Conteúdo Camada 1 (texto fixo)

#### Por que crescer aqui

Aqui o seu campo já vota. O eleitor escolheu o seu bloco político — só não escolheu você especificamente. A conversão é barata: não é preciso convencer o eleitor de que o bloco vale; basta fazê-lo saber que você é uma opção válida dentro dele.

#### Espaço a conquistar

- **Estratégia:** captura oportunística. O campo já vota, falta o eleitor saber que existe esse candidato.
- **Risco:** canibalização interna do bloco. Disputar voto com o "dono atual" daquela RA pode dar atrito sem ganho líquido.
- **Ações:** awareness (panfleto, sonoro, redes com mensagem do campo), endosso de lideranças do mesmo bloco na RA, eventos conjuntos com candidatos do bloco que têm reduto ali, mensagem identitária do campo (não pessoal).

### Conteúdo Camada 2 (analítico — varia por candidato)

#### Tabela "Suas RAs de crescimento"

Listar todas as RAs do candidato em **Espaço a conquistar**, ordenadas por **estoque potencial descendente**. Colunas:

- Região
- Aptos
- Votos (do candidato — geralmente baixo)
- % dos votos
- Performance (negativa)
- Força do campo (positiva)
- **Estoque** = `votos_campo_RA − votos_candidato_RA` (votos disponíveis no bloco que ainda não foram pra ele)

Cabeçalho da seção mostra: **"{N} regiões"**.

#### Insight gerado por regras

Estoque total = soma de `(votos_campo_RA − votos_candidato_RA)` em todas as RAs do candidato em Espaço a conquistar.

```
SE estoque_total ≥ 30% × total_votos_candidato:
  "Espaço grande: as {N} RAs de Espaço a conquistar têm {ESTOQUE} votos
   do seu campo ainda capturáveis. Conversão de 5% = +{ESTOQUE×0.05} votos.
   Frente principal de crescimento."

SE estoque_total entre 10% e 30% × total_votos_candidato:
  "Espaço moderado: {N} RAs com {ESTOQUE} votos do campo disponíveis.
   Conversão de 5% = +{ESTOQUE×0.05} votos. Boa frente complementar
   à defesa."

SE estoque_total < 10% × total_votos_candidato:
  "Espaço estreito: poucas RAs ou pouco voto disponível no campo.
   Crescimento via Espaço a conquistar tem rendimento limitado —
   priorize defesa."

SE N == 0:
  "Sem RAs em Espaço a conquistar. O seu campo já votou em você
   onde podia — crescimento exige ir além da base ideológica."
```

### Variáveis (Camada 2)

| Variável | Cálculo |
|---|---|
| `RAS_CRESCIMENTO[]` | RAs em "Espaço a conquistar" |
| `N` | count(`RAS_CRESCIMENTO`) |
| `ESTOQUE_RA` | `votos_campo_RA − votos_candidato_RA` por RA |
| `ESTOQUE_TOTAL` | soma de `ESTOQUE_RA` em todas as RAs |

---

## Página 5 — Decisões periféricas

**Esperado (em RAs grandes) + Sem espaço pelo campo.** Duas zonas que
não estão na frente da defesa nem do crescimento. Decisão é: quanto
investir aqui — pouco ou nada.

### Mockup (A4 paisagem)

```
╔══════════════════════════════════════════════════════════════════════╗
║  [logo]  DECISÕES PERIFÉRICAS                                        ║
║          Esperado (top peso) + Sem espaço pelo campo                 ║
╠══════════════════════════════════════════════════════════════════════╣
║  ▌ POR QUE PERIFÉRICAS                                               ║
║                                                                      ║
║  Estas zonas não estão na frente da defesa nem do crescimento.       ║
║  A decisão é simples: quanto investir aqui — pouco ou nada.          ║
║  Cada centavo gasto sem retorno previsível é um centavo a menos      ║
║  onde rende.                                                         ║
║                                                                      ║
╠══════════════════════════════════════════════════════════════════════╣
║  ▌ ESPERADO — top RAs por peso eleitoral · {N} regiões              ║
║                                                                      ║
║  Mantemos aqui apenas as RAs em Esperado com peso eleitoral          ║
║  significativo (≥ 5% dos votos do cargo no DF). Demais RAs em        ║
║  Esperado ficam fora — entram apenas se houver razão específica.     ║
║                                                                      ║
║  ┌────────────┬──────┬──────┬────┬───────┬───────┬─────────┐       ║
║  │ Região     │Aptos │Votos │ %  │ Perf. │ Campo │ Peso    │       ║
║  ├────────────┼──────┼──────┼────┼───────┼───────┼─────────┤       ║
║  │ Ceilândia  │ 302k │  ... │... │  +2%  │  +6%  │ 13,7%   │       ║
║  │ Taguatinga │ 213k │  ... │... │ −0,3% │ −0,5% │ 9,7%    │       ║
║  │ ...                                                              │
║  └────────────┴──────┴──────┴────┴───────┴───────┴─────────┘       ║
║                                                                      ║
║  Estratégia: presença pontual com motivo específico — volume,        ║
║  mensagem ou evento. Conversão é cara; retorno proporcional.         ║
║  Risco: dispersão de recursos sem virada perceptível.                ║
║  Ações:                                                              ║
║  • Presença mínima — panfleto, sonoro pontual                        ║
║  • Eventos só com retorno claro (não pulverizar agenda)              ║
║  • Observar evolução: RA grande em Esperado pode virar reduto        ║
║    com narrativa certa em ciclos futuros                             ║
║                                                                      ║
╠══════════════════════════════════════════════════════════════════════╣
║  ▌ SEM ESPAÇO PELO CAMPO — {N} regiões · {APTOS} aptos descartados  ║
║                                                                      ║
║  ┌──────────────┬──────┬──────┬────┬───────┬───────┐                ║
║  │ Região       │Aptos │Votos │ %  │ Perf. │ Campo │                ║
║  ├──────────────┼──────┼──────┼────┼───────┼───────┤                ║
║  │ Brazlândia   │ 51k  │  XYZ │0,X │ −35%  │ −12%  │                ║
║  │ Itapoã       │ 22k  │  XYZ │0,X │ −44%  │ −15%  │                ║
║  │ ...                                                              │
║  └──────────────┴──────┴──────┴────┴───────┴───────┘                ║
║                                                                      ║
║  Estratégia: não atira. Recursos vão pras 4 zonas acima.             ║
║  Risco: insistir aqui drena orçamento sem retorno.                   ║
║  Ações:                                                              ║
║  • Presença mínima ou nenhuma                                        ║
║  • Sinalização institucional só em campanhas conjuntas (presidencial)║
║  • Reavaliar a cada ciclo — RA pode mudar de status                  ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

### Conteúdo Camada 1 (texto fixo)

#### Por que periféricas

Estas zonas não estão na frente da defesa nem do crescimento. A decisão é simples: quanto investir aqui — pouco ou nada. Cada centavo gasto sem retorno previsível é um centavo a menos onde rende.

#### Esperado (top peso eleitoral)

- **Estratégia:** presença pontual com motivo específico — volume, mensagem ou evento. Conversão é cara; retorno proporcional.
- **Risco:** dispersão de recursos sem virada perceptível.
- **Ações:** presença mínima (panfleto, sonoro pontual), eventos só com retorno claro (não pulverizar a agenda), observar evolução — uma RA grande em Esperado pode virar reduto com narrativa certa em ciclos futuros.

#### Sem espaço pelo campo

- **Estratégia:** não atira. Recursos vão pras quatro zonas acima.
- **Risco:** insistir aqui drena orçamento sem retorno.
- **Ações:** presença mínima ou nenhuma, sinalização institucional só em campanhas conjuntas (presidencial, governamental), reavaliar a cada ciclo — RA pode mudar de status.

### Conteúdo Camada 2 (analítico — varia por candidato)

#### Tabela "Esperado — top RAs por peso"

Filtra **apenas** as RAs em Esperado com peso eleitoral ≥ 5% dos votos do cargo no DF. Ordenadas por peso descendente. Colunas:

- Região
- Aptos
- Votos
- % dos votos
- Performance
- Força do campo
- **Peso** = % dos votos do cargo no DF que vieram dessa RA

Demais RAs em Esperado (peso < 5%) ficam fora — não justificam investimento dirigido. Entram apenas via decisão consultiva específica.

#### Tabela "Sem espaço pelo campo"

Lista todas as RAs do candidato em **Sem espaço pelo campo**. Ordenadas por aptos descendente (volume descartado). Cabeçalho: **"{N} regiões · {APTOS_TOTAL} aptos descartados"**.

#### Insights gerados por regras

```
ESPERADO (top peso):
  SE N_filtrado == 0:
    "Nenhuma RA em Esperado entre as de top peso. Recursos liberados
     para defesa e crescimento."
  SE N_filtrado entre 1 e 3:
    "Atenção a {N_filtrado} RAs grandes neutras. Investimento pontual
     com retorno proporcional ao volume."
  SE N_filtrado >= 4:
    "{N_filtrado} RAs grandes neutras. Risco de dispersão — escolher
     1-2 com narrativa mais clara."

SEM ESPAÇO PELO CAMPO:
  SE pct_aptos_descartado >= 30% × DF:
    "Quase um terço do eleitorado descartado — perfil hiperconcentrado.
     Reforça a necessidade de defender o reduto."
  SE pct_aptos_descartado entre 10% e 30%:
    "{N} RAs descartadas — eleitorado fora do raio de captura."
  SE pct_aptos_descartado < 10%:
    "Pouco eleitorado descartado — perfil já cobre quase todo o DF."
```

### Variáveis (Camada 2)

| Variável | Cálculo |
|---|---|
| `RAS_ESPERADO_TOP[]` | RAs em "Esperado" com peso ≥ 5% dos votos do cargo |
| `RAS_SEM_ESPACO[]` | RAs em "Sem espaço pelo campo" |
| `APTOS_TOTAL_SEM_ESPACO` | sum(aptos) em `RAS_SEM_ESPACO` |
| `PCT_APTOS_DESCARTADO` | `APTOS_TOTAL_SEM_ESPACO` / total_aptos_DF |

---

## Página 6 — Quem é meu eleitor

**Perfil PDAD agregado.** Variáveis socioeconômicas das RAs onde o
candidato recebeu votos, ponderadas pelo voto, comparadas com a média
do DF.

### Mockup (A4 paisagem)

```
╔══════════════════════════════════════════════════════════════════════╗
║  [logo]  QUEM É MEU ELEITOR                                          ║
║          Perfil agregado das RAs onde você recebeu votos             ║
╠══════════════════════════════════════════════════════════════════════╣
║  ▌ COMO LER                                                          ║
║                                                                      ║
║  O eleitor-tipo é uma média das RAs onde você recebeu votos,         ║
║  ponderada pelo voto que cada uma deu. Não é uma pessoa real —       ║
║  é o perfil agregado de quem te elegeu.                              ║
║                                                                      ║
║  Verde = acima da média do DF · Vermelho = abaixo · Cinza = neutro   ║
║                                                                      ║
╠══════════════════════════════════════════════════════════════════════╣
║  ▌ PERFIL DO ELEITOR-TIPO vs MÉDIA DO DF                             ║
║                                                                      ║
║  ┌──────────────┬──────────────┬──────────────┬──────────────┐      ║
║  │ Renda P/C    │ Classe A/B   │ Ens. superior│ Serv. federal│      ║
║  │ R$ X,XXX     │ XX,X%        │ XX,X%        │ X,X%         │      ║
║  │ DF: R$ Y     │ DF: Y,Y%     │ DF: Y,Y%     │ DF: Y,Y%     │      ║
║  └──────────────┴──────────────┴──────────────┴──────────────┘      ║
║                                                                      ║
║  ┌──────────────┬──────────────┬──────────────┬──────────────┐      ║
║  │ Serv. distr. │ Benef. social│ Nativo DF    │ Idosos 60+   │      ║
║  │ X,X%         │ XX,X%        │ XX,X%        │ XX,X%        │      ║
║  │ DF: Y,Y%     │ DF: Y,Y%     │ DF: Y,Y%     │ DF: Y,Y%     │      ║
║  └──────────────┴──────────────┴──────────────┴──────────────┘      ║
║                                                                      ║
║  ▶ INSIGHT: {Frase gerada — destaca 2-3 desvios mais marcantes}     ║
║                                                                      ║
╠══════════════════════════════════════════════════════════════════════╣
║  ▌ COMO ISSO MUDA SUA CAMPANHA                                       ║
║                                                                      ║
║  O perfil do eleitor define mensagem, canal e tom:                   ║
║                                                                      ║
║  • Mensagem — os assuntos que ressoam variam com o perfil. Educação, ║
║    funcionalismo público, segurança, saúde têm peso diferente em     ║
║    cada classe e ocupação                                            ║
║  • Canal — redes sociais, panfleto, rádio comunitário, presença      ║
║    territorial penetram de forma desigual por classe e idade         ║
║  • Tom — perfil escolarizado tolera mais nuance e abstração;         ║
║    perfil popular pede mensagem direta e prática                     ║
║                                                                      ║
║  Atenção: dentro do seu próprio voto o perfil varia. O eleitor do    ║
║  Reduto pode ser diferente do eleitor do Espaço a conquistar.        ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

### Conteúdo Camada 1 (texto fixo)

#### Como ler

O eleitor-tipo é uma média das RAs onde você recebeu votos, ponderada pelo voto que cada uma deu. Não é uma pessoa real — é o perfil agregado de quem te elegeu.

**Verde** = acima da média do DF · **Vermelho** = abaixo · **Cinza** = neutro (próximo da média)

#### Como isso muda sua campanha

O perfil do eleitor define mensagem, canal e tom:

- **Mensagem** — os assuntos que ressoam variam com o perfil. Educação, funcionalismo público, segurança, saúde têm peso diferente em cada classe e ocupação.
- **Canal** — redes sociais, panfleto, rádio comunitário, presença territorial penetram de forma desigual por classe e idade.
- **Tom** — perfil escolarizado tolera mais nuance e abstração; perfil popular pede mensagem direta e prática.

**Atenção:** dentro do seu próprio voto o perfil varia. O eleitor do Reduto pode ser diferente do eleitor do Espaço a conquistar. Use este perfil pra calibrar a média — não pra simplificar a base.

### Conteúdo Camada 2 (analítico — varia por candidato)

#### 8 KPIs (cards) em 2 linhas de 4

Cada card mostra:
- **Label** (variável)
- **Valor do candidato** (média ponderada por voto)
- **Referência DF** (média do DF)
- **Cor**: verde se valor > DF, vermelho se valor < DF, cinza se ±5% da DF

Variáveis escolhidas (cobrem 4 dimensões: renda, escolaridade, ocupação, geração):

| Card | Variável (PDAD) | Dimensão |
|---|---|---|
| 1 | Renda per capita média | renda |
| 2 | % classe A/B | renda |
| 3 | % ensino superior (16+) | escolaridade |
| 4 | % servidor federal | ocupação |
| 5 | % servidor distrital | ocupação |
| 6 | % beneficiário de programa social | renda/vulnerabilidade |
| 7 | % nativo do DF | origem |
| 8 | % idosos 60+ | geração |

#### Cálculo da média ponderada

Para cada variável `var`:

```
valor_eleitor_tipo = sum(var_RA × votos_candidato_RA) / sum(votos_candidato_RA)
```

Soma sobre todas as RAs onde o candidato recebeu votos.

#### Insight gerado por regras

Identifica os **2-3 desvios mais marcantes** (% acima ou abaixo da DF) e gera frase descritiva:

```
SE classe_AB > DF +5pp E superior > DF +5pp:
  "Eleitor escolarizado e de classe alta — perfil cosmopolita."

SE serv_federal > DF +1.5pp:
  "Forte presença de servidor federal — perfil de carreira pública."

SE benef_social > DF +3pp E classe_AB < DF −5pp:
  "Eleitor popular e periférico — perfil dependente de presença
   territorial e prestação direta."

SE idoso_60 > DF +3pp:
  "Eleitor mais velho que a média — implicação: canais analógicos
   (rádio, presença, conversa direta) ainda funcionam bem."

SE servidor_distrital > DF +2pp:
  "Forte presença de servidor distrital — eleitor da máquina pública
   local; agenda territorial conta mais que ideológica."
```

Combina 2-3 dessas frases conforme os desvios. Se nenhum desvio
significativo, retorna: *"Perfil próximo da média do DF — não há
caracterização única; a base é heterogênea."*

### Variáveis (Camada 2)

| Variável | Cálculo |
|---|---|
| `valor_var` (8 vars) | média ponderada por voto |
| `media_DF_var` (8 vars) | direto da PDAD agregada do DF |
| `desvio_var` | `valor_var − media_DF_var` (em pp ou em R$) |
| `cor_var` | verde / vermelho / cinza conforme desvio |

---

## Página 7 — Alocação de esforço + Síntese

**Última página.** Traduz as 5 zonas em uma sugestão concreta de
alocação (% de esforço por frente) e fecha o documento com 4 achados-
âncora — as frases que o candidato precisa carregar.

### Mockup (A4 paisagem)

```
╔══════════════════════════════════════════════════════════════════════╗
║  [logo]  ALOCAÇÃO DE ESFORÇO + SÍNTESE                               ║
║          Para onde o esforço da campanha deve ir                     ║
╠══════════════════════════════════════════════════════════════════════╣
║  ▌ COMO PENSAR ALOCAÇÃO                                              ║
║                                                                      ║
║  Cada real de campanha tem retorno diferente por zona. Defender voto ║
║  existente é mais barato que conquistar voto novo. Conquistar voto   ║
║  onde o campo já vota é mais barato que criar campo. Atirar onde o   ║
║  campo não vota é desperdício.                                       ║
║                                                                      ║
║  A proporção abaixo é uma referência — ajuste conforme orçamento,    ║
║  estrutura territorial e momento da campanha.                        ║
║                                                                      ║
╠══════════════════════════════════════════════════════════════════════╣
║  ▌ ALOCAÇÃO SUGERIDA                                                 ║
║                                                                      ║
║  ┌─────────────────────────┬───────┬─────────────────────────────┐  ║
║  │ Frente                  │ % Esf │ Detalhe                     │  ║
║  ├─────────────────────────┼───────┼─────────────────────────────┤  ║
║  │ ▌ Defesa                │  XX%  │ {N} RAs · {VOTOS} votos     │  ║
║  │   Reduto + Voto pessoal │       │ ({SOMA_PCT}% da sua base)   │  ║
║  │ ▌ Crescimento           │  XX%  │ {N} RAs · estoque {ESTOQUE} │  ║
║  │   Espaço a conquistar   │       │ votos disponíveis no campo  │  ║
║  │ ▌ Esperado (top peso)   │  XX%  │ {N} RAs grandes neutras     │  ║
║  │   Presença pontual      │       │                             │  ║
║  │ ▌ Sem espaço pelo campo │   0%  │ {N} RAs · {APTOS} descartado│  ║
║  └─────────────────────────┴───────┴─────────────────────────────┘  ║
║                                                                      ║
║  ▶ JUSTIFICATIVA: {Frase gerada — explica a proporção em função do   ║
║    perfil e do patamar}                                              ║
║                                                                      ║
╠══════════════════════════════════════════════════════════════════════╣
║  ▌ 4 ACHADOS-ÂNCORA                                                  ║
║                                                                      ║
║  ① IDENTIDADE                                                        ║
║     {Frase: perfil de votação + posição no patamar}                  ║
║                                                                      ║
║  ② MAIOR FORÇA                                                       ║
║     {Frase: RA principal + zona + por quê}                           ║
║                                                                      ║
║  ③ MAIOR ESPAÇO                                                      ║
║     {Frase: RA com maior estoque + tamanho da conversão potencial}   ║
║                                                                      ║
║  ④ RESTRIÇÃO                                                         ║
║     {Frase: maior limite estrutural — Sem espaço ou base diluída}    ║
║                                                                      ║
╠══════════════════════════════════════════════════════════════════════╣
║  Fontes: PDAD 2021 (IPEDF) · TSE 2022. Estrategos.                   ║
╚══════════════════════════════════════════════════════════════════════╝
```

### Conteúdo Camada 1 (texto fixo)

#### Como pensar alocação

Cada real de campanha tem retorno diferente por zona. Defender voto existente é mais barato que conquistar voto novo. Conquistar voto onde o campo já vota é mais barato que criar campo. Atirar onde o campo não vota é desperdício.

A proporção abaixo é uma referência — ajuste conforme orçamento, estrutura territorial e momento da campanha.

### Conteúdo Camada 2 (analítico — varia por candidato)

#### Tabela "Alocação sugerida"

Quatro frentes, com % de esforço sugerido e detalhe quantitativo por linha:

| Frente | Detalhe |
|---|---|
| **Defesa** (Reduto + Voto pessoal) | `N_DEFESA` RAs · `VOTOS_DEFESA` votos (`PCT_DEFESA`% da base) |
| **Crescimento** (Espaço a conquistar) | `N_CRESC` RAs · estoque `ESTOQUE_TOTAL` votos do campo |
| **Esperado top** (peso ≥ 5%) | `N_ESP_TOP` RAs grandes neutras |
| **Sem espaço pelo campo** | `N_SEM` RAs · `APTOS_SEM` aptos descartados (sempre 0%) |

#### Regra de alocação (% de esforço)

A proporção é decidida por **regra simples** combinando perfil de votação × posição no patamar:

```
Caso 1 — Acima do patamar + Concentrado:
  Defesa 60% · Crescimento 30% · Esperado top 10%
  → "você tem reduto e folga; defenda o que já tem"

Caso 2 — Acima do patamar + Híbrido/Distribuído:
  Defesa 50% · Crescimento 35% · Esperado top 15%
  → "base ampla, folga; equilibre defesa e expansão"

Caso 3 — Abaixo do patamar + Concentrado:
  Defesa 45% · Crescimento 45% · Esperado top 10%
  → "tem reduto mas falta volume; precisa crescer tanto quanto defender"

Caso 4 — Abaixo do patamar + Híbrido/Distribuído:
  Defesa 40% · Crescimento 45% · Esperado top 15%
  → "sem reduto e sem volume; crescimento é frente principal"

Ajustes especiais:
  SE N_CRESC == 0:
    Crescimento → 0; redistribui 50/50 entre Defesa e Esperado top
  SE N_ESP_TOP == 0:
    Esperado top → 0; redistribui pra Defesa
```

#### Justificativa (frase gerada)

Frase curta abaixo da tabela, explicando o caso aplicado:

```
SE Caso 1: "Concentrado e {PATAMAR_PCT} acima do patamar — sua base é
            sólida e tem folga. Defesa carrega {DEFESA_PCT}% do esforço."

SE Caso 2: "Híbrido/Distribuído com {PATAMAR_PCT} de folga sobre o
            patamar — base larga sem hiperconcentração. Equilíbrio
            entre proteger o que já tem e expandir."

SE Caso 3: "Concentrado mas {PATAMAR_PCT} abaixo do patamar — tem reduto
            forte mas falta volume. Defesa e crescimento dividem
            esforço, com leve vantagem pro crescimento."

SE Caso 4: "Sem reduto definido e {PATAMAR_PCT} abaixo do patamar —
            crescimento é a frente principal. Antes de defender, é
            preciso construir base."
```

#### 4 Achados-âncora

Frases curtas geradas por regras a partir das páginas anteriores. Servem como **resumo carregável** — o que o candidato repete pra si mesmo no carro.

**① Identidade** (perfil + patamar)
```
"{Perfil} e {acima|abaixo} do patamar em {PATAMAR_PCT}.
 {N_REDUTOS} RAs carregam {SOMA_PCT_DEFESA}% dos seus votos."
```

**② Maior força** (a melhor RA)
```
SE RA_topo é Reduto consolidado:
  "{NOME_RA} é seu reduto consolidado — Performance {+X%}, e o campo
   inteiro vai bem ali ({+Y%}). Onde você está em casa."

SE RA_topo é Voto pessoal:
  "{NOME_RA} é voto pessoal — Performance {+X%} mas o campo é {Y%}.
   Voto vinculado a você, não ao bloco. Proteja a relação."
```

**③ Maior espaço** (RA com maior estoque)
```
SE existe RA em Espaço a conquistar:
  "{NOME_RA_ESTOQUE_TOPO}: o campo já entrega {VOTOS_CAMPO_RA} votos lá
   e você captou só {VOTOS_CAND_RA}. {ESTOQUE} votos disponíveis ao alcance."

SE não existe:
  "Sem RAs em Espaço a conquistar. O campo já votou em você onde podia —
   crescimento exige ir além da base ideológica."
```

**④ Restrição** (maior limite)
```
SE PCT_APTOS_DESCARTADO ≥ 30%:
  "{PCT}% do eleitorado do DF está em Sem espaço pelo campo —
   território fora do raio realista. Não atira lá."

SE base diluída (SOMA_PCT_DEFESA < 40%):
  "Base diluída: só {SOMA_PCT_DEFESA}% dos votos vêm de RAs de defesa.
   Antes de qualquer expansão, é preciso criar reduto."

SE Concentrado E patamar ABAIXO:
  "Concentrado mas frágil: depende de poucas RAs e ainda assim está
   abaixo do patamar. Risco de uma RA fraca derrubar a eleição."

(default — escolhe a restrição mais marcante das 3 acima)
```

### Variáveis (Camada 2)

| Variável | Cálculo |
|---|---|
| `N_DEFESA`, `VOTOS_DEFESA`, `PCT_DEFESA` | reaproveita Pág. 3 |
| `N_CRESC`, `ESTOQUE_TOTAL` | reaproveita Pág. 4 |
| `N_ESP_TOP` | reaproveita Pág. 5 |
| `N_SEM`, `APTOS_SEM`, `PCT_APTOS_DESCARTADO` | reaproveita Pág. 5 |
| `CASO_ALOCACAO` | 1, 2, 3 ou 4 conforme perfil × patamar |
| `DEFESA_PCT`, `CRESC_PCT`, `ESP_PCT` | da regra do caso |
| `RA_TOPO` | RA com maior Performance positiva (Pág. 2) |
| `RA_ESTOQUE_TOPO` | RA com maior estoque (Pág. 4) |

---

## Página 8 — Apêndice · As 33 RAs

**Tabela completa do território** como referência rápida. Permite ao
candidato conferir qualquer RA específica que não apareceu nas frentes
principais (Defesa, Crescimento, Decisões periféricas).

### Mockup (A4 paisagem)

```
╔════════════════════════════════════════════════════════════════════════╗
║  [logo]  APÊNDICE · AS 33 RAs                                          ║
║          Tabela completa para consulta rápida                          ║
╠════════════════════════════════════════════════════════════════════════╣
║  ▌ COMO LER                                                            ║
║                                                                        ║
║  Tabela ordenada por Status — Reduto primeiro, Sem espaço por último.  ║
║  Dentro de cada Status, ordenada por Performance descendente.          ║
║  As primeiras linhas são as mais importantes pra você; as últimas são  ║
║  território fora do raio de captura.                                   ║
║                                                                        ║
╠════════════════════════════════════════════════════════════════════════╣
║  ┌────────────────────┬──────┬──────┬─────┬───────┬───────┬─────────┐ ║
║  │ Região             │Aptos │Votos │  %  │ Perf. │ Campo │ Status  │ ║
║  ├────────────────────┼──────┼──────┼─────┼───────┼───────┼─────────┤ ║
║  │ Plano Piloto       │ 184k │6.890 │27,0 │ +223% │ +40%  │ ▌Reduto │ ║
║  │ Lago Sul           │  41k │1.853 │ 7,2 │ +289% │ +60%  │ ▌Reduto │ ║
║  │ Lago Norte         │  ... │  ... │ ... │ ...   │ ...   │ ▌Reduto │ ║
║  │ ...                                                                │ ║
║  ├────────────────────┼──────┼──────┼─────┼───────┼───────┼─────────┤ ║
║  │ Park Way           │5,9k  │  144 │ 0,6 │ +109% │ −12%  │ ▌V.P.   │ ║
║  │ ...                                                                │ ║
║  ├────────────────────┼──────┼──────┼─────┼───────┼───────┼─────────┤ ║
║  │ Ceilândia          │ 302k │  ... │ ... │  +2%  │  +6%  │ ▌Esp.   │ ║
║  │ ...                                                                │ ║
║  ├────────────────────┼──────┼──────┼─────┼───────┼───────┼─────────┤ ║
║  │ Recanto das Emas   │  93k │  ... │ ... │ −44%  │ +21%  │ ▌Conqui.│ ║
║  │ ...                                                                │ ║
║  ├────────────────────┼──────┼──────┼─────┼───────┼───────┼─────────┤ ║
║  │ Brazlândia         │  51k │  ... │ ... │ −35%  │ −12%  │ ▌Sem    │ ║
║  │ Itapoã             │  22k │  ... │ ... │ −44%  │ −15%  │ ▌Sem    │ ║
║  │ ... (33 linhas no total)                                           │ ║
║  └────────────────────┴──────┴──────┴─────┴───────┴───────┴─────────┘ ║
║                                                                        ║
║  Legenda Status:                                                       ║
║  ▌Reduto = Reduto consolidado · ▌V.P. = Voto pessoal                  ║
║  ▌Esp. = Esperado · ▌Conqui. = Espaço a conquistar                    ║
║  ▌Sem = Sem espaço pelo campo                                          ║
║                                                                        ║
╠════════════════════════════════════════════════════════════════════════╣
║  Fontes: PDAD 2021 (IPEDF) · TSE 2022. Estrategos.                     ║
╚════════════════════════════════════════════════════════════════════════╝
```

### Conteúdo Camada 1 (texto fixo)

#### Como ler

Tabela ordenada por Status — Reduto consolidado primeiro, Sem espaço pelo campo por último. Dentro de cada Status, ordenada por Performance descendente. As primeiras linhas são as mais importantes pra você; as últimas são território fora do raio de captura.

#### Legenda Status (rodapé da página)

| Sigla | Status |
|---|---|
| Reduto | Reduto consolidado |
| V.P. | Voto pessoal |
| Esp. | Esperado |
| Conqui. | Espaço a conquistar |
| Sem | Sem espaço pelo campo |

### Conteúdo Camada 2 (analítico — varia por candidato)

#### Tabela única — 33 linhas

Lista **todas as 33 RAs do DF**, sem filtro. Colunas:

- Região
- Aptos
- Votos (do candidato)
- % dos votos (frequência relativa)
- Performance
- Força do campo
- Status (badge colorido)

**Ordenação:**
1. Por Status (na ordem: Reduto consolidado → Voto pessoal → Esperado → Espaço a conquistar → Sem espaço pelo campo)
2. Dentro do Status, por Performance descendente

**Layout:** linhas com fundo levemente colorido por bloco de Status (banda visual sutil pra escanear), ou separadores entre os 5 blocos.

#### Cabeçalho da seção

Sem cabeçalho dinâmico — a página é puro apêndice. O "Como ler" e a legenda são fixos.

### Variáveis (Camada 2)

| Variável | Cálculo |
|---|---|
| `RAS_TODAS[]` | as 33 RAs (mesma lista do menu Estratégia) |
| `ordem` | `Status` (categórico ordenado) → `Performance` desc |
| (todas as colunas reaproveitam dados já calculados) | |

### Decisão de espaço

Cabe em uma página A4 paisagem com fonte 8-9pt e linhas compactas (33 linhas + cabeçalho). Se ficar apertado, considerar:
- Reduzir colunas (tirar "Aptos" — informação menos crítica)
- Quebrar em 2 colunas de 17/16 linhas lado a lado
- Usar página A4 retrato para o apêndice (decisão isolada — quebra o padrão paisagem do resto, mas é a página final e pode admitir exceção)

---

## Pendências e ideias em aberto

*(nada em aberto — MVP completa)*
