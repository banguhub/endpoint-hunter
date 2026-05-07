"""
filter.py — URL filtering and alive-check
------------------------------------------
1. filter_urls()  : remove static assets by file extension
2. check_alive()  : HTTP probe each URL; keep status < 500
"""

import os
from typing import List
from urllib.parse import urlparse

from modules.utils import print_info, print_success, print_warning

# ──────────────────────────────────────────────────────────────
# STATIC ASSET EXTENSIONS TO DISCARD
# ──────────────────────────────────────────────────────────────

STATIC_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".ico",
    ".svg", ".tiff",
    ".css",
    ".js", ".map",
    ".woff", ".woff2", ".ttf", ".eot", ".otf",
    ".mp4", ".mp3", ".avi", ".mov", ".wmv", ".flv", ".webm",
    ".pdf",
    ".zip", ".tar", ".gz", ".rar", ".7z",   # kept for detection elsewhere
}

# Extensions that look interesting despite being "files"
# (we keep these for the backup/shell category)
INTERESTING_EXTENSIONS = {".zip", ".tar", ".gz", ".rar", ".7z", ".bak", ".sql", ".dump"}


def filter_urls(urls: List[str]) -> List[str]:
    """
    Remove URLs whose path ends with a known static asset extension.

    URLs with interesting extensions (backup archives, etc.) are kept.

    Parameters
    ----------
    urls : list of normalized URL strings

    Returns
    -------
    Filtered list of URLs worth investigating.
    """
    filtered: List[str] = []

    for url in urls:
        try:
            path = urlparse(url).path.lower()
            _, ext = os.path.splitext(path)

            # Keep if it's an interesting extension even if "static"
            if ext in INTERESTING_EXTENSIONS:
                filtered.append(url)
                continue

            # Discard generic static assets
            if ext in STATIC_EXTENSIONS:
                continue

            filtered.append(url)

        except Exception:
            # Malformed URL — keep it for manual review
            filtered.append(url)

    return filtered


# ──────────────────────────────────────────────────────────────
# ALIVE CHECK
# ──────────────────────────────────────────────────────────────

def check_alive(
    urls: List[str],
    timeout: int = 5,
    max_workers: int = 20,
) -> List[str]:
    """
    Send HEAD requests to each URL; keep those that respond with
    HTTP status < 500 (i.e. reachable / not a server error).

    Uses a thread pool for speed.

    Parameters
    ----------
    urls        : list of URL strings to probe
    timeout     : per-request timeout in seconds (default 5)
    max_workers : concurrent threads (default 20)

    Returns
    -------
    List of alive URLs.
    """
    try:
        import requests
        from concurrent.futures import ThreadPoolExecutor, as_completed
    except ImportError:
        print_warning("requests library not found. Skipping alive check.")
        return urls

    alive: List[str] = []
    total = len(urls)

    print_info(f"Probing {total} URLs with {max_workers} threads (timeout={timeout}s)...")

    session = requests.Session()
    session.max_redirects = 3
    # Suppress SSL warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def probe(url: str):
        try:
            resp = session.head(
                url,
                timeout=timeout,
                allow_redirects=True,
                verify=False,
                headers={"User-Agent": "EndpointHunter/1.0 (security-recon)"},
            )
            if resp.status_code < 500:
                return url
        except Exception:
            pass
        return None

    completed = 0
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(probe, url): url for url in urls}
        for future in as_completed(futures):
            completed += 1
            result = future.result()
            if result:
                alive.append(result)
            # Simple progress indicator every 50 URLs
            if completed % 50 == 0 or completed == total:
                print_info(f"  Progress: {completed}/{total} probed | {len(alive)} alive")

    print_success(f"Alive check complete: {len(alive)}/{total} URLs responded.")
    return sorted(alive)
