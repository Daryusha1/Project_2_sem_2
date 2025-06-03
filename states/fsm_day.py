from aiogram.fsm.state import StatesGroup, State

class DayEntry(StatesGroup):
    color = State()
    smell = State()
    word = State()
    photo = State()
    music = State()
