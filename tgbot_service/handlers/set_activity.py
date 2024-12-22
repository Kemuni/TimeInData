from datetime import datetime
from typing import Dict, Any, List, Tuple

from aiogram import Router
from aiogram import types
from aiogram.enums import ContentType
from aiogram.filters import Command
from aiogram_dialog import DialogManager, Dialog, Window, StartMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Cancel, Checkbox
from aiogram_dialog.widgets.text import Const, Format

from APIParser import APIParser, ActivityBaseIn, ActivityTypes
from states.set_activity import SetActivityDialogSG


class ActivityFormatError(Exception):
    pass


SHOW_ACTIVITIES_BTN_ID = "show_activities_btn"
AVAILABLE_ACTIVITIES_STR = ", ".join(i.name.lower() for i in ActivityTypes)


async def getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    return {
        SHOW_ACTIVITIES_BTN_ID: dialog_manager.find(SHOW_ACTIVITIES_BTN_ID).is_checked(),
        'hours_to_submit_str': ", ".join(
            str(hour) + ':00' for hour in dialog_manager.start_data['hours_to_submit']
        ),
    }


def parse_hours_range(hour_str: str) -> range:
    """
    Parse hours range from text format.
    For example: hour_str="12-15" -> return range(12, 16); hour_str="12" -> return range(12, 13);
    :param hour_str: String format of hour. Example: "12-15" or "12".
    :return: Range of hours.
    """
    if '-' in hour_str:
        if hour_str.count('-') > 1:
            raise ActivityFormatError(
                '⚠️ Wrong hours format. Too many "-". Try again!'
            )
        from_hour, to_hour = list(map(int, hour_str.split('-')))
        if from_hour >= to_hour or to_hour >= 24:
            raise ActivityFormatError(
                f'⚠️ Wrong hours format. Period {from_hour}-{to_hour} is invalid. Try again!'
            )
        return range(from_hour, to_hour + 1)

    hour = int(hour_str)
    if hour >= 24:
        raise ActivityFormatError(
            f'⚠️ Hour cannot be more than 23. Try again!'
        )
    return range(hour, hour + 1)


def parse_activity_from_string(activity_row: str, hours_to_submit: set[int], user_id: int) \
        -> Tuple[List[ActivityBaseIn], set[int]]:
    """
    Parse activity from hour and activity string format. Return list of activities objects and new list of hours to
    submit.

    :param activity_row: String in format like "<time> <activity_type>" or "<from_time>-<to_time> <activity_type>",
    :param hours_to_submit: Hours, that user have to submit with activity.
    :param user_id: Telegram user ID.
    :return: Return list of activities objects and new list of hours to submit.
    """
    # Validate and parse data from text given
    try:
        hour_str: str
        activity: str
        hour_str, activity = activity_row.split()
    except ValueError:
        raise ActivityFormatError('⚠️ You have written your message in wrong format. Try again!')

    activity: str = activity.strip()
    if not hasattr(ActivityTypes, activity.upper()):
        raise ActivityFormatError(
            f'⚠️ The activity "{activity}" does not exist.\n'
            f'Available activities: {AVAILABLE_ACTIVITIES_STR}.\n'
            f'Try again!"'
        )

    # Create new activities objects and last hour validation
    today = datetime.now()
    activities = []
    for hour in parse_hours_range(hour_str):
        if hour not in hours_to_submit:
            raise ActivityFormatError(
                f"⚠️ You don't need to set activity for {hour} hour. Try again!"
            )

        hours_to_submit.remove(hour)
        activities.append(
            ActivityBaseIn(
                type=ActivityTypes[activity.upper()].value,
                time=datetime(today.year, today.month, today.day, hour).strftime(APIParser.DATETIME_FORMAT),
            )
        )

    return activities, hours_to_submit


async def process_message(message: types.Message, msg_input: MessageInput, manager: DialogManager):
    """ Get message and create activity from data given in user's message """
    hours_to_submit: set[int] = set(manager.start_data['hours_to_submit'])
    activities: List[ActivityBaseIn] = []
    activity_items = message.text.strip().split('\n')
    try:
        for activity_row in activity_items:
            new_activities, hours_to_submit = parse_activity_from_string(activity_row, hours_to_submit,
                                                                         message.from_user.id)
            activities.extend(new_activities)
    except ActivityFormatError as e:
        await message.reply(str(e))
        return

    if hours_to_submit:
        await message.reply('⚠️ You have to set activity for all hours. Try again!')
        return

    api: APIParser = manager.middleware_data['api']
    await api.add_user_activities(message.from_user.id, activities)

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
            '0-9 sleep \n'
            '10-15 work \n'
            '16 passive \n'
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

router = Router(name=__name__)
router.include_router(dialog)


@router.message(Command('set_activity'))
async def set_activities(message: types.Message, api: APIParser, dialog_manager: DialogManager):
    today = datetime.now()
    last_activity = await api.get_user_last_activity(message.from_user.id)
    last_activity_time = datetime.strptime(last_activity.time, APIParser.DATETIME_FORMAT)
    first_hour_to_set = last_activity_time.hour + 1 if last_activity and last_activity_time.day == today.day else 0
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
        await message.reply('⚠️ Currently, there are no hours to set activity.')
