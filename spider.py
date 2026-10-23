import argparse
from collections import deque
from pathlib import Path
from urllib.parse import urljoin, urldefrag, urlparse

import requests
from bs4 import BeautifulSoup

DEFAULT_OUTPUT = Path("output/discovered_urls.txt")
USER_AGENT = "Lowkey/0.1 (authorized web reconnaissance)"


def normalize_url(url):
    """Remove fragments so the same page is not crawled more than once."""
    return urldefrag(url.strip())[0]


def is_http_url(url):
    parsed = urlparse(url)
    return parsed.scheme.lower() in {"http", "https"} and bool(parsed.hostname)


def spider_urls(start_url, keyword="", max_pages=100, output_path=DEFAULT_OUTPUT):
    """Crawl same-host HTML links and save discovered HTTP(S) URLs."""
    start_url = normalize_url(start_url)
    parsed_start = urlparse(start_url)

    if not is_http_url(start_url):
        raise ValueError("Enter a complete HTTP(S) URL, e.g. https://example.com")

    allowed_host = parsed_start.hostname.lower()
    queue = deque([start_url])
    visited_pages = set()
    discovered_urls = set()

    with requests.Session() as session:
        session.headers.update({"User-Agent": USER_AGENT})

        while queue and len(visited_pages) < max_pages:
            current_url = normalize_url(queue.popleft())
            if current_url in visited_pages:
                continue

            parsed_current = urlparse(current_url)
            if not is_http_url(current_url) or parsed_current.hostname.lower() != allowed_host:
                continue

            visited_pages.add(current_url)

            try:
                response = session.get(current_url, timeout=10, allow_redirects=True)
                print(f"[{response.status_code}] {current_url}")
            except requests.RequestException as exc:
                print(f"[!] Request failed for {current_url}: {exc.__class__.__name__}")
                continue

            if "text/html" not in response.headers.get("Content-Type", "").lower():
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            for tag in soup.find_all("a", href=True):
                href = tag.get("href", "").strip()
                if not href or href.startswith(("mailto:", "javascript:", "tel:")):
                    continue

                absolute_url = normalize_url(urljoin(response.url, href))
                parsed_link = urlparse(absolute_url)

                if not is_http_url(absolute_url) or not parsed_link.hostname:
                    continue
                if parsed_link.hostname.lower() != allowed_host:
                    continue

                discovered_urls.add(absolute_url)

                # With no keyword, follow all same-host links. With a keyword,
                # only follow links whose full URL contains that keyword.
                if not keyword or keyword.lower() in absolute_url.lower():
                    if absolute_url not in visited_pages:
                        queue.append(absolute_url)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    all_urls = sorted(discovered_urls | {start_url})
    output_path.write_text("\n".join(all_urls) + ("\n" if all_urls else ""), encoding="utf-8")

    print(f"\nPages visited: {len(visited_pages)}")
    print(f"URLs saved: {len(all_urls)}")
    print(f"Output file: {output_path}")
    return all_urls


def main():
    parser = argparse.ArgumentParser(description="Lowkey: crawl an authorised website.")
    parser.add_argument("url", nargs="?", help="Starting URL")
    parser.add_argument("--keyword", default="", help="Only follow URLs containing this keyword")
    parser.add_argument("--max-pages", type=int, default=100, help="Maximum pages to request")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Output file")
    args = parser.parse_args()

    url = args.url or input("Enter the URL you are authorised to test: ").strip()
    keyword = args.keyword
    if not args.url and not keyword:
        keyword = input("Keyword (press Enter to follow all same-host links): ").strip()

    if args.max_pages < 1:
        parser.error("--max-pages must be at least 1")

    try:
        spider_urls(url, keyword, args.max_pages, args.output)
    except ValueError as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
