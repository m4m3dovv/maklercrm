from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.bot.states.customer_states import AddCustomerStates
from app.bot.keyboards.reply import get_cancel_menu, get_main_menu
from app.schemas.customer import CustomerCreate
from app.services.customer_service import CustomerService

router = Router(name="customer_router")

@router.message(F.text == "👥 Müştərilər")
async def customer_menu(message: Message):
    text = (
        "👥 <b>Müştərilər bölməsi</b>\n\n"
        "Yeni müştəri əlavə etmək üçün: /add_customer\n"
        "Müştərilərinizi görmək üçün: /my_customers"
    )
    await message.answer(text, parse_mode="HTML")

@router.message(Command("add_customer"))
async def start_add_customer(message: Message, state: FSMContext):
    await state.set_state(AddCustomerStates.waiting_for_fullname)
    await message.answer("Müştərinin ad və soyadını daxil edin (Məsələn: 'Əli Məmmədov'):", reply_markup=get_cancel_menu())

@router.message(AddCustomerStates.waiting_for_fullname, F.text)
async def process_customer_fullname(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await state.set_state(AddCustomerStates.waiting_for_phone)
    await message.answer("Müştərinin əlaqə nömrəsini daxil edin (Məsələn: '+994501234567'):")

@router.message(AddCustomerStates.waiting_for_phone, F.text)
async def process_customer_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.set_state(AddCustomerStates.waiting_for_budget)
    await message.answer("Müştərinin ev axtarışı üçün büdcəsini daxil edin (AZN). Əgər məlum deyilsə '0' yaza bilərsiniz:")

@router.message(AddCustomerStates.waiting_for_budget, F.text)
async def process_customer_budget(message: Message, state: FSMContext, db: AsyncSession, actor: User):
    try:
        budget = float(message.text.replace(',', '.'))
    except ValueError:
        return await message.answer("Düzgün məbləğ daxil edin.")
        
    data = await state.get_data()
    
    customer_create = CustomerCreate(
        full_name=data["full_name"],
        phone=data["phone"],
        budget=budget if budget > 0 else None,
        agent_id=actor.id
    )
    
    customer_obj = await CustomerService.create_customer(db, customer_create, actor)
    await state.clear()
    
    text = (
        f"✅ <b>Müştəri bazaya əlavə edildi!</b> (ID: {customer_obj.id})\n\n"
        f"👤 Ad/Soyad: {customer_obj.full_name}\n"
        f"📞 Telefon: {customer_obj.phone}\n"
        f"💰 Büdcə: {f'{customer_obj.budget} AZN' if customer_obj.budget else 'Məlum deyil'}"
    )
    
    await message.answer(text, parse_mode="HTML", reply_markup=get_main_menu(actor.role))
