from celery.schedules import crontab

celery.conf.beat_schedule = {
    "fetch-news-every-hour": {
        "task": "app.fetch_and_update_news",
        "schedule": crontab(minute=0, hour="*"),
        "args": ("AAPL",)  # Example stock
    }
}
