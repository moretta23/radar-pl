"""Baixa a tabela de resultado.php do Fundamentus e grava dados.json.

Uso:  python scripts/atualizar.py
"""
import json
import re
import ssl
import urllib.request
from datetime import datetime, timedelta, timezone
from html import unescape
from pathlib import Path

URL = "https://fundamentus.com.br/resultado.php"
SAIDA = Path(__file__).resolve().parent.parent / "dados.json"
BRASILIA = timezone(timedelta(hours=-3))

# Ordem das colunas em resultado.php
COLS = ["papel", "cotacao", "pl", "pvp", "psr", "dy", "p_ativo", "p_capgiro",
        "p_ebit", "p_acl", "ev_ebit", "ev_ebitda", "mrg_bruta", "mrg_ebit",
        "mrg_liq", "liq_corr", "roic", "roe", "liq2m", "patrim", "div_pl",
        "cresc5a"]
MANTER = ["cotacao", "pl", "pvp", "dy", "roe", "mrg_liq", "liq2m", "div_pl", "ev_ebit"]


def baixar():
    req = urllib.request.Request(URL, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9",
    })
    with urllib.request.urlopen(req, timeout=60, context=ssl.create_default_context()) as r:
        return r.read().decode("iso-8859-1")


def numero(txt):
    txt = re.sub(r"<[^>]+>", "", txt).strip().replace("%", "")
    txt = txt.replace(".", "").replace(",", ".")
    try:
        return float(txt)
    except ValueError:
        return None


def extrair(html):
    corpo = html.split("<tbody>", 1)[1].split("</tbody>", 1)[0]
    acoes = []
    for linha in re.findall(r"<tr[^>]*>(.*?)</tr>", corpo, re.S):
        celulas = re.findall(r"<td[^>]*>(.*?)</td>", linha, re.S)
        if len(celulas) != len(COLS):
            continue
        nome = re.search(r'title="([^"]*)"', celulas[0])
        item = {"t": re.sub(r"<[^>]+>", "", celulas[0]).strip(),
                "n": unescape(nome.group(1)) if nome else ""}
        for col, cel in zip(COLS[1:], celulas[1:]):
            if col in MANTER:
                item[col] = numero(cel)
        acoes.append(item)
    return acoes


def main():
    acoes = extrair(baixar())
    if len(acoes) < 100:
        raise SystemExit(f"Só {len(acoes)} linhas lidas: o layout do Fundamentus mudou?")
    dados = {"atualizado": datetime.now(BRASILIA).strftime("%d/%m/%Y %H:%M"), "acoes": acoes}
    SAIDA.write_text(json.dumps(dados, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    n = sum(1 for a in acoes if a["pl"] is not None and 0 < a["pl"] <= 7)
    print(f"{len(acoes)} papéis lidos, {n} com 0 < P/L <= 7 -> {SAIDA.name}")


if __name__ == "__main__":
    main()
