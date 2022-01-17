import re
import threading


def setInterval(func, sec):
	def func_wrapper():
		setInterval(func, sec)
		func()
	
	t = threading.Timer(sec, func_wrapper)
	t.start()
	return t


def translateInterval(intervalString):
	intervalNumber = False
	
	if str(intervalString).isdigit():
		return int(intervalString) * 60
	else:
		for key in dictionary:
			for item in dictionary[key]:
				if item in str(intervalString):
					interval = re.split('(\d+)', intervalString)
					if interval[0].isnumeric():
						intervalNumber = int(interval[0]) * int(key) * 60
					elif interval[1].isnumeric():
						intervalNumber = int(interval[1]) * int(key) * 60
					elif interval[2].isnumeric():
						intervalNumber = int(interval[2]) * int(key) * 60
	return intervalNumber


dictionary = {
	"1": ["דקה", "דקות"],
	"60": ["שעה", "שעות"],
	"1440": ["יום", "ימים"],
	"10080": ["שבוע", "שבועות"]
}
