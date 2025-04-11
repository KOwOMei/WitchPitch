from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from bot.handlers.common_handlers import register_common_handlers
from bot.handlers.audio_handlers import register_audio_handlers
import logging
import os
import dotenv


dotenv.load_dotenv()
TOKEN = os.getenv("TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
register_common_handlers(dp)
register_audio_handlers(dp)

async def on_startup(dp):
    logging.info("WitchPitch в сети, сучки!")

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)