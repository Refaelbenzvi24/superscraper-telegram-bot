import threading
import time

from outputControll import output
from botManager import bot


class BackgroundTasks(threading.Thread):
	def run(self, *args, **kwargs):
		while True:
			output('started listening to bot')
			bot.infinity_polling(timeout=60, long_polling_timeout=5)
			time.sleep(1)
