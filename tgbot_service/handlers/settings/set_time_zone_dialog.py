from datetime import datetime

from aiogram import types
from aiogram_dialog import DialogManager, Dialog, Window, ShowMode
from aiogram_dialog.widgets.kbd import Row, Cancel, Button, Counter, ManagedCounter
from aiogram_dialog.widgets.text import Const, Format
from loguru import logger

from APIParser import APIParser
from states.settings import SetTimeZoneSG

COUNTER_BTN_ID = "counter_btn_id"
SAVE_NEW_TZ_BTN_ID = "save_new_tz_btn_id"
INCREMENT_3_BTN_ID = 'increment_by_three_btn_id'
DECREMENT_3_BTN_ID = 'decrement_by_three_btn_id'


async def getter(dialog_manager: DialogManager, **_):
    counter_value = dialog_manager.find(COUNTER_BTN_ID).get_value()
    today = datetime.utcnow()
    return {
        "user_time_str": f"{(today.hour + counter_value) % 24}:{today.minute}"
    }


async def increment_three_counter(_, __, manager: DialogManager):
    counter_widget: ManagedCounter = manager.find(COUNTER_BTN_ID)
    await counter_widget.set_value(counter_widget.get_value() + 3)


async def decrement_three_counter(_, __, manager: DialogManager):
    counter_widget: ManagedCounter = manager.find(COUNTER_BTN_ID)
    await counter_widget.set_value(counter_widget.get_value() - 3)


async def save_new_timezone(callback: types.CallbackQuery, _, manager: DialogManager):
    """ Save new user time zone in the database and end dialog manager """
    if manager.is_preview():
        await manager.done(show_mode=ShowMode.SEND)
        return

    counter: ManagedCounter = manager.find(COUNTER_BTN_ID)
    timezone_delta = int(counter.get_value())

    api: APIParser = manager.middleware_data['api']
    await api.update_user_time_zone_delta(user_id=callback.from_user.id, new_tz_delta=timezone_delta)

    logger.info(f'User (tg_id={callback.from_user.id}) change time zone to UTC{timezone_delta:+}')
    today = datetime.utcnow()
    await callback.message.edit_text(
        f"Your time {(today.hour + timezone_delta) % 24}:{today.minute} have been saved! 💾"
    )

    await manager.done(show_mode=ShowMode.SEND)


async def on_start(_, manager: DialogManager):
    """ Set last saved user time zone delta for dialog from database """
    api: APIParser = manager.middleware_data['api']
    tz_delta = await api.get_user_time_zone_delta(manager.event.from_user.id)
    await manager.find(COUNTER_BTN_ID).set_value(tz_delta)


dialog = Dialog(
    Window(
        Const(
            "Let's configure your time zone 🌎\n"
            "Set your currently time that you have by tapping the buttons below! 👇\n"
        ),
        Format(
            "Your current time is <b>{user_time_str}</b>"
        ),
        Counter(
            id=COUNTER_BTN_ID,
            text=Format("UTC{value:+}"),
            default=0,
            min_value=-12,
            max_value=12,
        ),
        Row(
            Button(
                text=Const('-3'),
                id=DECREMENT_3_BTN_ID,
                on_click=decrement_three_counter,
            ),
            Button(
                text=Const('+3'),
                id=INCREMENT_3_BTN_ID,
                on_click=increment_three_counter,
            ),
        ),
        Row(
            Cancel(
                text=Const('Cancel ❌')
            ),
            Button(
                text=Const('Save 💾'),
                id=SAVE_NEW_TZ_BTN_ID,
                on_click=save_new_timezone,
            ),
        ),
        state=SetTimeZoneSG.set_tz,
        getter=getter,
    ),
    on_start=on_start,
)
