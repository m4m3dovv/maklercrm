from aiogram.fsm.state import State, StatesGroup

class AddPropertyStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_district = State()
    waiting_for_address = State()
    waiting_for_room_count = State()
    waiting_for_area = State()
    waiting_for_price = State()
    waiting_for_photo = State()
    confirm = State()
