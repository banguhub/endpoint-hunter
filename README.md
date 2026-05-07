# 🎯 Endpoint Hunter CLI

> **Web Application Security Reconnaissance Tool**

```
  ___         _             _     _  _            _
 | __|_ _  __| |_ __  ___(_)_ _| || |_  _ _ _  | |_ ___ _ _
 | _|| ' \/ _` | '_ \/ _ \ | ' \ __ | || | ' \ |  _/ -_) '_|
 |___|_||_\__,_| .__/\___/_|_||_|_||_|\_,_|_||_| \__\___|_|
               |_|
          Web Application Security Reconnaissance
```

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Author](https://img.shields.io/badge/Author-Sabbir-red?style=flat-square)](https://github.com/banghub)

---

## 📖 Description

**Endpoint Hunter CLI** is a professional, modular Python command-line tool designed for web application security reconnaissance. It automates the discovery and classification of security-sensitive endpoints that are commonly targeted during bug bounty programs and penetration tests.

Given a target domain, the tool:
1. Optionally enumerates subdomains via `subfinder`
2. Collects historical URLs via `gau` or `waybackurls`
3. Filters out static assets (images, CSS, fonts)
4. Classifies URLs into security-relevant categories
5. Optionally performs an alive check to filter live endpoints
6. Generates a structured report in both `.txt` and `.json` formats

---

## ✨ Features

- 🔍 **Subdomain Enumeration** — powered by `subfinder`
- 🌐 **URL Collection** — via `gau` (preferred) or `waybackurls` fallback
- 🧹 **Smart Filtering** — removes static assets, deduplicates, and normalizes URLs
- 🧠 **Endpoint Detection Engine** — keyword + regex pattern matching across 10 categories
- ✅ **Alive Check** — multi-threaded HTTP probing (HEAD requests)
- 📁 **Organized Output** — one `.txt` file per category + master URL list
- 📊 **Report Generation** — human-readable `report.txt` and machine-readable `report.json`
- 🎨 **Colored CLI** — clear progress indicators via `colorama`
- 🛡️ **Graceful Error Handling** — no crashes, limited-mode fallback when tools are missing

---

## 🗂️ Endpoint Categories

| Category      | Examples                                               |
|---------------|--------------------------------------------------------|
| `upload`      | `/upload`, `/file-upload`, `/media`, thumbnail APIs    |
| `logs`        | `/logs`, `/debug`, `phpinfo`, error log paths          |
| `backup`      | `.sql`, `.zip`, `/backup`, `/dump`, `/restore`        |
| `console`     | `/admin`, `/console`, `/dashboard`, `/jenkins`        |
| `plugin`      | `/plugin`, `/extension`, `/install`, `/marketplace`   |
| `shell`       | `cmd=`, `exec`, `c99.php`, web shell indicators       |
| `api`         | `/api/`, `/v1/`, `/graphql`, `/webhook`               |
| `params`      | `?file=`, `?path=`, `?redirect=`, `?url=`             |
| `admin_panels`| `/admin`, `/wp-admin`, `/phpmyadmin`, `/cpanel`       |
| `misc`        | Everything else that passes the filter                 |

---

## 📦 Installation

### Prerequisites

Install Python dependencies:

```bash
git clone https://github.com/banghub/endpoint-hunter
cd endpoint-hunter
pip install -r requirements.txt
```

### External Tools (optional but recommended)

The tool works in limited mode without these, but installs them for full functionality:

```bash
# subfinder — subdomain enumeration
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest

# gau — get all URLs (preferred)
go install github.com/lc/gau/v2/cmd/gau@latest

# waybackurls — Wayback Machine URL fetcher (fallback)
go install github.com/tomnomnom/waybackurls@latest
```

Make sure your Go `bin` directory is in `$PATH`:

```bash
export PATH=$PATH:$(go env GOPATH)/bin
```

---

## 🚀 Usage

```bash
python main.py
```

The tool will guide you through the following prompts:

```
[?] Enter target domain (e.g. example.com): example.com
[?] Perform subdomain enumeration? (y/n): y
[?] Perform alive check on URLs? (may take time) (y/n): y
```

### CLI Example Session

```
$ python main.py

  ___         _             _     _  _            _
 | __|_ _  __| |_ __  ___(_)_ _| || |_  _ _ _  | |_ ___ _ _
 ...

[*] Checking external tool dependencies...
[+] All external tools found.

[?] Enter target domain (e.g. example.com): testfire.net
[+] Target set to: testfire.net
[*] Results will be saved to: results/testfire_net_20240815_143022

[?] Perform subdomain enumeration? (y/n): y
[*] Running subfinder (this may take a moment)...
[+] Found 3 subdomains.

[*] Collecting URLs from 4 target(s)...
[*]   [gau] Fetching URLs for: testfire.net
[+] Unique normalized URLs: 1247

[+] After filtering static assets: 834 URLs remain.

[?] Perform alive check on URLs? (may take time) (y/n): y
[*] Probing 834 URLs with 20 threads (timeout=5s)...
[+] Alive check complete: 312/834 URLs responded.

[*] Running endpoint detection engine...
[+]   upload         :   12 URL(s)
[+]   logs           :    5 URL(s)
[+]   backup         :    8 URL(s)
[+]   console        :   18 URL(s)
[+]   plugin         :    3 URL(s)
[+]   shell          :    1 URL(s)
[+]   api            :   47 URL(s)
[+]   params         :   91 URL(s)
[+]   admin_panels   :   14 URL(s)
[+]   misc           :  113 URL(s)

[+] Text report saved: results/testfire_net_20240815_143022/report.txt
[+] JSON report saved: results/testfire_net_20240815_143022/report.json

═══════════════════════════════════════════════════════
  ✔  Scan complete! Results saved to: results/testfire_net_20240815_143022
═══════════════════════════════════════════════════════
```

---

## 📂 Output Structure

```
results/
└── testfire_net_20240815_143022/
    ├── all_urls.txt        ← All filtered, deduplicated URLs
    ├── alive_urls.txt      ← URLs that responded HTTP < 500
    ├── subdomains.txt      ← Discovered subdomains (if enabled)
    ├── upload.txt
    ├── logs.txt
    ├── backup.txt
    ├── console.txt
    ├── plugin.txt
    ├── shell.txt
    ├── api.txt
    ├── params.txt
    ├── admin_panels.txt
    ├── misc.txt
    ├── report.txt          ← Human-readable summary
    └── report.json         ← Machine-readable summary
```

### report.json example

```json
{
  "meta": {
    "tool": "Endpoint Hunter CLI v1.0",
    "author": "Sabbir",
    "github": "https://github.com/banghub"
  },
  "scan": {
    "timestamp": "2024-08-15 14:30:22",
    "target": "testfire.net",
    "total_urls": 834,
    "alive_urls": 312,
    "subdomain_count": 3
  },
  "categories": {
    "upload": 12,
    "logs": 5,
    "backup": 8,
    "console": 18,
    "plugin": 3,
    "shell": 1,
    "api": 47,
    "params": 91,
    "admin_panels": 14,
    "misc": 113
  },
  "subdomains": ["demo.testfire.net", "beta.testfire.net", "api.testfire.net"]
}
```

---

## 📸 Screenshots

> *Add terminal screenshots here once you have run the tool against a test target.*

---

## 🗃️ Project Structure

```
endpoint-hunter/
│
├── main.py                 ← Entry point / orchestrator
├── modules/
│   ├── __init__.py
│   ├── collector.py        ← URL collection (gau / waybackurls)
│   ├── subdomain.py        ← Subdomain enumeration (subfinder)
│   ├── filter.py           ← Static-asset filter + alive check
│   ├── detector.py         ← Endpoint categorization engine
│   ├── output.py           ← File saving + report generation
│   └── utils.py            ← Banner, colors, validation, prompts
│
├── results/                ← Scan outputs (auto-created)
├── requirements.txt
└── README.md
```

---

## 🤝 Connect

| Platform  | Link |
|-----------|------|
| GitHub    | [github.com/banghub](https://github.com/banghub) |
| LinkedIn  | [linkedin.com/in/sabbir-pentester](https://linkedin.com/in/sabbir-pentester) |
| Medium    | [banghub.medium.com](https://banghub.medium.com) |

---

## ⚖️ Legal Disclaimer

> **This tool is intended for authorized security testing only.**
>
> Running this tool against targets without explicit written permission from the owner is **illegal** and may violate computer fraud laws in your jurisdiction. The author is **not responsible** for any misuse or damage caused by this tool.
>
> Always obtain proper authorization before conducting any security testing.
> Use responsibly. Hunt legally. 🐛

---

*Made with ❤️ for the bug bounty community*
