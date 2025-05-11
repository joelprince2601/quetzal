from serpapi import GoogleSearch

def fetch_news(query):
    params = {
        "q": f"{query} stock news",
        "hl": "en",
        "gl": "us",
        "api_key": "0055ffe7b223901af40a28dfff9e20a71adc0ded71b9783580e14e488147d939"
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    return results.get("news_results", [])
