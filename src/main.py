from scrapperManager import startServer
from botManager import bot

from dataManager import setUserSearchKey, getSearchConfig, triggerOptionsKey, createUser, getUserConfig, saveUserConfig, \
	newSearchConfig, initialSearchConfig, deleteAllUserData, newSearchData
from scrapperManager import startScraper
from util import translateInterval
from config import BOT_PASSWORD

commandsList = '/help - הצגת כל הפקודות' \
               '\n /start - איפוס משתמש' \
               '\n /newSearch - הגדרת והתחלת חיפוש חדש' \
               '\n /resetSearch - איפוס הגדרות החיפוש הנוכחי והגדרה מחדש' \
               '\n /select - בחירת חיפוש לעריכה' \
               '\n /showAll - הצגת כל החיפושים' \
               '\n /stop - הפסקת החיפוש הנוחכי' \
               '\n /stopAll - הפסקת כל החיפושים' \
               '\n /delete - מחיקת החיפוש הנוכחי' \
               '\n /deleteAll - מחיקת כל החיפושים' \
               '\n /deleteUser - מחיקת המשתמש וכל הנתונים שקשורים אליו'


@bot.message_handler(commands=['start'])
def start(message):
	createUser(message.chat.id)
	bot.send_message(message.chat.id, 'היי, מה תרצה שיהיה שם המשתמש שלך?')


def setUsername(message):
	username = getUserConfig(message.chat.id)['username']
	
	if username == "":
		return True
	else:
		return False


@bot.message_handler(func=setUsername)
def setUsername(message):
	config = getUserConfig(message.chat.id)
	config['username'] = message.text
	saveUserConfig(config, message.chat.id)
	bot.send_message(message.chat.id, 'סיסמא והתחלנו!')


def authenticate(message):
	authenticated = getUserConfig(message.chat.id)['authenticated']
	
	if not authenticated:
		return True
	else:
		return False


@bot.message_handler(func=authenticate)
def authenticate(message):
	config = getUserConfig(message.chat.id)
	password = message.text
	
	if config['passwordCounter'] < 10:
		if str(password) == str(BOT_PASSWORD):
			config['authenticated'] = True
			config['passwordCounter'] = 0
			saveUserConfig(config, message.chat.id)
			bot.send_message(message.chat.id, 'התחברת בהצלחה!')
			bot.send_message(message.chat.id, commandsList)
		else:
			config['passwordCounter'] += 1
			saveUserConfig(config, message.chat.id)
			bot.send_message(message.chat.id, 'סיסמא שגוייה')
	else:
		bot.send_message(message.chat.id, 'הגעת למספר הנסיונות המירבי')


@bot.message_handler(commands=['help'])
def helpUser(message):
	bot.send_message(message.chat.id, commandsList)


@bot.message_handler(commands=['newSearch'])
def newSearch(message):
	newSearchConfig(message.chat.id)
	newSearchData(message.chat.id)
	bot.send_message(message.chat.id, 'היי, מה תרצה לחפש?')


@bot.message_handler(commands=['resetSearch'])
def resetSearch(message):
	config = getUserConfig(message.chat.id)
	pointer = config['pointer']
	config['searchConfigs'].pop(pointer)
	config['searchConfigs'].insert(pointer, initialSearchConfig)
	saveUserConfig(config, message.chat.id)
	bot.send_message(message.chat.id, 'היי, מה תרצה לחפש?')


@bot.message_handler(commands=['select'])
def select(message):
	config = getUserConfig(message.chat.id)
	config['select'] = True
	saveUserConfig(config, message.chat.id)
	bot.send_message(message.chat.id, 'אם תרצה להציג את כל האפוציות הקלד /showAll')
	bot.send_message(message.chat.id, 'איזה חיפוש תרצה לערוך?')


def selectCommand(message):
	config = getUserConfig(message.chat.id)
	
	return config['select']


@bot.message_handler(func=selectCommand)
def select(message):
	config = getUserConfig(message.chat.id)
	selected = message.text
	
	if selected.isnumric() and len(config['searchConfigs']) > selected:
		selected = int(message.text) - 1
		config['pointer'] = selected
		saveUserConfig(config, message.chat.id)
		bot.send_message(message.chat.id, 'הפעולה בוצע בהצלחה!')
	else:
		bot.d_message(message.chat.id, 'המספר שהכנסת לא תקין')


@bot.message_handler(commands=['showAll'])
def showAll(message):
	config = getUserConfig(message.chat.id)
	
	searchConfigsMessage = ''
	
	index = 1
	for searchConfig in config['searchConfigs']:
		_message = ''
		
		_message += 'מילות חיפוש - ' + searchConfig['search'] + '\n'
		
		_message += "מס' סידורי - " + str(index) + '\n'
		
		if searchConfig['state']:
			_message += 'פעיל - כן \n'
		else:
			_message += 'פעיל - לא \n'
		
		_message += 'מידות לחיפוש - ' + str(searchConfig['sizes']) + '\n'
		
		_message += 'עיגול מידות - ' + str(searchConfig['roundSizes']) + '\n'
		
		_message += 'תדירות - ' + str(searchConfig['intervalString']) + '\n'
		
		searchConfigsMessage += _message
		index += 1
	
	bot.send_message(message.chat.id, searchConfigsMessage)


@bot.message_handler(commands=['stop'])
def stop(message):
	config = getUserConfig(message.chat.id)
	pointer = config['pointer']
	
	setUserSearchKey(False, 'state', pointer, message.chat.id)
	bot.send_message(message.chat.id, 'החיפוש הופסק')


@bot.message_handler(commands=['stopAll'])
def stopAll(message):
	config = getUserConfig(message.chat.id)
	
	index = 0
	for searchConfig in config['searchConfigs']:
		setUserSearchKey(False, 'state', index, message.chat.id)
		index += 1
	bot.send_message(message.chat.id, 'כל החיפושים הופסקו')


@bot.message_handler(commands=['delete'])
def delete(message):
	config = getUserConfig(message.chat.id)
	pointer = config['pointer']
	
	config['searchConfigs'].pop(pointer)
	saveUserConfig(config, message.chat.id)
	bot.send_message(message.chat.id, 'המחיקה בוצע בהצלחה')


@bot.message_handler(commands=['deleteAll'])
def deleteAll(message):
	config = getUserConfig(message.chat.id)
	
	index = 0
	for searchConfig in config['searchConfigs']:
		setUserSearchKey(False, 'state', index, message.chat.id)
		config['searchConfigs'].pop(index)
		index += 1
	saveUserConfig(config, message.chat.id)
	bot.send_message(message.chat.id, 'כל המחיקות בוצעו בהצלחה')


@bot.message_handler(commands=['deleteUser'])
def deleteUser(message):
	deleteAllUserData(message.chat.id)
	bot.send_message(message.chat.id, 'המשתמש נמחק בהצלחה')


# setSearchText
def setSearchText(message):
	config = getUserConfig(message.chat.id)
	pointer = config['pointer']
	userConfig = getSearchConfig(message.chat.id, pointer)
	
	if userConfig:
		return userConfig["options"]["setSearchText"]
	else:
		return False


@bot.message_handler(func=setSearchText)
def setSearchText(message):
	config = getUserConfig(message.chat.id)
	pointer = config['pointer']
	
	setUserSearchKey(message.text, 'search', pointer, message.chat.id)
	triggerOptionsKey(message.chat.id, pointer, "setSizes")
	bot.send_message(message.chat.id, 'איזה מידות תרצה לחפש? \n לדוגמא: 40 41 42 43/ הכל')


# setSizes
def setSizes(message):
	config = getUserConfig(message.chat.id)
	pointer = config['pointer']
	
	userConfig = getSearchConfig(message.chat.id, pointer)
	if userConfig:
		return userConfig["options"]["setSizes"]
	else:
		return False


@bot.message_handler(func=setSizes)
def setSizes(message):
	config = getUserConfig(message.chat.id)
	pointer = config['pointer']
	
	sizes = message.text.split(" ")
	setUserSearchKey(sizes, 'sizes', pointer, message.chat.id)
	
	if ''.join(sizes).isnumeric():
		triggerOptionsKey(message.chat.id, pointer, "setRoundSizes")
		bot.send_message(message.chat.id,
		                 'האם תרצה שנעגל מידות? \n דוגמא: \n מידות: 42 42.5 43.5 44.5 44.75 \n מידות מעוגלות: 42 43 44 \n כן/לא')
	else:
		triggerOptionsKey(message.chat.id, pointer, "setInterval")
		bot.send_message(message.chat.id,
		                 'כל כמה זמן תרצה שנחפש?\n לדוג: 1 דקה = 1/ 1 דקה, 5 דקות= 5/ 5 דקות, שעה = 60/ שעה/ 1 שעה, 2 שעות, יום, ימים, שבוע, שבועות...')


# setRoundSizes
def setRoundSizes(message):
	config = getUserConfig(message.chat.id)
	pointer = config['pointer']
	
	userConfig = getSearchConfig(message.chat.id, pointer)
	if userConfig:
		return userConfig["options"]["setRoundSizes"]
	else:
		return False


@bot.message_handler(func=setRoundSizes)
def setRoundSeizes(message):
	config = getUserConfig(message.chat.id)
	pointer = config['pointer']
	
	if message.text == 'כן':
		setUserSearchKey(True, 'roundSizes', pointer, message.chat.id)
	elif message.text == 'לא':
		setUserSearchKey(False, 'roundSizes', pointer, message.chat.id)
	else:
		bot.send_message(message.chat.id, 'יש להזין כן/לא')
		return
	
	triggerOptionsKey(message.chat.id, pointer, "setInterval")
	bot.send_message(message.chat.id,
	                 'כל כמה זמן תרצה שנחפש?\n לדוג: 1 דקה = 1/ 1 דקה, 5 דקות= 5/ 5 דקות, שעה = 60/ שעה/ 1 שעה, 2 שעות, יום, ימים, שבוע, שבועות...')


# setInterval
def setIntervalCommand(message):
	config = getUserConfig(message.chat.id)
	pointer = config['pointer']
	
	userConfig = getSearchConfig(message.chat.id, pointer)
	
	if userConfig:
		return userConfig["options"]["setInterval"]
	else:
		return False


@bot.message_handler(func=setIntervalCommand)
def setIntervalCommand(message):
	config = getUserConfig(message.chat.id)
	pointer = config['pointer']
	
	intervalNumber = translateInterval(message.text)
	if type(intervalNumber) is int:
		setUserSearchKey(message.text, 'intervalString', pointer, message.chat.id)
		setUserSearchKey(intervalNumber, 'intervalNumber', pointer, message.chat.id)
		triggerOptionsKey(message.chat.id, pointer)
		
		setUserSearchKey(True, 'state', pointer, message.chat.id)
		
		bot.send_message(message.chat.id, 'התחלנו!')
		bot.send_message(message.chat.id,
		                 'שים לב! החיפוש הראשון יכול לקחת מעט זמן, תלוי בכמות התוצאות, לאחר מכן הפרש הזמן בין התוצאות יהיה קבוע!')
		
		startScraper(message.chat.id, intervalNumber, pointer)
	else:
		bot.send_message(message.chat.id, "יש להזין מספר/ יח' זמן לפי הדוגמאות למעלה")


startServer()
