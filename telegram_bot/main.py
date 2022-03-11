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

@dp.callback_query_handler(lambda call: call.data == "portfolio")
async def portfolio(query: types.CallbackQuery):
    markup = types.InlineKeyboardMarkup()
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{URL}/api/cases/") as response:
            if response.status == 200:
                cases = await response.json()
            else:
                logger.error(await response.text())
    num_pages = len(cases) // 8
    
    for portfolio_1, portfolio_2 in zip_longest(cases[0:8:2], cases[1:8:2]):
        buttons = []
        if portfolio_1:
            buttons.append(types.InlineKeyboardButton(text=portfolio_1[1], callback_data=f"cases:{portfolio_1[0]}"))
        if portfolio_2:
            buttons.append(types.InlineKeyboardButton(text=portfolio_2[1], callback_data=f"cases:{portfolio_2[0]}"))
        markup.row(*buttons)

    markup.row(
        types.InlineKeyboardButton("Назад", callback_data="previous_cases"),
        types.InlineKeyboardButton(f"1/{num_pages}", callback_data="page_count"),
        types.InlineKeyboardButton("Далее", callback_data="next_cases"),
    )

    text = (
        "cases"
    )

    await bot.send_message(chat_id=query.from_user.id, text=text, reply_markup=markup)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
