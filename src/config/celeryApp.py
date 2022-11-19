from celery import Celery
from src.config.vars import BROKER_URL, CELERY_BACKEND_URL

celery_app = Celery(
	broker=BROKER_URL,
	backend=CELERY_BACKEND_URL,
	accept_content=['application/json'],
	result_serializer='json',
	task_serializer='json'
)
