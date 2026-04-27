# Estrategos

Painel de inteligência política para análise eleitoral do Distrito Federal.
Combina dados socioeconômicos (PDAD 2021) com resultados eleitorais (TSE 2022)
para mapear como o voto se distribui no território — e o que isso significa
para cada candidato.

Solução de Inteligência Política da **Opinião Informação Estratégica**.

---

## Conteúdo

```
fase4_v2.py                   # Build base do dashboard (HTML + JS + dados)
injeta_geopolitica.py         # Adiciona o módulo Geopolítica > Território
injeta_candidato.py           # Adiciona o módulo Geopolítica > Candidato + Paper PDF
gerar_credencial.py           # Helper para criar/atualizar usuários do login
exemplo_relatorio_pdf.py      # Gera relatório PDF de candidato (standalone)
exemplo_contexto_pdf.py       # Gera relatório PDF de contexto DF (standalone)

fase3c_campo_politico.py      # Pipeline de cálculo do campo político por RA
extrair_votos_candidato_ra.py # Extração de votação por candidato × RA

outputs_fase2/                # Tabela mestre por RA (curada)
outputs_fase3/                # IPE + clusters + narrativas por RA
outputs_fase3c/               # Votos por campo + por candidato × RA

candidatos_2022_DF.csv        # Lista de candidatos DF 2022 (TSE)
Limite_RA_20190.json          # GeoJSON das 33 regiões administrativas
logo_opiniao.png              # Logomarca da Opinião

DECISOES_PROJETO.md           # Decisões canônicas (vocabulário, UX, métricas)
STORYTELLING_SPEC.md          # Especificação narrativa
SPE_PROJETO.md                # Histórico do projeto
```

---

## Como rodar

### 1. Crie suas credenciais de acesso

O dashboard tem uma tela de login (decorativa, client-side). Para
configurar usuários autorizados:

```bash
python3 gerar_credencial.py
```

O script pede usuário e senha, e cria/atualiza `credenciais.json`.
Esse arquivo **não é versionado** — fica só na sua máquina.

> **Atenção:** o login é uma "porta com fechadura simbólica" para evitar
> acesso casual. Quem abrir o devtools encontra o hash. Use para limitar
> acesso a clientes confiáveis, não como segurança real.

### 2. Construa o dashboard

A cadeia de build tem 3 etapas (ordem importa):

```bash
python3 fase4_v2.py            # gera dashboard_spe_df.html (base)
python3 injeta_geopolitica.py  # gera dashboard_com_geo.html (+ Território)
python3 injeta_candidato.py    # gera dashboard_com_candidato.html (final)
```

Abra `dashboard_com_candidato.html` no browser.

### 3. Login

Use as credenciais criadas no passo 1.

---

## Geração de PDFs (relatórios)

Três caminhos no dashboard:

- **Geopolítica > Território** · botão "🖨 Imprimir": gera PDF de 2 páginas
  (paper de contexto DF + visual do mapa).
- **Geopolítica > Candidato** · botão "🖨 Imprimir": gera PDF de 2 páginas
  (paper analítico do candidato + visual do mapa do candidato).
- **Contexto > Candidatos** · botão "🖨 Relatório" no painel direito:
  gera PDF de 1 página com o paper analítico do candidato.

Tudo em A4 paisagem.

Há também os scripts standalone para gerar amostras sem rodar o dashboard:

```bash
python3 exemplo_contexto_pdf.py            # gera relatorio_contexto_DF.html
python3 exemplo_relatorio_pdf.py DAMARES   # gera relatorio_DAMARES.html
```

Abrir no browser e Cmd+P → Salvar como PDF.

---

## Dados não versionados

Os dados brutos (TSE 2022 e PDAD 2021) **não estão no repositório** por
serem pesados (~5GB total) e públicos. As versões curadas que o pipeline
produz (em `outputs_fase2/`, `outputs_fase3/`, `outputs_fase3c/`) estão
versionadas e bastam para construir o dashboard.

Para refazer todo o pipeline a partir das fontes:

- **TSE 2022**: dados de votação por seção do DF, baixe em
  <https://dadosabertos.tse.jus.br/>
- **PDAD 2021**: tabulações por RA do IPEDF, em
  <https://www.ipe.df.gov.br/pdad/>

---

## Vocabulário canônico

Veja [DECISOES_PROJETO.md](DECISOES_PROJETO.md) para o vocabulário de
produto (Performance, Status, Reduto consolidado, Voto pessoal, Aliança
eleitoral, Dobradinha, etc.) e as decisões de UX/dados.

---

## Stack

Python 3 (pandas, numpy) · HTML/CSS/JS · Leaflet · sem dependências server-side.
