"""
detector.py — Endpoint Detection & Categorization Engine
---------------------------------------------------------
Uses keyword matching + regex patterns to classify URLs
into security-relevant categories.

Categories
----------
upload       — file upload endpoints
logs         — log viewers and debug panels
backup       — backup / database dump endpoints
console      — admin consoles, terminals, dashboards
plugin       — plugin / extension installers
shell        — potential web shells
api          — API versioned endpoints
params       — URLs with interesting query parameters
admin_panels — admin panel paths
misc         — everything that does not match above
"""

import re
from typing import Dict, List
from urllib.parse import urlparse, parse_qs

from modules.utils import print_info, print_success


# ──────────────────────────────────────────────────────────────
# DETECTION RULES
# Each rule is: (category_name, compiled_regex)
# Rules are evaluated IN ORDER; first match wins.
# ──────────────────────────────────────────────────────────────

_RULES: List[tuple] = [

    # ── Web shell indicators ───────────────────────────────────
    ("shell", re.compile(
        r"(cmd|exec|shell|c99|r57|wso|b374k|php-shell|webshell|passwd|"
        r"\.php\?cmd=|\.asp\?cmd=)",
        re.IGNORECASE,
    )),

    # ── Admin panels ───────────────────────────────────────────
    ("admin_panels", re.compile(
        r"(/admin|/administrator|/wp-admin|/phpmyadmin|/cpanel|/webadmin|"
        r"/siteadmin|/moderator|/manager|/control|/controlpanel|/admincp|"
        r"/admin-panel|/backend)",
        re.IGNORECASE,
    )),

    # ── Console / dashboard / terminal ────────────────────────
    ("console", re.compile(
        r"(/console|/terminal|/dashboard|/cockpit|/portal|/management|"
        r"/monitoring|/grafana|/kibana|/jenkins|/jira|/confluence|"
        r"/actuator|/h2-console|/spring|/swagger)",
        re.IGNORECASE,
    )),

    # ── File upload ────────────────────────────────────────────
    ("upload", re.compile(
        r"(upload|file[-_]?upload|image[-_]?upload|media|attach|"
        r"dropzone|multipart|filemanager|ckfinder|elfinder|moxieman)",
        re.IGNORECASE,
    )),

    # ── Image processing / thumbnails ──────────────────────────
    ("upload", re.compile(
        r"(thumbnail|thumb|resize|imgproxy|imagick|imagemagick|"
        r"crop|watermark|avatar|gravatar)",
        re.IGNORECASE,
    )),

    # ── Logs / debug panels ────────────────────────────────────
    ("logs", re.compile(
        r"(log|logs|debug|debugger|error[-_]?log|access[-_]?log|"
        r"system[-_]?log|event[-_]?log|trace|stacktrace|sentry|"
        r"\.log$|/log/|phpinfo|info\.php)",
        re.IGNORECASE,
    )),

    # ── Backup / restore / database ────────────────────────────
    ("backup", re.compile(
        r"(backup|back[-_]?up|restore|dump|export|db[-_]?dump|"
        r"database|\.sql|\.bak|\.tar|\.gz|\.zip|\.rar|\.7z|"
        r"archive|snapshot|migrate)",
        re.IGNORECASE,
    )),

    # ── Plugin / extension installer ──────────────────────────
    ("plugin", re.compile(
        r"(plugin|extension|addon|add[-_]?on|module|install|"
        r"marketplace|package|bundle|component)",
        re.IGNORECASE,
    )),

    # ── API endpoints ──────────────────────────────────────────
    ("api", re.compile(
        r"(/api/|/v\d+/|/graphql|/rest/|/rpc|/soap|/json|/xml|"
        r"/endpoint|/service|/services|/ws/|/webhook|/callback)",
        re.IGNORECASE,
    )),

    # ── Interesting parameters ─────────────────────────────────
    # Matched against the query string, not the path.
    ("params", re.compile(
        r"(file=|path=|redirect=|url=|next=|return=|rurl=|dest=|"
        r"destination=|go=|out=|view=|page=|include=|src=|source=|"
        r"load=|fetch=|read=|template=|open=|data=)",
        re.IGNORECASE,
    )),
]

# All valid category names (used to build the output dict)
ALL_CATEGORIES = [
    "upload", "logs", "backup", "console", "plugin",
    "shell", "api", "params", "admin_panels", "misc",
]


# ──────────────────────────────────────────────────────────────
# PUBLIC API
# ──────────────────────────────────────────────────────────────

def _classify(url: str) -> str:
    """
    Return the category name for a single URL.
    Evaluates path + query string against all rules.
    First match wins; falls back to 'misc'.
    """
    try:
        parsed  = urlparse(url)
        path    = parsed.path
        query   = parsed.query
        full    = path + ("?" + query if query else "")
    except Exception:
        full = url

    for category, pattern in _RULES:
        if pattern.search(full):
            return category

    return "misc"


def categorize_urls(urls: List[str]) -> Dict[str, List[str]]:
    """
    Classify each URL into one of the predefined security categories.

    Parameters
    ----------
    urls : list of URL strings (typically the alive URL set)

    Returns
    -------
    Dict mapping category → sorted list of matching URLs.
    """
    # Initialize all categories with empty lists
    result: Dict[str, List[str]] = {cat: [] for cat in ALL_CATEGORIES}

    for url in urls:
        cat = _classify(url)
        result[cat].append(url)

    # Sort each bucket
    for cat in result:
        result[cat].sort()

    # Print summary
    print_info("Categorization summary:")
    for cat in ALL_CATEGORIES:
        count = len(result[cat])
        if count:
            print_success(f"  {cat:<15}: {count} URL(s)")
        else:
            print_info(f"  {cat:<15}: 0")

    return result
