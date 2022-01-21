import json
import os

from config import FIRST_SEARCH_LIMIT, MAX_EXCEED_NUMBER
from botManager import bot

initialSearchConfig = {
	"state": False,
	"requests": 0,
	"search": "",
	"sizes": "",
	"roundSizes": False,
	"intervalString": "",
	"intervalNumber": None,
	"options": {
		"setSearchText": True,
		"setSizes": False,
		"setRoundSizes": False,
		"setInterval": False
	}
}


def blockSearch(userId, pointer):
	saveSearchData([], userId, pointer)
	searchConfig = getSearchConfig(userId, pointer)
	searchConfig['state'] = False
	saveSearchConfig(searchConfig, userId, pointer)
	bot.send_message(userId, 'חיפוש מס' + str(pointer + 1) + 'נחסם')
	bot.send_message(userId, "סיבת החסימה: מס' התוצאות חורג מהמגבלה")


def saveData(data, userId, pointer):
	# get existing data
	savedData = []
	newData = []
	if int(getSearchAmountOfRequests(userId, pointer)) > 0:
		savedData = getSearchData(userId, pointer)
	
	if data == 'exceed limitation':
		blockSearch(userId, pointer)
	
	if len(data) > FIRST_SEARCH_LIMIT:
		if len(savedData) > FIRST_SEARCH_LIMIT:
			searchConfig = getSearchConfig(userId, pointer)
			searchConfig['exceedCounter'] += 1
			saveSearchConfig(searchConfig, userId, pointer)
			if searchConfig['exceedCounter'] > MAX_EXCEED_NUMBER:
				blockSearch(userId, pointer)
	
	# mark all saved data as old
	_index = 0
	for _item in savedData:
		savedData[_index]['newData'] = False
		_index += 1
	
	for item in data:
		duplicated = False
		duplicatedItem = None
		duplicatedItemIndex = None
		
		if len(item['sizes']) > 0:
			_index = 0
			for _item in savedData:
				
				if _item['id'] == item['id']:
					duplicated = True
					duplicatedItemIndex = _index
					duplicatedItem = _item
				_index += 1
		
		if duplicated:
			item['sizes'] = includeUserSizes(item['sizes'], userId, pointer)
			duplicatedItem['sizes'] = includeUserSizes(duplicatedItem['sizes'], userId, pointer)
			newSizes = checkNewSizes(item['sizes'], duplicatedItem['sizes'])
			
			duplicatedItem['newData'] = newSizes
			savedData[duplicatedItemIndex] = duplicatedItem
		else:
			item['sizes'] = includeUserSizes(item['sizes'], userId, pointer)
			if len(item['sizes']) > 0:
				item['newData'] = True
				newData.append(item)
	
	for item in newData:
		savedData.append(item)
	
	saveSearchData(savedData, userId, pointer)
	increaseRequestCounter(1, pointer, userId)


def includeUserSizes(sizesToTransform, userId, pointer):
	config = getSearchConfig(userId, pointer)
	userSizes = config['sizes']
	roundNumbers = config['roundSizes']
	
	if userSizes[0] != 'הכל':
		if len(sizesToTransform) > 0 and len(userSizes) > 0:
			sizes = []
			
			def roundNum(n):
				return int(n)
			
			if roundNumbers:
				map(roundNum, sizesToTransform)
				map(roundNum, userSizes)
			
			for size in userSizes:
				if size in sizesToTransform:
					sizes.append(size)
			
			return sizes
		else:
			return []
	else:
		return sizesToTransform


def checkNewSizes(l1, l2):
	l1.sort()
	l2.sort()
	
	return not l1 == l2


def createUser(userId):
	initialUserConfig = {
		"id": userId,
		"username": "",
		"passwordCounter": 0,
		"authenticated": False,
		"select": False,
		"requests": 0,
		"pointer": 0,
		"searchConfigs": []
	}
	
	try:
		createUserConfig(userId)
		createUserDataFile(userId)
	except FileExistsError:
		saveUserConfig(initialUserConfig, userId)
		saveUserData([], userId)
		return
	saveUserData([], userId)
	saveUserConfig(initialUserConfig, userId)


def deleteAllUserData(userId):
	deleteFile('data/' + str(userId) + '.json')
	deleteFile('configs/' + str(userId) + '.json')


def getAmountOfRequests(userId):
	config = getUserConfig(userId)
	return config["requests"]


def getSearchAmountOfRequests(userId, pointer):
	searchConfig = getSearchConfig(userId, pointer)
	return searchConfig['requests']


def increaseRequestCounter(increment, pointer, userId):
	config = getUserConfig(userId)
	config['requests'] = int(config['requests']) + increment
	searchConfig = getSearchConfig(userId, pointer)
	searchConfig['requests'] = searchConfig['requests'] + increment
	saveUserConfig(config, userId)
	saveSearchConfig(searchConfig, userId, pointer)


def setUserSearchKey(data, key, pointer, userId):
	searchConfig = getSearchConfig(userId, pointer)
	searchConfig[key] = data
	saveSearchConfig(searchConfig, userId, pointer)


def setUserOptions(options, pointer, userId):
	config = getUserConfig(userId)
	config['searchConfigs'][pointer]['options'] = options
	saveUserConfig(config, userId)


def triggerOptionsKey(userId, pointer, key=None):
	optionsObject = {"setSearchText": False, "setSizes": False, "setRoundSizes": False, "setInterval": False}
	if key:
		optionsObject[key] = True
	setUserOptions(optionsObject, pointer, userId)


# user config functions
def createUserConfig(userId):
	createJson("configs/" + str(userId) + ".json")


def getUserConfig(userId):
	return readFromJson("configs/" + str(userId) + '.json')


def saveUserConfig(config, userId):
	writeToJson(config, "configs/" + str(userId) + ".json")


# user data functions
def createUserDataFile(userId):
	createJson("data/" + str(userId) + ".json")


def getUserData(userId):
	return readFromJson("data/" + str(userId) + ".json")


def saveUserData(data, userId):
	writeToJson(data, "data/" + str(userId) + ".json")


def newSearchData(userId):
	userData = getUserData(userId)
	userData.append([])
	saveUserData(userData, userId)


def getSearchData(userId, pointer):
	userData = getUserData(userId)
	return userData[pointer]


def saveSearchData(data, userId, pointer):
	userData = getUserData(userId)
	if len(userData) - 1 >= int(pointer):
		userData.pop(int(pointer))
	userData.insert(int(pointer), data)
	saveUserData(userData, userId)


# user search config functions
def newSearchConfig(userId):
	config = getUserConfig(userId)
	config['searchConfigs'].append(initialSearchConfig)
	config['pointer'] = len(config['searchConfigs']) - 1
	saveUserConfig(config, userId)


def getSearchConfig(userId, pointer):
	return getUserConfig(userId)['searchConfigs'][pointer]


def saveSearchConfig(searchConfig, userId, pointer):
	config = getUserConfig(userId)
	config['searchConfigs'][pointer] = searchConfig
	saveUserConfig(config, userId)


# write read to json functions
def readFromJson(filePath):
	file = open(filePath, "r", encoding='utf-8')
	data = file.read()
	data = json.loads(data)
	return data


def writeToJson(data, filePath):
	with open(filePath, "w", encoding='utf-8') as file:
		json.dump(data, file, skipkeys=False, ensure_ascii=False)


def createJson(filePath):
	open(filePath, "x")


def deleteFile(filePath):
	os.remove(filePath)

# def readFromFile(fileName):
# 	file = open(fileName, "r")
# 	data = file.read()
# 	data = json.loads(data)
# 	return data
#
#
# def writeToFile(data, fileName):
# 	with open(fileName, "w") as file:
# 		json.dump(data, file)
