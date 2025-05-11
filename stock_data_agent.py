import os
from typing import Dict, List, Optional, Union, Any
from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeout
import asyncio
import pandas as pd
from datetime import datetime
import json
from bs4 import BeautifulSoup
import logging
import random
import urllib.parse
from urllib.parse import urljoin
import re
from decimal import Decimal
import numpy as np
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FinancialDataParser:
    """Helper class for parsing financial data"""
    
    @staticmethod
    def extract_percentage(text: str) -> Optional[float]:
        """Extract percentage values from text"""
        if not text:
            return None
        match = re.search(r'(-?\d+\.?\d*)\s*%', text)
        return float(match.group(1)) if match else None

    @staticmethod
    def extract_amount(text: str) -> Optional[Decimal]:
        """Extract monetary amounts, handling crores/lakhs/millions"""
        if not text:
            return None
        # Remove commas and convert to lowercase
        text = text.replace(',', '').lower()
        
        # Extract number and multiplier
        number_match = re.search(r'(-?\d+\.?\d*)', text)
        if not number_match:
            return None
            
        amount = Decimal(number_match.group(1))
        
        # Apply multipliers based on units
        multipliers = {
            'cr': Decimal('10000000'),  # crore = 10 million
            'crore': Decimal('10000000'),
            'lakh': Decimal('100000'),
            'lakhs': Decimal('100000'),
            'million': Decimal('1000000'),
            'mn': Decimal('1000000'),
            'billion': Decimal('1000000000'),
            'bn': Decimal('1000000000')
        }
        
        for unit, multiplier in multipliers.items():
            if unit in text:
                amount *= multiplier
                break
                
        return amount

    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        # Remove extra whitespace and normalize
        text = ' '.join(text.split())
        # Remove special characters but keep % and currency symbols
        text = re.sub(r'[^\w\s%₹$€£.-]', '', text)
        return text.strip()

class StockDataAgent:
    def __init__(self):
        self.target_sites = {
            'moneycontrol': 'https://www.moneycontrol.com',
            'screener': 'https://www.screener.in',
            'investing_india': 'https://in.investing.com',
            'economic_times': 'https://economictimes.indiatimes.com',
            'tickertape': 'https://www.tickertape.in'
        }
        self.data_points = {
            'growth_rate': [],
            'performance': [],
            'marginal_changes': [],
            'capex': []
        }
        self.collected_urls = set()
        self.max_retries = 3
        self.timeout = 15000  # 15 seconds timeout

    async def safe_goto(self, page: Page, url: str, retries: int = 0) -> bool:
        """Safely navigate to a URL with retries and fallback strategies"""
        try:
            # First try with domcontentloaded
            await page.goto(url, timeout=self.timeout, wait_until='domcontentloaded')
            # Wait a bit for dynamic content
            await asyncio.sleep(2)
            return True
        except PlaywrightTimeout:
            if retries < self.max_retries:
                logger.warning(f"Timeout on {url}, retry {retries + 1}/{self.max_retries}")
                await asyncio.sleep(2 * (retries + 1))  # Exponential backoff
                return await self.safe_goto(page, url, retries + 1)
            logger.error(f"Failed to load {url} after {self.max_retries} retries")
            return False
        except Exception as e:
            logger.error(f"Error loading {url}: {str(e)}")
            return False

    async def extract_data_from_url(self, page: Page, url: str, data_type: str) -> Optional[Dict]:
        """Extract data from a specific URL"""
        if url in self.collected_urls:
            return None
        
        try:
            if not await self.safe_goto(page, url):
                return None

            # Get page content
            content = await page.content()
            soup = BeautifulSoup(content, 'lxml')
            
            # Extract data based on type
            data = {
                'url': url,
                'timestamp': datetime.now().isoformat(),
                'text_data': []
            }
            
            # Define search patterns for each data type
            patterns = {
                'growth_rate': r'(?:growth|increase|yoy|cagr|growth\s+rate)',
                'performance': r'(?:performance|return|metric|profit|revenue)',
                'marginal_changes': r'(?:qoq|yoy|quarter|year|change)',
                'capex': r'(?:capex|capital\s+expenditure|investment)'
            }
            
            # Look for data in both text content and table cells
            elements = []
            
            # Search in regular elements
            elements.extend(soup.find_all(['div', 'p', 'td', 'tr', 'li'], 
                text=re.compile(patterns[data_type], re.I)))
            
            # Search in tables
            tables = soup.find_all('table')
            for table in tables:
                if table.find(text=re.compile(patterns[data_type], re.I)):
                    elements.extend(table.find_all(['tr', 'td']))
            
            # Extract and clean text from elements
            for elem in elements:
                text = elem.get_text(strip=True)
                if text and len(text.strip()) > 10:
                    cleaned_text = FinancialDataParser.clean_text(text)
                    if cleaned_text not in data['text_data']:  # Avoid duplicates
                        data['text_data'].append(cleaned_text)
            
            if data['text_data']:
                self.collected_urls.add(url)
                return data
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting data from {url}: {str(e)}")
            return None

    async def scrape_company(self, browser: Browser, company_name: str):
        """Scrape data for a specific company"""
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        
        try:
            page = await context.new_page()
            await page.set_viewport_size({"width": 1920, "height": 1080})
            
            for site_name, base_url in self.target_sites.items():
                try:
                    # Create search URL based on site
                    if site_name == 'moneycontrol':
                        search_url = f"{base_url}/stocks/company-info/{company_name.replace(' ', '-')}"
                    elif site_name == 'screener':
                        search_url = f"{base_url}/company/{company_name.replace(' ', '-')}"
                    else:
                        search_query = f"{company_name} stock financial results"
                        search_url = f"{base_url}/search?q={urllib.parse.quote(search_query)}"
                    
                    if not await self.safe_goto(page, search_url):
                        continue
                    
                    await asyncio.sleep(1 + random.random())
                    
                    # Get all relevant links
                    content = await page.content()
                    soup = BeautifulSoup(content, 'lxml')
                    links = soup.find_all('a', href=True)
                    
                    relevant_urls = []
                    for link in links:
                        href = link['href']
                        if not href.startswith('http'):
                            href = urljoin(base_url, href)
                        
                        # Filter relevant URLs
                        if any(keyword in href.lower() for keyword in [
                            'stock', 'company', 'financial', 'share', 'quote',
                            company_name.lower().replace(' ', '-')
                        ]):
                            relevant_urls.append(href)
                    
                    # Process each relevant URL
                    for url in relevant_urls[:3]:  # Limit to top 3 results per site
                        for data_type in self.data_points.keys():
                            data = await self.extract_data_from_url(page, url, data_type)
                            if data:
                                self.data_points[data_type].append({
                                    'company': company_name,
                                    'source': site_name,
                                    **data
                                })
                        
                        # Add small random delay between URLs
                        await asyncio.sleep(1 + random.random())
                        
                except Exception as e:
                    logger.error(f"Error processing {site_name} for {company_name}: {str(e)}")
                    continue
                
        finally:
            await context.close()

    async def run(self, companies: List[str]):
        """Main method to run the scraping agent"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--disable-dev-shm-usage', '--no-sandbox']
            )
            try:
                for company in companies:
                    logger.info(f"Processing company: {company}")
                    await self.scrape_company(browser, company)
                    # Add small delay between companies
                    await asyncio.sleep(2 + random.random())
            finally:
                await browser.close()
        
        return self.data_points

    def save_results(self, output_dir: str = 'results'):
        """Save the scraped data with comprehensive analysis"""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Get unique companies
        companies = set(item['company'] for items in self.data_points.values() for item in items)
        
        # Process each company
        for company in companies:
            # Create company-specific directory
            company_dir = os.path.join(output_dir, company.replace(' ', '_'))
            os.makedirs(company_dir, exist_ok=True)
            
            # Filter data for this company
            company_data = {
                data_type: [
                    item for item in items
                    if item['company'] == company
                ]
                for data_type, items in self.data_points.items()
            }
            
            # Save raw data
            raw_data_file = os.path.join(company_dir, f"raw_data_{timestamp}.json")
            with open(raw_data_file, 'w', encoding='utf-8') as f:
                json.dump(company_data, f, indent=2, ensure_ascii=False)
            
            # Save CSV files for each data type
            for data_type, items in company_data.items():
                if items:
                    df = pd.DataFrame(items)
                    csv_filename = os.path.join(company_dir, f"{data_type}_{timestamp}.csv")
                    df.to_csv(csv_filename, index=False)
            
            logger.info(f"Saved data for {company} to {company_dir}")

if __name__ == "__main__":
    # Example usage with your chosen companies
    companies = [
        "TCS",
        "Reliance Industries",
        "HDFC Bank"
    ]
    
    # Create results directory if it doesn't exist
    os.makedirs("results", exist_ok=True)
    
    # Initialize and run the agent
    agent = StockDataAgent()
    asyncio.run(agent.run(companies))
    agent.save_results() 