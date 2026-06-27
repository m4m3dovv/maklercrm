from aiogram.fsm.state import State, StatesGroup

class AddCustomerStates(StatesGroup):
    waiting_for_fullname = State()
    waiting_for_phone = State()
    waiting_for_budget = State()
    waiting_for_district = State()
    confirm = State()
