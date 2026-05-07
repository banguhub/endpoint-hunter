"""
subdomain.py — Subdomain enumeration via subfinder
---------------------------------------------------
Runs subfinder as a subprocess, captures output,
deduplicates results, and returns a list of subdomains.
"""

import subprocess
import shutil
import os
from typing import List

from modules.utils import print_info, print_success, print_warning, print_error


def enumerate_subdomains(domain: str, output_dir: str) -> List[str]:
    """
    Run subfinder against `domain` and return a list of discovered subdomains.

    Parameters
    ----------
    domain     : root domain to enumerate (e.g. "example.com")
    output_dir : directory where subdomains.txt will be saved

    Returns
    -------
    List of subdomain strings (may be empty if subfinder is unavailable).
    """
    print_info(f"Starting subdomain enumeration for: {domain}")

    # ── Check tool availability ───────────────────────────────
    if shutil.which("subfinder") is None:
        print_warning("subfinder not found. Skipping subdomain enumeration.")
        return []

    # ── Build command ─────────────────────────────────────────
    cmd = ["subfinder", "-d", domain, "-silent"]

    try:
        print_info("Running subfinder (this may take a moment)...")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,         # 2-minute timeout
        )

        if result.returncode != 0 and not result.stdout.strip():
            print_warning(f"subfinder returned no output. stderr: {result.stderr.strip()}")
            return []

        # ── Parse & deduplicate output ────────────────────────
        raw_lines = result.stdout.strip().splitlines()
        subdomains = sorted(set(line.strip() for line in raw_lines if line.strip()))

        # Remove the root domain itself if subfinder echoed it back
        subdomains = [s for s in subdomains if s != domain]

        if subdomains:
            print_success(f"Found {len(subdomains)} subdomains.")
        else:
            print_warning("No subdomains discovered.")

        return subdomains

    except subprocess.TimeoutExpired:
        print_error("subfinder timed out after 120 seconds.")
        return []

    except FileNotFoundError:
        print_warning("subfinder binary not accessible. Skipping.")
        return []

    except Exception as exc:
        print_error(f"Unexpected error during subdomain enumeration: {exc}")
        return []
