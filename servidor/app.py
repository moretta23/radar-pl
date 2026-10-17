"""
Mais Tempo (PWA) no servidor da VPS, em https://vendas.moretta.com.br/metodo/

- Serve as telas do app (static/) e o dados.json guardado em DADOS_DIR.
- Roda scripts/atualizar.py (Fundamentus + Selic) todo dia útil às 19h (Brasília).
  Ao iniciar, se o dados.json for anterior ao último fechamento, atualiza na hora.
- Acesso por telefone (desde 17/10/2026; antes era CPF): a MESMA lista do Simulador de FII (bot @LiberaFii_bot). Este servidor
  não guarda telefones: pergunta ao servidor do FII (/api/acesso/*), com a senha ACESSO_SEGREDO.

Variáveis de ambiente:
  DADOS_DIR       pasta gravável de dados.json e setores.json   padrão: /dados
  HORA            horário da atualização (HH:MM, Brasília)      padrão: 19:00
  PORTA           porta HTTP                                    padrão: 8000
  EXIGIR_CPF      1 exige telefone liberado                          padrão: 1
  ACESSO_URL      controle de acesso do FII                     padrão: http://fii-app:8000/api/acesso
  ACESSO_SEGREDO  senha entre os servidores (a mesma do .env do fii-app)
"""
import hashlib
import json
import logging
import os
import shutil
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from flask import Flask, jsonify, request, send_from_directory

BASE = Path(__file__).parent
DADOS = Path(os.getenv("DADOS_DIR", "/dados"))
os.environ["DADOS_DIR"] = str(DADOS)  # atualizar.py lê a pasta daqui
import atualizar  # noqa: E402

FUSO = ZoneInfo("America/Sao_Paulo")
HORA, MINUTO = (int(x) for x in os.getenv("HORA", "19:00").split(":"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("metodo")
logging.getLogger("apscheduler").setLevel(logging.WARNING)
app = Flask(__name__, static_folder=None)

EXIGIR_CPF = os.getenv("EXIGIR_CPF", "1") == "1"
ACESSO_URL = os.getenv("ACESSO_URL", "http://fii-app:8000/api/acesso").rstrip("/")
ACESSO_SEGREDO = os.getenv("ACESSO_SEGREDO", "").strip()
APP_ACESSO = "metodo"  # nome deste app na lista de acesso
_conferidos: dict = {}  # (hash da chave, aparelho) -> até quando vale a última conferência ok


# ------------------------------------------------------------ acesso por telefone (lista do FII)

def _servico(caminho: str, corpo: dict):
    """Chama o controle de acesso do FII. Devolve (status, json); 503 se ele não responder."""
    req = urllib.request.Request(f"{ACESSO_URL}/{caminho}", json.dumps({**corpo, "app": APP_ACESSO}).encode(),
                                 {"Content-Type": "application/json", "X-Acesso-Segredo": ACESSO_SEGREDO})
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read() or b"{}")
        except ValueError:
            return e.code, {"erro": "servico_acesso"}
    except Exception as e:  # noqa: BLE001
        log.warning("Controle de acesso fora do ar: %s", e)
        return 503, {"erro": "servico_acesso"}


def _sem_cache(resp, status=200):
    resp.headers["Cache-Control"] = "no-store"
    return resp, status


def _erro_acesso():
    """None se o telefone do celular está liberado; senão a resposta de erro."""
    if not EXIGIR_CPF:
        return None
    chave = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    aparelho = request.headers.get("X-Aparelho", "")
    if not chave:
        return _sem_cache(jsonify(erro="sem_chave"), 401)
    k = (hashlib.sha256(chave.encode()).hexdigest(), aparelho)
    if _conferidos.get(k, 0) > time.time():
        return None
    status, r = _servico("conferir", {"chave": chave, "aparelho": aparelho})
    if status == 200 and r.get("ok"):
        _conferidos[k] = time.time() + 60  # confere de novo no máximo a cada minuto
        if len(_conferidos) > 2000:
            _conferidos.clear()
        return None
    erro = r.get("erro") or "servico_acesso"
    return _sem_cache(jsonify(erro=erro), 503 if erro == "servico_acesso" else 401 if erro == "sem_chave" else 403)


@app.post("/api/entrar")
def entrar():
    corpo = request.get_json(silent=True) or {}
    status, r = _servico("entrar", {k: corpo.get(k) for k in ("telefone", "aparelho", "nome", "email", "aceite")})
    return _sem_cache(jsonify(r), status)


def preparar():
    """Na primeira vez, copia os dados que vieram junto com o app para a pasta gravável."""
    DADOS.mkdir(parents=True, exist_ok=True)
    for nome in ("dados.json", "setores.json"):
        if not (DADOS / nome).exists() and (BASE / "inicial" / nome).exists():
            shutil.copy(BASE / "inicial" / nome, DADOS / nome)


def atualizar_dados():
    try:
        atualizar.main()
        log.info("Fundamentus: dados.json atualizado")
    except BaseException as e:  # atualizar.py usa SystemExit quando o Fundamentus falha; mantém os dados anteriores
        log.error("Falha ao atualizar do Fundamentus: %s", e)


def ultimo_fechamento(agora: datetime) -> datetime:
    d = agora.replace(hour=HORA, minute=MINUTO, second=0, microsecond=0)
    if d > agora:
        d -= timedelta(days=1)
    while d.weekday() >= 5:
        d -= timedelta(days=1)
    return d


def agendar():
    from apscheduler.schedulers.background import BackgroundScheduler
    s = BackgroundScheduler(timezone=FUSO)
    s.add_job(atualizar_dados, "cron", day_of_week="mon-fri", hour=HORA, minute=MINUTO, max_instances=1,
              coalesce=True, misfire_grace_time=3 * 3600)
    s.start()
    arq = DADOS / "dados.json"
    if not arq.exists() or datetime.fromtimestamp(arq.stat().st_mtime, FUSO) < ultimo_fechamento(datetime.now(FUSO)):
        s.add_job(atualizar_dados)  # dados antigos: baixa já, sem travar a inicialização
    log.info("Atualização do Fundamentus: dias úteis às %02d:%02d (Brasília)", HORA, MINUTO)


@app.get("/saude")
def saude():
    return "ok"


@app.get("/api/dados")
@app.get("/dados.json")  # endereço antigo: também exige telefone liberado
def dados():
    erro = _erro_acesso()
    if erro:
        return erro
    resp = send_from_directory(DADOS, "dados.json")
    resp.headers["Cache-Control"] = "no-store"
    return resp


@app.get("/")
def index():
    resp = send_from_directory(BASE / "static", "index.html")
    resp.headers["Cache-Control"] = "no-cache"
    return resp


@app.get("/<path:arquivo>")
def estaticos(arquivo):
    resp = send_from_directory(BASE / "static", arquivo)
    if arquivo in ("sw.js", "index.html", "manifest.webmanifest"):
        resp.headers["Cache-Control"] = "no-cache"
    return resp


if __name__ == "__main__":
    if EXIGIR_CPF and not ACESSO_SEGREDO:
        log.warning("EXIGIR_CPF=1 sem ACESSO_SEGREDO: ninguém vai conseguir entrar")
    preparar()
    agendar()
    from waitress import serve
    serve(app, host="0.0.0.0", port=int(os.getenv("PORTA", "8000")), threads=4)
