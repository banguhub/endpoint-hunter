"""
collector.py — URL collection via gau / waybackurls
----------------------------------------------------
Attempts gau first, falls back to waybackurls.
Collects, deduplicates, and normalizes URLs for all targets.
"""

import subprocess
import shutil
from typing import List, Set
from urllib.parse import urlparse, urlunparse

from modules.utils import print_info, print_success, print_warning, print_error


# ──────────────────────────────────────────────────────────────
# INTERNAL HELPERS
# ──────────────────────────────────────────────────────────────

def _normalize_url(url: str) -> str:
    """
    Normalize a URL:
    - lowercase scheme and host
    - strip trailing slash from path (unless path is "/")
    - remove fragment (#…) portions
    """
    try:
        parsed = urlparse(url.strip())
        # Rebuild with normalized components
        scheme = parsed.scheme.lower()
        netloc = parsed.netloc.lower()
        path   = parsed.path.rstrip("/") or "/"
        query  = parsed.query
        # Drop fragment entirely
        normalized = urlunparse((scheme, netloc, path, "", query, ""))
        return normalized
    except Exception:
        return url.strip()


def _run_gau(target: str) -> List[str]:
    """Run gau and return raw URL lines."""
    cmd = ["gau", "--subs", target]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        return result.stdout.strip().splitlines()
    except subprocess.TimeoutExpired:
        print_warning(f"gau timed out for {target}.")
        return []
    except Exception as exc:
        print_warning(f"gau error for {target}: {exc}")
        return []


def _run_waybackurls(target: str) -> List[str]:
    """Run waybackurls and return raw URL lines."""
    cmd = ["waybackurls", target]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        return result.stdout.strip().splitlines()
    except subprocess.TimeoutExpired:
        print_warning(f"waybackurls timed out for {target}.")
        return []
    except Exception as exc:
        print_warning(f"waybackurls error for {target}: {exc}")
        return []


def _collect_for_target(target: str) -> List[str]:
    """
    Try gau first; fall back to waybackurls.
    Returns a list of raw URL strings.
    """
    if shutil.which("gau"):
        print_info(f"  [gau] Fetching URLs for: {target}")
        urls = _run_gau(target)
        if urls:
            return urls

    if shutil.which("waybackurls"):
        print_info(f"  [waybackurls] Fetching URLs for: {target}")
        return _run_waybackurls(target)

    print_warning(f"  Neither gau nor waybackurls available for {target}. Skipping.")
    return []


# ──────────────────────────────────────────────────────────────
# PUBLIC API
# ──────────────────────────────────────────────────────────────

def collect_urls(targets: List[str]) -> List[str]:
    """
    Collect URLs from all targets (domain + subdomains).

    Steps:
    1. Run gau or waybackurls per target
    2. Normalize each URL
    3. Deduplicate via a set
    4. Return sorted list

    Parameters
    ----------
    targets : list of domain strings to query

    Returns
    -------
    Deduplicated, normalized list of URL strings.
    """
    seen: Set[str] = set()
    total_raw = 0

    for target in targets:
        raw_urls = _collect_for_target(target)
        total_raw += len(raw_urls)

        for url in raw_urls:
            url = url.strip()
            if not url:
                continue
            # Only keep http/https
            if not (url.startswith("http://") or url.startswith("https://")):
                continue
            normalized = _normalize_url(url)
            seen.add(normalized)

    print_info(f"Raw URL count (pre-dedup): {total_raw}")
    print_success(f"Unique normalized URLs: {len(seen)}")

    return sorted(seen)
