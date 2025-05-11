import requests
from bs4 import BeautifulSoup

def scrape_news(news_list):
    detailed_news = []
    for news in news_list:
        url = news["link"]
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")
        content = " ".join([p.text for p in paragraphs[:5]])  # Extract first 5 paragraphs
        detailed_news.append({"title": news["title"], "content": content, "link": url})
    return detailed_news
