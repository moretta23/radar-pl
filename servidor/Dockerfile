FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
COPY app.py atualizar.py /app/
COPY inicial /app/inicial
COPY static /app/static
ENV PYTHONUNBUFFERED=1
CMD ["python", "app.py"]
