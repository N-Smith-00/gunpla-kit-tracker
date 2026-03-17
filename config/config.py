from dotenv import load_dotenv
import os
import re

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "./data/kits.db")
BOT_TOKEN = os.getenv("BOT_TOKEN")

VALID_SCALES = ["1/1", "1/12", "1/48", "1/60", "1/100", "1/144", "nonscale"]