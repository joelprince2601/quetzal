# Stock Data Scraping Agent

This project implements an intelligent web scraping agent using Crawl4AI to collect stock-related data from various Indian financial websites. The agent is designed to mimic human browsing behavior and collect specific financial metrics.

## Data Points Collected

The agent collects the following types of financial data:

1. Company Growth Rate
2. Performance Tracking
3. Marginal Improvements (QoQ, YoY changes)
4. Capital Expenditure (Capex) differences

## Target Websites

The agent scrapes data from the following financial websites:
- Moneycontrol
- NSE India
- BSE India
- Screener.in
- Investing.com India
- Economic Times Markets
- Tickertape
- Equitymaster
- MarketMojo
- CMIE

## Installation

1. Clone this repository
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the scraping agent:
```bash
python stock_data_agent.py
```

The scraped data will be saved in the `results` directory with timestamped CSV files for each data type.

## Features

- Asynchronous scraping for improved performance
- Human-like browsing behavior to avoid detection
- Robust error handling and logging
- Structured data output in CSV format
- Configurable target websites and data points

## Output

The agent creates separate CSV files for each type of data:
- growth_rate_{timestamp}.csv
- performance_{timestamp}.csv
- marginal_changes_{timestamp}.csv
- capex_{timestamp}.csv

## Notes

- Ensure you comply with the terms of service and robots.txt of the target websites
- Some websites may require authentication or have rate limiting
- The agent includes random delays to avoid overwhelming the target servers 