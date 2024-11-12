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
import os
from google_functions import *
from keyboard import *
from connect_db import *
from datetime import *
from aioredis import *
from bot_settings import *
import json
import copy
from bot_settings import *
async def renew_wishes_database(script_id, database_url, redis_url):

    database_url = urlparse(database_url)
    conn = psycopg2.connect(
    host=database_url.hostname,
    user=database_url.username,
    password=database_url.password,
    port=database_url.port)
    bot_storage = await Redis.from_url(redis_url)
    string_to_send = "Hi the following wishes are done\n\n"
    #checking all birthdays a month from now
    result = await get_all_from_table(conn, "chat_details", database_url)
    result1 = await get_one_column_from_table(conn, "birthdays", "name", database_url)
    checking = []
    for x in result1:
        checking.append(x[0])
    date_now = datetime.now().strftime("%d/%m")
    date_later = (datetime.now() + timedelta(days=30)).strftime("%d/%m")
    adding_wishes = []
    removing_wishes = []
    #check for adding wishes
    for x in result:
        if date_later == x[3] and x[2] not in checking:
            dict = {}
            dict["soft_deadline"] = (datetime.now() + timedelta(days=7)).strftime("%d/%m")
            dict["hard_deadline"] = (datetime.now() + timedelta(days=14)).strftime("%d/%m")
            dict["name"] = x[2]
            dict["chatid"] = x[0]
            await add_into_table(conn, "birthdays", dict, database_url)
            await google_function(script_id, "create_sheet_python", dict["name"])
            adding_wishes.append(x[2])

    #check for removing wishes
    result1 = await get_all_from_table(conn, "birthdays", database_url)
    count = []
    for x in result1:
        if x[3] == date_now:
            await delete_from_table(conn, "birthdays", "name", x[0], database_url)
            removing_wishes.append(x[0])
        else:
            count.append(x[0])
    
    if adding_wishes == [] and removing_wishes == []:
        await bot_storage.set("current_brithday_wishes", json.dumps(count))
        await bot_storage.close()
        conn.close()
    else:
        result2 = await get_all_from_table(conn, "wishes_reminder", database_url)
        for y in result2:
            not_done_wishes = json.loads(y[2])
            adding_wishes1 = copy.deepcopy(adding_wishes)
            if adding_wishes != []:
                if y[1] in adding_wishes1:
                    adding_wishes1.remove(y[1])
                not_done_wishes1 = not_done_wishes + adding_wishes1
            
            else:
                not_done_wishes1 = not_done_wishes

            if removing_wishes != []:
                for z in removing_wishes:
                    if z in not_done_wishes1:
                        not_done_wishes1.remove(z)
    

            await update_in_table(conn, "wishes_reminder", "chatid", y[0], {"wishes_not_done":json.dumps(not_done_wishes1)}, database_url)
        
        #for reminding when its done!
        if removing_wishes != [] and birthday_ic_id != "":
            for z in removing_wishes:
                
                url_link = await google_function(script_id, "get_sheet_url", z)
                string_to_send += z + ": " + url_link + '\n'
            await bot.send_message(birthday_ic_id, string_to_send)

        await bot_storage.set("current_brithday_wishes", json.dumps(count))
        await bot_storage.close()
        conn.close()

async def submit_wishes(script_id, target, array):
    try:
        return(google_function( script_id, "submit_wishes_python", target, array))
    except:
        return("error")



def main():
    asyncio.run(renew_wishes_database(script_id=script_id, database_url=DATABASE_URL, redis_url=REDIS_URL))


if __name__ == "__main__":
    main()
    
