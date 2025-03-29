import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('foodai')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Add recommendations to included modules
app.autodiscover_tasks([
    'analyzer',
    'recommendations'
])

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')