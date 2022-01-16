import json
from util import translateInterval


def saveData(data, userId):
	savedData = []
	if int(getAmountOfRequests(userId)) > 0:
		savedData = getUserData(userId)
	localData = []
	
	for item in data:
		item = item[0]
		duplicated = False
		duplicatedItem = None
		
		_index = 0
		if len(savedData) > 0:
			for _item in savedData:
				if _item['id'] == item['id']:
					duplicated = True
					duplicatedItem = _item
				
				if _index == len(data) - 1:
					if duplicated:
						newSizes = checkNewSizes(item['sizes'], duplicatedItem['sizes'])
						
						if newSizes:
							item['newData'] = True
							localData.append(item)
						else:
							item['newData'] = False
							localData.append(item)
				_index += 1
		if not duplicated:
			item['newData'] = True
			localData.append(item)
	
	saveUserData(localData, userId)
	increaseRequestCounter(1, userId)


def checkNewSizes(l1, l2):
	l1.sort()
	l2.sort()
	if l1 == l2:
		return False
	else:
		return True


def createUser(userId):
	config = {
		"requests": 0,
		"search": "",
		"sizes": "",
		"roundSizes": False,
		"interval": None,
		"options": {
			"setSearchText": True,
			"setSizes": False,
			"setRoundSizes": False,
			"setInterval": False
		}
	}
	
	try:
		createUserConfig(userId)
		createUserDataFile(userId)
	except FileExistsError:
		saveUserConfig(config, userId)
		saveUserData('', userId)
		return
	saveUserConfig(config, userId)


def getAmountOfRequests(userId):
	config = getUserConfig(userId)
	return config["requests"]


def increaseRequestCounter(increment, userId):
	config = getUserConfig(userId)
	config['requests'] = int(config['requests']) + increment
	saveUserConfig(config, userId)


def setUserSearch(searchText, userId):
	config = getUserConfig(userId)
	config['search'] = searchText
	saveUserConfig(config, userId)


def setUserSizes(sizes, userId):
	config = getUserConfig(userId)
	config['sizes'] = sizes
	saveUserConfig(config, userId)


def setUserRoundSizes(state, userId):
	config = getUserConfig(userId)
	config['roundSizes'] = state
	saveUserData(config, userId)


def setUserInterval(interval, userId):
	config = getUserConfig(userId)
	config['interval'] = interval
	saveUserConfig(config, userId)


def setUserOptions(options, userId):
	config = getUserConfig(userId)
	config['options'] = options
	saveUserConfig(config, userId)


def triggerOptionsKey(userId, key=None):
	optionsObject = {"setSearchText": False, "setSizes": False, "setRoundSizes": False, "setInterval": False}
	if key:
		optionsObject[key] = True
	setUserOptions(optionsObject, userId)


def getUserData(userId):
	return readFromJson("data/" + str(userId) + ".json")


def saveUserData(data, userId):
	writeToJson(data, "data/" + str(userId) + ".json")


def createUserDataFile(userId):
	createJson("data/" + str(userId) + ".json")


def getUserConfig(userId):
	return readFromJson("configs/" + str(userId) + '.json')


def saveUserConfig(config, userId):
	writeToJson(config, "configs/" + str(userId) + ".json")


def createUserConfig(userId):
	createJson("configs/" + str(userId) + ".json")


def readFromJson(fileName):
	file = open(fileName, "r", encoding='utf-8')
	data = file.read()
	data = json.loads(data)
	return data


def writeToJson(data, fileName):
	with open(fileName, "w", encoding='utf-8') as file:
		json.dump(data, file, skipkeys=False, ensure_ascii=False)


def createJson(fileName):
	open(fileName, "x")

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
