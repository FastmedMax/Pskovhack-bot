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
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)

    markup.add(
        types.InlineKeyboardButton("Портфолио")
    )
    markup.add(
        types.InlineKeyboardButton("Мероприятия")
    )
    markup.add(
        types.InlineKeyboardButton("О компании")
    )
    markup.add(
        types.InlineKeyboardButton("Обратная связь")
    )

    await message.reply(
        "Здесь будет очень важное приветствие!",
        reply_markup=markup)


@dp.message_handler(lambda call: call.text == "Портфолио")
async def portfolio(query: types.CallbackQuery):
    markup = types.InlineKeyboardMarkup()
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{URL}/api/cases/") as response:
            if response.status == 200:
                cases = await response.json()
            else:
                logger.error(await response.text())

    num_pages = len(cases) // 8
    if num_pages == 0:
        num_pages = 1

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


@dp.callback_query_handler(lambda call: call.data in ["previous_cases", "next_cases"])
async def change_cases(call: types.CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{URL}/api/cases/") as response:
            if response.status == 200:
                cases = await response.json()
            else:
                logger.error(await response.text())

    nav_buttons = call.message.reply_markup.inline_keyboard[-1]
    num_pages_btn = nav_buttons[1]
    current_page, count_pages = map(int, num_pages_btn.text.split("/"))

    if current_page == count_pages and call.data == "next_cases":
        return
    elif current_page == 1 and call.data == "previous_cases":
        return

    if call.data == "previous_cases":
        next_page = current_page - 1
    else:
        next_page = current_page + 1
    num_pages_btn.text = f"{next_page}/{count_pages}"
    nav_buttons[1] = num_pages_btn

    markup = types.InlineKeyboardMarkup()
    start_index_1 = current_page * 8
    if next_page == 1:
        start_index_1 = 0
    start_index_2 = start_index_1 + 1
    stop_index = next_page * 8

    for portfolio_1, portfolio_2 in zip_longest(cases[start_index_1:stop_index:2], cases[start_index_2:stop_index:2]):
        buttons = []
        if portfolio_1:
            buttons.append(types.InlineKeyboardButton(text=portfolio_1[1], callback_data=f"cases:{portfolio_1[0]}"))
        if portfolio_2:
            buttons.append(types.InlineKeyboardButton(text=portfolio_2[1], callback_data=f"cases:{portfolio_2[0]}"))
        markup.row(*buttons)

    markup.row(*nav_buttons)

    await bot.edit_message_reply_markup(
        chat_id=chat_id, message_id=message_id, reply_markup=markup
    )


@dp.callback_query_handler(lambda call: call.data.startswith("cases"))
async def case(query: types.CallbackQuery):
    case = query.data.split(":")
    id = case[1]
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{URL}/api/cases/{id}") as response:
            if response.status == 200:
                case = await response.json()
            else:
                logger.error(await response.text())

    text = md.text(
        md.bold(case["title"]),
        md.italic(case["description"]),
        sep='\n',
    )

    await bot.send_message(chat_id=query.from_user.id, text=text, parse_mode=types.ParseMode.MARKDOWN)


@dp.message_handler(lambda call: call.text == "О компании")
async def about(query: types.CallbackQuery):
    text = "Информация."

    await bot.send_message(chat_id=query.from_user.id, text=text)


@dp.message_handler(lambda call: call.text == "Мероприятия")
async def events(query: types.CallbackQuery):
    markup = types.InlineKeyboardMarkup()
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{URL}/api/events/") as response:
            if response.status == 200:
                events = await response.json()
            else:
                logger.error(await response.text())

    num_pages = len(events) // 8
    if num_pages == 0:
        num_pages = 1

    for event_1, event_2 in zip_longest(events[0:8:2], events[1:8:2]):
        buttons = []
        if event_1:
            buttons.append(types.InlineKeyboardButton(text=event_1[1], callback_data=f"events:{event_1[0]}"))
        if event_2:
            buttons.append(types.InlineKeyboardButton(text=event_2[1], callback_data=f"events:{event_2[0]}"))
        markup.row(*buttons)

    markup.row(
        types.InlineKeyboardButton("Назад", callback_data="previous_events"),
        types.InlineKeyboardButton(f"1/{num_pages}", callback_data="page_count"),
        types.InlineKeyboardButton("Далее", callback_data="next_events"),
    )

    text = (
        "events"
    )

    await bot.send_message(chat_id=query.from_user.id, text=text, reply_markup=markup)


@dp.callback_query_handler(lambda call: call.data in ["previous_events", "next_events"])
async def change_cases(call: types.CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{URL}/api/events/") as response:
            if response.status == 200:
                cases = await response.json()
            else:
                logger.error(await response.text())

    nav_buttons = call.message.reply_markup.inline_keyboard[-1]
    num_pages_btn = nav_buttons[1]
    current_page, count_pages = map(int, num_pages_btn.text.split("/"))

    if current_page == count_pages and call.data == "next_events":
        return
    elif current_page == 1 and call.data == "previous_events":
        return

    if call.data == "previous_events":
        next_page = current_page - 1
    else:
        next_page = current_page + 1
    num_pages_btn.text = f"{next_page}/{count_pages}"
    nav_buttons[1] = num_pages_btn

    markup = types.InlineKeyboardMarkup()
    start_index_1 = current_page * 8
    if next_page == 1:
        start_index_1 = 0
    start_index_2 = start_index_1 + 1
    stop_index = next_page * 8

    for event_1, event_2 in zip_longest(cases[start_index_1:stop_index:2], cases[start_index_2:stop_index:2]):
        buttons = []
        if event_1:
            buttons.append(types.InlineKeyboardButton(text=event_1[1], callback_data=f"events:{event_1[0]}"))
        if event_2:
            buttons.append(types.InlineKeyboardButton(text=event_2[1], callback_data=f"events:{event_2[0]}"))
        markup.row(*buttons)

    markup.row(*nav_buttons)

    await bot.edit_message_reply_markup(
        chat_id=chat_id, message_id=message_id, reply_markup=markup
    )


@dp.callback_query_handler(lambda call: call.data.startswith("events"))
async def case(query: types.CallbackQuery):
    event = query.data.split(":")
    id = event[1]
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{URL}/api/events/{id}") as response:
            if response.status == 200:
                event = await response.json()
            else:
                logger.error(await response.text())

    text = md.text(
        md.bold(event["title"]),
        md.italic(event["description"]),
        sep='\n',
    )

    await bot.send_message(chat_id=query.from_user.id, text=text, parse_mode=types.ParseMode.MARKDOWN)


@dp.message_handler(lambda call: call.text == "Обратная связь")
async def callback(query: types.CallbackQuery):
    await Form.name.set()
    text = "Как вас зовут?"
    await bot.send_message(chat_id=query.from_user.id, text=text)

@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    await Form.next()
    async with state.proxy() as data:
        data["name"] = message.text

    text = "Какой у вас номер телефона/почты?"
    await bot.send_message(chat_id=message.from_user.id, text=text)

@dp.message_handler(state=Form.contact)
async def process_contact(message: types.Message, state: FSMContext):
    await Form.next()
    async with state.proxy() as data:
        data["contact"] = message.text

    text = "Какой у вас вопрос?"
    await bot.send_message(chat_id=message.from_user.id, text=text)

@dp.message_handler(state=Form.text)
async def process_text(message: types.Message, state: FSMContext):
    callback = {}
    async with state.proxy() as data:
        data["text"] = message.text
        callback = data.as_dict()

    callback["type"] = "TELEGRAM"
    callback["user_id"] = message.from_user.id

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{URL}/api/callback/", json=callback) as response:
            if not response.status == 201:
                logger.error(await response.text())

    await state.finish()
    text = "Ваш запрос сформирован."
    await bot.send_message(chat_id=message.from_user.id, text=text)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
