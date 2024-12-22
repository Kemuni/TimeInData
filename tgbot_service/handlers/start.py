from typing import Dict, Any

from aiogram import Router
from aiogram import types
from aiogram.filters import CommandStart
from aiogram_dialog import DialogManager, Dialog, Window, StartMode
from aiogram_dialog.widgets.kbd import Start, Column, Back
from aiogram_dialog.widgets.text import Const, Format

from states.settings import SettingsDialogSG
from states.start import StartDialogSG


async def getter(event_from_user: types.User, **kwargs) -> Dict[str, Any]:
    return {
        "full_name": event_from_user.full_name,
    }


dialog = Dialog(
    Window(
        Format(
            "Hello, {full_name}! 👋\n"
        ),
        Const(
            "I am a bot that will help you with time management. "
            "I'll show to you how much time takes your activities 🕣\n"
            "If you want to know more about it, tap on the button at the bottom! 👇"
        ),
        Start(
            Const('Tell me more!'), id="to_bot_description", state=StartDialogSG.description,
        ),
        getter=getter,
        state=StartDialogSG.greeting,
    ),
    Window(
        Const(
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
        ),
        Column(
            Back(Const("⬅️ Back")),
            Start(
                Const("Let's try it! 🚩"),
                id="to_user_settings",
                state=SettingsDialogSG.time,
                mode=StartMode.RESET_STACK,
            ),
        ),
        state=StartDialogSG.description,
    ),
)


router = Router()
router.include_router(dialog)


@router.message(CommandStart())
async def start(message: types.Message, dialog_manager: DialogManager):
    # it is important to reset stack because user wants to restart everything
    await dialog_manager.start(StartDialogSG.greeting, mode=StartMode.RESET_STACK)
