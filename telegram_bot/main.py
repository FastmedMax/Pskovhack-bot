import os
from itertools import zip_longest

import aiohttp
from loguru import logger
from aiogram.utils import markdown as md
from aiogram.dispatcher import FSMContext
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup


URL = os.getenv("DJANGO_HOST")
API_TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class Form(StatesGroup):
    name = State()
    contact = State()
    text = State()


@dp.message_handler(commands="start")
async def start_cmd_handler(message: types.Message):
    markup = types.InlineKeyboardMarkup()

    markup.add(
        types.InlineKeyboardButton("Портфолио", callback_data="portfolio")
    )
    markup.add(
        types.InlineKeyboardButton("Мероприятия", callback_data="events")
    )
    markup.add(
        types.InlineKeyboardButton("О компании", callback_data="about")
    )
    markup.add(
        types.InlineKeyboardButton("Обратная связь", callback_data="callback")
    )

    await message.reply(
        "Здесь будет очень важное приветствие!",
        reply_markup=markup)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
