from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
import logging
import os
import dotenv


dotenv.load_dotenv()
TOKEN = os.getenv("TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

async def on_startup(dp):
    logging.info("WitchPitch в сети, сучки!")

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)