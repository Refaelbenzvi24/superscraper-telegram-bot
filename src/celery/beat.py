import uvicorn
from celery.schedules import crontab
from ..config.celeryApp import celery_app
from ..config.vars import SEARCH_INTERVAL_IN_MINUTES
from ..shared.tasks.tasks import queue_periodic_scraping


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
	print("Setting up periodic tasks")
	sender.add_periodic_task(
		crontab(minute=f'*/{SEARCH_INTERVAL_IN_MINUTES}'),
		queue_periodic_scraping.s(),
		name=f'scrape every {SEARCH_INTERVAL_IN_MINUTES} minutes'
	)


def main():
	celery_app.Beat(
		pool='solo',
		hostname='celery@beat',
		loglevel='info',
		task_events=True
	).run()


if __name__ == '__main__':
	main()