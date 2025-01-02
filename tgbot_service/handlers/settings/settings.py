from aiogram import Router
from aiogram.filters import Command
from aiogram_dialog import DialogManager, Dialog, Window, StartMode
from aiogram_dialog.widgets.kbd import Row, Cancel, Start, Column
from aiogram_dialog.widgets.text import Const

from states.settings import SettingsDialogSG, SetNotifyHoursSG, SetTimeZoneSG
from . import set_notify_hours_dialog, set_time_zone_dialog

SET_NOTIFY_HOURS_DIALOG_BTN_ID: str = "set_notify_hours_dialog_btn"
SET_TZ_DIALOG_BTN_ID: str = "set_tz_dialog_btn"


dialog = Dialog(
    Window(
        Const(
            "Settings menu! ⚙️\n"
            "Please, tap the buttons below to make some changes! 👇\n"
        ),
        Column(
            Start(
                text=Const('Change time zone 🌎'),
                id=SET_TZ_DIALOG_BTN_ID,
                state=SetTimeZoneSG.set_tz,
            ),
            Start(
                text=Const('Change notify hours 🕣'),
                id=SET_NOTIFY_HOURS_DIALOG_BTN_ID,
                state=SetNotifyHoursSG.set_time,
            ),
            Cancel(
                text=Const('Cancel ❌')
            ),
        ),
        state=SettingsDialogSG.main_menu,
    ),
)


router = Router(name=__name__)
router.include_router(set_notify_hours_dialog.dialog)
router.include_router(set_time_zone_dialog.dialog)
router.include_router(dialog)


@router.message(Command('settings'))
async def settings(_, dialog_manager: DialogManager):
    """ Start settings dialog """
    await dialog_manager.start(SettingsDialogSG.main_menu, mode=StartMode.RESET_STACK)
