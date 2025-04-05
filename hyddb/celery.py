import os
from datetime import timedelta

from celery import Celery
from django.conf import settings


def to_seconds(*args, **kwargs):
    return timedelta(*args, **kwargs).total_seconds()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hyddb.settings')

app = Celery('hyddb',
             broker='amqp://rabbit',
             backend='redis://redis')

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Optional configuration, see the application user guide.
app.conf.update(
    CELERYD_TASK_TIME_LIMIT=to_seconds(hours=2),
    CELERY_TRACK_STARTED=True,
    CELERY_ACKS_LATE=True,
    CELERY_TASK_RESULT_EXPIRES=to_seconds(weeks=2),
    CELERY_ACCEPT_CONTENT=['json'],
    CELERY_RESULT_SERIALIZER='json',
    CELERY_TASK_SERIALIZER='json',
    CELERY_ROUTES={
        'classifier.tasks.classify_upstream_protein': {'queue': 'cdd'},
    }
)

if __name__ == '__main__':
    app.start()
