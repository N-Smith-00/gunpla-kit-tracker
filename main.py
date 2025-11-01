import asyncio
from bot.bot import bot
from config.config import BOT_TOKEN
# from scraper import run_scraper
from database.db_connection import get_conn
from database.db_init import init_db
from config.scraper_config import SCRAPER_INTERVAL_HOURS

init_db()

conn = get_conn()

# async def periodic_scrape():
#     while True:
#         print("Starting scrape")
#         try:
#             await run_scraper
#         except Exception as e:
#             print(f'error in scraper: {e}')
#         await asyncio.sleep(SCRAPER_INTERVAL_HOURS * 3600)
               
async def main():
    # asyncio.create_task(periodic_scrape())
    await bot.start(BOT_TOKEN)
    
if __name__ == "__main__":
    asyncio.run(main())