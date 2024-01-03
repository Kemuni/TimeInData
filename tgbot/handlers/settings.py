import operator
from typing import Dict, Any

from aiogram import Router
from aiogram import types
from aiogram.filters import Command
from aiogram_dialog import DialogManager, Dialog, Window
from aiogram_dialog.widgets.kbd import Checkbox, Multiselect, Group, Row, Cancel, Button
from aiogram_dialog.widgets.text import Const, Format
from loguru import logger

from tgbot.states.settings import SettingsDialogSG

NEED_EXAMPLE_BTN_ID: str = "need_example"
HOURS_SELECTED_BTN_ID: str = "hours_select"


async def getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
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


async def save_settings(callback: types.CallbackQuery, button: Button, manager: DialogManager):
    if manager.is_preview():
        await manager.done()
        return

    selected_hours: list[int] = list(map(int, manager.find(HOURS_SELECTED_BTN_ID).get_checked()))
    selected_hours.sort()
    selected_hours_str = ', '.join(f"{i:02d}:00" for i in selected_hours)

    logger.info(f'User (tg_id={callback.from_user.id}) change settings hours to {selected_hours_str}')
    await callback.message.edit_text(
        f"The hours have been saved! 💾\n"
        f"I will send you notification in: {selected_hours_str}"
    )

    await manager.done()


dialog = Dialog(
    Window(
        Const(
            "Firstly let's configure time for notification 🕣\n"
            "Please, tap the buttons with comfortable to you time below! 👇\n"
            "❗ Remember, that you will set activities for hours before selected."
        ),
        Const(
            "\n<i>For example, if you have notification in 7 am and 10 am, in 10 am "
            "you will set activities for time from 7 am to 9 am.</i>",
            when=NEED_EXAMPLE_BTN_ID,
        ),
        Checkbox(
            checked_text=Const('Hide example'),
            unchecked_text=Const('Show example'),
            id=NEED_EXAMPLE_BTN_ID,
        ),
        Group(
            Multiselect(
                checked_text=Format('✓ {item[0]}'),
                unchecked_text=Format('{item[0]}'),
                id=HOURS_SELECTED_BTN_ID,
                item_id_getter=operator.itemgetter(1),
                items='hours',
            ),
            width=4,
        ),
        Row(
            Cancel(
                text=Const('Cancel ❌')
            ),
            Button(
                text=Const('Save 💾'),
                id="save_settings",
                on_click=save_settings,
                when='hours_selected',
            ),
        ),
        getter=getter,
        state=SettingsDialogSG.time,
    ),
)


router = Router()
router.include_router(dialog)


@router.message(Command('settings'))
async def settings(message: types.Message, dialog_manager: DialogManager):
    await dialog_manager.start(SettingsDialogSG.time)
