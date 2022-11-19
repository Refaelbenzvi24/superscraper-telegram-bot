from ..config.database import Base, engine
from ..config.vars import TOKEN
from telegram.ext import Updater
from .conversations.start_coneversation import get_start_handler


def main():
	print('creating tables')
	Base.metadata.create_all(engine)
	
	print('Starting bot...')
	updater = Updater(TOKEN)
	
	dispatcher = updater.dispatcher
	
	dispatcher.add_handler(get_start_handler())
	
	updater.start_polling()
	
	updater.idle()


if __name__ == "__main__":
	main()
