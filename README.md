# Método Tempo

App de celular (PWA) que lista as ações da B3 com P/L até 7, com dados de
[fundamentus.com.br](https://www.fundamentus.com.br/resultado.php).

- `index.html`: o app (filtros de P/L, liquidez, busca e ordenação).
- `dados.json`: os dados, regravados todo dia útil às 19h (Brasília) pelo
  workflow `.github/workflows/atualizar.yml`.
- `scripts/atualizar.py`: baixa o Fundamentus e grava `dados.json`.
- `scripts/gerar_icones.py`: desenha os ícones em `icons/`.

## Publicar

1. Envie esta pasta para um repositório no GitHub.
2. Em **Settings → Pages**, escolha *Deploy from a branch*, branch `main`, pasta `/ (root)`.
3. O app fica em `https://<seu-usuario>.github.io/<repositorio>/`.

## Instalar no Android

Abra o endereço no Chrome, toque nos três pontinhos e escolha **Instalar app**
(ou **Adicionar à tela inicial**).

## Atualizar à mão

Na aba **Actions** do repositório, abra *Atualizar dados* e clique em **Run workflow**.
