from datetime import datetime


def output(content):
	print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' :: ' + content)
