

import logging
import aiogram.utils.markdown as md
import asyncio
import logging
import sys
from asyncio import CancelledError, Future, Lock
from typing import Any, AsyncGenerator, Dict, List, Optional, Union
from aiogram import Bot, F, Router, html
from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import types
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.exceptions import TelegramAPIError
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.methods.edit_message_text import EditMessageText
from aiogram.methods.edit_message_reply_markup import EditMessageReplyMarkup
from aiogram.methods.send_chat_action import SendChatAction
from aiogram.dispatcher.event.event import EventObserver
import os

from urllib3 import Retry
from google_functions import *
from keyboard import *
import openai
import psycopg2
from urllib.parse import urlparse
import aioschedule
from classes_modified import *


def check_for_assert(envtarget, backup=None):
    try:
        assert (target := os.environ.get(envtarget))
        return target
    except AssertionError:
        return backup

creator_id = ""
birthday_ic_id = ""
script_id = check_for_assert("SCRIPT_ID", '')
API_TOKEN = check_for_assert("TOKEN", '')
REDIS_URL = check_for_assert("REDIS_URL", '')
DATABASE_URL = check_for_assert("DATABASE_URL", "")
storage = RedisStorage_custom.from_url(REDIS_URL)
bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher(storage=storage)
database_url = urlparse(DATABASE_URL)
conn = psycopg2.connect(
    host=database_url.hostname,
    user=database_url.username,
    password=database_url.password,
    port=database_url.port)


def main():
    pass


if __name__ == "__main__":
    main()
