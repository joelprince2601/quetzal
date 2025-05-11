from transformers import pipeline

classifier = pipeline("text-classification", model="deepseek-ai/deepseek-r1")

def analyze_news(news_list):
    relevant_news = []
    for news in news_list:
        analysis = classifier(news["title"])
        if analysis[0]["label"] == "relevant":
            relevant_news.append(news)
    return relevant_news
