import uuid

from ..config.celeryApp import celery_app

celery_app.config_from_object(__name__)


def main():
	workers_map = celery_app.control.inspect().active()
	workers_list = []
	
	if workers_map is not None:
		workers_list = [*workers_map.keys()]
	
	worker = celery_app.Worker(
		pool='solo',
		hostname=f'celery@worker@{len(workers_list)}@{uuid.uuid4()}',
		loglevel='info',
		task_events=True,
		include=['src.shared.tasks.tasks']
	)
	worker.start()


if __name__ == '__main__':
	main()
