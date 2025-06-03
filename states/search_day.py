from aiogram.fsm.state import StatesGroup, State

class SearchDay(StatesGroup):
    waiting_for_date = State()
