import requests


def fetch(url: str, user_agent: str, timeout: float) -> tuple[int, str]:
    # shortcut: 2xx bodies are stored as text, upgrade when non-HTML responses must be skipped
    response = requests.get(url, timeout=timeout, headers={"User-Agent": user_agent})
    return response.status_code, response.text if response.ok else ""
