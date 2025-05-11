from celery import Celery

def make_celery(app):
    """Initialize Celery with Flask configuration"""
    celery = Celery(
        app.import_name,
        backend=app.config["CELERY_RESULT_BACKEND"],
        broker=app.config["CELERY_BROKER_URL"]
    )
    celery.conf.update(app.config)
    return celery
