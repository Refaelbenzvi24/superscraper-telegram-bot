import threading
import time

from outputControll import output

from os import listdir
from scrapper import scrape

from BackgroundTask import BackgroundTasks
from dataManager import getUserConfig, getSearchConfig, getSearchData
from util import setInterval
from botManager import bot


def startServer():
	t = BackgroundTasks()
	t.start()
	usersConfigFiles = [f for f in listdir('configs')]
	
	for file in usersConfigFiles:
		file = file.split('.')
		userId = file[0]
		config = getUserConfig(userId)
		index = 0
		for config in config['searchConfigs']:
			if config['state']:
				startScraper(userId, config['intervalNumber'], index)
			index += 1


def newScrapeThread(userId, pointer):
	output('thread for ' + str(userId) + ' opened')
	thread = threading.Thread(name=userId, target=scrape(userId, pointer))
	thread.start()
	time.sleep(1)
	thread.join()
	sendUserData(userId, pointer)
	output('thread for ' + str(userId) + ' closed')
	return


def startScraper(userId, intervalNumber, pointer):
	def scraper(_userId=userId):
		config = getSearchConfig(_userId, pointer)
		if config['state']:
			newScrapeThread(_userId, pointer)
		else:
			interval.cancel()
	
	interval = setInterval(scraper, intervalNumber)
	scraper(userId)


def sendUserData(userId, pointer):
	data = getSearchData(userId, pointer)
	config = getSearchConfig(userId, pointer)
	newData = False
	
	for item in data:
		if item['newData'] and config['sizes'][0] != 'הכל':
			sizes = " ".join(item['sizes'])
			
			if sizes != '':
				message = item['title'] + '\n' + 'מידות: ' + str(sizes) + '\n' + 'מחיר: ' + item['price'] + \
				          '\n' + item['link']
				if item['imageUrl']:
					bot.send_photo(userId, item['imageUrl'], message)
				else:
					bot.send_message(userId, message)
				newData = True
			elif config['requests'] == 0:
				bot.send_message(userId, 'לא נמצאו כרגע תוצאות למידות שביקשת, אנחנו נמשיך לחפש')
		
		elif item['newData'] and config['sizes'][0] == 'הכל':
			message = item['title'] + '\n' + 'מידות: ' + " ".join(item["sizes"]) + '\n' + 'מידות: ' + \
			          '\n' + 'מחיר: ' + item['price'] + '\n' + item['link']
			bot.send_photo(userId, item['imageUrl'], message)
	if newData and config['requests'] == 0:
		bot.send_message(userId, 'זה מה שמצאנו כרגע לחיפוש שהזנת, במידה ויהיו שינויים נעדכן!')


def compareSizes(l1, l2, roundNumbers=False):
	if len(l1) > 0 and len(l2) > 0:
		sizes = ''
		
		def roundNum(n):
			return int(n)
		
		if roundNumbers:
			map(roundNum, l1)
			map(roundNum, l2)
		
		for size in l2:
			if size in l1:
				sizes += ' ' + size + ' '
		
		return sizes
	else:
		return
