from dotenv import load_dotenv
import os

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "./data/kits.db")
BOT_TOKEN = os.getenv("BOT_TOKEN")
