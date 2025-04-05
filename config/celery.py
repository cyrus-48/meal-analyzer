import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('foodai')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks([
    'analyzer',
    'recommendations'
])

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
    
    
app.conf.beat_schedule = {
    'process-pending-analyses': {
        'task': 'analyzer.tasks.process_pending_analyses',
        'schedule': 300000.0,
    },
}