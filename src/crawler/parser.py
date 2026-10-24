from bs4 import BeautifulSoup

from common.url_utils import normalize_url


def parse(html: str, page_url: str) -> tuple[str, str, list[str]]:
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.get_text(" ", strip=True)[:300] if soup.title else ""
    for tag in soup(["script", "style"]):
        tag.decompose()
    content = soup.get_text(" ", strip=True)[:8000]
    links: list[str] = []
    seen: set[str] = set()
    for tag in soup.find_all("a", href=True):
        url = normalize_url(tag["href"], page_url)
        if url is None or url == page_url or url in seen:
            continue
        seen.add(url)
        links.append(url)
    return title, content, links
