"""
utils.py — Utility helpers for Endpoint Hunter CLI
----------------------------------------------------
Handles: banner, colored output, domain validation,
         dependency checks, and user prompts.
"""

import re
import shutil
import sys

# ── Try to import colorama for cross-platform color support ──
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    _HAS_COLOR = True
except ImportError:
    _HAS_COLOR = False

    # Stub so the rest of the code never crashes
    class _Stub:
        def __getattr__(self, _):
            return ""

    Fore = _Stub()
    Style = _Stub()


# ──────────────────────────────────────────────────────────────
# BANNER
# ──────────────────────────────────────────────────────────────

BANNER = r"""
  ___         _             _     _  _            _
 | __|_ _  __| |_ __  ___(_)_ _| || |_  _ _ _  | |_ ___ _ _
 | _|| ' \/ _` | '_ \/ _ \ | ' \ __ | || | ' \ |  _/ -_) '_|
 |___|_||_\__,_| .__/\___/_|_||_|_||_|\_,_|_||_| \__\___|_|
               |_|
          Web Application Security Reconnaissance
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Author  : Sabbir
  GitHub  : https://github.com/banghub
  LinkedIn: https://linkedin.com/in/sabbir-pentester
  Medium  : https://banghub.medium.com
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  [!] For authorized security testing use only
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


def print_banner():
    """Print the tool banner with color."""
    print(Fore.CYAN + Style.BRIGHT + BANNER + Style.RESET_ALL)


# ──────────────────────────────────────────────────────────────
# COLORED OUTPUT HELPERS
# ──────────────────────────────────────────────────────────────

def print_info(message: str):
    """[*] Informational message — blue."""
    print(Fore.BLUE + f"[*] {message}" + Style.RESET_ALL)


def print_success(message: str):
    """[+] Success message — green."""
    print(Fore.GREEN + f"[+] {message}" + Style.RESET_ALL)


def print_warning(message: str):
    """[-] Warning message — yellow."""
    print(Fore.YELLOW + f"[-] {message}" + Style.RESET_ALL)


def print_error(message: str):
    """[!] Error message — red."""
    print(Fore.RED + f"[!] {message}" + Style.RESET_ALL)


# ──────────────────────────────────────────────────────────────
# DOMAIN HELPERS
# ──────────────────────────────────────────────────────────────

# Regex: allows subdomains, main domain, and TLD (2-6 chars)
_DOMAIN_RE = re.compile(
    r"^(?:[a-zA-Z0-9]"
    r"(?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?"
    r"\.)+"
    r"[a-zA-Z]{2,6}$"
)


def clean_domain(raw: str) -> str:
    """
    Strip protocol, trailing slashes, and whitespace from user input.

    Examples:
        https://example.com/  → example.com
        http://sub.example.com → sub.example.com
    """
    raw = raw.strip()
    # Remove protocol
    raw = re.sub(r"^https?://", "", raw, flags=re.IGNORECASE)
    # Remove path / trailing slash
    raw = raw.split("/")[0].strip()
    return raw.lower()


def validate_domain(domain: str) -> bool:
    """Return True if domain matches a valid domain pattern."""
    return bool(_DOMAIN_RE.match(domain))


# ──────────────────────────────────────────────────────────────
# DEPENDENCY CHECK
# ──────────────────────────────────────────────────────────────

REQUIRED_TOOLS = {
    "subfinder": "https://github.com/projectdiscovery/subfinder",
    "gau":       "https://github.com/lc/gau",
    "waybackurls": "https://github.com/tomnomnom/waybackurls",
}


def check_dependencies():
    """
    Check whether external tools are installed.
    Print warnings for missing tools but do NOT exit.
    """
    print_info("Checking external tool dependencies...")

    missing = []
    for tool, url in REQUIRED_TOOLS.items():
        if shutil.which(tool) is None:
            missing.append((tool, url))

    if missing:
        print_warning("Some tools are missing (limited mode will be used):")
        for tool, url in missing:
            print(Fore.YELLOW + f"   ✗ {tool} — install from: {url}" + Style.RESET_ALL)
    else:
        print_success("All external tools found.")


# ──────────────────────────────────────────────────────────────
# USER PROMPT
# ──────────────────────────────────────────────────────────────

def prompt_yes_no(question: str) -> bool:
    """
    Ask a yes/no question and return True for 'y', False for 'n'.
    Loops until a valid answer is given.
    """
    while True:
        answer = input(Fore.CYAN + f"{question} (y/n): " + Style.RESET_ALL).strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print_warning("Please enter 'y' or 'n'.")
