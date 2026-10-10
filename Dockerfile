# syntax=docker/dockerfile:1

FROM python:3.13-slim

# Verhindert .pyc Dateien und sorgt für direktes stdout/stderr (wichtig fürs Logging via cron)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Erst nur requirements kopieren -> Docker cached diesen Layer,
# solange sich requirements.txt nicht ändert (schnellere Rebuilds)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Restlichen Projektcode kopieren
COPY . .

CMD ["python", "main.py"]
