import time

from outputControll import output

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException
from dataManager import saveData, getUserConfig, getSearchConfig, getSearchAmountOfRequests
from config import FIRST_SEARCH_LIMIT, MAX_SEARCH_LIMIT


def scrape(userId, pointer):
	chrome_options = webdriver.ChromeOptions()
	chrome_options.add_experimental_option("excludeSwitches", ["ignore-certificate-errors"])
	chrome_options.add_argument('--disable-gpu')
	chrome_options.add_argument("--headless")
	
	driver = webdriver.Chrome(chrome_options=chrome_options)
	driver.get('https://www.terminalx.com/')
	
	searchConfig = getSearchConfig(userId, pointer)
	searchText = searchConfig['search']
	search(searchText, driver)
	itemsList = getList(driver, userId, pointer)
	saveData(itemsList, userId, pointer)
	
	time.sleep(2)
	driver.quit()
	
	output('scrape ended successfully for user: ' + str(userId))
	return


def search(searchText, driver):
	try:
		searchButton = driver.find_element(By.CLASS_NAME, 'search-button_1ENs')
		searchButton.click()
	except ElementClickInterceptedException:
		return
	searchBox = driver.find_element(By.CLASS_NAME, 'input_3rQh')
	searchBox.send_keys(searchText)
	submitSearch = driver.find_element(By.CLASS_NAME, 'submit_2NTz')
	submitSearch.click()


def getList(driver, userId, pointer):
	driver.implicitly_wait(5)
	
	itemsList = driver.find_elements(By.CLASS_NAME, 'listing-product_3mjp')
	
	scrollingPagination(len(itemsList), driver)
	
	itemsList = driver.find_elements(By.CLASS_NAME, 'listing-product_3mjp')
	
	if len(itemsList) > FIRST_SEARCH_LIMIT:
		if int(getSearchAmountOfRequests(userId, pointer)) == 0:
			return 'exceed limitation'
	
	if len(itemsList) > MAX_SEARCH_LIMIT:
		return 'exceed limitation'
	
	items = getItems(itemsList, driver)
	
	return items


def scrollingPagination(listLength, driver):
	driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
	
	time.sleep(1)
	itemsList = driver.find_elements(By.CLASS_NAME, 'listing-product_3mjp')
	
	if len(itemsList) == listLength:
		return
	else:
		scrollingPagination(len(itemsList), driver)


def getItems(items_list, driver):
	items = []
	
	driver.implicitly_wait(0)
	for item in items_list:
		if len(item.find_elements(By.CLASS_NAME, 'item__short_tayt')) > 0:
			items.append(getItemData(item))
	return items


def getItemData(item):
	itemObject = {}
	
	itemElement = item.find_element(By.CLASS_NAME, 'tx-link_29YD')
	
	link = itemElement.get_attribute('href')
	
	imageUrl = item.find_element(By.TAG_NAME, 'img').get_attribute('src')
	title = item.find_element(By.CLASS_NAME, 'title_3ZxJ').get_attribute('innerHTML')
	price = item.find_element(By.CLASS_NAME, 'final-price_8CiX').get_attribute('innerHTML')
	
	itemObject['id'] = link.split('/')[len(link.split('/')) - 1]
	itemObject['title'] = title
	itemObject['link'] = link
	itemObject['imageUrl'] = imageUrl
	itemObject['price'] = price
	
	sizes = []
	
	imageDiv = item.find_element(By.CLASS_NAME, 'img-link_29yX')
	sizesBox = imageDiv.find_element(By.CLASS_NAME, 'items-wrapper_362-')
	sizesElement = sizesBox.find_elements(By.CLASS_NAME, 'item__short_tayt')
	for sizeElement in sizesElement:
		classes = sizeElement.get_attribute('class')
		if 'not-available_3TOC' not in classes:
			sizes.append(sizeElement.get_attribute('innerHTML'))
	
	itemObject['sizes'] = sizes
	
	return itemObject
