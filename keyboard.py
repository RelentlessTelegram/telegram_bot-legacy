from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
async def build_keyboard_sf(string):
    keyboard = []
    temp = []
    count = 0
    choice = string.split('|')
    for x in choice:
        if count != 3:
            temp.append(KeyboardButton(text=x))
            count += 1
        else:
            count = 1
            keyboard.append(temp)
            temp = [KeyboardButton(text=x)]
    keyboard.append(temp)
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard = True, one_time_keyboard = True)


async def build_inline_keyboard(array):
    keyboard = []
    temp = []
    count = 0
    for x in array:
        if count != 2:
            temp.append(InlineKeyboardButton(text=x, callback_data=x))
            count += 1
        else:
            count = 1
            keyboard.append(temp)
            temp = [InlineKeyboardButton(text=x, callback_data=x)]
    if count != 2 or len(temp) == 2:
        keyboard.append(temp)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def main():
    pass

if __name__ == "__main__":
    main()
