from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.bot.states.property_states import AddPropertyStates
from app.bot.keyboards.reply import get_cancel_menu, get_main_menu
from app.bot.keyboards.inline import property_actions_kb
from app.schemas.property import PropertyCreate
from app.services.property_service import PropertyService
from app.models.property import PropertyStatus

router = Router(name="property_router")

@router.message(F.text == "🏠 Evlər")
async def property_menu(message: Message):
    text = (
        "🏠 <b>Evlər bölməsi</b>\n\n"
        "Yeni ev əlavə etmək üçün: /add_property\n"
        "Aktiv evlərinizi görmək üçün: /my_properties"
    )
    await message.answer(text, parse_mode="HTML")

@router.message(Command("add_property"))
async def start_add_property(message: Message, state: FSMContext):
    await state.set_state(AddPropertyStates.waiting_for_title)
    await message.answer("Yeni ev üçün başlıq daxil edin (Məsələn: 'Gənclik metrosu yaxınlığında 3 otaqlı təmirli ev'):", reply_markup=get_cancel_menu())

@router.message(AddPropertyStates.waiting_for_title, F.text)
async def process_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(AddPropertyStates.waiting_for_district)
    await message.answer("Evin yerləşdiyi rayonu daxil edin (Məsələn: 'Nərimanov rayonu'):")

@router.message(AddPropertyStates.waiting_for_district, F.text)
async def process_district(message: Message, state: FSMContext):
    await state.update_data(district=message.text)
    await state.set_state(AddPropertyStates.waiting_for_address)
    await message.answer("Dəqiq ünvanı daxil edin (Məsələn: 'Atatürk prospekti 45'):")

@router.message(AddPropertyStates.waiting_for_address, F.text)
async def process_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await state.set_state(AddPropertyStates.waiting_for_room_count)
    await message.answer("Otaq sayını daxil edin (Məsələn: '3'):")

@router.message(AddPropertyStates.waiting_for_room_count, F.text)
async def process_room_count(message: Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("Xahiş olunur, sadəcə rəqəm daxil edin (Məsələn: 3):")
        
    await state.update_data(room_count=int(message.text))
    await state.set_state(AddPropertyStates.waiting_for_area)
    await message.answer("Evin sahəsini (kv.m) daxil edin (Məsələn: 120.5):")

@router.message(AddPropertyStates.waiting_for_area, F.text)
async def process_area(message: Message, state: FSMContext):
    try:
        area = float(message.text.replace(',', '.'))
    except ValueError:
        return await message.answer("Xahiş olunur, düzgün rəqəm daxil edin (Məsələn: 120.5):")
        
    await state.update_data(area=area)
    await state.set_state(AddPropertyStates.waiting_for_price)
    await message.answer("Evin qiymətini (AZN) daxil edin (Məsələn: 250000):")

@router.message(AddPropertyStates.waiting_for_price, F.text)
async def process_price_and_save(message: Message, state: FSMContext, db: AsyncSession, actor: User):
    try:
        price = float(message.text.replace(',', '.'))
    except ValueError:
        return await message.answer("Xahiş olunur, düzgün məbləğ daxil edin (Məsələn: 250000):")
        
    await state.update_data(price=price)
    data = await state.get_data()
    
    prop_create = PropertyCreate(
        title=data["title"],
        district=data["district"],
        address=data["address"],
        room_count=data["room_count"],
        area=data["area"],
        price=data["price"],
        agent_id=actor.id,
        status=PropertyStatus.ACTIVE
    )
    
    property_obj = await PropertyService.create_property(db, prop_create, actor)
    await state.clear()
    
    text = (
        f"✅ <b>Ev uğurla bazaya əlavə edildi!</b> (ID: {property_obj.id})\n\n"
        f"📌 {property_obj.title}\n"
        f"📍 {property_obj.district}, {property_obj.address}\n"
        f"🚪 Otaq: {property_obj.room_count} | 📐 Sahə: {property_obj.area} kv.m\n"
        f"💰 Qiymət: {property_obj.price} AZN"
    )
    
    await message.answer(text, parse_mode="HTML", reply_markup=get_main_menu(actor.role))
    await message.answer("Ev üzərində əməliyyatlar etmək üçün aşağıdakı düymələrdən istifadə edin:", reply_markup=property_actions_kb(property_obj.id))
