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
from aiogram.client.session.base import BaseSession
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
from database_admin_settings import *
import random
# Configure logging
logging.basicConfig(level=logging.INFO)







#all codes downwards
observer_shutdown =  EventObserver()
observer_startup = EventObserver()
router = Router()



#Starting the bot
@router.message(Command(commands=["start"]))
async def send_welcome(message: types.Message, state: FSMContext):
    await send_main_menu_settings(message, state)
    """
    This handler will be called when user sends `/start` or `/help` command
    """

@router.message(Command(commands=["restart"]))
async def reset_state(message: types.Message, state: FSMContext):
    await message.answer("Clear! Press or type /start again!", reply_markup=ReplyKeyboardRemove())
    await state.clear()

#results of choice
@router.callback_query(State_menu.starting)
async def choosing(callback_query: types.CallbackQuery, state: FSMContext):
    callback = callback_query.data
    if callback == 'Service Feedback':
        '''
        sf_showing = await storage.get_data_global(key = "sf_showing")
        sf_title = await storage.get_data_global(key = "sf_title")
        sf_type = await storage.get_data_global(key = "sf_type")
        sf_choice = await storage.get_data_global(key = "sf_choice")
        '''
        sf_showing, sf_title, sf_type, sf_choice = await asyncio.gather(storage.get_data_global(key = "sf_showing"), storage.get_data_global(key = "sf_title"), storage.get_data_global(key = "sf_type"), storage.get_data_global(key = "sf_choice"))
        form_title = sf_showing[0] + '\n\n' + sf_showing[1]
        message = callback_query.message
        await message.edit_text(form_title, reply_markup=InlineKeyboardMarkup(inline_keyboard=[]))
        if sf_type[0] == "LIST" or sf_type[0] == 'MULTIPLE_CHOICE':
            keyboard = await build_keyboard_sf(sf_choice[0])
            await message.answer(sf_title[0], reply_markup=keyboard)
            await state.set_state(State_menu.sf)
            await state.set_data({"count":0})

    elif callback == "Wishes":
        message = callback_query.message
        checking = (await get_one_column_from_table(conn, "chat_details", "chatid", DATABASE_URL))
        checking1 = []
        for x in checking:
            checking1.append(x[0])
        if str(message.chat.id) in checking1:
            result = await storage.get_data_global("current_brithday_wishes")
            checking2 = (await get_from_table(conn, "chat_details", str(message.chat.id), DATABASE_URL))[0][2]
            if checking2 in result:
                result.remove(checking2)
            if len(result) != 0:
                inline_keyboard = await build_inline_keyboard(result)
                await message.edit_text(text="Who do you wanna wish for?", reply_markup=inline_keyboard)
                await state.set_state(State_menu.wishes)
            else:
                inline_keyboard = await build_inline_keyboard(["<< Back <<"])
                await message.edit_text(text="Currently there is no one's birthday coming up! Try again some other time!", reply_markup=inline_keyboard)
                await state.set_state(State_menu.starting_callback)

        else:
            inline_keyboard = await build_inline_keyboard(["<< Back <<"])
            await message.edit_text(text="Chat not registered! Please press 'Remember Me!' before proceeding", reply_markup=inline_keyboard)
            await state.set_state(State_menu.starting_callback)
    
    elif callback == 'Remind Me SF!':
        chatid = str(callback_query.message.chat.id)
        result = await add_into_table(conn, "sf_reminder", {"chatid": chatid, "done":"No"}, DATABASE_URL)
        message = callback_query.message
        inline_keyboard = await build_inline_keyboard(["<< Back <<"])
        if result == 'Done':
            await message.edit_text(text="Okay, I will help you remind for SF!", reply_markup=inline_keyboard)
        else:
            
            await delete_from_table(conn, "sf_reminder", "chatid", str(message.chat.id), DATABASE_URL)
            await message.edit_text(text="Okay, I will stop reminding you for SF!", reply_markup=inline_keyboard)
        await state.set_state(State_menu.starting_callback)

    elif callback == "Remember Me!":
        message = callback_query.message
        result = await check_id_in_table(conn, "chat_details", str(callback_query.message.chat.id), database_url=DATABASE_URL)
        if result == True:
            inline_keyboard = await build_inline_keyboard(["<< Back <<"])
            await message.edit_text("But I remembered you already!", reply_markup=inline_keyboard)
            await state.set_state(State_menu.starting_callback)
        elif result == False:
            await state.set_state(State_menu.remember_me_name)
            await message.edit_text(text="Enter your first name",reply_markup=InlineKeyboardMarkup(inline_keyboard=[]))
    
    elif callback == "Edit Your Details":
        await view_details(callback_query, state, conn, DATABASE_URL)


#edit_details
@router.callback_query(State_menu.view_details)
async def view_details_menu(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == "<< Back <<":
        await send_main_menu_settings(callback_query, state)
    
    else:
        data = {}
        data["column"] = callback_query.data
        await callback_query.message.edit_text("Enter in your new details(type 'back' to go back to previous menu)")
        await state.set_data(data)
        await state.set_state(State_menu.edit_details)

@router.message(State_menu.edit_details)
async def edit_details_menu(message: types.Message, state: FSMContext):
    if message.text.lower() == "back":
        await view_details(message, state,conn,DATABASE_URL)
    else:
        data = await state.get_data()
        await update_in_table(conn=conn, table_name="chat_details", condition="chatid", parameter=str(message.chat.id), dict={data["column"]:message.text}, database_url=DATABASE_URL)
        inline_keyboard = await build_inline_keyboard(["<< Back <<"])
        await message.answer_sticker("CAACAgIAAxkBAAEc7sFj4zzxzAdZkBxx41Zv1M2dwpaBbAACNhMAAujW4hK5o_LnYoJUMi4E")
        await message.answer("Change made! I will remember the new info!", reply_markup=inline_keyboard)        
 
@router.callback_query(State_menu.edit_details)
async def view_details_menu_return(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == "<< Back <<":
        await view_details(callback_query, state, conn,DATABASE_URL)






###service feedback
@router.message(State_menu.sf)
async def sf(message: types.Message, state: FSMContext):
    data = await state.get_data()
    length = int(data["count"])
    data[length] = message.text
    length += 1
    sf_title, sf_type, sf_choice = await asyncio.gather(storage.get_data_global(key = "sf_title"), storage.get_data_global(key = "sf_type"), storage.get_data_global(key = "sf_choice"))
    if len(sf_title) == length:
        #submit form
        await message.answer('submitting SF...', reply_markup=ReplyKeyboardRemove())
        response = []
        for x in data:
            if x != 'count':
                response.append(data[x])
        await SendChatAction(chat_id = str(message.chat.id), action = "typing")
        result = await google_function(script_id, 'submit_form', response)
        print(result)
        if result == "submitted":
            await message.answer_sticker("CAACAgIAAxkBAAEc7sFj4zzxzAdZkBxx41Zv1M2dwpaBbAACNhMAAujW4hK5o_LnYoJUMi4E")
            inline_keyboard = await build_inline_keyboard(["<< Back <<"])
            await message.answer('Submitted! Have a nice day!', reply_markup=inline_keyboard)
            result = await(update_in_table(conn, "sf_reminder", "chatid",str(message.chat.id), {"done":"Yes"}, DATABASE_URL))
            await state.set_state(State_menu.starting_callback)
        else:
            await message.answer_sticker("CAACAgIAAxkBAAEc7sNj4z1lHz20eNuC1-e7114fe4pNpAAC3hMAAujW4hJymOg_Xmxaui4E")
            inline_keyboard = await build_inline_keyboard(["<< Back <<"])
            await message.answer('Sorry! I cannot submit your service feedback, you may have entered invalid answers for the questions! Please try again and make sure to use the custom keyboard when prompted!', reply_markup=inline_keyboard)
            await state.set_state(State_menu.starting_callback)

    else:
        if str(sf_type[length-1]) == 'MULTIPLE_CHOICE' and message.text == "Yes":
            data[length] = 'Nil'
            length += 1

        if str(sf_type[length]) == 'MULTIPLE_CHOICE' or str(sf_type[length]) == 'LIST':
            keyboard = await build_keyboard_sf(sf_choice[length])
            await message.answer(sf_title[length], reply_markup=keyboard)
        else:
            await message.answer(sf_title[length])
        data["count"] = length
        await state.update_data(data)

@router.callback_query(State_menu.starting_callback)
async def back_main_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await send_main_menu_settings(callback_query, state)

###wishes
@router.callback_query(State_menu.wishes)
async def wishes(callback_query: types.CallbackQuery, state: FSMContext):
    message = callback_query.message
    await message.edit_text(text="Type your wish for " + str(callback_query.data), reply_markup=InlineKeyboardMarkup(inline_keyboard=[]))
    data = await state.get_data()
    data["name"] = callback_query.data
    await state.set_data(data)
    await state.set_state(State_menu.wishes_submit)

@router.message(State_menu.wishes_submit)
async def wishes_submit(message: types.Message, state: FSMContext):
    await message.answer(text= "Submitting...")
    data = await state.get_data()
    target = data["name"]
    wish = message.text
    chatid = str(message.chat.id)
    await SendChatAction(chat_id = str(message.chat.id), action = "typing")
    result = await get_from_table(conn, "chat_details", str(chatid), DATABASE_URL)
    result1 = await google_function(script_id, "submit_wishes_python", target, [result[0][2], wish])
    if result1 == 'Submitted':
        await message.answer_sticker("CAACAgIAAxkBAAEc7sFj4zzxzAdZkBxx41Zv1M2dwpaBbAACNhMAAujW4hK5o_LnYoJUMi4E")
        ls = (await get_from_table(conn, "wishes_reminder", chatid, DATABASE_URL))[0]
        ls = json.loads(ls[2])
        if target in ls:
            ls.remove(target)
        await update_in_table(conn, "wishes_reminder", "chatid",chatid, {"wishes_not_done":json.dumps(ls)}, DATABASE_URL)
        inline_keyboard = await build_inline_keyboard(["<< Back <<"])
        await message.answer(text="Submitted! Have a nice day!", reply_markup=inline_keyboard)
        
    else:
        inline_keyboard = await build_inline_keyboard(["<< Back <<"])
        await message.answer(text="Error, unable to submit!", reply_markup=inline_keyboard)
    await state.set_state(State_menu.starting_callback)


###remember me!
@router.message(State_menu.remember_me_name)
async def remember_me_birthday(message: types.Message, state: FSMContext):
    data = await state.set_data({"name":message.text})
    await message.answer(text="Enter your birthday in this format\n 'dd/mm'")
    await state.set_state(State_menu.remember_me_birthday)

@router.message(State_menu.remember_me_birthday)
async def remember_me_housing(message: types.Message, state: FSMContext):
    data = await state.get_data()
    data["birthday"] = message.text
    await message.answer(text="Enter your address (enter Nil if None)")
    await state.update_data(data)
    await state.set_state(State_menu.remember_me_housing)


@router.message(State_menu.remember_me_housing)
async def record(message: types.Message, state: FSMContext):
    data = await state.get_data()
    dict = {"chatid": str(message.chat.id),
    "userid": str(message.chat.username or "None"),
    "name": data["name"],
    "birthday": data["birthday"],
    "housing": message.text
    }
    result = await get_one_column_from_table(conn, "birthdays", "name", DATABASE_URL)
    avaliable_wishing = []
    for x in result:
        avaliable_wishing.append(x[0])
    dict1 = {"chatid": str(message.chat.id),
    "name": data["name"],
    "wishes_not_done": json.dumps(avaliable_wishing)
    }
    result = await add_into_table(conn, "chat_details", dict, DATABASE_URL)
    result1 = await add_into_table(conn, "wishes_reminder", dict1, DATABASE_URL)
    if result == 'Done' and result1 == 'Done':
        await message.answer_sticker("CAACAgIAAxkBAAEc7sFj4zzxzAdZkBxx41Zv1M2dwpaBbAACNhMAAujW4hK5o_LnYoJUMi4E")
        inline_keyboard = await build_inline_keyboard(["<< Back <<"])
        await message.answer(text="Okay! I have remembered you!", reply_markup=inline_keyboard)
        
    else:
        await message.answer_sticker("CAACAgIAAxkBAAEdBEFj5d25tC2nsDdYHNhXyUJbKAEf7wACIRMAAujW4hL2_bx62eekiS4E")
        inline_keyboard = await build_inline_keyboard(["<< Back <<"])
        await message.answer(text="But I have already remembered you!", reply_markup=inline_keyboard)
    await state.set_state(State_menu.starting_callback)


###admin stuff

@router.message(Command(commands=["init_database"]))
async def init_database_admin(message: types.Message, state: FSMContext):
    await message.answer("initalizing_database...")
    result = await init_database(conn=conn)
    if result == "Done":
        await add_into_table(conn, "admin", {"chatid": str(message.chat.id)}, DATABASE_URL)
        await message.answer("Done initalizing database!")

    elif result == "Initalized":
        await message.answer("Sorry, you're not allowed to use this command!")

@router.message(Command(commands=["admin"]))
async def admin_menu(message: types.Message, state: FSMContext):
    check = await check_id_in_table(conn=conn, table_name="admin", parameter=str(message.chat.id), database_url = DATABASE_URL)
    if check == False:
        await message.answer("I'm sorry but you're not an admin for this bot! Ask other admins to add for you!")
        return
    await send_admin_settings(message, state)


@router.callback_query(State_menu.admin_menu2)
async def admin_menu_2(callback_query: types.CallbackQuery, state: FSMContext):
    await send_admin_settings(callback_query, state)

@router.callback_query(State_menu.admin_menu)
async def admin_menu_3(callback_query: types.CallbackQuery, state: FSMContext):
    callback = callback_query.data
    if callback == "Edit Database":
        await database_chatid_columns(callback_query, state, conn, DATABASE_URL)



    elif callback == "Refresh Form":
        await callback_query.message.edit_text("Please Wait...", reply_markup=InlineKeyboardMarkup(inline_keyboard=[]))
        ls = await import_form(script_id)
        await asyncio.gather([storage.set_data_global(key = 'sf_showing', data = ls[0]),
        storage.set_data_global(key = 'sf_title', data = ls[1])
        , storage.set_data_global(key = 'sf_type', data = ls[2])
        ,storage.set_data_global(key = 'sf_entry', data = ls[3])
        ,storage.set_data_global(key = 'sf_choice', data = ls[4])])
        inline_keyboard = await build_inline_keyboard(["<< Back <<"])
        await callback_query.message.edit_text('Refreshed Service Feedback!', reply_markup=inline_keyboard)
        await state.set_state(State_menu.admin_menu2)

    elif callback == "Add Admin":
        result = await get_one_column_from_table(conn=conn, table_name="chat_details", condition="chatid, name", database_url=DATABASE_URL)
        ls = []
        string = ""
        for x in result:
            string += x[0] + '   ' + x[1] + '\n'
            ls.append(x[0])
        ls.append("<< Back <<")
        inline_keyboard = await build_inline_keyboard(ls)
        await callback_query.message.edit_text(string)
        await callback_query.message.answer("Choose id to be Admin", reply_markup=inline_keyboard)
        await state.set_state(State_menu.add_admin)

@router.callback_query(State_menu.add_admin)
async def adding_admin(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == "<< Back <<":
        await send_admin_settings(callback_query, state)
    
    else:
        result = await check_id_in_table(conn=conn, table_name = "admin", parameter=(str(callback_query.data)), database_url=DATABASE_URL)
        if result == False:
            await add_into_table(conn=conn, table_name  = "admin", dict= {"chatid":str(callback_query.data)}, database_url=DATABASE_URL)
            inline_keyboard = await build_inline_keyboard(["<< Back <<"])
            await callback_query.message.edit_text(("Done! {} added!").format(callback_query.data), reply_markup=inline_keyboard)
            await state.set_state(State_menu.admin_menu2)
        elif result == True:
            await delete_from_table(conn=conn, table_name="admin", condition="chatid",parameter=str(callback_query.data),database_url=DATABASE_URL)
            inline_keyboard = await build_inline_keyboard(["<< Back <<"])
            await callback_query.message.edit_text(("Done! {} deleted!").format(callback_query.data), reply_markup=inline_keyboard)
            await state.set_state(State_menu.admin_menu2)


#database_admin
@router.callback_query(State_menu.database_columns)
async def chooosing_database_chatid(callback_query: types.CallbackQuery, state: FSMContext):
    callback = callback_query.data
    if callback == "<< Back <<":
        await send_admin_settings(callback_query, state)
    else:
        data = {}
        data["column"] = callback
        await database_chatid_id(callback_query, state, data, DATABASE_URL)
        
@router.callback_query(State_menu.database_key)
async def editing_column(callback_query: types.CallbackQuery, state: FSMContext):
    callback = callback_query.data
    if callback == "<< Back <<":
        await database_chatid_columns(callback_query, state, conn, DATABASE_URL)

    else:
        data = await state.get_data()
        data["key"] = callback
        await callback_query.message.edit_text("Type the new value ", reply_markup=InlineKeyboardMarkup(inline_keyboard=[]))
        await state.set_state(State_menu.database_write)
        await state.set_data(data)

@router.message(State_menu.database_write)
async def write_database(message: types.Message, state: FSMContext):
    if message.text == "Back":
        data = await state.get_data()
        await database_chatid_id(message, state, data, DATABASE_URL)
    
    else:
        data = await state.get_data()
        if data["column"] == "chatid" and message.text == "DELETE ALL":
            await delete_from_table(conn=conn, table_name="chat_details", condition="chatid", parameter=data["key"], database_url=DATABASE_URL)
            await delete_from_table(conn=conn, table_name="wishes_reminder", condition="chatid", parameter=data["key"], database_url=DATABASE_URL)
        else:
            await update_in_table(conn=conn, table_name="chat_details", condition="chatid", parameter=data["key"], dict={data["column"]:message.text}, database_url=DATABASE_URL)
        inline_keyboard = await build_inline_keyboard(['<< Back <<'])
        await message.answer("Change made!", reply_markup=inline_keyboard)

@router.callback_query(State_menu.database_write)
async def back_write_database(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == "<< Back <<":
        data = await state.get_data()
        await database_chatid_id(callback_query, state, data, DATABASE_URL)


#others
'''
@router.message()
async def echo(message: types.Message, state: FSMContext):

    prompt = "Respond to " + "'" + message.text + "'" + " in a uwu tone"
    await SendChatAction(chat_id = message.chat.id, action="typing")
    response = openai.Completion.create(model="text-davinci-003", prompt=prompt, max_tokens = 2048, temperature=0.5)
    await message.answer(response["choices"][0]["text"])
'''
@router.message()
async def echo(message: types.Message, state: FSMContext):
    await echo_back(message, state)

async def echo_back(message, state):
    if "thank" in message.text.lower() or "ty" in message.text.lower():
        ls = ["CAACAgIAAxkBAAEdByBj5iobeaCQqZR8HQYWE_jO9Lf4LAAC0xMAAujW4hKlgAmiWhe0yS4E","CAACAgIAAxkBAAEdByJj5iodPGIUib_kfCQ_qkBKmWF3XgACzBMAAujW4hJDLteTQiPHXS4E","CAACAgIAAxkBAAEdBx5j5ioH17Ws2kllZBrmHSuNrkfnPAAC2RMAAujW4hJ7hcSWXXkbSC4E","CAACAgIAAxkBAAEdBxRj5imVdkGOp97cjF-lCiE1wB1HwwACNxMAAujW4hJwl6j8RxqETi4E","CAACAgIAAxkBAAEdBn1j5hzoBavZw8RNLVD7vaGnq8nPYwACzxMAAujW4hJQNc1MYX6kQy4E", "CAACAgIAAxkBAAEdBn9j5hzp5udCgMSIBjbCc72hX7tk1wAC0BMAAujW4hLdTZBHdzssey4E"]
        sticker = ls[random.randint(0, len(ls) - 1)]
        await message.answer_sticker(sticker)
    else:
        await message.answer("Oops I forgot what you're doing! Please press /start or use the inline keyboard to send service feedback or wishes!")

async def sf_reminder():
    result = await get_all_from_table(conn, "sf_reminder", DATABASE_URL)
    for x in result:
        if x[1] == "No":
            await bot.send_sticker(chat_id=x[0], sticker="CAACAgIAAxkBAAEdBW1j5gABA3wYp8mBCS-26uhU8EkapE0AAh8TAALo1uISyyJQSCYXIHIuBA")
            await bot.send_message(chat_id=x[0], text="Hi please send service feedback ty!")
        await asyncio.sleep(3)

async def wish_reminder():
    result = await get_all_from_table(conn, "wishes_reminder", DATABASE_URL)
    result1 = await get_all_from_table(conn, "birthdays", DATABASE_URL)
    wish_details = {}
    for w in result1:
        wish_details[w[0]] = w
    for x in result:
        a = json.loads(x[2])
        if a != []:
            await bot.send_sticker(chat_id=x[0], sticker="CAACAgIAAxkBAAEdBW1j5gABA3wYp8mBCS-26uhU8EkapE0AAh8TAALo1uISyyJQSCYXIHIuBA")
            string_text = 'Wishes Reminders~~\n\n'
            for y in a:
                soft_deadline = wish_details[y][2]
                string_text += y + ' - ' + soft_deadline + '\n'
            
            await bot.send_message(chat_id=x[0], text=(string_text + '\nPlease send by the respective deadlines if you have not done so! Thanks!'))
            await asyncio.sleep(3)

async def refresh_sf_reminder():
    ls = await import_form(script_id)
    await asyncio.gather(storage.set_data_global(key = 'sf_showing', data = ls[0]),
    storage.set_data_global(key = 'sf_title', data = ls[1])
    , storage.set_data_global(key = 'sf_type', data = ls[2])
    ,storage.set_data_global(key = 'sf_entry', data = ls[3])
    ,storage.set_data_global(key = 'sf_choice', data = ls[4]))
    await update_all_in_table(conn, table_name="sf_reminder", condition="done", parameter="No", database_url = DATABASE_URL)

async def refresh_connections():
    try:
        await storage.set_data_global(key="check", data="0")
        await add_into_table(conn=conn, table_name="admin", dict={"chatid":"0"}, database_url=DATABASE_URL)
        await bot.me()
        logging.info("All connections working")
    
    except:
        
        date_now = datetime.now() + timedelta(hours=8)
        logging.info("Error some connections are not working as of " + date_now)
        if creator_id != '':
            await bot.send_message(creator_id, "Error some connections are not working as of " + date_now.strftime("%m/%d/%Y, %H:%M:%S"))
        



async def schedule_tasks():
    aioschedule.every().sunday.at("04:00").do(sf_reminder)
    aioschedule.every().sunday.at("07:00").do(sf_reminder)
    aioschedule.every().sunday.at("08:00").do(sf_reminder)
    aioschedule.every().sunday.at("09:00").do(sf_reminder)
    aioschedule.every().friday.at("15:59").do(refresh_sf_reminder)

    aioschedule.every().day.at("17:30").do(renew_wishes_database, script_id = script_id, database_url=DATABASE_URL, redis_url = REDIS_URL)
    aioschedule.every().day.at("02:00").do(wish_reminder)
    aioschedule.every().day.at("12:00").do(wish_reminder)

    aioschedule.every(15).minutes.do(refresh_connections)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


@observer_startup()
async def on_startup():
    asyncio.create_task(schedule_tasks())
    date_now = datetime.now() + timedelta(hours=8)
    logging.info(date_now)

@observer_shutdown()
async def on_shutdown():
    logging.warning('Shutting down..')

    # Close DB connection (if used)
    await dp.storage.close()
    conn.close()
    logging.warning('Bye!')



async def main():
    # Initialize bot and dispatcher
    dp.include_router(router)
    dp.shutdown = observer_shutdown
    dp.startup = observer_startup
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
