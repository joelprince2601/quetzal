# Stock Market News Agent

This agent scrapes and analyzes stock market news using the GNews API to help make informed investment decisions.

## Features

- Fetches latest stock market news from multiple reliable sources
- Processes and filters news based on relevance
- Calculates relevance scores for each news item
- Removes duplicate news entries
- Saves results in a structured CSV format with timestamps

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. The API key is already configured in the script.

## Usage

Simply run the script:
```bash
python stock_news_agent.py
```

The script will:
1. Fetch news for various stock market-related keywords
2. Process and score the relevance of each news item
3. Save the results in a CSV file named `stock_news_YYYYMMDD_HHMMSS.csv`

## Output Format

The CSV file contains the following columns:
- title: The news article title
- description: A brief description or summary of the news
- published_date: When the news was published
- publisher: The source of the news
- url: Link to the full article
- relevance_score: A score from 0-10 indicating the article's relevance to stock market analysis

## Note

The relevance score is calculated based on the presence of important financial terms in both the title and description of the news articles. Higher scores indicate potentially more relevant news for stock market analysis. 