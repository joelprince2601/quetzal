import requests
import time
from bs4 import BeautifulSoup
from flask import Flask, jsonify
from transformers import pipeline
from serpapi import GoogleSearch

# Flask App
app = Flask(__name__)

# SerpAPI Key (Replace with your own)
SERPAPI_KEY = "0055ffe7b223901af40a28dfff9e20a71adc0ded71b9783580e14e488147d939"

# Initialize AI Classifier (Using DistilBERT for sentiment analysis)
classifier = pipeline("sentiment-analysis")

# OpenAI GPT for reasoning (Optional)
GPT_API_KEY = "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"

# Function to fetch news from Google News API
def fetch_news(query):
    params = {
        "q": query,
        "hl": "en",
        "gl": "us",
        "api_key": SERPAPI_KEY
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    return results.get("news_results", [])

# Function to scrape news from Reuters (Example)
def scrape_news(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    articles = soup.find_all("article")

    news_data = []
    for article in articles:
        title = article.find("h2").text if article.find("h2") else "No title"
        link = article.find("a")["href"] if article.find("a") else "No link"
        news_data.append({"title": title, "link": link})

    return news_data

# Function to filter relevant news using AI
def filter_news(news_list):
    relevant_news = []
    for news in news_list:
        analysis = classifier(news["title"])
        if analysis[0]["label"] == "POSITIVE":  # Assuming positive sentiment indicates relevance
            relevant_news.append(news)
    
    return relevant_news

# Function to analyze news impact using GPT (Optional)
def analyze_news(news_text):
    headers = {"Authorization": f"Bearer {GPT_API_KEY}"}
    data = {"model": "gpt-4", "messages": [{"role": "user", "content": f"Analyze this news: {news_text}"}]}
    response = requests.post("https://api.openai.com/v1/chat/completions", json=data, headers=headers)
    
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return "Analysis failed."

# Flask API Route
@app.route('/stock-news/<symbol>', methods=['GET'])
def get_stock_news(symbol):
    news = fetch_news(f"{symbol} stock performance")
    filtered_news = filter_news(news)

    # Optional reasoning
    for news_item in filtered_news:
        news_item["impact_analysis"] = analyze_news(news_item["title"])
    
    return jsonify({"stock": symbol, "news": filtered_news})

# Run Flask Server
if __name__ == "__main__":
    app.run(debug=True, port=5000)
