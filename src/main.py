import telebot
import threading
import time

from config import API_KEY
from outputControll import output

from os import listdir
from scrapper import scrape
from dataManager import setUserSearch, setUserRoundSizes, setUserInterval, setUserSizes, triggerOptionsKey, \
	getUserConfig, saveUserConfig, getUserData, createUser
from util import translateInterval, setInterval

bot = telebot.TeleBot(API_KEY)


def startServer():
	usersConfigFiles = [f for f in listdir('configs')]
	
	for file in usersConfigFiles:
		file = file.split('.')
		userId = file[0]
		config = getUserConfig(userId)
		configOptions = config['options']
		if not configOptions['setSearchText'] and not configOptions['setSizes'] and not configOptions[
			'setRoundSizes'] and not configOptions['setInterval']:
			startScraper(userId, config['interval'])


def newScrapeThread(userId):
	output('thread for ' + userId + ' opened')
	t = threading.Thread(name=userId, target=scrape(userId))
	t.start()
	time.sleep(1)
	t.join()
	output('thread for ' + userId + ' closed')
	return


def startScraper(userId, intervalNumber):
	def scraper(_userId=userId):
		_config = getUserConfig(_userId)
		newScrapeThread(_userId)
		sendUserData(_userId)
		if _config['stop']:
			t.cancel()
	
	t = setInterval(scraper, intervalNumber)
	scraper(userId)


def sendUserData(userId):
	data = getUserData(userId)
	config = getUserConfig(userId)
	newData = False
	
	for item in data:
		if item['newData'] and config['sizes'][0] != 'הכל':
			sizes = compareSizes(item['sizes'], config['sizes'], config['roundSizes'])
			
			if sizes != '':
				message = item['title'] + '\n' + 'מידות: ' + str(sizes) + '\n' + 'מחיר: ' + item['price'] + \
				          '\n' + item['link']
				bot.send_photo(userId, item['imageUrl'], message)
				newData = True
			elif config['requests'] == 0:
				bot.send_message(userId, 'לא נמצאו כרגע תוצאות למידות שביקשת, אנחנו נמשיך לחפש')
		
		elif item['newData'] and config['sizes'][0] == 'הכל':
			message = item['title'] + '\n' + 'מידות: ' + " ".join(item["sizes"]) + '\n' + 'מידות: ' + \
			          '\n' + 'מחיר: ' + item['price'] + '\n' + item['link']
			bot.send_photo(userId, item['imageUrl'], message)
	if newData:
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
		return ''


@bot.message_handler(commands=['start'])
def start(message):
	createUser(message.chat.id)
	bot.send_message(message.chat.id, '/help - הצגת כל הפקודות')
	bot.send_message(message.chat.id, 'היי, מה תרצה לחפש?')


@bot.message_handler(commands=['stop'])
def stop(message):
	config = getUserConfig(message.chat.id)
	config['stop'] = True
	saveUserConfig(config, message.chat.id)
	bot.send_message(message.chat.id, 'החיפוש הופסק')


def setSearchText(message):
	userConfig = getUserConfig(message.chat.id)
	if userConfig:
		return userConfig["options"]["setSearchText"]
	else:
		return False


@bot.message_handler(commands=['help'])
def helpUser(message):
	bot.send_message(message.chat.id,
	                 '/start - התחלת חיפוש חדש \n /restart - אתחול של החיפוש הנוכחי \n /stop - הפסק את החיפוש')


@bot.message_handler(func=setSearchText)
def setSearchText(message):
	setUserSearch(message.text, message.chat.id)
	triggerOptionsKey(message.chat.id, "setSizes")
	bot.send_message(message.chat.id, 'איזה מידות תרצה לחפש? \n לדוגמא: 40 41 42 43/ הכל')


def setSizes(message):
	userConfig = getUserConfig(message.chat.id)
	if userConfig:
		return userConfig["options"]["setSizes"]
	else:
		return False


@bot.message_handler(func=setSizes)
def setSizes(message):
	sizes = message.text.split(" ")
	setUserSizes(sizes, message.chat.id)
	
	if ''.join(sizes).isnumeric():
		triggerOptionsKey(message.chat.id, "setRoundSizes")
		bot.send_message(message.chat.id,
		                 'האם תרצה שנעגל מידות? \n דוגמא: \n מידות: 42 42.5 43.5 44.5 \n מידות מעוגלות: 42 43 44 \n כן/לא')
	else:
		triggerOptionsKey(message.chat.id, "setInterval")
		bot.send_message(message.chat.id,
		                 'כל כמה זמן תרצה שנחפש?\n לדוג: 1 דקה = 1/ 1 דקה, 5 דקות= 5/ 5 דקות, שעה = 60/ שעה/ 1 שעה, 2 שעות, יום, ימים, שבוע, שבועות...')


def setRoundSizes(message):
	userConfig = getUserConfig(message.chat.id)
	if userConfig:
		return userConfig["options"]["setRoundSizes"]
	else:
		return False


@bot.message_handler(func=setRoundSizes)
def setRoundSeizes(message):
	if message.text == 'כן':
		setUserRoundSizes(True, message.chat.id)
	elif message.text == 'לא':
		setUserRoundSizes(False, message.chat.id)
	else:
		bot.send_message(message.chat.id, 'יש להזין כן/לא')
		return
	
	triggerOptionsKey(message.chat.id, "setInterval")
	bot.send_message(message.chat.id,
	                 'כל כמה זמן תרצה שנחפש?\n לדוג: 1 דקה = 1/ 1 דקה, 5 דקות= 5/ 5 דקות, שעה = 60/ שעה/ 1 שעה, 2 שעות, יום, ימים, שבוע, שבועות...')


def setIntervalCommand(message):
	userConfig = getUserConfig(message.chat.id)
	
	if userConfig:
		return userConfig["options"]["setInterval"]
	else:
		return False


@bot.message_handler(func=setIntervalCommand)
def setIntervalCommand(message):
	intervalNumber = translateInterval(message.text)
	if type(intervalNumber) is int:
		setUserInterval(intervalNumber, message.chat.id)
		triggerOptionsKey(message.chat.id)
		
		config = getUserConfig(message.chat.id)
		config['stop'] = False
		saveUserConfig(config, message.chat.id)
		
		bot.send_message(message.chat.id, 'התחלנו!')
		startScraper(message.chat.id, intervalNumber)
	else:
		bot.send_message(message.chat.id, "יש להזין מספר/ יח' זמן לפי הדוגמאות למעלה")


@bot.message_handler(commands=['restart'])
def restart(message):
	config = getUserConfig(message.chat.id)
	intervalNumber = config['interval']
	searchText = config['search']
	sizes = config['sizes']
	
	config['stop'] = False
	saveUserConfig(config, message.chat.id)
	
	if intervalNumber and searchText and sizes:
		bot.send_message(message.chat.id, 'התחלנו!')
		startScraper(message.chat.id, intervalNumber)
	else:
		bot.send_message(message.chat.id, 'חסרים פרטים, יש לרשום start ע"מ להתחיל')


class BackgroundTasks(threading.Thread):
	def run(self, *args, **kwargs):
		while True:
			output('started listening to bot')
			bot.infinity_polling(timeout=60, long_polling_timeout=5)
			time.sleep(1)


t = BackgroundTasks()
t.start()
startServer()
