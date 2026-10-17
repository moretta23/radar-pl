# Mais Tempo

App de celular (PWA) que lista as ações da B3 com P/L baixo, com dados de
[fundamentus.com.br](https://www.fundamentus.com.br/resultado.php).

**No ar em https://vendas.moretta.com.br/metodo/** (VPS). O endereço do GitHub
Pages mostra só um aviso de mudança.

- `app/`: as telas do app (index.html, manifest, sw.js, ícones).
- `servidor/`: o servidor da VPS (serve o app e baixa os dados às 19h nos dias úteis).
- `scripts/atualizar.py`: baixa o Fundamentus e a Selic e grava `dados.json`.
- `scripts/gerar_icones.py` e `scripts/gerar_qrcode.py`: ícones e QR code em `app/icons/`.
- `index.html` e `sw.js` da raiz: aviso de mudança de endereço (GitHub Pages).

Detalhes, publicação e pontos de atenção: `NOTAS.md`.
