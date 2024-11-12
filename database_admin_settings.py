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
from classes_modified import *
from main_menu_settings import *
from admin_settings import *
from bot_settings import *

async def database_chatid_columns(message, state, conn, database_url):
    if type(message) == types.CallbackQuery:
        result = await get_column_titles_from_table(conn=conn, table_name="chat_details", database_url=database_url)
        ls = []
        for x in result:
            ls.append(x[0])
        ls.append("<< Back <<")
        inline_keyboard = await build_inline_keyboard(ls)
        await message.message.edit_text("Choose column to edit (if you wish to delete a id entry, type DELETE ALL in the chatid section)", reply_markup=inline_keyboard)
        await state.set_state(State_menu.database_columns)
    
    elif type(message) == types.Message:
        pass

async def database_chatid_id(message, state, data,database_url):
    if type(message) == types.CallbackQuery:
        result = await get_one_column_from_table(conn=conn, table_name="chat_details",condition= "chatid," + data["column"],database_url=database_url)
        string = "Results: \n"
        ls = []
        print(result)
        for x in result:
            if x[1] == None:
                x = (x[0], 'Nil')
            string += x[0] + "   " +x[1] + "\n"
            ls.append(x[0])
        ls.append("<< Back <<")
        inline_keyboard = await build_inline_keyboard(ls)
        await message.message.answer(string)
        await message.message.answer("Choose target ID", reply_markup=inline_keyboard)
        await state.set_data(data)
        await state.set_state(State_menu.database_key)

    elif type(message) == types.Message:
        result = await get_one_column_from_table(conn=conn, table_name="chat_details",condition="chatid," + data["column"],database_url=database_url)
        string = "Results:\n"
        ls = []
        for x in result:
            if x[1] == None:
                x = (x[0], 'Nil')
            string += x[0] + '   ' + x[1] + "\n"
            ls.append(x[0])
        ls.append("<< Back <<")
        inline_keyboard = build_inline_keyboard(ls)
        await message.answer(string)
        await message.answer("Choose target ID", reply_markup=inline_keyboard)
        await state.set_data(data)
        await state.set_state(State_menu.database_key)

def main():
    pass


if __name__ == "__main__":
    main()
