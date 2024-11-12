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
from redis.asyncio.client import Redis
from redis.asyncio.connection import ConnectionPool
from google_functions import *
from keyboard import *
import openai
import psycopg2
from urllib.parse import urlparse
import aioschedule
from connect_db import *
import json
from wishes import *
from pytz import timezone
import time
from urllib3 import Retry

class RedisStorage_custom(RedisStorage):
    @classmethod
    def from_url(
        cls, url: str, connection_kwargs: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> "RedisStorage":
        """
        Create an instance of :class:`RedisStorage` with specifying the connection string

        :param url: for example :code:`redis://user:password@host:port/db`
        :param connection_kwargs: see :code:`redis` docs
        :param kwargs: arguments to be passed to :class:`RedisStorage`
        :return: an instance of :class:`RedisStorage`
        """
        if connection_kwargs is None:
            connection_kwargs = {}
        pool = ConnectionPool.from_url(url, **connection_kwargs)
        redis = Redis(connection_pool=pool, health_check_interval=10, socket_connect_timeout=10,retry_on_timeout=True, socket_keepalive=True)
        return cls(redis=redis, **kwargs)
    async def set_data_global(self, key, data):
        if not data:
            await self.redis.delete(key)
            return
        await self.redis.set(
            key,
            json.dumps(data),
            ex=self.data_ttl,
        )

    async def get_data_global(self, key):
        value = await self.redis.get(key)
        if value is None:
            return {}
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        return json.loads(value)

class State_menu(StatesGroup):
    starting = State()
    starting_callback = State()
    sf = State()
    wishes = State()
    wishes_submit = State()
    remember_me_name = State()
    remember_me_birthday = State()
    remember_me_housing = State()
    view_details = State()
    edit_details = State()
    admin_menu = State()
    admin_menu2 = State()
    add_admin = State()
    database = State()
    database_columns = State()
    database_key = State()
    database_write = State()

    
def main():
    pass


if __name__ == "__main__":
    main()