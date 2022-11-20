from types import SimpleNamespace

from ...config.botApi import api_bot
from ...config.database import session
from ...shared.models.product import Product
from ...shared.models.search import Search
from ...shared.models.searchProduct import SearchProduct
from ...shared.models.subscription import Subscription
from ...shared.models.user import User
from src.shared.tasks.scrapers.terminalx import scrape_products
from ...config.celeryApp import celery_app


def send_products(telegram_id: int, products: [Product]):
	print(f'Sending {len(products)} products to {telegram_id}')
	
	for product in products:
		api_bot.send_photo(
			chat_id=telegram_id,
			photo=product.image_url,
			caption=f"{product.title}\n{product.price}\n{product.link}"
		)


def scrape_and_save_products(search_text: str):
	products_list = scrape_products(search_text)
	
	print(f"Found {len(products_list)} products")
	
	search_in_db = Search(search_text).get()
	
	for product in products_list:
		if product.title == '':
			continue
		
		product = Product(
			title=product.title,
			price=product.price,
			link=product.link,
			image_url=product.image_url,
			available_sizes=product.available_sizes
		)
		
		if not product.exists():
			product.add()
			product.commit()
		
		product.commit()
		product_in_db = product.get()
		search_product = SearchProduct(search_in_db.id, product_in_db.id)
		search_product.add()
		search_product.commit()


@celery_app.task(name='get_products')
def get_and_send_products(search_text: str, telegram_id: int):
	user_object = SimpleNamespace(id=telegram_id, first_name='', last_name='')
	user = User(user_object)
	user_in_db = user.get()
	
	search = Search(search_text)
	search_in_db = search.get()
	search_products = search_in_db.products
	
	if len(search_products) == 0:
		scrape_and_save_products(search_text)
	
	user_search_subscription = Subscription(user_in_db.id, search_in_db.id)
	subscription_in_db = user_search_subscription.get()
	
	products = session.query(Product) \
		.filter(Product.currently_on_website.is_(True)) \
		.filter(Product.available_sizes.overlap(subscription_in_db.sizes)) \
		.join(SearchProduct, aliased=True) \
		.join(Search, aliased=True) \
		.filter(Search.search_text == search_text) \
		.join(Product, aliased=True) \
		.all()
	
	send_products(telegram_id, products)


def send_new_products_to_subscribers(search_text: str, products: [Product]):
	search = Search(search_text).get()
	
	subscribers = search.subscribers
	
	subscribers_telegram_ids = [subscriber.telegram_id for subscriber in subscribers]
	
	for telegram_id in subscribers_telegram_ids:
		user = User(telegram_id).get()
		subscription_in_db = Subscription(user.id, search.id).get()
		
		send_products(telegram_id, [product for product in products if any(size in product.available_sizes for size in subscription_in_db.sizes)])


@celery_app.task(name='start_periodic_scraping')
def start_periodic_scraping(search_text: str):
	print(f"Scraping for {search_text}")
	products_list = scrape_products(search_text)
	print(f"Found {len(products_list)} products")
	
	search_in_db = Search(search_text).get()
	
	new_products_list = []
	
	for product in products_list:
		if product.title == '':
			continue
		
		product = Product(
			title=product.title,
			price=product.price,
			link=product.link,
			image_url=product.image_url,
			available_sizes=product.available_sizes
		)
		
		if not product.exists():
			product.add()
			product.commit()
			new_products_list.append(product.get())
		
		product.commit()
		product_in_db = product.get()
		search_product = SearchProduct(search_in_db.id, product_in_db.id)
		search_product.add()
		search_product.commit()
	
	send_new_products_to_subscribers(search_text, new_products_list)


@celery_app.task(name='queue_periodic_scraping')
def queue_periodic_scraping():
	print("hello")
	searches = session.query(Search).all()
	for search in searches:
		start_periodic_scraping.delay(search.search_text)
