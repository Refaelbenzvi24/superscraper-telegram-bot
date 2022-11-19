import uvicorn
from ..config.celeryApp import celery_app

celery_app.config_from_object(__name__)


def main():
	worker = celery_app.Worker(
		pool='solo',
		hostname='celery@worker',
		loglevel='info',
		task_events=True,
		include=['src.shared.tasks.tasks']
	)
	worker.start()


if __name__ == '__main__':
	main()
