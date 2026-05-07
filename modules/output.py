"""
output.py — Output management and report generation
----------------------------------------------------
Handles:
  - Output directory creation
  - Saving URL lists and categorized files
  - Generating report.txt and report.json
"""

import json
import os
from datetime import datetime
from typing import Dict, List

from modules.utils import print_info, print_success, print_error


# ──────────────────────────────────────────────────────────────
# DIRECTORY SETUP
# ──────────────────────────────────────────────────────────────

def setup_output_directory(domain: str) -> str:
    """
    Create the output directory for this scan:

        results/<domain>_<YYYYMMDD_HHMMSS>/

    Parameters
    ----------
    domain : cleaned domain string (e.g. "example.com")

    Returns
    -------
    Absolute path to the created directory.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Replace dots in domain to keep directory names clean
    safe_domain = domain.replace(".", "_")
    dir_name    = f"{safe_domain}_{timestamp}"
    output_dir  = os.path.join("results", dir_name)

    try:
        os.makedirs(output_dir, exist_ok=True)
        print_info(f"Output directory created: {output_dir}")
    except OSError as exc:
        print_error(f"Failed to create output directory: {exc}")
        raise

    return output_dir


# ──────────────────────────────────────────────────────────────
# FILE SAVERS
# ──────────────────────────────────────────────────────────────

def _write_lines(filepath: str, lines: List[str]) -> None:
    """Write a list of strings to a file, one per line."""
    try:
        with open(filepath, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + ("\n" if lines else ""))
        print_success(f"Saved: {filepath} ({len(lines)} entries)")
    except OSError as exc:
        print_error(f"Could not write {filepath}: {exc}")


def save_all_urls(output_dir: str, urls: List[str]) -> None:
    """Save the complete deduplicated URL list to all_urls.txt."""
    _write_lines(os.path.join(output_dir, "all_urls.txt"), urls)


def save_alive_urls(output_dir: str, urls: List[str]) -> None:
    """Save the alive URL list to alive_urls.txt."""
    _write_lines(os.path.join(output_dir, "alive_urls.txt"), urls)


def save_subdomains(output_dir: str, subdomains: List[str]) -> None:
    """Save discovered subdomains to subdomains.txt."""
    _write_lines(os.path.join(output_dir, "subdomains.txt"), subdomains)


def save_categorized(output_dir: str, categorized: Dict[str, List[str]]) -> None:
    """
    Save each category bucket to its own <category>.txt file.

    Files are created even for empty categories (0 bytes)
    to make the output structure predictable.
    """
    for category, urls in categorized.items():
        filepath = os.path.join(output_dir, f"{category}.txt")
        _write_lines(filepath, urls)


# ──────────────────────────────────────────────────────────────
# REPORT GENERATION
# ──────────────────────────────────────────────────────────────

def generate_report(
    output_dir: str,
    domain: str,
    all_urls: List[str],
    alive_urls: List[str],
    subdomains: List[str],
    categorized: Dict[str, List[str]],
) -> None:
    """
    Generate both a human-readable report.txt and a machine-readable
    report.json inside `output_dir`.

    Parameters
    ----------
    output_dir   : path to the scan's output directory
    domain       : target domain
    all_urls     : full filtered URL list
    alive_urls   : URL list after alive check
    subdomains   : list of discovered subdomains
    categorized  : dict of category → URL list
    """
    scan_time   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    category_counts = {cat: len(urls) for cat, urls in categorized.items()}

    # ── Plain-text report ──────────────────────────────────────
    lines = [
        "=" * 55,
        "          ENDPOINT HUNTER CLI — SCAN REPORT",
        "=" * 55,
        f"  Date/Time   : {scan_time}",
        f"  Target      : {domain}",
        f"  Total URLs  : {len(all_urls)}",
        f"  Alive URLs  : {len(alive_urls)}",
        f"  Subdomains  : {len(subdomains)}",
        "",
        "  ── Category Breakdown ──────────────────────────",
    ]

    for cat, count in category_counts.items():
        bar  = "█" * min(count, 40)
        lines.append(f"  {cat:<15}: {count:>4}  {bar}")

    lines += [
        "",
        "  ── Top Findings (first 5 per category) ────────",
    ]

    for cat, urls in categorized.items():
        if urls:
            lines.append(f"\n  [{cat.upper()}]")
            for url in urls[:5]:
                lines.append(f"    {url}")

    lines += [
        "",
        "=" * 55,
        "  ⚠  This report is for authorized testing only.",
        "=" * 55,
    ]

    txt_path = os.path.join(output_dir, "report.txt")
    try:
        with open(txt_path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")
        print_success(f"Text report saved: {txt_path}")
    except OSError as exc:
        print_error(f"Could not write report.txt: {exc}")

    # ── JSON report ────────────────────────────────────────────
    report_data = {
        "meta": {
            "tool":    "Endpoint Hunter CLI v1.0",
            "author":  "Sabbir",
            "github":  "https://github.com/banghub",
        },
        "scan": {
            "timestamp":       scan_time,
            "target":          domain,
            "total_urls":      len(all_urls),
            "alive_urls":      len(alive_urls),
            "subdomain_count": len(subdomains),
        },
        "categories": category_counts,
        "subdomains": subdomains,
    }

    json_path = os.path.join(output_dir, "report.json")
    try:
        with open(json_path, "w", encoding="utf-8") as fh:
            json.dump(report_data, fh, indent=2)
        print_success(f"JSON report saved: {json_path}")
    except OSError as exc:
        print_error(f"Could not write report.json: {exc}")
