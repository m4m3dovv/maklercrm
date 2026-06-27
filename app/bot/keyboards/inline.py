from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.models.property import PropertyStatus

def property_actions_kb(property_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📝 Redaktə et", callback_data=f"prop_edit_{property_id}")
    builder.button(text="🔄 Statusu dəyiş", callback_data=f"prop_status_{property_id}")
    builder.button(text="🗑 Sil", callback_data=f"prop_del_{property_id}")
    builder.adjust(2, 1)
    return builder.as_markup()

def property_status_kb(property_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🟢 Aktiv", callback_data=f"set_status_{property_id}_{PropertyStatus.ACTIVE.value}")
    builder.button(text="🟡 Rezerv", callback_data=f"set_status_{property_id}_{PropertyStatus.RESERVED.value}")
    builder.button(text="🔴 Satıldı", callback_data=f"set_status_{property_id}_{PropertyStatus.SOLD.value}")
    builder.button(text="🔵 Kirayə verildi", callback_data=f"set_status_{property_id}_{PropertyStatus.RENTED.value}")
    builder.button(text="⬅️ Geri", callback_data=f"prop_view_{property_id}")
    builder.adjust(2, 2, 1)
    return builder.as_markup()
