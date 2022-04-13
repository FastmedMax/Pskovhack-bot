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
    KEYBOARD_WITH_BUILDER = (
        Keyboard(one_time=False, inline=False)
        .add(Text("Просмотреть портфолио", payload={"command": "portfolio"}))
        .add(Text("Информация о мероприятиях", payload={"command": "events"}))
        .row()
        .add(Text("Информация о компании", payload={"command": "about"}))
        .add(Text("Обратная связь/вопрос", payload={"command": "callback"}))
        .get_json()
    )

    text = (
        "Приветствует всех в нашем (мультифункциональном) боте ПСКОВХАК! "
        "С помощью этого бота Вы можете просмотреть наше портфолио, узнать "
        "подробную информацию о компании, получить информацию о наших ближайших "
        "мероприятиях и получить от нас фидбек (задать нам свои вопросы)."
    )

    await message.answer(text=text, keyboard=KEYBOARD_WITH_BUILDER)


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

    text = (
        "Здесь Вы можете просмотреть наш портфолио – все наши работы и проекты, "
        "над которыми мы усердно трудились. Воспользуйтесь кнопками навигации, "
        "чтобы просмотреть динамический список кейсов. "
    )

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

    text = (
        "Здесь Вы можете получить информацию о наших ближайших мероприятиях. "
        "Воспользуйтесь кнопками навигации, чтобы просмотреть динамический список мероприятий. "
    )

    for element in list_elements:
        template = template_gen(
            *element
        )

        await message.answer(message=text, template=template)


@bot.on.message(payload={"command":"about"})
async def about(message: Message):
    text = (
        "PskovHack - это ИТ компания, которая выросла из сообщества участников "
        "в мероприятиях в формате хакатон. Мы участвовали в около 35 хакатонах "
        "от Всероссийских до Международных. Совместно с партнерами "
        "(Гильдия игропрактиков, GeekZ, Seldon, Практики Будущего) организовали "
        "4 всероссийских игровых хакатона, также организовали на базе ПсковГУ "
        "локальных хакатон \"СпортХак\". После побед и организации хакатонов перешли "
        "к выполнению коммерческих заказов и созданию инвестиционных проектов. "
        "Опыт разработки PskovHack включает в себя разработку проектов для мин. "
        "цифры Развития и связи Алтайского края, для ПсковГУ, профкома МГУ и многих "
        "других структур."
    )

    await message.answer(message=text)


@bot.on.message(payload={"command":"callback"})
async def callback(message: Message):
    await bot.state_dispenser.set(message.peer_id, MenuState.NAME)

    user_id = message.peer_id
    user_data[user_id] = {}

    text_intro = (
        "Этот раздел является своеобразной книгой жалоб и предложений: "
        "здесь Вы можете написать свои пожелания относительно наших проектов "
        "и сервисов, (описать опыт работы в каком-либо из них), "
        "а также задать нам все интересующие Вас вопросы. "
    )

    text = (
        "Чтобы задать нам вопрос, ответьте, пожалуйста, на несколько вопросов:\n"
        "Подскажите, как к Вам можно обращаться."
    )

    await message.answer(message=text_intro)
    await message.answer(message=text)


@bot.on.message(state=MenuState.NAME)
async def process_name(message: Message):
    await bot.state_dispenser.set(message.peer_id, MenuState.CONTACT)

    user_id = message.peer_id
    user_data[user_id]["name"] = message.text

    text = "Укажите свои контактные данные: номер телефона или адрес электронной почты."
    await message.answer(message=text)

@bot.on.message(state=MenuState.CONTACT)
async def process_contact(message: Message):
    await bot.state_dispenser.set(message.peer_id, MenuState.TEXT)

    user_id = message.peer_id
    user_data[user_id]["contact"] = message.text

    text = "Задайте свой вопрос или напишите свои пожелания. Мы ответим Вам в ближайшее время. Заранее спасибо!"
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

    text = "Спасибо за Ваше сообщение! Вы сможете увидеть ответы на все ваши запросы в этом чате."
    await message.answer(message=text)

bot.run_forever()