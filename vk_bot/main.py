import os

import aiohttp
from loguru import logger
from vkbottle import Keyboard, Text, BaseStateGroup, TemplateElement, template_gen
from vkbottle.bot import Bot, Message


URL = os.getenv("DJANGO_HOST")
bot = Bot(token=os.getenv("VK_TOKEN"))


bot.run_forever()