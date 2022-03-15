import os

import aiohttp
from loguru import logger
from vkbottle import Keyboard, Text, BaseStateGroup, TemplateElement, template_gen
from vkbottle.bot import Bot, Message


URL = os.getenv("DJANGO_HOST")
bot = Bot(token=os.getenv("VK_TOKEN"))


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

bot.run_forever()