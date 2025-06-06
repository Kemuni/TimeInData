import operator
from typing import Dict, Any, List

from aiogram import types
from aiogram_dialog import DialogManager, Dialog, Window, ShowMode
from aiogram_dialog.widgets.kbd import Checkbox, Multiselect, Group, Row, Cancel, Button, ManagedMultiselect
from aiogram_dialog.widgets.text import Const, Format
from loguru import logger

from APIParser import APIParser
from states.settings import SetNotifyHoursSG

NEED_EXAMPLE_BTN_ID: str = "need_example"
HOURS_SELECTED_BTN_ID: str = "hours_select"


async def getter(dialog_manager: DialogManager, **_) -> Dict[str, Any]:
    return {
        NEED_EXAMPLE_BTN_ID: dialog_manager.find(NEED_EXAMPLE_BTN_ID).is_checked(),
        'hours': (
            ['00:00', 0], ['01:00', 1], ['02:00', 2], ['03:00', 3],
            ['04:00', 4], ['05:00', 5], ['06:00', 6], ['07:00', 7],
            ['08:00', 8], ['09:00', 9], ['10:00', 10], ['11:00', 11],
            ['12:00', 12], ['13:00', 13], ['14:00', 14], ['15:00', 15],
            ['16:00', 16], ['17:00', 17], ['18:00', 18], ['19:00', 19],
            ['20:00', 20], ['21:00', 21], ['22:00', 22], ['23:00', 23]
        ),
        'hours_selected': dialog_manager.find(HOURS_SELECTED_BTN_ID).get_checked(),
    }


async def set_every_notify_hour(_, __, manager: DialogManager):
    """ Set every hour from Multiselect widget """
    multi = manager.find(HOURS_SELECTED_BTN_ID)
    for hour in range(24):
        await multi.set_checked(hour, True)


async def clear_notify_hours(_, __, manager: DialogManager):
    """ Clear every hour from Multiselect widget """
    multi: ManagedMultiselect = manager.find(HOURS_SELECTED_BTN_ID)
    await multi.reset_checked()


async def save_notify_hours(callback: types.CallbackQuery, _, manager: DialogManager):
    """ Save new user notify hours in the database and end dialog manager """
    if manager.is_preview():
        await manager.done(show_mode=ShowMode.SEND)
        return

    selected_hours: List[int] = manager.find(HOURS_SELECTED_BTN_ID).get_checked()
    selected_hours.sort()
    selected_hours_str = ', '.join(f"{i:02d}:00" for i in selected_hours)

    api: APIParser = manager.middleware_data['api']
    await api.update_user_notify_hours(user_id=callback.from_user.id, notify_hours=selected_hours)

    logger.info(f'User (tg_id={callback.from_user.id}) change notify hours to {selected_hours_str}')
    await callback.message.edit_text(
        f"The hours have been saved! 💾\n"
        f"I will send you notification in: {selected_hours_str}"
    )

    await manager.done(show_mode=ShowMode.SEND)


async def on_start(_, manager: DialogManager):
    """ Set last saved user data for dialog from database """
    multi = manager.find(HOURS_SELECTED_BTN_ID)
    api: APIParser = manager.middleware_data['api']
    user_notify_hours = await api.get_user_notify_hours(manager.event.from_user.id)
    if user_notify_hours:
        for hour in user_notify_hours:
            await multi.set_checked(hour, True)


dialog = Dialog(
    Window(
        Const(
            "Let's configure time for notification 🕣\n"
            "Please, tap the buttons with comfortable to you time below! 👇\n"
            "❗ Remember, that you will set activities for hours before selected."
        ),
        Const(
            "\n<i>For example, if you have notification in 7 am and 10 am, in 10 am "
            "you will set activities for time from 7 am to 9 am.</i>",
            when=NEED_EXAMPLE_BTN_ID,
        ),
        Checkbox(
            checked_text=Const('Hide example 🗒'),
            unchecked_text=Const('Show example 🗒'),
            id=NEED_EXAMPLE_BTN_ID,
        ),
        Group(
            Multiselect(
                checked_text=Format('✓ {item[0]}'),
                unchecked_text=Format('{item[0]}'),
                id=HOURS_SELECTED_BTN_ID,
                type_factory=int,
                item_id_getter=operator.itemgetter(1),
                items='hours',
            ),
            width=4,
        ),
        Row(
            Button(
                text=Const('Set every hour'),
                id="set_every_notify_hour",
                on_click=set_every_notify_hour,
            ),
            Button(
                text=Const('Clear hours 🗑️'),
                id="clear_notify_hour",
                on_click=clear_notify_hours,
            ),
        ),
        Row(
            Cancel(
                text=Const('Cancel ❌')
            ),
            Button(
                text=Const('Save 💾'),
                id="save_settings",
                on_click=save_notify_hours,
                when='hours_selected',
            ),
        ),
        getter=getter,
        state=SetNotifyHoursSG.set_time,
    ),
    on_start=on_start,
)
