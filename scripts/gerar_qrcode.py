"""Gera icons/qrcode.png com o endereço do app e o ícone no meio.

Uso:  python scripts/gerar_qrcode.py
"""
from pathlib import Path

import qrcode
from PIL import Image, ImageDraw

LINK = "https://vendas.moretta.com.br/metodo/"
PASTA = Path(__file__).resolve().parent.parent / "app" / "icons"
COR = (17, 17, 17)

qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=14, border=3)
qr.add_data(LINK)
img = qr.make_image(fill_color=COR, back_color="white").convert("RGB").resize((600, 600), Image.NEAREST)

# Ícone no meio, com moldura branca arredondada (o nível H aguenta cobrir o centro)
lado = 150
moldura = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
ImageDraw.Draw(moldura).rounded_rectangle((0, 0, lado - 1, lado - 1), radius=32, fill="white")
icone = Image.open(PASTA / "icon-192.png").convert("RGBA").resize((lado - 16, lado - 16), Image.LANCZOS)
mascara = Image.new("L", icone.size, 0)
ImageDraw.Draw(mascara).rounded_rectangle((0, 0, icone.size[0] - 1, icone.size[1] - 1), radius=26, fill=255)
moldura.paste(icone, (8, 8), mascara)
img.paste(moldura, ((600 - lado) // 2, (600 - lado) // 2), moldura)
img.save(PASTA / "qrcode.png")
print("QR para", LINK)
