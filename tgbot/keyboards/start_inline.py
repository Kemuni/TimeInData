from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_bot_description_kb():
    """ Return keyboard markup with one button to get bot description """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Tell me more!', callback_data='bot_description'),
            ]
        ]
    )


def get_user_first_try_kb():
    """ Return keyboard markup with one button to go the settings for the first time """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Let's try it!", callback_data='user_first_try'),
            ]
        ]
    )
