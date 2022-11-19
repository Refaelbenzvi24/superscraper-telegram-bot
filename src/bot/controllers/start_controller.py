from ...shared.models.user import User
from ...shared.tasks.tasks import get_and_send_products
from telegram import Update


def start_search(update: Update):
	user = User(update.effective_user)
	user_in_db = user.get()
	user_settings = user_in_db.settings
	search_text = user_settings.current_editing_search_text
	
	get_and_send_products.apply_async(args=[search_text, update.effective_user.id])
