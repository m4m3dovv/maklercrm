import json
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.bot.states.property_states import AddPropertyStates
from app.bot.keyboards.reply import get_cancel_menu, get_main_menu
from app.bot.keyboards.inline import property_actions_kb, property_status_kb
from app.schemas.property import PropertyCreate
from app.services.property_service import PropertyService
from app.models.property import PropertyStatus
from app.repositories.property_repo import property_repo

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
    await message.answer("Yeni ev üçün başlıq daxil edin (Məsələn: 'Gənclik metrosunda təmirli ev'):", reply_markup=get_cancel_menu())

@router.message(AddPropertyStates.waiting_for_title, F.text)
async def process_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(AddPropertyStates.waiting_for_district)
    await message.answer("Evin yerləşdiyi rayonu daxil edin:")

@router.message(AddPropertyStates.waiting_for_district, F.text)
async def process_district(message: Message, state: FSMContext):
    await state.update_data(district=message.text)
    await state.set_state(AddPropertyStates.waiting_for_address)
    await message.answer("Dəqiq ünvanı daxil edin:")

@router.message(AddPropertyStates.waiting_for_address, F.text)
async def process_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await state.set_state(AddPropertyStates.waiting_for_room_count)
    await message.answer("Otaq sayını daxil edin:")

@router.message(AddPropertyStates.waiting_for_room_count, F.text)
async def process_room_count(message: Message, state: FSMContext):
    await state.update_data(room_count=int(message.text))
    await state.set_state(AddPropertyStates.waiting_for_floor)
    await message.answer("Ev neçənci mərtəbədə yerləşir? (Həyət evidirsə 1 yazın):")

@router.message(AddPropertyStates.waiting_for_floor, F.text)
async def process_floor(message: Message, state: FSMContext):
    await state.update_data(floor=int(message.text))
    await state.set_state(AddPropertyStates.waiting_for_total_floors)
    await message.answer("Binanın ümumi mərtəbə sayını daxil edin:")

@router.message(AddPropertyStates.waiting_for_total_floors, F.text)
async def process_total_floors(message: Message, state: FSMContext):
    await state.update_data(total_floors=int(message.text))
    await state.set_state(AddPropertyStates.waiting_for_area)
    await message.answer("Evin sahəsini (kv.m) daxil edin:")

@router.message(AddPropertyStates.waiting_for_area, F.text)
async def process_area(message: Message, state: FSMContext):
    await state.update_data(area=float(message.text.replace(',', '.')))
    await state.set_state(AddPropertyStates.waiting_for_document_type)
    await message.answer("Sənədin növünü daxil edin (Çıxarış, Müqavilə, Bələdiyyə və s.):")

@router.message(AddPropertyStates.waiting_for_document_type, F.text)
async def process_doc(message: Message, state: FSMContext):
    await state.update_data(document_type=message.text)
    await state.set_state(AddPropertyStates.waiting_for_owner_phone)
    await message.answer("Ev sahibinin əlaqə nömrəsini daxil edin:")

@router.message(AddPropertyStates.waiting_for_owner_phone, F.text)
async def process_owner_phone(message: Message, state: FSMContext):
    await state.update_data(owner_phone=message.text)
    await state.set_state(AddPropertyStates.waiting_for_price)
    await message.answer("Evin qiymətini (AZN) daxil edin:")

@router.message(AddPropertyStates.waiting_for_price, F.text)
async def process_price(message: Message, state: FSMContext):
    await state.update_data(price=float(message.text.replace(',', '.')))
    await state.set_state(AddPropertyStates.waiting_for_photo)
    await message.answer("Evin bir şəklini göndərin (Məcbur deyil, 'Keç' yaza bilərsiniz):")

@router.message(AddPropertyStates.waiting_for_photo, F.photo)
@router.message(AddPropertyStates.waiting_for_photo, F.text)
async def process_photo_and_save(message: Message, state: FSMContext, **kwargs):
    db: AsyncSession = kwargs.get("db")
    actor: User = kwargs.get("actor")
    data = await state.get_data()
    
    photo_ids = []
    if message.photo:
        photo_ids.append(message.photo[-1].file_id)
        
    prop_create = PropertyCreate(
        title=data["title"],
        district=data["district"],
        address=data["address"],
        room_count=data["room_count"],
        floor=data.get("floor"),
        total_floors=data.get("total_floors"),
        area=data["area"],
        document_type=data.get("document_type"),
        owner_phone=data.get("owner_phone"),
        price=data["price"],
        images=json.dumps(photo_ids) if photo_ids else None,
        agent_id=actor.id,
        status=PropertyStatus.ACTIVE
    )
    
    property_obj = await PropertyService.create_property(db, prop_create, actor)
    await state.clear()
    
    text = (
        f"✅ <b>Ev uğurla bazaya əlavə edildi!</b> (ID: {property_obj.id})\n\n"
        f"📌 {property_obj.title}\n"
        f"📍 Ünvan: {property_obj.district}, {property_obj.address}\n"
        f"🚪 Otaq: {property_obj.room_count} | 📐 Sahə: {property_obj.area} kv.m\n"
        f"🏢 Mərtəbə: {property_obj.floor} / {property_obj.total_floors}\n"
        f"📄 Sənəd: {property_obj.document_type}\n"
        f"📞 Ev Sahibi: {property_obj.owner_phone}\n"
        f"💰 Qiymət: {property_obj.price:,.2f} AZN"
    )
    
    if photo_ids:
        await message.answer_photo(photo_ids[0], caption=text, parse_mode="HTML", reply_markup=get_main_menu(actor.role))
    else:
        await message.answer(text, parse_mode="HTML", reply_markup=get_main_menu(actor.role))
        
    await message.answer("İdarəetmə:", reply_markup=property_actions_kb(property_obj.id))

# ======================== CALLBACK QUERIES (SİL, STATUS DƏYİŞ) ========================

@router.callback_query(F.data.startswith("prop_del_"))
async def delete_property(callback: CallbackQuery, **kwargs):
    db: AsyncSession = kwargs.get("db")
    prop_id = int(callback.data.split("_")[-1])
    
    # Gələcəkdə bura PermissionDenied check əlavə edəcəyik
    await property_repo.delete(db, prop_id)
    await callback.message.edit_text(f"✅ Ev (ID: {prop_id}) sistemdən silindi.")
    await callback.answer("Silindi!")

@router.callback_query(F.data.startswith("prop_status_"))
async def change_status_menu(callback: CallbackQuery):
    prop_id = int(callback.data.split("_")[-1])
    await callback.message.edit_reply_markup(reply_markup=property_status_kb(prop_id))

@router.callback_query(F.data.startswith("set_status_"))
async def set_property_status(callback: CallbackQuery, **kwargs):
    db: AsyncSession = kwargs.get("db")
    actor: User = kwargs.get("actor")
    
    parts = callback.data.split("_")
    prop_id = int(parts[2])
    new_status = parts[3]
    
    try:
        await PropertyService.change_status(db, prop_id, PropertyStatus(new_status), actor)
        await callback.message.edit_text(f"✅ Evin statusu dəyişdirildi: <b>{new_status.upper()}</b>", parse_mode="HTML")
    except Exception as e:
        await callback.answer(f"Xəta: {e}", show_alert=True)
