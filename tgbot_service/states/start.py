from aiogram.fsm.state import StatesGroup, State


class StartDialogSG(StatesGroup):
    greeting = State()
    description = State()
    menu = State()
