import requests
import json
import trafilatura 
import time 
import datetime

from pathlib import Path 

from config import MINIFLUX_API_KEY, MINIFLUX_URL, MINIFLUX_TIMEOUT, OPENROUTER_API_KEY, NTFY_URL, NTFY_TOPIC

FAILED_IDS_FILE = Path("failed_ids.json")

# Load file of failed articles to summarize 
def load_failed_ids() -> set[int]:
    if FAILED_IDS_FILE.exists():
        return set(json.loads(FAILED_IDS_FILE.read_text()))
    return set()

# save file of failes articles to summarize
def save_failed_ids(ids: set[int]) -> None:
    FAILED_IDS_FILE.write_text(json.dumps(list(ids)))
    

# get articles from miniflux 
def get_unread_articles() -> list[dict]: 
    params = {
        "status": "unread",
        "direction": "desc"
    }

    headers = {
        "X-Auth-Token" : MINIFLUX_API_KEY
    }

    try:
        response = requests.get(
            f"{MINIFLUX_URL}/v1/entries", 
            headers=headers,
            params=params,
            timeout=MINIFLUX_TIMEOUT
        )
        response.raise_for_status()
        data = response.json()

        return [
            {
                "id": entry["id"],
                "title": entry["title"],
                "content": entry["content"],
                "url": entry["url"],
                "feed_name": entry["feed"]["title"]
            }
            for entry in data.get("entries", [])
        ]
    except requests.exceptions.HTTPError as e:
        print("An HTTP error occurred:", e)
    except requests.exceptions.RequestException as e:
        print("A request error occurred:", e)
        
# access articles via html and retrieve text
def get_article_content(article_url: str) -> str:
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    }

    try:
        html = requests.get(article_url, headers=HEADERS)
        html.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"{datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')}Fehler beim Laden von {article_url}: {e}")
        return None
    
    article_content = trafilatura.extract(html.text)
    if not article_content:
        print(f"{datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')}Fehler beim Extrahieren des Inhalts von {article_url}")
        return None
    else: 
        return article_content

# send article to ai and let it summarize 
def summarize_article(article_title: str, article_content: str) -> str:
    prompt_template = Path("prompt.txt").read_text(encoding="utf-8")
    prompt = prompt_template.format(
        article_title=article_title,
        article_content=article_content
    )

    try: 
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}"
            },
            data = json.dumps({
                "models": [
                    "google/gemma-4-26b-a4b-it:free",
                    "google/gemma-4-31b-it:free",
                    "z-ai/glm-5.2:free"
                    ],
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
        )
        response.raise_for_status()
        data = response.json()["choices"][0]["message"]["content"]
        return data
    except requests.exceptions.HTTPError as e:
        print("An HTTP error occurred:", e)
        print("Response body:", response.text)
        return None
    except requests.exceptions.RequestException as e:
        print("A request error occurred:", e)
        return None

# construct message and send to ntfy 
def send_to_ntfy(title: str, content: str, url: str) -> None:
    message = f"{content}\n\nRead more: {url}"
    try: 
        requests.post(
            f"{NTFY_URL}/{NTFY_TOPIC}",
            data=f"{message}",
            headers={
                "Title": title.encode("utf-8"),
                "Priority": "3"
            }
        )
    except requests.exceptions.HTTPError as e:
        print("An HTTP error occurred:", e)
    except requests.exceptions.RequestException as e:
        print("A request error occurred:", e)
        
# marks articles to be flagged as read 
def mark_article_as_read(id: int) -> None: 
    response = requests.put(
        f"{MINIFLUX_URL}/v1/entries",
        headers={
            "X-Auth-Token" : MINIFLUX_API_KEY
        },
        json = {
            "entry_ids": [id],
            "status": "read"
        }
    )


def main():
    failed_ids = load_failed_ids()
    article_list = get_unread_articles()
    if not article_list:
        pass
    else:
        for entry in article_list: 
            if entry["id"] in failed_ids:
                continue 
            
            article_content = get_article_content(entry["url"])
            if article_content is None:
                failed_ids.add(entry["id"])
                print(f"{datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')}Failed to extract content for article: {entry['url']}")
                continue
            
            time.sleep(4)
            summarized_article = summarize_article(entry["title"], article_content)
            if summarized_article is None:
                failed_ids.add(entry["id"])
                print(f"{datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')}Failed to summarize article: {entry['title']}")
                continue
            
            send_to_ntfy(entry["title"], summarized_article, entry["url"])
            mark_article_as_read(entry["id"])
            # time.sleep(4)
    save_failed_ids(failed_ids)
    time.sleep(4)

if __name__ == '__main__':
    main()
