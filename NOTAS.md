# Método Tempo: notas do projeto (para melhorias futuras)

Criado em 15/10/2026 como "Radar P/L"; renomeado para "Método Tempo" em 16/10/2026. App no ar: **https://vendas.moretta.com.br/metodo/** (VPS, desde 17/10/2026).
Endereço antigo https://moretta23.github.io/radar-pl/ agora só mostra o aviso
"o Método Tempo mudou de endereço" (`index.html` e `sw.js` da raiz, que também
apagam o app antigo guardado nos celulares). As telas do app ficam em `app/`.
Repositório: https://github.com/moretta23/radar-pl
Conversa completa que criou o app: `D:\Dropbox\CLAUDE\App de Metodo Tempo\conversa\`.

## Na VPS (endereço principal, desde 17/10/2026)

- VPS 178.104.158.79, usuário `moretta`, chave `~/.ssh/id_vps_claude`. Container
  `metodo-app` em `~/apps/metodo-app` (docker compose + Caddy, rota `/metodo/`),
  no mesmo esquema do Simulador de FII.
- `servidor/app.py` serve as telas e o `dados.json` da pasta `~/apps/metodo-app/dados`,
  e roda `scripts/atualizar.py` de segunda a sexta às 19h (Brasília). Se o
  Fundamentus falhar, mantém os dados anteriores. Ver erros:
  `cd ~/apps && docker compose logs --tail 50 metodo-app`.
- Atualizar na hora: `docker compose exec -T metodo-app python atualizar.py`.
- Publicar mudanças do app: `sh servidor/montar.sh PASTA` monta a pasta, enviar
  para `~/apps/metodo-app` (sem apagar `dados/`) e
  `docker compose up -d --build metodo-app`. Aumentar o `CACHE` do `sw.js`.
- QR code: `python scripts/gerar_qrcode.py` (endereço da VPS).

## Como funcionava no GitHub (desligado em 17/10/2026)

- O site do Fundamentus não permite que um app no celular leia os dados direto
  (bloqueio de CORS). Por isso os dados são baixados no servidor do GitHub e
  gravados em `dados.json`, que o app lê.
- `.github/workflows/atualizar.yml` rodava `scripts/atualizar.py` nos dias úteis
  às 19h; o agendamento foi tirado (só roda à mão, em **Actions**).
- O script busca: a tabela `resultado.php` do Fundamentus; a Selic meta no
  Banco Central (série SGS 432); e o setor de cada papel (`resultado.php?setor=N`
  para os 43 setores), guardado em `setores.json` e rebuscado só 1x por semana.
- O app é um PWA: `manifest.webmanifest` (nome, cores, ícones) e `sw.js`
  (funciona sem internet, sempre tenta buscar dados novos primeiro).
- GitHub Pages publica a branch `main`, pasta raiz.

## O que o app tem (16/10/2026)

- Visual (17/10/2026): mesma cara do Simulador de FII, tema escuro com a paleta
  Vamos Juntos · Vivendo Capital (preto, laranja #F6B651, verde #74D352), fontes
  Nunito + Permanent Marker. Ícone: barras verdes, linha de corte laranja, fundo preto.

- Topo: ícone + "Método Tempo", contagem de empresas e botão de QR code
  (janela com QR, "Enviar link" e instruções de instalação Android/iPhone).
- Quadro amarelo "P/L do Tesouro hoje" = 100 ÷ Selic meta, com a Selic ao lado.
- Busca por ticker ou nome.
- Barras: P/L máx. (1 a 30, padrão 7); P/VP mín. e máx. (0 a 5, "livre" nas
  pontas; com limite ativo, P/VP negativo sai); Dív/PL máx. (0 a 5, passo 0,1,
  padrão 0,5); ROE mín. e Margem mín. (0% a 40%, "livre" em 0).
- Setor (lista dos setores do Fundamentus), Ordem (P/L, DY, ROE, margem,
  liquidez, P/VP), Liquidez (padrão ≥ R$ 100 mil/dia).
- Quadrinhos: "Só P/L positivo" (marcado) e "Receita crescendo (5 anos)"
  (Cresc. Rec. 5a > 0).
- Fichas: ticker (link para o Fundamentus), nome, setor, P/L e cotação, régua
  do P/L, e 7 indicadores: DY, P/VP, ROE, margem líq., Dív/PL, Rec. 5 anos, liquidez.
- Os filtros escolhidos ficam salvos no celular de cada pessoa.

## Pontos de atenção

- O Fundamentus bloqueia por alguns minutos quem faz muitos pedidos seguidos,
  e devolve páginas vazias para User-Agent de Chrome completo: o script usa
  `User-Agent: Mozilla/5.0` + `Accept: */*` e pausas de 3 s entre setores.
  Se a página principal vier vazia, o script para sem apagar o `dados.json`.
- O Fundamentus aceitou o acesso do GitHub (16/10/2026) e da VPS (17/10/2026).
- Nome no celular: quem instalou como "Radar P/L" só vê "Método Tempo" depois que
  o Android atualizar o app (pode levar até 1 dia, às vezes pede confirmação) ou
  removendo e instalando de novo. No iPhone o nome fica fixo: tem que remover e
  adicionar de novo à Tela de Início.
- Bancos aparecem com Dív/PL 0,00 (o Fundamentus não calcula para bancos).
- Workflows agendados do GitHub são desativados após 60 dias sem atividade
  no repositório; os commits diários mantêm ativo.
- Ao mudar arquivos do app, aumente o número em `CACHE = "radar-pl-v16"` no
  `app/sw.js` para os celulares pegarem a versão nova.
- O histórico do git fica fora do Dropbox, em
  `C:\Users\NOTEBOOK\git-repos\metodo-tempo.git` (o Dropbox travava os
  arquivos internos do git). A pasta `git-antigo-radar` é uma cópia velha e
  pode ser apagada.
- Para testar antes de publicar: `sh servidor/montar.sh PASTA`, depois, dentro
  de PASTA, `DADOS_DIR=PASTA/dados PORTA=8766 python app.py` e abrir
  `http://localhost:8766` (ou `http://192.168.15.3:8766` no celular).

## Ideias de melhoria

- Detalhe ao tocar na ficha, com EV/EBIT (já está no `dados.json`).
- Marcar nas fichas as empresas com P/L abaixo do P/L do Tesouro.
- Filtros extras: DY mínimo, excluir bancos/holdings.
- Histórico: guardar um arquivo por dia e mostrar quem entrou/saiu da lista.
- Versão em inglês/espanhol para amigos de fora.
- Ranking combinado (ex.: "Fórmula Mágica": EV/EBIT + ROIC).
