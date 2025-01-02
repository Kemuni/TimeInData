from aiogram.fsm.state import StatesGroup, State


class SettingsDialogSG(StatesGroup):
    main_menu = State()


class SetTimeZoneSG(StatesGroup):
    set_tz = State()


class SetNotifyHoursSG(StatesGroup):
    set_time = State()
