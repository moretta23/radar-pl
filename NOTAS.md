# Método Tempo: notas do projeto (para melhorias futuras)

Criado em 15/10/2026 como "Radar P/L"; renomeado para "Método Tempo" em 16/10/2026. App no ar: https://moretta23.github.io/radar-pl/
Repositório: https://github.com/moretta23/radar-pl

## Como funciona

- O site do Fundamentus não permite que um app no celular leia os dados direto
  (bloqueio de CORS). Por isso os dados são baixados no servidor do GitHub e
  gravados em `dados.json`, que o app lê.
- `.github/workflows/atualizar.yml` roda `scripts/atualizar.py` de segunda a
  sexta às 22h UTC (19h de Brasília) e faz commit do `dados.json` novo.
  Para rodar na hora: aba **Actions** → *Atualizar dados* → **Run workflow**.
- O app é um PWA: `manifest.webmanifest` (nome, cores, ícones) e `sw.js`
  (funciona sem internet, sempre tenta buscar dados novos primeiro).
- GitHub Pages publica a branch `main`, pasta raiz.

## Decisões tomadas

- Filtro principal: P/L ≤ 7 (ajustável de 1 a 15 no app).
- Por padrão mostra só P/L positivo (P/L negativo = empresa com prejuízo).
- Liquidez padrão ≥ R$ 100 mil/dia, para tirar papéis sem negociação.
- Colunas guardadas do Fundamentus: cotação, P/L, P/VP, DY, ROE, margem
  líquida, liquidez 2 meses, dívida líq./patrimônio, EV/EBIT.
  (A tabela tem 22 colunas; a lista completa está em `COLS` no atualizar.py.)
- Ícone: barras de P/L com linha de corte; as abaixo da linha em verde.
  Para mudar, edite `scripts/gerar_icones.py` e rode `python scripts/gerar_icones.py`.

## Pontos de atenção

- Ainda não confirmado se o Fundamentus aceita acesso vindo dos servidores do
  GitHub. Se a Action falhar, alternativa: rodar `scripts/atualizar.py` no
  computador e dar `git push` (havia uma tarefa agendada no app do Claude,
  "Atualizar Radar P/L Fundamentus", hoje pausada).
- Workflows agendados do GitHub são desativados após 60 dias sem atividade
  no repositório; os commits diários mantêm ativo.
- Ao mudar arquivos do app, aumente o número em `CACHE = "radar-pl-v2"` no `sw.js`
  (v3, v4…) para os celulares pegarem a versão nova.

## Ideias de melhoria

- Mostrar EV/EBIT, margem e dívida (já estão no `dados.json`) num detalhe ao tocar.
- Filtros extras: DY mínimo, ROE mínimo, excluir bancos/holdings.
- Histórico: guardar um arquivo por dia e mostrar quem entrou/saiu da lista.
- Versão em inglês/espanhol para amigos de fora.
- Ranking combinado (ex.: "Fórmula Mágica": EV/EBIT + ROIC).
