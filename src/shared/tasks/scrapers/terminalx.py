from pyquery import PyQuery as pq

URL = "https://terminalx.com"
search_endpoint = "catalogsearch/result/"

PRODUCTS_SELECTOR = "#app-root > div.app-content_5dEK > main > div.page-inner_2NeR > div > div.listing-content_2Leu > div.listing-main_byCk > div.product-list-wrapper_1--3 > ol > li"
NO_RESULTS_DIV_SELECTOR = "#app-root > div.app-content_5dEK > main > div.page-inner_2NeR > div > div.warning_1vFK.toast_hN0l.rtl_1l4_.full-width_p5rD.no-results-toast_1W0U"

NO_RESULTS_DIV_CONTENT = "אין תוצאות לשאילתת חיפוש שלך."


def build_search_query(search_text: str, page: int = 1):
	return f"?p={page}&q={search_text}"


class Product:
	def __init__(self, title: str, image_url: str, price: str, available_sizes: [str], link: str):
		self.title = title
		self.price = price
		self.image_url = image_url
		self.available_sizes = available_sizes
		self.link = link


def check_for_no_results(doc) -> bool:
	no_results_div = doc(NO_RESULTS_DIV_SELECTOR)
	
	return no_results_div and NO_RESULTS_DIV_CONTENT in no_results_div.text()


def scrape_products(search_text, page=1, products_list: [Product] or None = None) -> [] or [Product]:
	print(f"Getting products for {search_text} on page {page}")
	if products_list is None:
		products_list = []
	
	search_url = f"{URL}/{search_endpoint}{build_search_query(search_text, page)}"
	doc = pq(url=search_url)
	
	no_results = check_for_no_results(doc)
	
	if no_results:
		return products_list
	
	products = doc(PRODUCTS_SELECTOR)
	
	if len(products) == 0:
		return products_list
	
	products_data = products.map(lambda i, e: Product(
		title=pq(e).find("a.title_3ZxJ").text(),
		image_url=pq(e).find("img.image_3k9y").attr("src"),
		price=pq(e).find("div.final-price_8CiX").text().split("₪")[0].strip(),
		available_sizes=pq(e).find("div.item__short_tayt:not(.not-available_3TOC):not(.item-scroll_DHKG)").map(lambda i, e: pq(e).text().split('.')[0]),
		link=f"{URL}{pq(e).find('a.title_3ZxJ').attr('href')}"
	))
	
	products_list.extend(products_data)
	
	return scrape_products(search_text, page + 1, products_list)
