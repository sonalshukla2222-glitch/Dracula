import argparse
import sys
from pathlib import Path
from urllib.parse import urlparse

import requests
import urllib3

DEFAULT_INPUT = Path("output/discovered_urls.txt")
DEFAULT_OUTPUT = Path("output/active_targets.txt")
DEFAULT_REPORT = Path("output/probe_results.tsv")
USER_AGENT = "Lowkey/0.1 (authorized web reconnaissance)"


def is_http_url(url):
    parsed = urlparse(url)
    return parsed.scheme.lower() in {"http", "https"} and bool(parsed.hostname)


def read_targets(input_path=None, use_stdin=False):
    """Read one URL per line from a file or standard input."""
    if use_stdin:
        lines = sys.stdin.read().splitlines()
    else:
        path = Path(input_path or DEFAULT_INPUT)
        if not path.exists():
            raise FileNotFoundError(
                f"Input file not found: {path}. Run spider.py first, "
                "or pass --input targets.txt, or use --stdin."
            )
        lines = path.read_text(encoding="utf-8").splitlines()

    targets = []
    seen = set()
    for line in lines:
        url = line.strip()
        if not url or url.startswith("#") or url in seen:
            continue
        seen.add(url)
        if is_http_url(url):
            targets.append(url)
        else:
            print(f"[SKIP] Invalid HTTP(S) URL: {url}")
    return targets


def probe_targets(input_path=DEFAULT_INPUT, output_path=DEFAULT_OUTPUT,
                  report_path=DEFAULT_REPORT, timeout=8, use_stdin=False):
    """
    Check HTTP(S) responsiveness and save responding URLs.

    TLS certificate verification stays enabled. HEAD is tried first; if a server
    rejects HEAD, a streaming GET is used as a fallback. Any HTTP response
    (including 401, 403, or 404) means the web server responded.
    """
    targets = read_targets(input_path, use_stdin=use_stdin)
    output_path = Path(output_path)
    report_path = Path(report_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    active_urls = []
    report_rows = ["URL\tHTTP_STATUS\tFINAL_URL"]

    with requests.Session() as session:
        session.headers.update({"User-Agent": USER_AGENT})

        for url in targets:
            try:
                response = session.head(
                    url, timeout=timeout, allow_redirects=True
                )

                # Some servers do not support HEAD. Retry with GET, without
                # downloading the response body into memory.
                if response.status_code in {405, 501}:
                    response.close()
                    response = session.get(
                        url, timeout=timeout, allow_redirects=True, stream=True
                    )

                status = response.status_code
                final_url = response.url
                response.close()

                print(f"[RESPONDS] {status} {url}")
                active_urls.append(url)
                report_rows.append(f"{url}\t{status}\t{final_url}")

            except requests.exceptions.SSLError:
                print(f"[TLS ERROR] {url} (certificate verification failed)")
            except requests.exceptions.Timeout:
                print(f"[TIMEOUT] {url}")
            except requests.exceptions.ConnectionError:
                print(f"[CONNECTION ERROR] {url}")
            except requests.RequestException as exc:
                print(f"[REQUEST ERROR] {url} ({exc.__class__.__name__})")

    output_path.write_text(
        "\n".join(active_urls) + ("\n" if active_urls else ""),
        encoding="utf-8",
    )
    report_path.write_text("\n".join(report_rows) + "\n", encoding="utf-8")

    print(f"\nTargets checked: {len(targets)}")
    print(f"Targets that returned an HTTP response: {len(active_urls)}")
    print(f"Active URL list: {output_path}")
    print(f"Detailed report: {report_path}")
    return active_urls


def main():
    parser = argparse.ArgumentParser(
        description="Lowkey: check HTTP(S) targets for responsiveness."
    )
    parser.add_argument(
        "--input", default=str(DEFAULT_INPUT),
        help="Input file with one URL per line (default: output/discovered_urls.txt)",
    )
    parser.add_argument(
        "--stdin", action="store_true",
        help="Read URLs from standard input instead of an input file",
    )
    parser.add_argument(
        "--output", default=str(DEFAULT_OUTPUT),
        help="Output file containing responding URLs",
    )
    parser.add_argument(
        "--report", default=str(DEFAULT_REPORT),
        help="Detailed TSV report path",
    )
    parser.add_argument(
        "--timeout", type=float, default=8,
        help="Timeout per request in seconds (default: 8)",
    )
    args = parser.parse_args()

    if args.timeout <= 0:
        parser.error("--timeout must be greater than zero")

    try:
        probe_targets(
            args.input, args.output, args.report, args.timeout, args.stdin
        )
    except FileNotFoundError as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
