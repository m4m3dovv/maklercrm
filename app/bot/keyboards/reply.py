from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from app.models.user import UserRole


def get_main_menu(role: UserRole) -> ReplyKeyboardMarkup:
    """Əsas menyu klaviaturasını qaytarır (İstifadəçi roluna görə fərqlənir)"""
    builder = ReplyKeyboardBuilder()
    
    # Hamı üçün olan menyular
    builder.button(text="🏠 Evlər")
    builder.button(text="👥 Müştərilər")
    
    # Təkcə Admin və Manager üçün
    if role in [UserRole.ADMIN, UserRole.MANAGER]:
        builder.button(text="👨‍💼 Agentlər")
        
    builder.button(text="🤖 AI Köməkçi")
    builder.button(text="📊 Statistika")
    
    # Düymələri 2-2 düzürük
    builder.adjust(2)
    
    return builder.as_markup(resize_keyboard=True, is_persistent=True)

def get_cancel_menu() -> ReplyKeyboardMarkup:
    """Əməliyyatı ləğv etmək üçün düymə"""
    builder = ReplyKeyboardBuilder()
    builder.button(text="❌ Ləğv et")
    return builder.as_markup(resize_keyboard=True)
