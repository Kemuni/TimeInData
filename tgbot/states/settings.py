from aiogram.fsm.state import StatesGroup, State


class SettingsDialogSG(StatesGroup):
    time = State()
