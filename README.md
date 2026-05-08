# CyberSec Ops Toolkit 2.0
 
## Overview

**What does your toolkit do?**
The CyberSec Ops Toolkit is a modular, Python-based framework designed for security assessments and operational data gathering. It features a unified CLI to manage local file scanning, multithreaded network port scanning, packet sniffing, web scraping, headless browser automation, remote SSH execution, and centralized reporting via a local HTTP dashboard.

**How to install dependencies?**
Ensure you have Python 3.8+ installed, then run:
`pip install scapy requests beautifulsoup4 selenium paramiko send2trash`

**How to run the toolkit?**
The toolkit is executed via the `main.py` entry point followed by a specific subcommand:
`python main.py <subcommand> [arguments]`

---

## Subcommands

### 1. `scan`
**Description:** Scans a directory for suspicious file contents using regex and quarantines threats.
**Example:**
`python main.py scan --dir ./var/www/html --ext *.php`

### 2. `net-scan`
**Description:** A multi-threaded network scanner for identifying open ports across IPs or CIDR blocks.
**Example:**
`python main.py net-scan --target 192.168.1.0/24 --ports 22 80 443 --threads 50`

### 3. `sniff`
**Description:** Captures unencrypted network traffic and analyzes packets for credentials.
**Example:**
`python main.py sniff --iface eth0 --count 100`

### 4. `scrape`
**Description:** Extracts specific CSS-selected data and hidden emails from a target web page.
**Example:**
`python main.py scrape --url http://target.local --selectors h1 p`

### 5. `web-auto`
**Description:** Navigates to a target URL using a headless browser and captures a screenshot.
**Example:**
`python main.py web-auto --url http://target.local/admin`

### 6. `ssh`
**Description:** Executes commands remotely on a target machine via SSH or locally via subprocess.
**Example:**
`python main.py ssh --host 10.0.0.5 --user root --cmd "whoami" --pwd "toor"`


### 7. `serve`
**Description:** Spawns a lightweight local HTTP server to host and view the `reports` directory.
**Example:**
`python main.py serve --port 8080`


### 8. `report`
**Description:** Merges individual tool JSON logs into an executive summary and can send SMTP alerts.
**Example:**
`python main.py report --email admin@local.domain`


---

## Checklist of Required Modules

| Module                 | Where used?                                                                              |
|:-----------------------|:-----------------------------------------------------------------------------------------|
| `argparse`             | `cli` (Main CLI router and argument parsing)                                             |
| `base64`               | `web-auto`, `sniff`, `report` (Encoding screenshots and headers)                         |
| `bs4` (beautiful-soup) | `scrape` (HTML DOM parsing)                                                              |
| `datetime`             | Used across all modules for timestamping logs                                            |
| `email`                | `report` (MIME email construction)                                                       |
| `fnmatch`              | `scan` (Filtering file extensions)                                                       |
| `glob`                 | `scan`, `report` (Finding/aggregating files in directories)                              |
| `http`                 | `serve` (Local HTTP dashboard server)                                                    |
| `Pillow`               | `web-auto`, `web-auto` (Custom module for local image display)                           |
| `itertools`            | `net-scan` (Generating combined lists of IPs and Ports)                                  |
| `json`                 | Used across all modules for reading and writing report files                             |
| `os`                   | Used across all modules for directory handling and path checks                           |
| `paramiko`             | `ssh` (Remote SSH client connection)                                                     |
| `pathlib`              | `web-auto` (Advanced path management/formatting)                                         |
| `random`               | `net-scan` (Randomizing scan order and adding time jitter)                               |
| `re`                   | `scan`, `sniff`, `scrape`, `utils` (Regex pattern matching and sanitization)             |
| `requests`             | `scrape` (Fetching target HTML content)                                                  |
| `scapy`                | `sniff` (Network interface packet capturing)                                             |
| `selenium`             | `web-auto` (Headless browser automation)                                                 |
| `send2trash`           | `scan` (Safely quarantining malicious files to OS recycle bin)                           |
| `shutil`               | `scan` (File moving and copying operations)                                              |
| `socket`               | `net-scan`, `report` (Port scanning and raw SMTP connections)                            |
| `subprocess`           | `ssh` (Executing OS-level local commands)                                                |
| `sys`                  | `cli` (Handling system exit codes and arguments)                                         |
| `threading`            | `net-scan` (Parallelizing scan tasks across CPU threads)                                 |
| `time`                 | `net-scan` (Enforcing delays and thread sleep cycles)                                    |
| `pytest`               | `tests` (Executing the automated testing suite)                                          |
| `hypothesis`           | `test_web_auto` (Property-based testing and input fuzzing)                               |
| `responses`            | `test_web_auto` (Mocking HTTP requests for the `scrape` module tests)                    |

---

## Three Self-Chosen New Modules

## Three Self-Chosen New Modules

### 1. `pytest`
*   **What does it do?** It is a powerful testing framework for writing simple, readable, and scalable Python test cases.
*   **Why did you choose it?** Python's built-in `unittest` requires heavy boilerplate. `pytest` allows for rapid test development using clean `assert` statements, features automatic test discovery, and provides highly detailed error tracebacks.
*   **Where and how is it used in the code?** Used in the `tests` directory as the primary test runner to execute our automated testing suite and validate the core logic of our operational modules.

### 2. `hypothesis`
*   **What does it do?** It is an advanced library for property-based testing and input fuzzing.
*   **Why did you choose it?** Security tools must handle unpredictable inputs gracefully. Instead of hardcoding test values, `hypothesis` generates thousands of edge-case, malformed, and randomized inputs to ensure our toolkit doesn't crash unexpectedly.
*   **Where and how is it used in the code?** Used in the `tests` directory to automatically fuzz the input parameters of our modules (e.g., feeding random strings to the regex scanner or malformed IP data to the subnet calculator).

### 3. `responses`
*   **What does it do?** It is a utility library used to intercept and mock HTTP requests made by the Python `requests` library.
*   **Why did you choose it?** Automated tests should be fast and run offline. Hitting live websites during testing is slow and unreliable. `responses` catches outgoing requests and instantly returns fake, predetermined HTML data.
*   **Where and how is it used in the code?** Used in the `tests` directory to mock the target URLs for the `scrape` module, allowing us to safely test DOM parsing and regex extraction without generating actual network traffic.
---

## Ethical disclaimer
> **Use only on your own devices / legal test environments.**#
 
 
