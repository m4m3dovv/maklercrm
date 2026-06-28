from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from app.models.user import User, UserRole, SubscriptionType
from app.bot.keyboards.reply import get_main_menu
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

router = Router(name="common_router")

@router.message(CommandStart())
async def cmd_start(message: Message, actor: User, state: FSMContext):
    await state.clear()
    
    if not actor.is_subscribed() and actor.role != UserRole.ADMIN:
        welcome_text = (
            f"Salam, <b>{actor.full_name}</b>! 👋\n"
            f"NEXORA CRM sisteminə xoş gəldiniz.\n\n"
            f"❌ Sizin hesabınız aktiv deyil. Sistemi istifadə etmək üçün paket seçməlisiniz."
        )
        from aiogram.utils.keyboard import ReplyKeyboardBuilder
        kb = ReplyKeyboardBuilder()
        kb.button(text="💳 Abunə ol")
        return await message.answer(welcome_text, reply_markup=kb.as_markup(resize_keyboard=True), parse_mode="HTML")

    welcome_text = (
        f"Salam, <b>{actor.full_name}</b>! 👋\n"
        f"NEXORA CRM sisteminə xoş gəldiniz.\n\n"
        f"Sizin rolunuz: <i>{actor.role.value.capitalize()}</i>\n"
        f"Paketiniz: <b>{actor.subscription.value.upper()}</b>"
    )
    await message.answer(welcome_text, reply_markup=get_main_menu(actor.role), parse_mode="HTML")


@router.message(F.text == "💳 Abunə ol")
async def subscription_menu(message: Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="Standart (15 AZN / Ay)", callback_data="pay_standart")
    kb.button(text="Premium (30 AZN / Ay)", callback_data="pay_premium")
    kb.adjust(1)
    
    text = (
        "💎 <b>Paket seçin:</b>\n\n"
        "<b>Standart (15 AZN)</b> - Ayda limitsiz ev qeydiyyatı.\n"
        "<b>Premium (30 AZN)</b> - Əlavə olaraq AI elan mətnləri, PDF/Excel hesabatlar çıxarış imkanı."
    )
    await message.answer(text, reply_markup=kb.as_markup(), parse_mode="HTML")

# Qeyd: Gələcəkdə burada real ödəniş (Stripe/Pulpal) API quraşdırılacaq. İndilik admin-ə bildiriş getməli və ya təsdiqlənməlidir.
@router.callback_query(F.data.startswith("pay_"))
async def fake_payment_checkout(callback: CallbackQuery):
    pack = callback.data.split("_")[1]
    amount = 15 if pack == "standart" else 30
    
    await callback.message.edit_text(
        f"Müraciətiniz qəbul edildi. Zəhmət olmasa kartınıza <b>{amount} AZN</b> mədaxil edin və "
        f"qəbzi sistemin rəhbərinə göndərin. Sizin Telegram İD-niz: <code>{callback.from_user.id}</code>",
        parse_mode="HTML"
    )

@router.message(F.text == "❌ Ləğv et")
async def cancel_action(message: Message, actor: User, state: FSMContext):
    await state.clear()
    await message.answer("Əməliyyat ləğv edildi.", reply_markup=get_main_menu(actor.role))
