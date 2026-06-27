
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from app.models.user import User
from app.bot.keyboards.reply import get_main_menu

router = Router(name="common_router")

@router.message(CommandStart())
async def cmd_start(message: Message, actor: User, state: FSMContext):
    await state.clear()
    
    # SADƏCƏ TEXT, KEYBOARD OLMADAN (Problemin keyboard-da olub-olmadığını anlamaq üçün)
    welcome_text = (
        f"Salam, <b>{actor.full_name}</b>! 👋\n"
        f"Sizin rolunuz: <i>{actor.role.value.capitalize()}</i>\n"
        f"Database bağlantısı uğurludur!"
    )
    
    try:
        # 1-ci test: Sadəcə mətn göndəririk
        await message.answer(welcome_text, parse_mode="HTML")
        
        # 2-ci test: Keyboard əlavə edirik
        await message.answer("Menyu yüklənir...", reply_markup=get_main_menu(actor.role))
    except Exception as e:
        await message.answer(f"Cavab göndərərkən xəta: {str(e)}")

@router.message(F.text == "❌ Ləğv et")
async def cancel_action(message: Message, actor: User, state: FSMContext):
    await state.clear()
    await message.answer("Əməliyyat ləğv edildi.", reply_markup=get_main_menu(actor.role))
