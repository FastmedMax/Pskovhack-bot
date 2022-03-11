import os
from itertools import zip_longest

import aiohttp
from loguru import logger
from aiogram.utils import markdown as md
from aiogram.dispatcher import FSMContext
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
