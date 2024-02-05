from datetime import datetime
from typing import Dict, Any, List

from aiogram import Router
from aiogram import types
from aiogram.enums import ContentType
from aiogram.filters import Command
from aiogram_dialog import DialogManager, Dialog, Window, StartMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Cancel, Checkbox
from aiogram_dialog.widgets.text import Const, Format

from database import DatabaseRepo, ActivityTypes, Activity
from tgbot.states.set_activity import SetActivityDialogSG


SHOW_ACTIVITIES_BTN_ID = "show_activities_btn"
AVAILABLE_ACTIVITIES_STR = ", ".join(i.name.lower() for i in ActivityTypes)


async def getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    return {
        SHOW_ACTIVITIES_BTN_ID: dialog_manager.find(SHOW_ACTIVITIES_BTN_ID).is_checked(),
        'hours_to_submit_str': ", ".join(
            str(hour)+':00' for hour in dialog_manager.start_data['hours_to_submit']
        ),
    }


async def process_message(message: types.Message, msg_input: MessageInput, manager: DialogManager):
    """ Get message and create activity from data given in user's message """
    hours_to_submit: set[int] = set(manager.start_data['hours_to_submit'])
    activities: List[Activity] = []
    activity_items = message.text.strip().split('\n')
    today = datetime.now()
    try:
        for hour, activity in map(str.split, activity_items):
            hour = int(hour)
            activity = activity.strip()

            if not hasattr(ActivityTypes, activity.upper()):
                await message.reply(
                    f'The activity "{activity}" does not exist.\n'
                    f'Available activities: {AVAILABLE_ACTIVITIES_STR}.\n'
                    f'Try again!"'
                )
                return

            if hour not in hours_to_submit:
                await message.reply(
                    f"You don't need to set activity for {hour} hour. Try again!"
                )
                return

            hours_to_submit.remove(hour)
            activities.append(
                Activity(
                    user_id=message.from_user.id,
                    type=activity.upper(),
                    time=datetime(today.year, today.month, today.day, hour),
                )
            )
    except ValueError:
        await message.reply('You have written your message in wrong format. Try again!')
        return

    if hours_to_submit:
        await message.reply('You have to set activity for all hours. Try again!')
        return

    db: DatabaseRepo = manager.middleware_data['db']
    await db.add_objs(activities)

    await manager.next()


dialog = Dialog(
    Window(
        Const(
            'Now is time to set your activity for last hour(s)! 🕣'
        ),
        Format(
            'You need to write your activity for {hours_to_submit_str} 📝'
        ),
        Const(
            f"\n📌 <b>Available activities:</b> {AVAILABLE_ACTIVITIES_STR}",
            when=SHOW_ACTIVITIES_BTN_ID,
        ),
        Const(
            '\n🗒 Write in message your activities in format:\n'
            '17 work \n'
            '18 study \n'
            '19 sleep \n'
        ),
        MessageInput(process_message, content_types=ContentType.TEXT),
        Checkbox(
            checked_text=Const('Hide available activities 📌'),
            unchecked_text=Const('Show available activities 📌'),
            id=SHOW_ACTIVITIES_BTN_ID,
        ),
        Cancel(
            text=Const('Cancel ❌')
        ),
        getter=getter,
        state=SetActivityDialogSG.start,
    ),
    Window(
        Const('New activities saved!'),
        state=SetActivityDialogSG.finish,
    ),
)


router = Router()
router.include_router(dialog)


@router.message(Command('set_activities'))
async def set_activities(message: types.Message, db: DatabaseRepo, dialog_manager: DialogManager):
    today = datetime.now()
    last_activity = await db.users.get_last_activity(message.from_user.id)
    first_hour_to_set = last_activity.time.hour + 1 if last_activity and last_activity.time.day == today.day else 0
    hours_to_submit = [hour for hour in range(first_hour_to_set, today.hour)]

    if hours_to_submit:
        await dialog_manager.start(
            SetActivityDialogSG.start,
            mode=StartMode.RESET_STACK,
            data={
                'hours_to_submit': hours_to_submit,
            }
        )
    else:
        await message.reply('⚠️ There are no hours to set activity.')
