"""
Mais Tempo (PWA) no servidor da VPS, em https://vendas.moretta.com.br/metodo/

- Serve as telas do app (static/) e o dados.json guardado em DADOS_DIR.
- Roda scripts/atualizar.py (Fundamentus + Selic) todo dia útil às 19h (Brasília).
  Ao iniciar, se o dados.json for anterior ao último fechamento, atualiza na hora.
- Aberto para qualquer pessoa (sem CPF).

Variáveis de ambiente:
  DADOS_DIR   pasta gravável de dados.json e setores.json   padrão: /dados
  HORA        horário da atualização (HH:MM, Brasília)      padrão: 19:00
  PORTA       porta HTTP                                    padrão: 8000
"""
import logging
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from flask import Flask, send_from_directory

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


@app.get("/dados.json")
def dados():
    resp = send_from_directory(DADOS, "dados.json")
    resp.headers["Cache-Control"] = "no-cache"
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
    preparar()
    agendar()
    from waitress import serve
    serve(app, host="0.0.0.0", port=int(os.getenv("PORTA", "8000")), threads=4)
