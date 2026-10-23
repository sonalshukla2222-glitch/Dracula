import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

visited_urls = set()


def spider_urls(url, keyword):
    try:
        response = requests.get(url)
    except:
        print(f"request failed blud{url}")
        return

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        a_tags = soup.find_all('a')
        urls = []
        for tag in a_tags:
            href = tag.get('href')
            if href is not None and href != "":
                urls.append(href)
        for i in urls:
            if i not in visited_urls:
                visited_urls.add(i)
                url_join = urljoin(url, i)
                if keyword in url_join:
                    print(url_join)
                    spider_urls(url_join, keyword)
                else:
                    pass

url = input("Hey what is the url: ")
keyword = input("Okay now, what is the keyword: ")
spider_urls(url, keyword)
