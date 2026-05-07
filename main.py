#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════╗
║           ENDPOINT HUNTER CLI - v1.0                  ║
║      Web Application Security Reconnaissance          ║
║                                                       ║
║  Author : Sabbir                                      ║
║  GitHub : https://github.com/banghub                 ║
║  LinkedIn: https://linkedin.com/in/sabbir-pentester   ║
║  Medium : https://banghub.medium.com                  ║
╚═══════════════════════════════════════════════════════╝
"""

import sys
import os

# Make sure modules are importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.utils import (
    print_banner,
    print_info,
    print_success,
    print_warning,
    print_error,
    validate_domain,
    clean_domain,
    check_dependencies,
    prompt_yes_no,
)
from modules.subdomain import enumerate_subdomains
from modules.collector import collect_urls
from modules.filter import filter_urls
from modules.detector import categorize_urls
from modules.output import (
    setup_output_directory,
    save_all_urls,
    save_alive_urls,
    save_subdomains,
    save_categorized,
    generate_report,
)


def main():
    """Main entry point for Endpoint Hunter CLI."""

    # ── 1. Banner ──────────────────────────────────────────────
    print_banner()

    # ── 2. Dependency check ────────────────────────────────────
    check_dependencies()

    # ── 3. Get target domain ───────────────────────────────────
    print()
    raw_domain = input("\033[1;36m[?] Enter target domain (e.g. example.com): \033[0m").strip()

    if not raw_domain:
        print_error("No domain provided. Exiting.")
        sys.exit(1)

    domain = clean_domain(raw_domain)

    if not validate_domain(domain):
        print_error(f"Invalid domain format: '{domain}'. Exiting.")
        sys.exit(1)

    print_success(f"Target set to: {domain}")

    # ── 4. Output directory ────────────────────────────────────
    output_dir = setup_output_directory(domain)
    print_info(f"Results will be saved to: {output_dir}")

    # ── 5. Subdomain enumeration ───────────────────────────────
    subdomains = []
    if prompt_yes_no("\n[?] Perform subdomain enumeration?"):
        subdomains = enumerate_subdomains(domain, output_dir)
    else:
        print_info("Skipping subdomain enumeration. Using root domain only.")

    targets = [domain] + subdomains

    # ── 6. URL collection ──────────────────────────────────────
    print_info(f"\nCollecting URLs from {len(targets)} target(s)...")
    raw_urls = collect_urls(targets)

    if not raw_urls:
        print_warning("No URLs collected. Exiting.")
        sys.exit(0)

    print_success(f"Collected {len(raw_urls)} raw URLs.")

    # ── 7. Filter & deduplicate ────────────────────────────────
    filtered_urls = filter_urls(raw_urls)
    print_success(f"After filtering static assets: {len(filtered_urls)} URLs remain.")

    save_all_urls(output_dir, filtered_urls)

    # ── 8. Alive check ─────────────────────────────────────────
    alive_urls = []
    if prompt_yes_no("\n[?] Perform alive check on URLs? (may take time)"):
        from modules.filter import check_alive
        alive_urls = check_alive(filtered_urls)
        print_success(f"Alive URLs: {len(alive_urls)}")
        save_alive_urls(output_dir, alive_urls)
    else:
        print_info("Skipping alive check.")
        alive_urls = filtered_urls  # treat all as alive for categorization

    # ── 9. Categorization ──────────────────────────────────────
    print_info("\nRunning endpoint detection engine...")
    categorized = categorize_urls(alive_urls)

    total_categorized = sum(len(v) for v in categorized.values())
    print_success(f"Categorized {total_categorized} endpoints across {len(categorized)} categories.")

    save_categorized(output_dir, categorized)

    # ── 10. Save subdomains ────────────────────────────────────
    if subdomains:
        save_subdomains(output_dir, subdomains)

    # ── 11. Report ─────────────────────────────────────────────
    generate_report(
        output_dir=output_dir,
        domain=domain,
        all_urls=filtered_urls,
        alive_urls=alive_urls,
        subdomains=subdomains,
        categorized=categorized,
    )

    # ── 12. Done ───────────────────────────────────────────────
    print()
    print("\033[1;32m" + "═" * 55)
    print(f"  ✔  Scan complete! Results saved to: {output_dir}")
    print("═" * 55 + "\033[0m")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_warning("\n\n[!] Interrupted by user. Exiting cleanly.")
        sys.exit(0)
