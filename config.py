import os 

from dotenv import load_dotenv

load_dotenv()

def _require_env(name: str) -> str: 
    value = os.getenv(name)
    if value is None:
        raise RuntimeError(f"Environment variable '{name}' is required but not set.")
    return value

MINIFLUX_API_KEY = _require_env("MINIFLUX_API_KEY")
MINIFLUX_URL = _require_env("MINIFLUX_URL")
OPENROUTER_API_KEY = _require_env("OPENROUTER_API_KEY")
NTFY_URL = _require_env("NTFY_URL")
NTFY_TOPIC = _require_env("NTFY_TOPIC")
MINIFLUX_TIMEOUT = int(os.getenv("MINIFLUX_TIMEOUT", "10"))