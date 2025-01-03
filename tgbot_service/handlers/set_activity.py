from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Iterator

from aiogram import Router, F
from aiogram import types
from aiogram.enums import ContentType
from aiogram.filters import Command
from aiogram_dialog import DialogManager, Dialog, Window, StartMode, ShowMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Cancel, Checkbox
from aiogram_dialog.widgets.text import Const, Format

from APIParser import APIParser, ActivityBaseIn, ActivityTypes, Activity
from states.set_activity import SetActivityDialogSG


class ActivityFormatError(Exception):
    pass


SHOW_ACTIVITIES_BTN_ID = "show_activities_btn"
AVAILABLE_ACTIVITIES_STR = ", ".join(i.name.lower() for i in ActivityTypes)


async def getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    return {
        SHOW_ACTIVITIES_BTN_ID: dialog_manager.find(SHOW_ACTIVITIES_BTN_ID).is_checked(),
        'hours_to_submit_str': ", ".join(
            str(hour) + ':00' for hour in dialog_manager.dialog_data['hours_to_submit']
        ),
    }


def parse_hours_range(hour_str: str) -> Union[Iterator[int], range]:
    """
    Parse hours range from text format.
    For example: hour_str="12-15" -> return range(12, 16); "12" -> return [12]; "23-3" -> return [23, 00, 01, 02]
    :param hour_str: String format of hour. Example: "12-15" or "12".
    :return: Range or iterator of hours.
    """
    if '-' not in hour_str:
        hour = int(hour_str)
        if hour >= 24:
            raise ActivityFormatError(
                f'⚠️ Hour cannot be more than 23. Try again!'
            )
        return range(hour, hour + 1)  # "12" = [12]

    if hour_str.count('-') > 1:
        raise ActivityFormatError(
            '⚠️ Wrong hours format. Too many "-". Try again!'
        )

    # Parsing hours range if we have '-' symbol
    from_hour, to_hour = list(map(int, hour_str.split('-')))
    if any(i >= 24 for i in [from_hour, to_hour]) or from_hour == to_hour:
        raise ActivityFormatError(
            f'⚠️ Wrong hours format. Period {from_hour}-{to_hour} is invalid. Try again!'
        )

    if from_hour > to_hour:  # "23-3" = [23, 00, 01, 02]
        return (i % 24 for i in range(from_hour, 24 + to_hour + 1))
    return range(from_hour, to_hour + 1)  # "13-16" = [13, 14, 15]


def parse_activity_from_string(
        activity_row: str, hours_to_submit: set[int], tz_delta: int, start_date: datetime
) -> List[ActivityBaseIn]:
    """
    Parse activity from hour and activity string format. Return list of activities objects and new list of hours to
    submit.

    :param activity_row: String in format like "<time> <activity_type>" or "<from_time>-<to_time> <activity_type>",
    :param hours_to_submit: Hours, that user have to submit with activity.
    :param tz_delta: User's delta of time zone (i.e. UTC+3 = 3, UTC-2 = -2).
    :param start_date: Datetime when user start dialog and our program calculate `hours_to_submit`.
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

    # Create new activities objects
    start_date = datetime(start_date.year, start_date.month, start_date.day, start_date.hour)
    tz_start_date = start_date + timedelta(hours=tz_delta)
    activities: List[ActivityBaseIn] = []
    for hour in parse_hours_range(hour_str):
        if hour not in hours_to_submit:
            raise ActivityFormatError(
                f"⚠️ You don't need to set activity for {hour} hour or you have already set it. Try again!"
            )

        hours_to_submit.remove(hour)
        hours_gap = (24 - hour + tz_start_date.hour) if hour >= tz_start_date.hour else tz_start_date.hour - hour
        activities.append(
            ActivityBaseIn(
                type=ActivityTypes[activity.upper()].value,
                time=(start_date - timedelta(hours=hours_gap)).strftime(APIParser.DATETIME_FORMAT),  # To UTC format
            )
        )

    return activities


async def process_message(message: types.Message, _, manager: DialogManager):
    """ Get message and create activity from data given in user's message """
    # Validating user message and converting it into a list of activities
    hours_to_submit: set[int] = set(manager.dialog_data['hours_to_submit'])
    tz_delta: int = manager.dialog_data['tz_delta']
    start_date: datetime = manager.dialog_data['start_date']

    activities: List[ActivityBaseIn] = []
    activity_items = message.text.strip().split('\n')
    try:
        for activity_row in activity_items:
            new_activities = parse_activity_from_string(activity_row, hours_to_submit, tz_delta, start_date)
            activities.extend(new_activities)
    except ActivityFormatError as e:
        await message.reply(str(e))
        return

    if hours_to_submit:
        await message.reply('⚠️ You have to set activity for all hours. Try again!')
        return

    # Sending user's activities to our API service
    api: APIParser = manager.middleware_data['api']
    await api.add_user_activities(message.from_user.id, activities)

    await manager.next()


def get_hours_to_submit(last_activity: Optional[Activity] = None, to_date: Optional[datetime] = None) -> list[int]:
    """
    Receive last activity object and return list of hours that user can fill via activity.
    :param last_activity: Object of last user's activity.
    :param to_date: Deadline date to check hours without activity.
    :return: List of hours that user can fill via activity.
    """
    today = to_date or datetime.utcnow()
    if last_activity is None:  # If user is new for us - let him fill only today's hour
        return [hour for hour in range(0, today.hour)]

    # Otherwise, let user set activity to all 24 hours gap, including yesterday
    last_activity_time = datetime.strptime(last_activity.time, APIParser.DATETIME_FORMAT)
    if last_activity_time.date() == today.date():
        return [hour for hour in range(last_activity_time.hour + 1, today.hour)]

    if today.date() - last_activity_time.date() <= timedelta(days=1):
        from_hour = last_activity_time.hour + 1
    else:
        from_hour = today.hour

    return [hour % 24 for hour in range(from_hour, 24 + today.hour)]


async def on_start(_, manager: DialogManager) -> None:
    """ Get start data for the dialog """
    api = manager.middleware_data['api']
    tz_delta = await api.get_user_time_zone_delta(manager.event.from_user.id)
    last_activity = await api.get_user_last_activity(manager.event.from_user.id)

    # Provide date to dialog for excepting errors with activity when user start the dialog in time like 17:59
    utc_today = datetime.utcnow()
    hours_to_submit = [(hour + tz_delta) % 24 for hour in get_hours_to_submit(last_activity, to_date=utc_today)]
    if not hours_to_submit:
        if isinstance(manager.event, types.CallbackQuery):
            msg = manager.event.message
        else:
            msg = manager.event
        await msg.answer('⚠️ Currently, there are no hours to set activity.')
        await manager.done()
        return

    manager.dialog_data['hours_to_submit'] = hours_to_submit
    manager.dialog_data['tz_delta'] = tz_delta
    manager.dialog_data['start_date'] = utc_today


dialog = Dialog(
    Window(
        Const(
            'Now is time to set your activity for last hour(s)! 🕣'
        ),
        Format(
            '📝 You need to write your activity for {hours_to_submit_str}'
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
            default=True,
            id=SHOW_ACTIVITIES_BTN_ID,
        ),
        Cancel(
            text=Const('Cancel ❌')
        ),
        getter=getter,
        state=SetActivityDialogSG.start,
    ),
    Window(
        Const('New activities saved! 🎉'),
        state=SetActivityDialogSG.finish,
    ),
    on_start=on_start,
)

router = Router(name=__name__)
router.message.filter(~F.is_new_user)
router.callback_query.filter(~F.is_new_user)
router.include_router(dialog)


@router.message(Command('set_activity'))
async def set_activity(_, dialog_manager: DialogManager):
    await dialog_manager.start(
        SetActivityDialogSG.start,
        mode=StartMode.RESET_STACK,
    )
