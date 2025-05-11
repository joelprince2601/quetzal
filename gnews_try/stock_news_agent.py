import os
import json
import requests
import feedparser
from datetime import datetime, timedelta
import pandas as pd
from abc import ABC, abstractmethod
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import yfinance as yf
from typing import List, Dict, Optional

class NewsAPIBase(ABC):
    """Abstract base class for news API implementations"""
    
    # Maximum number of articles to fetch per call
    MAX_ARTICLES = 10
    
    @abstractmethod
    def fetch_news(self, symbol: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Fetch news from the API"""
        pass

    @abstractmethod
    def get_api_details(self) -> Dict:
        """Get the details of the API"""
        pass

class NewsAPIClient(NewsAPIBase):
    """NewsAPI implementation"""
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2/everything"

    def fetch_news(self, symbol: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        params = {
            'q': symbol,
            'from': start_date.strftime('%Y-%m-%d'),
            'to': end_date.strftime('%Y-%m-%d'),
            'apiKey': self.api_key,
            'language': 'en',
            'sortBy': 'publishedAt'
        }
        
        response = requests.get(self.base_url, params=params)
        if response.status_code != 200:
            raise Exception(f"NewsAPI Error: {response.json().get('message', 'Unknown error')}")
        
        articles = response.json().get('articles', [])
        return [
            {
                'title': article['title'],
                'description': article['description'],
                'url': article['url'],
                'source': article['source']['name'],
                'published_at': article['publishedAt']
            }
            for article in articles
        ]

    def get_api_details(self) -> Dict:
        return {
            'name': 'NewsAPI',
            'rate_limit': '100 requests/day',
            'requires_key': True
        }

class AlphaVantageClient(NewsAPIBase):
    """Alpha Vantage News API implementation"""
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"

    def get_api_details(self) -> Dict:
        return {
            'name': 'Alpha Vantage',
            'rate_limit': '5 requests/minute',
            'requires_key': True
        }

    def fetch_news(self, symbol: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        try:
            params = {
                'function': 'NEWS_SENTIMENT',
                'apikey': self.api_key,
                'keywords': symbol,
                'limit': self.MAX_ARTICLES,  # Use constant
                'from': start_date.strftime('%Y-%m-%d'),
                'to': end_date.strftime('%Y-%m-%d')
            }
            
            response = requests.get(self.base_url, params=params)
            
            if response.status_code == 401:
                print("Invalid API key for Alpha Vantage")
                return []
                
            response.raise_for_status()
            data = response.json()
            
            if 'feed' not in data:
                print(f"API Error: {data.get('Note', 'Unknown error')}")
                return []
            
            # Convert Alpha Vantage format to standard format
            articles = []
            for item in data['feed'][:self.MAX_ARTICLES]:  # Ensure max limit
                articles.append({
                    'title': item.get('title'),
                    'description': item.get('summary'),
                    'url': item.get('url'),
                    'source': {'name': item.get('source')},
                    'published_at': item.get('time_published')
                })
                
            return articles
            
        except Exception as e:
            print(f"Error fetching from Alpha Vantage: {str(e)}")
            return []

class MarketauxClient(NewsAPIBase):
    """Marketaux API implementation"""
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.marketaux.com/v1/news/all"

    def get_api_details(self) -> Dict:
        return {
            'name': 'Marketaux',
            'rate_limit': '100 requests/day',
            'requires_key': True
        }

    def fetch_news(self, symbol: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        try:
            params = {
                'api_token': self.api_key,
                'language': 'en',
                'limit': self.MAX_ARTICLES,  # Use constant
                'search': symbol,
                'from': start_date.strftime('%Y-%m-%d'),
                'to': end_date.strftime('%Y-%m-%d')
            }
            
            response = requests.get(self.base_url, params=params)
            
            if response.status_code == 401:
                print("Invalid API key for Marketaux")
                return []
                
            response.raise_for_status()
            data = response.json()
            
            if 'data' not in data:
                print(f"API Error: {data.get('error', {}).get('message', 'Unknown error')}")
                return []
            
            # Convert Marketaux format to standard format
            articles = []
            for item in data['data'][:self.MAX_ARTICLES]:  # Ensure max limit
                articles.append({
                    'title': item.get('title'),
                    'description': item.get('description'),
                    'url': item.get('url'),
                    'source': {'name': item.get('source')},
                    'published_at': item.get('published_at')
                })
                
            return articles
            
        except Exception as e:
            print(f"Error fetching from Marketaux: {str(e)}")
            return []

class BingNewsClient(NewsAPIBase):
    """Bing News API implementation"""
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.bing.microsoft.com/v7.0/news/search"

    def get_api_details(self) -> Dict:
        return {
            'name': 'Bing News',
            'rate_limit': '1000 transactions/month',
            'requires_key': True
        }

    def fetch_news(self, symbol: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        headers = {
            'Ocp-Apim-Subscription-Key': self.api_key
        }
        params = {
            'q': f"{symbol} stock",
            'count': 100,
            'freshness': 'Week',
            'mkt': 'en-US'
        }
        
        response = requests.get(self.base_url, headers=headers, params=params)
        if response.status_code != 200:
            raise Exception(f"Bing News API Error: {response.json().get('message', 'Unknown error')}")
        
        articles = response.json().get('value', [])
        return [
            {
                'title': article['name'],
                'description': article['description'],
                'url': article['url'],
                'source': article['provider'][0]['name'],
                'published_at': article['datePublished']
            }
            for article in articles
        ]

class GoogleNewsClient(NewsAPIBase):
    """Google News RSS implementation (no API key needed)"""
    def __init__(self):
        pass

    def get_api_details(self) -> Dict:
        return {
            'name': 'Google News',
            'rate_limit': 'Unlimited',
            'requires_key': False
        }

    def fetch_news(self, symbol: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        feed_url = f"https://news.google.com/rss/search?q={symbol}+stock&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(feed_url)
        
        return [
            {
                'title': entry.title,
                'description': entry.description,
                'url': entry.link,
                'source': entry.source.title if hasattr(entry, 'source') else 'Google News',
                'published_at': entry.published
            }
            for entry in feed.entries
        ]

class YahooFinanceClient(NewsAPIBase):
    """Yahoo Finance RSS implementation (no API key needed)"""
    def __init__(self):
        pass

    def get_api_details(self) -> Dict:
        return {
            'name': 'Yahoo Finance',
            'rate_limit': 'Unlimited',
            'requires_key': False
        }

    def fetch_news(self, symbol: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        stock = yf.Ticker(symbol)
        news = stock.news
        
        return [
            {
                'title': article['title'],
                'description': article.get('summary', ''),
                'url': article['link'],
                'source': 'Yahoo Finance',
                'published_at': datetime.fromtimestamp(article['providerPublishTime']).isoformat()
            }
            for article in news
        ]

class StockNewsAgent:
    # Default API keys
    DEFAULT_API_KEYS = {
        'newsapi': '2c11424340684a6687f3675eb09d6def',  # Default NewsAPI key
        'alphavantage': 'SGAWY6DPXP9HXOSW',  # Default Alpha Vantage key
        'marketaux': 'JHe86IHgMO7UeNFkZEGGn3p9EeEQJHVL7YwTHIXx',  # Default Marketaux key
        'bing': '23d988c6912d4f1c9c1111fae19807f2'  # Default Bing News API key
    }

    def __init__(self, api_keys: Dict[str, str]):
        """Initialize the StockNewsAgent with API keys for different services.
        
        Args:
            api_keys (dict): Dictionary of API keys. If None, uses default keys.
        """
        # Use provided API keys or fall back to defaults
        self.api_keys = api_keys if api_keys else self.DEFAULT_API_KEYS
        
        self.api_clients = {
            'newsapi': NewsAPIClient(self.api_keys.get('newsapi')),
            'alphavantage': AlphaVantageClient(self.api_keys.get('alphavantage')),
            'marketaux': MarketauxClient(self.api_keys.get('marketaux')),
            'bing': BingNewsClient(self.api_keys.get('bing')),
            'google': GoogleNewsClient(),  # No API key needed
            'yahoo': YahooFinanceClient()  # No API key needed
        }
        
        # Major Indian companies with more additions
        self.indian_companies = {
            "Reliance Industries": "RELIANCE.NS",
            "TCS": "TCS.NS",
            "HDFC Bank": "HDFCBANK.NS",
            "Infosys": "INFY.NS",
            "ITC": "ITC.NS",
            "State Bank of India": "SBIN.NS",
            "Bharti Airtel": "BHARTIARTL.NS",
            "HUL": "HINDUNILVR.NS",
            "ICICI Bank": "ICICIBANK.NS",
            "Adani Enterprises": "ADANIENT.NS",
            "Wipro": "WIPRO.NS",
            "Axis Bank": "AXISBANK.NS",
            "Bajaj Finance": "BAJFINANCE.NS",
            "Asian Paints": "ASIANPAINT.NS",
            "Maruti Suzuki": "MARUTI.NS",
            "Sun Pharma": "SUNPHARMA.NS",
            "Tata Motors": "TATAMOTORS.NS",
            "Tech Mahindra": "TECHM.NS",
            "Power Grid": "POWERGRID.NS",
            "NTPC": "NTPC.NS",
            "L&T": "LT.NS",
            "Kotak Mahindra Bank": "KOTAKBANK.NS",
            "Titan Company": "TITAN.NS",
            "UltraTech Cement": "ULTRACEMCO.NS",
            "Bajaj Auto": "BAJAJ-AUTO.NS"
        }

    def get_available_companies(self):
        """Return list of available Indian companies."""
        return list(self.indian_companies.keys())

    def get_available_apis(self):
        """Return list of available API services."""
        return [client.get_api_details() for client in self.api_clients.values()]

    def process_news_data(self, news_items):
        """Process and structure the news data."""
        processed_data = []
        current_date = datetime.now()
        
        for item in news_items:
            # Parse and validate the date
            published_date = item.get('published_at', '')
            try:
                # Try different date formats
                for date_format in [
                    '%Y-%m-%dT%H:%M:%SZ',  # Standard ISO format
                    '%Y%m%dT%H%M%S',       # Compact format
                    '%Y-%m-%d %H:%M:%S',   # Common format
                    '%Y-%m-%d'             # Date only format
                ]:
                    try:
                        parsed_date = datetime.strptime(published_date, date_format)
                        # Check if date is in the future
                        if parsed_date > current_date:
                            # If future date, set to current date
                            parsed_date = current_date
                        published_date = parsed_date.strftime('%Y-%m-%d %H:%M:%S')
                        break
                    except ValueError:
                        continue
            except Exception:
                # If date parsing fails, use current date
                published_date = current_date.strftime('%Y-%m-%d %H:%M:%S')

            news_data = {
                'title': item.get('title', ''),
                'description': item.get('description', ''),
                'published_date': published_date,
                'publisher': item.get('source', {}).get('name', ''),
                'url': item.get('url', ''),
                'image': ''  # RSS feed doesn't provide images
            }
            processed_data.append(news_data)
            
        return processed_data

    def run(self, symbol: str, start_date: datetime, end_date: datetime, api_choice: str = 'google') -> List[Dict]:
        """Main method to run the news gathering process."""
        try:
            # Get the selected API client
            api_client = self.api_clients.get(api_choice)
            if not api_client:
                print(f"Invalid API choice: {api_choice}")
                return []

            print(f"\nFetching news using {api_client.get_api_details()['name']} with symbol: {symbol}")
            news_items = api_client.fetch_news(symbol, start_date, end_date)
            processed_news = self.process_news_data(news_items)
            
            # Convert to DataFrame and sort by date
            df = pd.DataFrame(processed_news)
            if not df.empty:
                # Sort by date
                df = df.sort_values('published_date', ascending=False)
                # Always take exactly 10 articles (or all if less than 10)
                df = df.head(api_client.MAX_ARTICLES)
            
            print(f"\nTotal articles fetched: {len(df)}")
            return df.to_dict(orient='records')
            
        except Exception as e:
            print(f"Error in run method: {str(e)}")
            return []

if __name__ == "__main__":
    # Example usage with multiple API keys
    api_keys = {
        'newsapi': 'your_newsapi_key',
        'alphavantage': 'your_alphavantage_key',
        'marketaux': 'your_marketaux_key',
        'bing': 'your_bing_news_api_key'
    }
    agent = StockNewsAgent(api_keys)
    news_data = agent.run("AAPL", datetime.now() - timedelta(days=7), datetime.now()) 