# app/utils/web.py
import requests
from bs4 import BeautifulSoup
from typing import Optional, List, Dict
import re
import logging

logger = logging.getLogger("strive-code-ai.web")

# Robust HTTP client with retries and headers
_session = requests.Session()
_session.headers.update({
    "User-Agent": "Strive-Code-AI/1.0 (+https://strive-code.ai)"
})
_adapter = requests.adapters.HTTPAdapter(max_retries=3)
_session.mount("http://", _adapter)
_session.mount("https://", _adapter)

def fetch_url(url: str, timeout: int = 15) -> Optional[str]:
    """
    Fetch any public URL with resilience.
    Returns HTML string or None on failure.
    """
    try:
        resp = _session.get(url, timeout=timeout, allow_redirects=True)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        logger.warning(f"[WEB] Failed to fetch {url}: {e}")
        return None

def extract_code_blocks(html: str, lang: Optional[str] = None) -> List[str]:
    """
    Extract <pre><code> blocks from HTML.
    Optionally filter by language class.
    """
    soup = BeautifulSoup(html, "html.parser")
    blocks = []
    for pre in soup.find_all("pre"):
        code_tag = pre.find("code")
        if not code_tag:
            continue
        if lang and f"class=\"language-{lang}\"" not in str(code_tag):
            continue
        blocks.append(code_tag.get_text())
    return blocks

def scrape_github_trending(language: str = "python") -> List[Dict]:
    """
    Scrape GitHub trending repos for a language.
    """
    url = f"https://github.com/trending/{language}?since=daily"
    html = fetch_url(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    repos = []
    for article in soup.find_all("article", class_="Box-row"):
        title = article.find("h2")
        if not title:
            continue
        repo_path = title.find("a")["href"].strip("/")
        stars = article.find("a", class_="Link--muted")
        stars = stars.get_text(strip=True).replace(",", "") if stars else "0"
        desc = article.find("p", class_="col-9")
        desc = desc.get_text(strip=True) if desc else ""

        repos.append({
            "name": repo_path,
            "url": f"https://github.com/{repo_path}",
            "stars": int(stars),
            "description": desc
        })
    return repos

def is_valid_url(url: str) -> bool:
    """Basic URL validation."""
    return bool(re.match(r"^https?://([\da-z\.-]+)\.([a-z\.]{2,6})([/\w \.-]*)*/?$", url))
