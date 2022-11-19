import logging

from ..controllers.start_controller import start_search
from ...shared.models.search import Search
from ...shared.models.subscription import Subscription
from ...shared.models.user import User
from ...config.vars import BOT_ACCESS_PASSWORD
from ...shared.models.userSettings import UserSettings
from telegram import ReplyKeyboardRemove, Update
from telegram.ext import (
	CommandHandler,
	MessageHandler,
	ConversationHandler,
	CallbackContext,
	Filters
)

logger = logging.getLogger(__name__)

VERIFY_PASSWORD, ENTER_SEARCH_STRING, SIZE, MORE_SIZES = range(4)


def start(update: Update, context: CallbackContext) -> int:
	user = User(update.effective_user)
	user_in_db = user.get()
	
	if user.exists():
		
		if user_in_db.is_authenticated:
			update.message.reply_text('Please enter what you are looking for!')
			return ENTER_SEARCH_STRING
		
		if user_in_db.incorrect_password_attempts >= 3 or user_in_db.disabled:
			update.message.reply_text("You have entered the password incorrectly 3 times. your account has been blocked.")
			return ConversationHandler.END
	
	update.message.reply_text('Hi! Please enter a password so we could start!')
	
	return VERIFY_PASSWORD


def verify_password(update: Update, context: CallbackContext) -> int:
	message_content = update.message.text
	
	user = User(update.effective_user)
	
	if not user.exists():
		user.add()
	
	user_in_db = user.get()
	
	if user_in_db.incorrect_password_attempts >= 3:
		update.message.reply_text("You have entered the password incorrectly 3 times. your account has been blocked.")
		return ConversationHandler.END
	
	if message_content == BOT_ACCESS_PASSWORD:
		user_in_db.is_authenticated = True
		user.commit()
		
		update.message.reply_text('Password is correct! \n'
		                          'please enter what you are looking for!')
		
		return ENTER_SEARCH_STRING
	
	update.message.reply_text('Password is incorrect!, please try again')
	
	user_in_db.incorrect_password_attempts += 1
	user.commit()
	
	return VERIFY_PASSWORD


def enter_search_string(update: Update, context: CallbackContext) -> int:
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
	
	update.message.reply_text('Please enter what size you are looking for!')
	
	return SIZE


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


def size(update: Update, context: CallbackContext) -> int:
	if not update.message.text.isdigit():
		update.message.reply_text('Please enter a number!')
		return SIZE
	
	add_size(update)
	
	return MORE_SIZES


def more_sizes(update: Update, context: CallbackContext) -> int:
	if not update.message.text.isdigit():
		update.message.reply_text('Please enter a number!')
		return MORE_SIZES
	
	add_size(update)
	
	return MORE_SIZES


def start_searching(update: Update, context: CallbackContext) -> int:
	"""Ends conversation from InlineKeyboardButton."""
	update.message.reply_text("I'm done! \n"
	                          "I will notify you when the products list is available!")
	
	start_search(update)
	
	return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
	"""Cancels and ends the conversation."""
	user = update.message
	logger.info("User %s canceled the conversation.", user.from_user.first_name)
	
	update.message.reply_text('Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove())
	
	return ConversationHandler.END


start_handler = [CommandHandler('start', start)]
cancel_handler = [CommandHandler('cancel', cancel)]


def get_start_handler():
	"""Returning an handler of the start conversation"""
	
	return ConversationHandler(
		entry_points=[*start_handler],
		states={
			VERIFY_PASSWORD: [MessageHandler(Filters.text, verify_password), *cancel_handler],
			ENTER_SEARCH_STRING: [MessageHandler(Filters.text, enter_search_string), *cancel_handler],
			SIZE: [MessageHandler(Filters.text, size), *cancel_handler],
			MORE_SIZES: [
				CommandHandler('next', start_searching),
				MessageHandler(Filters.text, more_sizes),
				*cancel_handler
			]
		},
		fallbacks=[*start_handler, *cancel_handler]
	)
