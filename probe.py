print("script started")
import sys
import requests


def urls(out_file):  

    good_urls = []
    bad_urls = []

    url2 = sys.stdin.read().splitlines()

    for url in url2:
        url = url.strip()
        try:
            res = requests.head(url, verify=False)

            if res.status_code == 200:
                good_urls.append(url)

        except requests.exceptions.MissingSchema:
            bad_urls.append(url)
            continue
        except requests.exceptions.ConnectionError:
            bad_urls.append(url)
            continue

    with open(out_file, 'w') as file:
        file.write('\n'.join(good_urls))

    print(f"saved urls {out_file}")



out_file = 'filtered_urls.txt'
urls(out_file)
