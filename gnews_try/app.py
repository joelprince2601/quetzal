import streamlit as st
from datetime import datetime, timedelta
from stock_news_agent import StockNewsAgent
import pandas as pd

# Initialize session state
if 'news_agent' not in st.session_state:
    api_keys = {
        'newsapi': st.secrets.get('NEWSAPI_KEY', ''),
        'bing': st.secrets.get('BING_NEWS_KEY', ''),
        'alphavantage': st.secrets.get('ALPHAVANTAGE_KEY', ''),
        'marketaux': st.secrets.get('MARKETAUX_KEY', '')
    }
    st.session_state.news_agent = StockNewsAgent(api_keys)

# Page config
st.set_page_config(
    page_title="Stock News Aggregator",
    page_icon="📈",
    layout="wide"
)

# Title and description
st.title("📈 Stock News Aggregator")
st.markdown("""
This app aggregates news articles about stocks from multiple sources. 
Enter a stock symbol and select a date range to get started.
""")

# Input section
col1, col2, col3 = st.columns([2, 2, 2])

with col1:
    symbol = st.text_input("Stock Symbol", value="AAPL", help="Enter a stock symbol (e.g., AAPL, GOOGL)")

with col2:
    start_date = st.date_input(
        "Start Date",
        value=datetime.now() - timedelta(days=7),
        max_value=datetime.now(),
        help="Select start date for news articles"
    )

with col3:
    end_date = st.date_input(
        "End Date",
        value=datetime.now(),
        max_value=datetime.now(),
        help="Select end date for news articles"
    )

# API selection
available_apis = st.session_state.news_agent.get_available_apis()
api_options = {api['name']: api for api in available_apis}
selected_api = st.selectbox(
    "Select News API",
    options=list(api_options.keys()),
    help="Choose which news API to use"
)

# Convert API name to internal ID
api_id_map = {
    'NewsAPI': 'newsapi',
    'Bing News': 'bing',
    'Google News': 'google',
    'Yahoo Finance': 'yahoo'
}

if st.button("Fetch News"):
    try:
        with st.spinner('Fetching news articles...'):
            api_id = api_id_map[selected_api]
            news_data = st.session_state.news_agent.run(
                symbol=symbol,
                start_date=datetime.combine(start_date, datetime.min.time()),
                end_date=datetime.combine(end_date, datetime.max.time()),
                api_choice=api_id
            )

            if not news_data:
                st.warning("No news articles found for the given criteria.")
            else:
                # Display news articles
                for article in news_data:
                    with st.expander(article['title']):
                        st.write(f"**Source:** {article['publisher']}")
                        st.write(f"**Published:** {article['date']}")
                        st.write(article['description'])
                        st.markdown(f"[Read more]({article['url']})")

    except Exception as e:
        error_message = str(e)
        if "rate limit" in error_message.lower():
            st.error("API rate limit exceeded. Please try again later or switch to a different API.")
        elif "invalid api key" in error_message.lower():
            st.error("Invalid API key. Please check your API key configuration.")
        else:
            st.error(f"An error occurred: {error_message}")

# Footer with API information
st.markdown("---")
st.markdown("### API Information")
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Available APIs")
    for api in available_apis:
        st.markdown(f"- **{api['name']}**")
        st.markdown(f"  - Rate Limit: {api['rate_limit']}")
        st.markdown(f"  - Requires API Key: {'Yes' if api['requires_key'] else 'No'}")

with col2:
    st.markdown("#### Tips")
    st.markdown("""
    - Google News and Yahoo Finance are free and don't require API keys
    - For better results, use official stock symbols (e.g., AAPL instead of Apple)
    - If one API fails, try another one
    - Keep date ranges reasonable (1-2 weeks) for best results
    """) 