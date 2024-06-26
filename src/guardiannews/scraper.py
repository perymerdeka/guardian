import json
import requests
from guardiannews.models import NewsScraped

from datetime import datetime
from typing import Any
from bs4 import BeautifulSoup
from rich import print


# url = "https://www.theguardian.com/ |artanddesign |/2024/apr/24/|  claudette-johnson-art-cotton-capital-nominated-for-turner-prize"


class GuardianSpider(object):
    def __init__(self):
        self.base_url: str = "https://www.theguardian.com"
        # self.category: Optional[str] = category
        self.date: str = datetime.now().strftime("/%Y/%b/%d/")
        # self.subcategory: Optional[str] = subcategory

    def get_response(self, url: str) -> BeautifulSoup:
        headers: dict[str, Any] = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        }

        res = requests.get(url=url, headers=headers)
        print("Site Status Code: ", res.status_code)

        #  response checking
        with open("response.html", "w", encoding="utf-8") as file:
            file.write(res.text)
        #f = open("response.html", 'w+')
        #f.write(res.text)
        #f.close()

        # scrape process
        soup: BeautifulSoup = BeautifulSoup(res.text, "html.parser")

        return soup

    def get_latest_news(self, soup: BeautifulSoup):
        # res = requests.get(os.path.join(self.base_url, "international"), headers=headers)

        contents = soup.find("div", attrs={"id": "container-headlines"}).find_all("li")
        for content in contents:
            title: str = content.find("span", attrs={"class": "show-underline"}).text.strip()
            print(title)

    def get_category(self, soup: BeautifulSoup):
        categories: list[dict[str, str]] = []
        navbar = soup.find('div', attrs={'data-component': 'nav2'})

        # get pillar list
        pillars = navbar.find('ul', attrs={'data-testid': 'pillar-list'}).find_all('a')
        for pillar in pillars:
            link = pillar.get('href')
            category = pillar.text

            data_pillar: dict[str, str] = {
                "link": link,
                "category": category
            }
            categories.append(data_pillar)

        menubar = navbar.find('ul', attrs={'role': 'menubar'}).find_all('a')
        for menu in menubar:
            data_menubar: dict[str, str] = {
                'link': menu.get('href'),
                'category': menu.text
            }
            categories.append(data_menubar)

        # return hasil
        print("Generate URL")
        with open('categories.json', 'w') as json_file:
            json.dump(categories, json_file)

        return categories

    def get_spesific_news(self):
        pass

    def get_news_by_category(self):
        pass

    def get_news_by_subcategory(self, url : str ):
        soup = self.get_response(url)
        urls : list[BeautifulSoup] = soup.find_all("a", class_= "dcr-lv2v9o")
        urls = [f"https://www.theguardian.com{url['href']}" for url in urls]

        return urls

    def get_detail_news(self, url : str):
        soup = self.get_response(url)
        title = soup.find("div", attrs={"class" : "dcr-1msbrj1"}) #class_="dcr-tjsa08" == attrs={"class" : "dcr-tjsa08"}
        title = title.get_text()
        tag_news = soup.find("aside", class_="dcr-ien304")
        tag_news : list[BeautifulSoup] = tag_news.find_all("span")[-1].get_text()
        paragraphs : list[BeautifulSoup] = soup.find_all("p", class_="dcr-iy9ec7")
        paragraphs = [i.get_text() for i in paragraphs]
        paragraphs = "\n".join(paragraphs)
        authors : list[BeautifulSoup] = soup.find_all("a", rel="author")
        authors = [i.get_text() for i in authors]
        published_time = soup.find("span", class_="dcr-u0h1qy").get_text()
        output = NewsScraped(title=title,
                             tag_news=tag_news,
                             paragraphs=paragraphs,
                             authors=authors,
                             published_time=published_time)
        return output