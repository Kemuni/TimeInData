from typing import Dict, Any, Iterable

from aiogram import Router, F
from aiogram import types
from aiogram.enums import ContentType
from aiogram.filters import Command
from aiogram_dialog import DialogManager, Dialog, Window, StartMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Cancel, Checkbox
from aiogram_dialog.widgets.text import Const, Format
from loguru import logger

from app.api_parser import APIParser
from app.exceptions import ActivitySlotsAdapterException
from app.exceptions import (
    NotFoundActivitySlotException,
    ActivitySlotAlreadyHasActivityException,
    ActivitySlotsControllerInitException
)
from app.states.set_activity import SetActivityDialogSG
from app.types import ActivityBaseIn, ActivityTypes
from app.utils.activity_slots_controller import ActivitySlotsController
from app.utils.slots_controller_adapter import ActivitySlotsToAiogramDialogAdapter


class ActivityFormatError(Exception):
    pass


SHOW_ACTIVITIES_BTN_ID = "show_activities_btn"
AVAILABLE_ACTIVITIES_STR = ", ".join(i.name.lower() for i in ActivityTypes)


async def getter(dialog_manager: DialogManager, **_) -> Dict[str, Any]:
    try:
        slots_controller = ActivitySlotsToAiogramDialogAdapter.get_controller_from_dialog_data(dialog_manager)
    except ActivitySlotsAdapterException as exc:
        logger.error(f"Failed to get activity slots controller from dialog data. Error: {exc}")
        await dialog_manager.done()
        return {}

    missing_slots_str = ""
    for filtered_slots in slots_controller.get_slots_filtered_by_date():
        activities_str_hours = (f'{slot.local_hour:02d}:00' for slot in filtered_slots.activity_slots)
        missing_slots_str += f"<b>{filtered_slots.local_date.strftime("%d %B")}</b>: {', '.join(activities_str_hours)}\n"
    return {
        SHOW_ACTIVITIES_BTN_ID: dialog_manager.find(SHOW_ACTIVITIES_BTN_ID).is_checked(),
        'missing_slots_str': missing_slots_str,
    }


def parse_hours_range(hour_str: str) -> Iterable[int]:
    """
    Parse hours range from text format.
    For example: hour_str="12-14" -> return [12, 13, 14]; "12" -> return [12]; "23-3" -> return [23, 00, 01, 02, 03];
    :param hour_str: String format of hour. Example: "12-15" or "12".
    :return: Iterable[int] of hours.
    """
    if '-' not in hour_str:
        try:
            hour = int(hour_str)
        except ValueError:
            raise ActivityFormatError(
                f'⚠️ "{hour_str}" must be a number from 0 to 23. Try again!'
            )
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
        to_hour += 24
    return ((from_hour + i) % 24 for i in range(to_hour - from_hour + 1)) # "13-16" = [13, 14, 15]


def parse_activity_from_string(activity_data_str: str, slots_controller: ActivitySlotsController) -> None:
    """
    Parse activity from hour and activity string format. Add activity to slots controller.

    :param activity_data_str: String in format like "<time> <activity_type>" or "<from_time>-<to_time> <activity_type>",
    :param slots_controller: ActivitySlotsController instance.
    """
    # Validate and parse data from text given
    try:
        hour_str, activity_str = activity_data_str.split()
    except ValueError:
        raise ActivityFormatError('⚠️ You have written your message in wrong format. Try again!')

    try:
        activity = ActivityTypes(activity_str.strip().upper())
    except ValueError:
        raise ActivityFormatError(
            f'⚠️ The activity "{activity_str}" does not exist.\n'
            f'Available activities: {AVAILABLE_ACTIVITIES_STR}.\n'
            f'Try again!"'
        )

    # Add new activities objects
    for hour in parse_hours_range(hour_str):
        try:
            slots_controller.add_activity_slot(hour, activity)
        except NotFoundActivitySlotException:
            raise ActivityFormatError(
                f"⚠️ You don't need to set activity for {hour:02d}:00 hour. Try again!"
            )
        except ActivitySlotAlreadyHasActivityException:
            raise ActivityFormatError(
                f"⚠️ You have already set activity for {hour} hour. Try again!"
            )


async def process_message(message: types.Message, _, manager: DialogManager) -> None:
    """ Get message and create activity from data given in user's message """
    # Validating the user message and converting it into a list of activities
    try:
        slots_controller = ActivitySlotsToAiogramDialogAdapter.get_controller_from_dialog_data(manager)
    except ActivitySlotsAdapterException as exc:
        logger.error(f"Failed to get activity slots controller from dialog data. Error: {exc}")
        await manager.done()
        return

    activity_items = message.text.strip().split('\n')
    try:
        for activity_row in activity_items:
            parse_activity_from_string(activity_row, slots_controller)
    except ActivityFormatError as e:
        await message.reply(str(e))
        return

    if not slots_controller.has_all_slots_filled():
        await message.reply('⚠️ You have to set activity for ALL specified hours. Try again!')
        return

    # Sending user's activities to our API service
    api: APIParser = manager.middleware_data['api']
    activities_for_api = [
        ActivityBaseIn(utc_date=slot.utc_date, utc_hour=slot.utc_hour, type=str(slot.activity_type.value))
        for slot in slots_controller.get_all_slots()
    ]
    await api.add_user_activities(message.from_user.id, activities_for_api)

    await message.reply('New activities saved! 🎉')
    await manager.done()


async def on_start(_, manager: DialogManager) -> None:
    """ Get start data for the dialog """
    api = manager.middleware_data['api']
    tz_delta = await api.get_user_time_zone_delta(manager.event.from_user.id)
    api_missing_slots_data = await api.get_closest_activity_missing_slots(manager.event.from_user.id)

    # Provide date to dialog about missing activity slots
    if not api_missing_slots_data.has_missing_slots or api_missing_slots_data.missing_slots is None:
        if isinstance(manager.event, types.CallbackQuery):
            msg = manager.event.message
        else:
            msg = manager.event
        await msg.answer('⚠️ Currently, there are no hours to set activity.')
        await manager.done()
        return

    try:
        slots_controller = ActivitySlotsController(api_missing_slots_data.missing_slots, tz_delta)
    except ActivitySlotsControllerInitException as exc:
        logger.error(f'Error on ActivitySlotsController initialization: {exc}')
        await manager.done()
        return

    try:
        ActivitySlotsToAiogramDialogAdapter.add_controller_to_dialog_data(slots_controller, dialog_manager=manager)
    except ActivitySlotsAdapterException as exc:
        logger.error(f"Failed to add activity slots controller to dialog_data. Error: {exc}")
        await manager.done()
        return


dialog = Dialog(
    Window(
        Const(
            'Now is time to set your activity for last hour(s)! 🕣'
        ),
        Format(
            '📝 You need to write your activity for next hour-slots: \n{missing_slots_str}'
        ),
        Const(
            f"\n📌 <b>Available activities:</b> {AVAILABLE_ACTIVITIES_STR}",
            when=SHOW_ACTIVITIES_BTN_ID,
        ),
        Const(
            '\n🗒 Write in message your activities in format <i>(only hours range, date is redundant)</i>:\n'
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
    on_start=on_start,
)

router = Router(name=__name__)
router.message.filter(~F.is_new_user)
router.callback_query.filter(~F.is_new_user)
router.include_router(dialog)


@router.message(Command('set_activity', 'set_activities'))
async def set_activity(_, dialog_manager: DialogManager):
    await dialog_manager.start(
        SetActivityDialogSG.start,
        mode=StartMode.RESET_STACK,
    )
