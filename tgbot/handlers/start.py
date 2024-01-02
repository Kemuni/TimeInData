from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram import types

from tgbot.keyboards.start_inline import get_bot_description_kb, get_user_first_try_kb

router = Router()


@router.message(CommandStart())
async def user_start(message: types.Message):
    await message.reply(
        f"Hello, {message.from_user.full_name}! 👋\n"
        f"I am a bot that will help you with time management. "
        f"I'll show to you how much time takes your activities 🕣\n"
        f"If you want to know more about it, tap on the button at the bottom! 👇",
        reply_markup=get_bot_description_kb(),
    )


@router.callback_query(F.data == 'bot_description')
async def bot_description(callback: types.CallbackQuery):
    await callback.message.answer(
        "My main task is collection your activity every specific time period. "
        "There are <b>8 type</b> of activities:\n"
        "1. Sleep 😴\n"
        "2. Work 💰\n"
        "3. Studying 👨‍🏫\n"
        "4. Family 👪\n"
        "5. Friends 🤝\n"
        "6. Passive 😐\n"
        "7. Exercise 🏋️\n"
        "8. Reading 📖\n"
        "\n"
        "And after some time I will show you in diagrams and graphs how many time do you spend for each activity. 📈\n"
        "This can be helpful for you to plan your time more accurately!"
    )
    await callback.message.answer(
        'Do you want to try this?',
        reply_markup=get_user_first_try_kb()
    )
    await callback.answer()

@router.callback_query(F.data == 'user_first_try')
async def user_first_try(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Good choice! 👍\n"
        "Let's start from settings ⚙️"
    )
    # Here will be starting state to get base data
    await callback.answer()
