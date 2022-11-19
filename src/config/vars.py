import os

DB_DIALECT = os.environ.get("DB_DIALECT", "postgresql")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "1234")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_DATABASE = os.environ.get("DB_DATABASE", "superscraper")

BROKER_TYPE = os.environ.get("BROKER_TYPE", "amqp")
BROKER_HOST = os.environ.get("BROKER_HOST", "localhost")
BROKER_PORT = os.environ.get("BROKER_PORT", "5672")
BROKER_USER = os.environ.get("BROKER_USER", "guest")
BROKER_PASSWORD = os.environ.get("BROKER_PASSWORD", "guest")

CELERY_BACKEND_URL = os.environ.get("CELERY_BACKEND_URL", "rpc://")
BROKER_URL = f"{BROKER_TYPE}://{BROKER_USER}:{BROKER_PASSWORD}@{BROKER_HOST}:{BROKER_PORT}/"
DB_URL = f"{DB_DIALECT}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"

BOT_ACCESS_PASSWORD = os.environ.get("BOT_ACCESS_PASSWORD", "password")
TOKEN = os.environ.get("TOKEN")
SEARCH_INTERVAL_IN_MINUTES = int(os.environ.get("SEARCH_INTERVAL_IN_MINUTES", "5"))
