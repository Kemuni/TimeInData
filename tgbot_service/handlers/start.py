from typing import Dict, Any

from aiogram import Router, F
from aiogram import types
from aiogram.filters import Command
from aiogram_dialog import DialogManager, Dialog, Window, StartMode
from aiogram_dialog.widgets.kbd import Start, Column, Back, Cancel
from aiogram_dialog.widgets.text import Const, Format

from states.set_activity import SetActivityDialogSG
from states.settings import SetNotifyHoursSG, SettingsDialogSG
from states.start import StartDialogSG

TO_BOT_DESCRIPTION_BTN_ID = 'to_bot_description_btn_id'
TO_USER_SETTINGS_BTN_ID = 'to_user_settings_btn_id'

TO_SETTINGS_BTN_ID = 'to_settings_btn_id'
TO_SET_ACTIVITIES_BTN_ID = 'to_set_activities_btn_id'
EXIT_BTN_ID = 'exit_btn_id'


async def getter(event_from_user: types.User, **_) -> Dict[str, Any]:
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
            Const('Tell me more!'), id=TO_BOT_DESCRIPTION_BTN_ID, state=StartDialogSG.description,
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
                id=TO_USER_SETTINGS_BTN_ID,
                state=SetNotifyHoursSG.set_time,
                mode=StartMode.RESET_STACK,
            ),
        ),
        state=StartDialogSG.description,
    ),
    Window(
        Format(
            "Hello, {full_name}! 👋\n"
        ),
        Const(
            "I am here to help you with time management 🕣 \n\n"
            "Tap on the button below! 👇"
        ),
        Column(
            Start(
                Const("Settings ⚙️"),
                id=TO_SETTINGS_BTN_ID,
                state=SettingsDialogSG.main_menu,
            ),
            Start(
                Const("Set activity 🚩"),
                id=TO_SET_ACTIVITIES_BTN_ID,
                state=SetActivityDialogSG.start,
            ),
            Cancel(
                Const("Exit"),
                id=EXIT_BTN_ID,
            ),
        ),
        getter=getter,
        state=StartDialogSG.menu,
    ),
)


router = Router(name=__name__)
dialog.message.filter(~F.text.startswith('/'))
router.include_router(dialog)


@router.message(Command(commands=['start', 'menu']))
async def start(_, dialog_manager: DialogManager, is_new_user: bool):
    if is_new_user:
        await dialog_manager.start(StartDialogSG.greeting, mode=StartMode.RESET_STACK)
    else:
        await dialog_manager.start(StartDialogSG.menu, mode=StartMode.RESET_STACK)
