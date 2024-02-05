from aiogram.fsm.state import StatesGroup, State


class SetActivityDialogSG(StatesGroup):
    start = State()
    finish = State()
