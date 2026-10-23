# Dracula

**Dracula** is a small Python web-reconnaissance project with two scripts supplied by its author:

- `spider.py` — the web spider script.
- `probe.py` — the URL probing/filtering script.

## Files

```text
Dracula/
├── README.md
├── spider.py
├── probe.py
├── requirements.txt
├── .gitignore
└── output/
    └── .gitkeep
```

## Requirements

- Python 3
- `requests`
- `beautifulsoup4`

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Spider

Run:

```bash
python spider.py
```

The script prompts for a URL and a keyword. It uses `requests` to fetch pages, `BeautifulSoup` to find HTML anchor links, and `urljoin` to resolve relative links.

## Probe

The probe reads URLs from standard input and writes URLs returning HTTP status `200` to `filtered_urls.txt`.

Example input from a text file:

```bash
python probe.py < targets.txt
```

PowerShell:

```powershell
Get-Content targets.txt | python probe.py
```

## Important notes about the supplied scripts

The Python scripts in this repository are preserved exactly as supplied by the project author, without code changes.

- The supplied `spider.py` has an incomplete `else:` block and will raise a syntax error until its author chooses to fix it.
- The supplied `probe.py` uses `verify=False`, which disables TLS certificate verification. That can make HTTPS checks insecure.
- The probe only records responses with status code `200`; other status codes are not written to its good-URL output.
- The probe reads from standard input, so provide a list of URLs using input redirection or a pipe.

Only test websites and systems you own or have explicit permission to assess.

## Contributing

Contributions are welcome. If you want to add another feature, consider placing it in a separate Python module and documenting its dependencies and usage here.

1. Fork the repository.
2. Create a branch for your change.
3. Test changes only in a local lab or against authorised targets.
4. Open a Pull Request describing the change and how it was tested.

Do not commit credentials, private target lists, or real reconnaissance output.

## License

No license has been selected yet. Add a `LICENSE` file if you want to grant others explicit permission to reuse, modify, or redistribute this project.
