from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from app.models.user import User
from app.bot.keyboards.reply import get_main_menu

router = Router(name="common_router")


@router.message(CommandStart())
async def cmd_start(message: Message, actor: User, state: FSMContext):
    """Bot işə düşəndə istifadəçini qarşılayır."""
    await state.clear()
    welcome_text = (
        f"Salam, <b>{actor.full_name}</b>! 👋\n"
        f"NEXORA CRM sisteminə xoş gəldiniz.\n\n"
        f"Sizin rolunuz: <i>{actor.role.value.capitalize()}</i>\n"
        f"Aşağıdakı menyudan istədiyiniz bölməni seçə bilərsiniz."
    )
    await message.answer(welcome_text, reply_markup=get_main_menu(actor.role), parse_mode="HTML")


@router.message(F.text == "❌ Ləğv et")
async def cancel_action(message: Message, actor: User, state: FSMContext):
    """İstənilən cari əməliyyatı dayandırır və əsas menyuya qayıdır."""
    current_state = await state.get_state()
    if current_state is None:
        return
        
    await state.clear()
    await message.answer("Əməliyyat ləğv edildi.", reply_markup=get_main_menu(actor.role))
