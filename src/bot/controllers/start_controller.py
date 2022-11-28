from ...shared.models.search import Search
from ...shared.models.subscription import Subscription
from ...shared.models.user import User
from ...shared.models.userSettings import UserSettings
from ...shared.tasks.tasks import get_and_send_products
from telegram import Update


def commit_search(update: Update):
	search_text = update.message.text
	search = Search(search_text)
	user = User(update.effective_user)
	
	if not search.exists():
		search.add()
		search.commit()
	
	user_in_db = user.get()
	search_in_db = search.get()
	
	if user_in_db not in search_in_db.subscribers:
		subscription = Subscription(user_in_db.id, search_in_db.id)
		subscription.add()
		subscription.commit()
	
	user_settings = UserSettings(user_in_db.id)
	user_settings_in_db = user_settings.get()
	user_settings_in_db.current_editing_search_text = search_text
	user_settings.commit()


def add_size(update: Update):
	size = update.message.text
	
	user = User(update.effective_user)
	user_in_db = user.get()
	
	search = Search(user_in_db.settings.current_editing_search_text)
	search_in_db = search.get()
	
	subscription = Subscription(user_in_db.id, search_in_db.id)
	
	subscription.add_size(int(size))
	
	update.message.reply_text('Would you like to add another size?'
	                          'if not, please enter /next')


def start_search(update: Update):
	user = User(update.effective_user)
	user_in_db = user.get()
	user_settings = user_in_db.settings
	search_text = user_settings.current_editing_search_text
	
	print(f'User {user_in_db.id} started searching for {search_text}')
	get_and_send_products.apply_async(args=[search_text, update.effective_user.id])
