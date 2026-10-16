"""Baixa a tabela de resultado.php do Fundamentus (com o setor de cada papel)
e a Selic meta do Banco Central, e grava dados.json.

Uso:  python scripts/atualizar.py
"""
import json
import re
import ssl
import time
import urllib.request
from datetime import datetime, timedelta, timezone
from html import unescape
from pathlib import Path

URL = "https://fundamentus.com.br/resultado.php"
URL_SETORES = "https://fundamentus.com.br/buscaavancada.php"
SAIDA = Path(__file__).resolve().parent.parent / "dados.json"
SETORES = Path(__file__).resolve().parent.parent / "setores.json"
BRASILIA = timezone(timedelta(hours=-3))
# Série 432 do SGS/Banco Central: meta da taxa Selic (% ao ano)
URL_SELIC = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados/ultimos/1?formato=json"

# Ordem das colunas em resultado.php
COLS = ["papel", "cotacao", "pl", "pvp", "psr", "dy", "p_ativo", "p_capgiro",
        "p_ebit", "p_acl", "ev_ebit", "ev_ebitda", "mrg_bruta", "mrg_ebit",
        "mrg_liq", "liq_corr", "roic", "roe", "liq2m", "patrim", "div_pl",
        "cresc5a"]
MANTER = ["cotacao", "pl", "pvp", "dy", "roe", "mrg_liq", "liq2m", "div_pl", "ev_ebit", "cresc5a"]


def baixar(url=URL):
    req = urllib.request.Request(url, headers={
        # Com um User-Agent de Chrome completo o Fundamentus devolve as páginas
        # por setor vazias; este par de cabeçalhos funciona para todas.
        "User-Agent": "Mozilla/5.0",
        "Accept": "*/*",
    })
    with urllib.request.urlopen(req, timeout=60, context=ssl.create_default_context()) as r:
        return r.read().decode("iso-8859-1")


def selic():
    """Selic meta e o "P/L do Tesouro" (100 / taxa). None se o BC não responder."""
    try:
        req = urllib.request.Request(URL_SELIC, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30, context=ssl.create_default_context()) as r:
            taxa = float(json.load(r)[-1]["valor"])
        return {"selic": taxa, "pl": round(100 / taxa, 2)}
    except Exception as e:
        print("Aviso: Selic não obtida:", e)
        return None


def setores():
    """{papel: nome do setor}, guardado em setores.json e rebuscado no máximo
    uma vez por semana (o Fundamentus bloqueia rajadas de pedidos).
    Busca resultado.php?setor=N para cada setor, com pausas; se uma página vier
    vazia, mantém o que já se sabia daquele papel."""
    try:
        cache = json.loads(SETORES.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        cache = {"atualizado": "", "papeis": {}}
    mapa = dict(cache.get("papeis", {}))
    hoje = datetime.now(BRASILIA).date()
    try:
        idade = (hoje - datetime.strptime(cache["atualizado"], "%Y-%m-%d").date()).days
    except ValueError:
        idade = 999
    if mapa and idade < 7:
        return mapa
    try:
        html = baixar(URL_SETORES)
        bloco = re.search(r'<select[^>]*name="setor"[^>]*>(.*?)</select>', html, re.S).group(1)
        lista = re.findall(r'<option value="(\d+)"[^>]*>([^<]+)', bloco)
        lidos = 0
        for num, nome in lista:
            time.sleep(3)
            pagina = baixar(f"{URL}?setor={num}")
            if not pagina:
                print(f"Aviso: setor {num} veio vazio (bloqueio?); parando e mantendo o anterior")
                break
            for papel in re.findall(r"detalhes\.php\?papel=([A-Z0-9]+)", pagina):
                mapa[papel] = unescape(nome).strip()
            lidos += 1
        if lidos == len(lista):
            cache["atualizado"] = hoje.isoformat()
        print(f"{lidos} de {len(lista)} setores lidos, {len(mapa)} papéis com setor")
    except Exception as e:
        print("Aviso: setores não obtidos:", e)
    cache["papeis"] = mapa
    SETORES.write_text(json.dumps(cache, ensure_ascii=False, indent=0, sort_keys=True), encoding="utf-8")
    return mapa


def numero(txt):
    txt = re.sub(r"<[^>]+>", "", txt).strip().replace("%", "")
    txt = txt.replace(".", "").replace(",", ".")
    try:
        return float(txt)
    except ValueError:
        return None


def extrair(html):
    if "<tbody>" not in html:
        raise SystemExit("Fundamentus devolveu a página vazia (bloqueio temporário?); dados.json mantido.")
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
    setor = setores()
    for a in acoes:
        if a["t"] in setor:
            a["s"] = setor[a["t"]]
    dados = {"atualizado": datetime.now(BRASILIA).strftime("%d/%m/%Y %H:%M"),
             "tesouro": selic(), "acoes": acoes}
    SAIDA.write_text(json.dumps(dados, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    n = sum(1 for a in acoes if a["pl"] is not None and 0 < a["pl"] <= 7)
    print(f"{len(acoes)} papéis lidos, {n} com 0 < P/L <= 7 -> {SAIDA.name}")


if __name__ == "__main__":
    main()
