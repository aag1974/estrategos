# API de dados estática do Estrategos — Design (implementado)

**Data:** 2026-06-01
**Status:** Implementado

## Objetivo

Expor a base do Estrategos como JSON estático para um parceiro consumir
programaticamente (inclusive por uma IA), fora do dashboard.

## Decisões fechadas com o usuário

1. **Tipo:** API de **dados** (não auth, não gestão de usuários).
2. **Formato:** **arquivo único com tudo** (não múltiplos endpoints).
3. **Acesso:** **caminho com token** (`/api/<token>/estrategos.json`). NÃO é
   autenticação real — o repo é público e o dashboard já embute a mesma base;
   o token só tira a URL da vitrine. Caveat registrado e aceito pelo usuário.
4. **Consumidor:** uma IA do parceiro → acompanha um prompt
   (`docs/PROMPT_API_IA.md`) que descreve o schema.

## Arquitetura

Sem servidor. O `gerar_estrategos.py`, ao final do build (passo 5/5), grava
`api/<token>/estrategos.json`. `git commit` + `push` → GitHub Pages serve em
`https://estrategos.opiniao.inf.br/api/<token>/estrategos.json`, com
`Access-Control-Allow-Origin: *` (consumo cross-origin liberado).

- O token vem de `api_token.txt` (gerado uma vez com `secrets.token_hex(16)`,
  reusado entre builds → URL estável).
- JSON **compacto** (`separators=(",",":")`) — ~5,3 MB. Indentado dobrava o
  tamanho (~14,6 MB) sem ganho para consumo por código.
- Sai do mesmo build do dashboard → sempre em sincronia com o que ele mostra.

## Conteúdo do arquivo

Top-level: `schema, produto, descricao, gerado_em, fontes, contagens,
candidatos, ras, votos_eleitos, metas_campo, pesquisas, geo`.

- `candidatos[]`: `cands_detalhados` + `slug` (único; colisão → `-2`, `-3`…).
- `ras{}`: estrutura de `montar_dados()` (socioeconômico + eleitoral + `votos` +
  `spe` + `narrativa`).
- `votos_eleitos`, `metas_campo`: podem vir vazios se faltar a base de eleitos.
- `pesquisas`: `pesquisas_df.json`. `geo`: GeoJSON das 33 RAs.

Schema documentado em detalhe em `docs/PROMPT_API_IA.md`.

## Verificação

1. `python3 gerar_estrategos.py` → cria `api/<token>/estrategos.json` (5,3 MB).
2. JSON válido (`json.load`); `contagens` batem (792 candidatos, 33 RAs).
3. Slugs únicos. Campos `idx`/`status`/`spe` conferidos contra a interpretação
   do prompt.
4. Pós-deploy: `curl -I` na URL confirma `Access-Control-Allow-Origin: *`.

## Fora de escopo (futuro)

- Autenticação real / API keys (exigiria runtime).
- Arquivos por-candidato (`candidatos/<slug>.json`) — descartado a favor do
  arquivo único.
- Filtros via query string (impossível em arquivo estático).
