from aiogram.fsm.state import State, StatesGroup

class AddPropertyStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_district = State()
    waiting_for_address = State()
    waiting_for_room_count = State()
    waiting_for_floor = State()          # Yeni
    waiting_for_total_floors = State()   # Yeni
    waiting_for_area = State()
    waiting_for_document_type = State()  # Yeni
    waiting_for_owner_phone = State()    # Yeni
    waiting_for_price = State()
    waiting_for_photo = State()          # Yeni (Şəkillər qəbul etmək üçün)
    confirm = State()
