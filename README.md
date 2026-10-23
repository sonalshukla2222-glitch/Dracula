# Lowkey

**Lowkey** is a small Python web-reconnaissance project for learning and authorised security testing. It currently has two separate modules:

- **Spider** — crawls links on a website and saves discovered same-host HTTP(S) URLs.
- **Probe** — checks a list of HTTP(S) URLs and records which targets returned an HTTP response.

> **Permission first:** Only use Lowkey on websites and systems you own or have explicit permission to test. Respect scope, rate limits, and the target's terms. This project is an educational starting point, not a replacement for a professional assessment process.

## Project structure

```text
lowkey/
├── README.md
├── spider.py
├── probe.py
├── requirements.txt
├── .gitignore
└── output/
    └── .gitkeep
```

Generated results are written into `output/` by default. They are ignored by Git so you don't accidentally publish target lists or scan results.

## Requirements

- Python 3.10 or newer recommended
- Internet access to the authorised test site
- `requests` and `beautifulsoup4` (installed below)

## Installation

### 1. Clone the repository

Replace `YOUR-USERNAME` with your GitHub username after you publish the repository:

```bash
git clone https://github.com/YOUR-USERNAME/lowkey.git
cd lowkey
```

Or download the repository ZIP from GitHub and extract it.

### 2. Create a virtual environment

**Windows PowerShell:**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can run the environment's Python directly instead:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**Linux / Kali / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

## Usage

Use a site you control or have permission to test. The examples below use `https://example.com` as a placeholder; replace it with your authorised target.

### Spider: discover URLs

```bash
python spider.py https://example.com
```

This follows same-host links, up to 100 pages by default, and writes the starting URL plus discovered links to:

```text
output/discovered_urls.txt
```

Set a page limit:

```bash
python spider.py https://example.com --max-pages 25
```

Only follow links whose URL contains a keyword:

```bash
python spider.py https://example.com --keyword products
```

Choose a different output file:

```bash
python spider.py https://example.com --output output/my_urls.txt
```

The optional keyword controls which discovered links are followed for further crawling. URLs found on the same hostname are still recorded. The spider does not follow links to other hostnames.

### Probe: check URL responsiveness

Run the probe after the spider:

```bash
python probe.py
```

By default, it reads `output/discovered_urls.txt` and writes results to:

```text
output/active_targets.txt
```

You can also provide your own text file containing one HTTP(S) URL per line:

```bash
python probe.py --input targets.txt --output output/active_targets.txt
```

Adjust the per-request timeout:

```bash
python probe.py --timeout 5
```

The probe sends one HTTP GET request per URL. A URL is considered responsive if the server returns an HTTP status code. For example, `200`, `301`, `401`, `403`, and `404` all indicate that an HTTP server responded; they do **not** all mean the page is accessible or that a vulnerability exists. Connection failures and timeouts are reported as no response.

## Typical workflow

1. Run the spider against an authorised website.
2. Review `output/discovered_urls.txt`.
3. Run the probe on the discovered URLs.
4. Review `output/active_targets.txt`.
5. Manually validate interesting results within the approved scope.

## Output format

`discovered_urls.txt` contains one URL per line.

`active_targets.txt` contains tab-separated columns:

```text
# URL    HTTP_STATUS    FINAL_URL
https://example.com    200    https://example.com/
```

The values above are illustrative, not the result of a real scan.

## Current limitations

- The spider reads links from HTML anchors; it does not execute JavaScript.
- It stays on the starting hostname and does not discover every URL or hidden endpoint.
- The probe checks HTTP(S) responsiveness only. It does not perform port scanning, vulnerability detection, or exploitation.
- Network errors can have many causes, so “no response” does not prove a host is offline.
- Use low request volumes and stop if the site becomes unstable.

## Contributing

Contributions are welcome.

1. Fork the repository on GitHub.
2. Create a branch for your change:

   ```bash
   git checkout -b feature/your-feature
   ```

3. Add or edit a module. For example, a new reconnaissance feature should generally live in its own Python file (such as `headers.py`) rather than making `spider.py` responsible for everything.
4. Keep dependencies listed in `requirements.txt`.
5. Test only against a local lab or an authorised target.
6. Commit and push your branch:

   ```bash
   git add .
   git commit -m "Add: describe your change"
   git push origin feature/your-feature
   ```

7. Open a Pull Request on GitHub and explain what changed, how you tested it, and any new dependencies.

Please do not commit credentials, private target lists, tokens, or real reconnaissance output. Generated `output/*.txt` files are ignored by Git.

## License

No license has been selected yet. Before publishing, choose a license (for example, MIT) and add its text in a `LICENSE` file. Without a license, others generally do not receive explicit permission to reuse, modify, or redistribute your code.
