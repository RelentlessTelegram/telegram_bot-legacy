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


async def send_main_menu_settings(message, state):
    if type(message) == types.Message:
        await message.answer_sticker("CAACAgIAAxkBAAEc7r1j4zwg8DSy3wnrdeWHSg5qA9N5KgACJhMAAujW4hIfQm23Xqw9ZC4E")
        inline_keyboard = await build_inline_keyboard(['Service Feedback', 'Wishes', 'Remind Me SF!', 'Remember Me!', 'Edit Your Details'])
        await message.answer('Welcome to Relentless 1 Bot!\n\n Please be patient with me!\nIf you feel like I\'m not listening to you, or want to get out of stuff, type /restart! \n\n If you have encountered any bugs, please inform my creator at @qazer25!', reply_markup=inline_keyboard)
        await (state.set_state(State_menu.starting))
    elif type(message) == types.CallbackQuery:
        inline_keyboard = await build_inline_keyboard(['Service Feedback', 'Wishes', 'Remind Me SF!', 'Remember Me!','Edit Your Details'])
        await message.message.edit_text('Welcome to Relentless 1 Bot!\n\n Please be patient with me!\nIf you feel like I\'m not listening to you, or want to get out of stuff, type /restart! \n\nIf you have encountered any bugs, please inform my creator at @qazer25!', reply_markup=inline_keyboard)
        await (state.set_state(State_menu.starting))


async def view_details(message, state, conn, database_url):
    if type(message) == types.CallbackQuery:
        check = await check_id_in_table(conn, "chat_details", str(message.message.chat.id), database_url)
        if check == True:
            callback_query = message
            result = await get_from_table(conn=conn, table_name="chat_details", chatid=str(callback_query.message.chat.id), database_url=database_url)
            columns = await get_column_titles_from_table(conn=conn, table_name="chat_details", database_url=database_url)
            check_names_to_wishes_not_proper = await get_one_column_from_table(conn=conn, table_name="birthdays", condition="chatid", database_url=database_url)
            check_names_to_wishes = []
            for x in check_names_to_wishes_not_proper:
                check_names_to_wishes.append(x[0])
            string = "This is what I can remember about you! \n\n"
            ls = []
            for x in range(len(columns)):
                if columns[x][0] != "chatid" and columns[x][0] != "userid":
                    result_to_string = result[0][x]
                    if result_to_string == None:
                        result_to_string = "Nil"
                    if str(callback_query.message.chat.id) in check_names_to_wishes and columns[x][0] == 'name':
                        string += columns[x][0] + ': ' + result_to_string + " (not editable at the moment!)\n"
                    else:
                        string += columns[x][0] + ': ' + result_to_string + "\n"
                        ls.append(columns[x][0])
            string += "\n What do you want me to change?"
            ls.append("<< Back <<")
            inline_keyboard = await build_inline_keyboard(ls)
            await callback_query.message.edit_text(string, reply_markup=inline_keyboard)
            await state.set_state(State_menu.view_details)
        else:
            inline_keyboard = await build_inline_keyboard(["<< Back <<"])
            await message.message.edit_text("Sorry who are you again? Please press 'Remember Me!' first!", reply_markup=inline_keyboard)
            await state.set_state(State_menu.starting_callback)
    elif type(message) == types.Message:
        
        check = await check_id_in_table(conn, "chat_details", str(message.chat.id), database_url)
        if check == True:
            result = await get_from_table(conn=conn, table_name="chat_details", chatid=str(message.chat.id), database_url=database_url)
            columns = await get_column_titles_from_table(conn=conn, table_name="chat_details", database_url=database_url)
            check_names_to_wishes_not_proper = await get_one_column_from_table(conn=conn, table_name="birthdays", condition="chatid", database_url=database_url)
            check_names_to_wishes = []
            for x in check_names_to_wishes_not_proper:
                check_names_to_wishes.append(x[0])
            string = "This is what I can remember about you! \n\n"
            ls = []
            
            for x in range(len(columns)):
                if columns[x][0] != "chatid" and columns[x][0] != "userid":
                    result_to_string = result[0][x]
                    if result_to_string == None:
                        result_to_string = "Nil"
                    if str(message.chat.id) in check_names_to_wishes and columns[x][0] == 'name':
                        string += columns[x][0] + ': ' + result_to_string + " (not editable at the moment!)\n"
                    else:
                        string += columns[x][0] + ': ' + result_to_string + "\n"
                        ls.append(columns[x][0])
            string += "\n What do you want me to change?"
            ls.append("<< Back <<")
            inline_keyboard = await build_inline_keyboard(ls)
            await message.answer(string, reply_markup=inline_keyboard)
            await state.set_state(State_menu.view_details)
        else:
            inline_keyboard = await build_inline_keyboard(["<< Back <<"])
            await message.answer("Sorry who are you again? Please press 'Remember Me!' first!", reply_markup=inline_keyboard)
            await state.set_state(State_menu.starting_callback)
        
def main():
    pass


if __name__ == "__main__":
    main()
