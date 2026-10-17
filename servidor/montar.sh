#!/bin/sh
# Monta a pasta que vai para a VPS (~/apps/metodo-app): servidor + telas do app + dados iniciais.
# Uso: sh servidor/montar.sh DESTINO
set -e
APP="$(cd "$(dirname "$0")/.." && pwd)"
D="$1"
rm -rf "$D" && mkdir -p "$D/static" "$D/inicial"
cp "$APP/servidor/app.py" "$APP/servidor/Dockerfile" "$APP/servidor/requirements.txt" "$D/"
cp "$APP/scripts/atualizar.py" "$D/"
cp "$APP/index.html" "$APP/manifest.webmanifest" "$APP/sw.js" "$D/static/"
cp -r "$APP/icons" "$D/static/"
cp "$APP/dados.json" "$APP/setores.json" "$D/inicial/"
printf 'dados\n__pycache__\n' > "$D/.dockerignore"
