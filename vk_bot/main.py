import os

import aiohttp
from loguru import logger
from vkbottle import Keyboard, Text, BaseStateGroup, TemplateElement, template_gen
from vkbottle.bot import Bot, Message


URL = os.getenv("DJANGO_HOST")
bot = Bot(token=os.getenv("VK_TOKEN"))

user_data = {}


class MenuState(BaseStateGroup):
    NAME = 1
    CONTACT = 2
    TEXT = 3


@bot.on.message(text="Start")
@bot.on.message(payload={"command":"start"})
async def hi_handler(message: Message):
    users_info = await bot.api.users.get(message.from_id)
    KEYBOARD_WITH_BUILDER = (
        Keyboard(one_time=False, inline=False)
        .add(Text("Портфолио", payload={"command": "portfolio"}))
        .add(Text("Мероприятия", payload={"command": "events"}))
        .row()
        .add(Text("О компании", payload={"command": "about"}))
        .add(Text("Обратная связь", payload={"command": "callback"}))
        .get_json()
    )
    await message.answer("Привет, {}".format(users_info[0].first_name), keyboard=KEYBOARD_WITH_BUILDER)


@bot.on.message(payload={"command":"portfolio"})
async def portfolio(message: Message):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{URL}/api/cases/") as response:
            if response.status == 200:
                cases = await response.json()
            else:
                logger.error(await response.text())

    keyboard_1 = Keyboard().add(Text("button 1", {})).get_json()
    list_elements = []
    elements = []
    for i, case in enumerate(cases):
        if (i // 10) == 1:
            list_elements.append(elements)
            elements = []

        elements.append(TemplateElement(
            buttons=keyboard_1,
            title=case[1],
            description=case[2]
        ))

    list_elements.append(elements)

    text = "Список"

    for element in list_elements:
        template = template_gen(
            *element
        )

        await message.answer(message=text, template=template)


@bot.on.message(payload={"command":"events"})
async def events(message: Message):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{URL}/api/events/") as response:
            if response.status == 200:
                events = await response.json()
            else:
                logger.error(await response.text())

    keyboard_1 = Keyboard().add(Text("button 1", {})).get_json()
    list_elements = []
    elements = []
    for i, event in enumerate(events):
        if (i // 10) == 1:
            list_elements.append(elements)
            elements = []

        elements.append(TemplateElement(
            buttons=keyboard_1,
            title=event[1],
            description=event[2]
        ))

    list_elements.append(elements)

    text = "Список"

    for element in list_elements:
        template = template_gen(
            *element
        )

        await message.answer(message=text, template=template)


@bot.on.message(payload={"command":"about"})
async def about(message: Message):
    text = "Информация о комапнии"
    await message.answer(message=text)


@bot.on.message(payload={"command":"callback"})
async def callback(message: Message):
    await bot.state_dispenser.set(message.peer_id, MenuState.NAME)

    user_id = message.peer_id
    user_data[user_id] = {}

    text = "Как вас зовут?"
    await message.answer(message=text)

@bot.on.message(state=MenuState.NAME)
async def process_name(message: Message):
    await bot.state_dispenser.set(message.peer_id, MenuState.CONTACT)

    user_id = message.peer_id
    user_data[user_id]["name"] = message.text

    text = "Какой у вас номер телефона/почты?"
    await message.answer(message=text)

@bot.on.message(state=MenuState.CONTACT)
async def process_contact(message: Message):
    await bot.state_dispenser.set(message.peer_id, MenuState.TEXT)

    user_id = message.peer_id
    user_data[user_id]["contact"] = message.text

    text = "Какой у вас вопрос?"
    await message.answer(message=text)

@bot.on.message(state=MenuState.TEXT)
async def process_text(message: Message):
    id = message.peer_id
    callback = {}
    callback["type"] = "VK"
    callback["user_id"] = id
    callback["text"] = message.text
    callback.update(user_data.pop(id))

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{URL}/api/callback/", json=callback) as response:
            if not response.status == 201:
                logger.error(await response.text())

    text = "Ваш запрос сформирован."
    await message.answer(message=text)

bot.run_forever()