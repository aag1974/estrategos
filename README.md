# Estrategos

Painel de inteligência política para análise eleitoral do Distrito Federal.
Combina dados socioeconômicos (PDAD 2021) com resultados eleitorais (TSE 2022)
para mapear como o voto se distribui no território — e o que isso significa
para cada candidato.

Solução de Inteligência Política da **Opinião Informação Estratégica**.

---

## Conteúdo

```
gerar_estrategos.py           # Build unificado: lê template, monta dados, escreve index.html
estrategos_template.html      # Template com 10 placeholders preenchidos por gerar_estrategos
gerar_credencial.py           # Helper para criar/atualizar usuários do login
gerar_playbook_dados.py       # Gera JSON do playbook por candidato

coletor_pesquisas.py          # Baixa pesquisas TSE Dados Abertos, filtra UF, gera JSON canônico
extrair_pesquisas.py          # Claude Haiku lê os questionários PDF e extrai cenários

fase3c_campo_politico.py      # Pipeline de cálculo do campo político por RA
extrair_votos_candidato_ra.py # Extração de votação por candidato × RA

outputs_fase2/                # Tabela mestre por RA (curada)
outputs_fase3/                # IPE + clusters + narrativas por RA
outputs_fase3c/               # Votos por campo + por candidato × RA

candidatos_2022_DF.csv        # Lista de candidatos DF 2022 (TSE)
Limite_RA_20190.json          # GeoJSON das 33 regiões administrativas
logo_opiniao.png              # Logomarca da Opinião

docs/                         # Decisões, metodologia, storytelling, inventário
_arquivo/                     # Scripts/HTMLs sem referência ativa (histórico)
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

```bash
python3 gerar_estrategos.py    # gera index.html
```

O script lê `estrategos_template.html` (template com 9 placeholders),
monta os dados (D, A5_CANDS, GEO_DATA, GC_DATA, etc.) a partir dos
`outputs_fase*/` + `dados_tse_cache/` + `Limite_RA_20190.json`, e escreve
o `index.html` final.

Abra `index.html` no browser. O nome `index.html` é exigido por
hospedagens estáticas (GitHub Pages, Cloudflare Pages, Netlify) — basta
publicar a pasta diretamente.

### 3. Login

Use as credenciais criadas no passo 1.

### 4. (Opcional) Atualizar o catálogo de pesquisas

A seção **Ferramentas › Clipping de Pesquisas** lê o catálogo TSE
embarcado pelo `gerar_estrategos.py` a partir de
`outputs_pesquisas/pesquisas_df.json`. Para atualizar:

```bash
# 1. Baixa o ZIP CKAN do TSE, filtra DF, atualiza o JSON
python3 coletor_pesquisas.py --uf DF

# Para baixar também os PDFs dos questionários (~377 MB → extrai só DF)
python3 coletor_pesquisas.py --uf DF --baixar-pdfs

# 2. (Opcional) Roda extração IA dos questionários PDF para extrair
#    cargos, cenários e candidatos testados
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
python3 extrair_pesquisas.py --uf DF

# 3. Re-gera o dashboard com o catálogo atualizado
python3 gerar_estrategos.py
```

A extração IA (passo 2) é opcional. Sem ela, o catálogo mostra metadata
das pesquisas (instituto, datas, cargos, plano amostral) e link pro
PesqEle TSE; com ela, mostra também os cenários estruturados (lista de
candidatos testados em cada cargo, tipo estimulada/espontânea/rejeição).

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

Veja [docs/DECISOES_PROJETO.md](docs/DECISOES_PROJETO.md) para o vocabulário de
produto (Performance, Status, Reduto consolidado, Voto pessoal, Aliança
eleitoral, Dobradinha, etc.) e as decisões de UX/dados.

---

## Stack

Python 3 (pandas, numpy) · HTML/CSS/JS · Leaflet · sem dependências server-side.
