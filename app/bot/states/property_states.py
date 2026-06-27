from aiogram.fsm.state import State, StatesGroup

class AddPropertyStates(StatesGroup):
    waiting_for_deal_type = State()      # Satılır yoxsa Kirayə
    waiting_for_property_type = State()  # Bina, Həyət, Torpaq...
    waiting_for_title = State()
    waiting_for_district = State()
    waiting_for_address = State()
    waiting_for_room_count = State()
    waiting_for_floor = State()
    waiting_for_total_floors = State()
    waiting_for_area = State()
    waiting_for_document_type = State()
    waiting_for_owner_phone = State()
    waiting_for_price = State()
    waiting_for_photos = State()         # ŞƏKİLLƏR YIĞIMI ÜÇÜN
    confirm = State()
