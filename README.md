# RSS-Summarizer

Holt ungelesene Artikel aus [Miniflux](https://miniflux.app/), extrahiert den Volltext, lässt ihn über [OpenRouter](https://openrouter.ai/) zusammenfassen und sendet die Zusammenfassung per [ntfy](https://ntfy.sh/) als Push-Benachrichtigung. Verarbeitete Artikel werden in Miniflux als gelesen markiert.

## Ablauf

1. Ungelesene Einträge über die Miniflux-API abrufen
2. Artikeltext von der Original-URL laden und mit `trafilatura` extrahieren
3. Zusammenfassung über OpenRouter erzeugen (Prompt aus `prompt.txt`)
4. Zusammenfassung an ntfy senden
5. Artikel in Miniflux als gelesen markieren

Artikel, bei denen das Laden oder Zusammenfassen fehlschlägt, werden in `failed_ids.json` gespeichert und bei späteren Läufen übersprungen.

## Voraussetzungen

- Python 3.13 (oder Docker)
- Miniflux-Instanz mit API-Key
- OpenRouter-API-Key
- ntfy-Server und Topic

## Konfiguration

Die Konfiguration erfolgt über Umgebungsvariablen (oder eine `.env`-Datei):

| Variable             | Pflicht | Beschreibung                          |
| -------------------- | ------- | ------------------------------------- |
| `MINIFLUX_API_KEY`   | ja      | API-Key für Miniflux                  |
| `MINIFLUX_URL`       | ja      | Basis-URL der Miniflux-Instanz        |
| `OPENROUTER_API_KEY` | ja      | API-Key für OpenRouter                |
| `NTFY_URL`           | ja      | URL des ntfy-Servers                  |
| `NTFY_TOPIC`         | ja      | ntfy-Topic für die Benachrichtigungen |
| `MINIFLUX_TIMEOUT`   | nein    | Timeout in Sekunden (Standard: `10`)  |

Beispiel `.env`:

```env
MINIFLUX_API_KEY=...
MINIFLUX_URL=https://miniflux.example.com
OPENROUTER_API_KEY=...
NTFY_URL=https://ntfy.example.com
NTFY_TOPIC=rss-summaries
```

## Lokal ausführen

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Das Skript läuft einmal durch und beendet sich. Für regelmäßige Ausführung z. B. per Cron oder Task Scheduler starten.

## Docker

Image bauen und pushen (Standard-Tag `latest`):

```bash
./build-and-push.sh [tag]
```

Container ausführen:

```bash
docker run --rm --env-file .env zoiaflorian/summarizer:latest
```

Damit `failed_ids.json` zwischen Läufen erhalten bleibt, kann die Datei als Volume eingebunden werden:

```bash
docker run --rm --env-file .env -v "$(pwd)/failed_ids.json:/app/failed_ids.json" zoiaflorian/summarizer:latest
```

## Projektstruktur

| Datei                | Beschreibung                                |
| -------------------- | ------------------------------------------- |
| `main.py`            | Hauptlogik                                  |
| `config.py`          | Laden der Umgebungsvariablen                |
| `prompt.txt`         | Prompt-Vorlage (`{article_title}`, `{article_content}`) |
| `Dockerfile`         | Container-Image                             |
| `build-and-push.sh`  | Build und Push des Images                   |
