"""Desenha o ícone do Método Tempo: barras de P/L com uma linha de corte;
as barras abaixo da linha (as baratas) ficam em verde-menta.

Uso:  python scripts/gerar_icones.py
"""
from pathlib import Path
from PIL import Image, ImageDraw

SAIDA = Path(__file__).resolve().parent.parent / "app" / "icons"
S = 4  # supersampling para bordas suaves

FUNDO_TOPO = (10, 58, 40)
FUNDO_BASE = (6, 33, 23)
MENTA = (95, 227, 161)
APAGADA = (255, 255, 255, 60)
LINHA = (255, 214, 120)


def gradiente(tam):
    img = Image.new("RGBA", (tam, tam))
    px = img.load()
    for y in range(tam):
        t = y / (tam - 1)
        cor = tuple(round(a + (b - a) * t) for a, b in zip(FUNDO_TOPO, FUNDO_BASE)) + (255,)
        for x in range(tam):
            px[x, y] = cor
    return img


def desenho(tam, escala):
    """Barras + linha de corte, centradas, ocupando `escala` do lado."""
    camada = Image.new("RGBA", (tam, tam), (0, 0, 0, 0))
    d = ImageDraw.Draw(camada)
    area = tam * escala
    x0 = (tam - area) / 2
    base = (tam + area) / 2 - area * 0.04
    alturas = [0.42, 0.78, 0.30, 0.95, 0.52]   # fração da área
    corte = 0.58                               # linha "P/L = 7"
    n = len(alturas)
    larg = area / (n * 1.55)
    vao = (area - n * larg) / (n - 1)
    r = larg * 0.28
    for i, h in enumerate(alturas):
        bx = x0 + i * (larg + vao)
        topo = base - area * h
        cor = MENTA if h <= corte else APAGADA
        d.rounded_rectangle([bx, topo, bx + larg, base], radius=r, fill=cor)
    # linha de corte tracejada
    yl = base - area * corte
    esp = area * 0.025
    traco, gap = area * 0.07, area * 0.04
    x = x0 - area * 0.04
    while x < x0 + area * 1.04:
        d.rounded_rectangle([x, yl - esp / 2, min(x + traco, x0 + area * 1.04), yl + esp / 2],
                            radius=esp / 2, fill=LINHA)
        x += traco + gap
    return camada


def icone(tam, maskable=False, cantos=True):
    g = tam * S
    img = gradiente(g)
    img.alpha_composite(desenho(g, 0.56 if maskable else 0.66))
    if cantos and not maskable:
        mask = Image.new("L", (g, g), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, g - 1, g - 1], radius=g * 0.22, fill=255)
        img.putalpha(mask)
    return img.resize((tam, tam), Image.LANCZOS)


def main():
    SAIDA.mkdir(exist_ok=True)
    icone(192).save(SAIDA / "icon-192.png")
    icone(512).save(SAIDA / "icon-512.png")
    icone(512, maskable=True).save(SAIDA / "maskable-512.png")
    icone(180, cantos=False).convert("RGB").save(SAIDA / "apple-touch-icon.png")
    icone(48).save(SAIDA / "favicon.png")
    print("ícones gerados em", SAIDA)


if __name__ == "__main__":
    main()
