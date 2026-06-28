import json
import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.bot.states.property_states import AddPropertyStates
from app.bot.keyboards.reply import get_cancel_menu, get_main_menu
from app.bot.keyboards.inline import property_actions_kb, property_status_kb
from app.schemas.property import PropertyCreate
from app.services.property_service import PropertyService
from app.models.property import Property, PropertyStatus, PropertyType, DealType
from app.repositories.property_repo import property_repo

router = Router(name="property_router")

# ======================== MENYULAR ========================
def get_deal_type_kb():
    kb = ReplyKeyboardBuilder()
    kb.button(text="Satılır")
    kb.button(text="Kirayə verilir")
    kb.button(text="❌ Ləğv et")
    kb.adjust(2, 1)
    return kb.as_markup(resize_keyboard=True)

def get_property_type_kb():
    kb = ReplyKeyboardBuilder()
    kb.button(text="Bina evi")
    kb.button(text="Həyət evi / Bağ evi")
    kb.button(text="Torpaq sahəsi")
    kb.button(text="Obyekt / Ofis")
    kb.button(text="❌ Ləğv et")
    kb.adjust(2, 2, 1)
    return kb.as_markup(resize_keyboard=True)

def get_finish_photo_kb():
    kb = ReplyKeyboardBuilder()
    kb.button(text="✅ Şəkillər Bitdi")
    kb.button(text="❌ Ləğv et")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)

from aiogram.utils.keyboard import InlineKeyboardBuilder
def get_property_categories_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ Yeni Əmlak Əlavə Et", callback_data="add_property_action")
    kb.button(text="🏢 Bina evlərim", callback_data="my_props_bina")
    kb.button(text="🏡 Həyət evlərim", callback_data="my_props_heyet")
    kb.button(text="🌍 Torpaq sahələrim", callback_data="my_props_torpaq")
    kb.button(text="🏢 Obyektlərim", callback_data="my_props_obyekt")
    kb.button(text="📋 Bütün Əmlaklarım", callback_data="my_props_all")
    kb.adjust(1, 2, 2, 1)
    return kb.as_markup()

# ======================== EVLƏR BÖLMƏSİ ========================
@router.message(F.text == "🏠 Evlər")
async def property_menu(message: Message):
    text = "🏠 <b>Əmlak İdarəetmə Paneli</b>\n\nAşağıdakı kateqoriyalardan birini seçin:"
    await message.answer(text, parse_mode="HTML", reply_markup=get_property_categories_kb())

@router.callback_query(F.data == "add_property_action")
async def action_add_property(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AddPropertyStates.waiting_for_deal_type)
    await callback.message.answer("Əmlak satılır, yoxsa kirayə verilir?", reply_markup=get_deal_type_kb())
    await callback.answer()

@router.message(Command("add_property"))
async def start_add_property(message: Message, state: FSMContext):
    await state.set_state(AddPropertyStates.waiting_for_deal_type)
    await message.answer("Əmlak satılır, yoxsa kirayə verilir?", reply_markup=get_deal_type_kb())

@router.message(AddPropertyStates.waiting_for_deal_type)
async def process_deal_type(message: Message, state: FSMContext):
    deal = DealType.SATIS if message.text and "Satılır" in message.text else DealType.KIRAYE
    await state.update_data(deal_type=deal)
    await state.set_state(AddPropertyStates.waiting_for_property_type)
    await message.answer("Əmlakın növünü seçin:", reply_markup=get_property_type_kb())

@router.message(AddPropertyStates.waiting_for_property_type)
async def process_property_type(message: Message, state: FSMContext):
    prop_map = {
        "Bina evi": PropertyType.BINA_EVI,
        "Həyət evi / Bağ evi": PropertyType.HEYET_EVI,
        "Torpaq sahəsi": PropertyType.TORPAQ,
        "Obyekt / Ofis": PropertyType.OBYEKT
    }
    ptype = prop_map.get(message.text, PropertyType.BINA_EVI)
    await state.update_data(property_type=ptype)
    
    await state.set_state(AddPropertyStates.waiting_for_title)
    await message.answer("Yeni əmlak üçün qısa başlıq yazın (Məs: Gənclikdə 3 otaqlı):", reply_markup=get_cancel_menu())

@router.message(AddPropertyStates.waiting_for_title)
async def process_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(AddPropertyStates.waiting_for_district)
    await message.answer("Əmlakın yerləşdiyi rayonu daxil edin (Məs: Nərimanov):")

@router.message(AddPropertyStates.waiting_for_district)
async def process_district(message: Message, state: FSMContext):
    await state.update_data(district=message.text)
    await state.set_state(AddPropertyStates.waiting_for_address)
    await message.answer("Dəqiq ünvanı daxil edin:")

@router.message(AddPropertyStates.waiting_for_address)
async def process_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await state.set_state(AddPropertyStates.waiting_for_room_count)
    await message.answer("Otaq sayını daxil edin (Torpaqdırsa 0 yazın):")

@router.message(AddPropertyStates.waiting_for_room_count)
async def process_room(message: Message, state: FSMContext):
    await state.update_data(room_count=int(message.text) if message.text and message.text.isdigit() else 0)
    await state.set_state(AddPropertyStates.waiting_for_floor)
    await message.answer("Neçənci mərtəbədə yerləşir? (Bina evi deyilsə 1 yazın):")

@router.message(AddPropertyStates.waiting_for_floor)
async def process_floor(message: Message, state: FSMContext):
    await state.update_data(floor=int(message.text) if message.text and message.text.isdigit() else 1)
    await state.set_state(AddPropertyStates.waiting_for_total_floors)
    await message.answer("Binanın ümumi mərtəbə sayını daxil edin (Həyət evidirsə 1 yazın):")

@router.message(AddPropertyStates.waiting_for_total_floors)
async def process_total_floors(message: Message, state: FSMContext):
    await state.update_data(total_floors=int(message.text) if message.text and message.text.isdigit() else 1)
    await state.set_state(AddPropertyStates.waiting_for_area)
    await message.answer("Sahəsini daxil edin (kv.m və ya sot):")

@router.message(AddPropertyStates.waiting_for_area)
async def process_area(message: Message, state: FSMContext):
    try:
        area = float(message.text.replace(',', '.'))
    except (ValueError, AttributeError):
        area = 1.0
    await state.update_data(area=area)
    await state.set_state(AddPropertyStates.waiting_for_document_type)
    await message.answer("Sənədin növünü yazın (Çıxarış, Müqavilə, Bələdiyyə və s.):")

@router.message(AddPropertyStates.waiting_for_document_type)
async def process_doc(message: Message, state: FSMContext):
    await state.update_data(document_type=message.text)
    await state.set_state(AddPropertyStates.waiting_for_owner_phone)
    await message.answer("Ev sahibinin (müştərinin) əlaqə nömrəsini daxil edin:")

@router.message(AddPropertyStates.waiting_for_owner_phone)
async def process_owner(message: Message, state: FSMContext):
    await state.update_data(owner_phone=message.text)
    await state.set_state(AddPropertyStates.waiting_for_price)
    await message.answer("Əmlakın qiymətini (AZN) daxil edin (Məsələn: 125000):")

@router.message(AddPropertyStates.waiting_for_price)
async def process_price(message: Message, state: FSMContext):
    try:
        price = float(message.text.replace(',', '.'))
    except (ValueError, AttributeError):
        return await message.answer("Xahiş olunur, düzgün məbləğ daxil edin:")
        
    await state.update_data(price=price)
    await state.update_data(photo_ids=[])
    
    await state.set_state(AddPropertyStates.waiting_for_photos)
    await message.answer(
        "Əla! İndi mənə əmlakın şəkillərini göndərin.\n\n"
        "Bütün şəkilləri (tək-tək və ya qrup halında) göndərdikdən sonra "
        "MÜTLƏQ aşağıdakı düyməni sıxın ki, bazaya yadda saxlanılsın:", 
        reply_markup=get_finish_photo_kb(), parse_mode="HTML"
    )

@router.message(AddPropertyStates.waiting_for_photos, F.photo)
async def just_collect_photos(message: Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photo_ids", [])
    photos.append(message.photo[-1].file_id)
    await state.update_data(photo_ids=photos)


@router.message(AddPropertyStates.waiting_for_photos, F.text == "✅ Şəkillər Bitdi")
async def save_all_property_data(message: Message, state: FSMContext, **kwargs):
    await message.answer("Sistemə yazılır, zəhmət olmasa gözləyin... ⏳")
    
    db: AsyncSession = kwargs.get("db")
    actor: User = kwargs.get("actor")
    
    data = await state.get_data()
    photos = data.get("photo_ids", [])
    
    try:
        prop_create = PropertyCreate(
            title=data.get("title", "Başlıqsız"),
            property_type=data.get("property_type", PropertyType.BINA_EVI),
            deal_type=data.get("deal_type", DealType.SATIS),
            district=data.get("district", "-"),
            address=data.get("address", "-"),
            room_count=data.get("room_count", 0),
            floor=data.get("floor", 1),
            total_floors=data.get("total_floors", 1),
            area=data.get("area", 0.0),
            document_type=data.get("document_type", "-"),
            owner_phone=data.get("owner_phone", "-"),
            price=data.get("price", 0.0),
            images=json.dumps(photos) if photos else None,
            agent_id=actor.id,
            status=PropertyStatus.ACTIVE
        )
        
        property_obj = await PropertyService.create_property(db, prop_create, actor)
        await state.clear()
        
        text = (
            f"✅ <b>Əmlak uğurla bazaya əlavə edildi!</b> (ID: {property_obj.id})\n\n"
            f"🏷 <b>{property_obj.deal_type.value}</b> - {property_obj.property_type.value}\n"
            f"📌 {property_obj.title}\n"
            f"📍 {property_obj.district}, {property_obj.address}\n"
            f"🚪 Otaq: {property_obj.room_count} | 📐 Sahə: {property_obj.area} kv.m\n"
            f"🏢 Mərtəbə: {property_obj.floor} / {property_obj.total_floors}\n"
            f"📄 Sənəd: {property_obj.document_type}\n"
            f"📞 Sahib: {property_obj.owner_phone}\n"
            f"💰 Qiymət: <b>{property_obj.price:,.2f} AZN</b>\n"
            f"📸 Yüklənən şəkil sayı: {len(photos)}"
        )
        
        if photos:
            await message.answer_photo(photos[0], caption=text, parse_mode="HTML", reply_markup=get_main_menu(actor.role))
        else:
            await message.answer(text, parse_mode="HTML", reply_markup=get_main_menu(actor.role))
            
        await message.answer("Əmlakı idarə etmək üçün:", reply_markup=property_actions_kb(property_obj.id))
        
    except Exception as e:
        await message.answer(f"Ev yadda saxlanılarkən xəta baş verdi: {str(e)}")
        await state.clear()


# ======================== KATEQORİYALARLA EV AXTARIŞI ========================
@router.message(Command("my_properties"))
async def my_properties_cmd(message: Message):
    text = "Aşağıdakı kateqoriyalardan birini seçin:"
    await message.answer(text, parse_mode="HTML", reply_markup=get_property_categories_kb())

@router.callback_query(F.data.startswith("my_props_"))
async def show_properties_by_category(callback: CallbackQuery, **kwargs):
    db: AsyncSession = kwargs.get("db")
    actor: User = kwargs.get("actor")
    category_slug = callback.data.split("_")[2]
    
    stmt = select(Property).where(Property.agent_id == actor.id)
    cat_name = "Bütün Əmlaklarım"
    
    if category_slug == "bina":
        stmt = stmt.where(Property.property_type == PropertyType.BINA_EVI)
        cat_name = "🏢 Bina Evləri"
    elif category_slug == "heyet":
        stmt = stmt.where(Property.property_type == PropertyType.HEYET_EVI)
        cat_name = "🏡 Həyət / Bağ Evləri"
    elif category_slug == "torpaq":
        stmt = stmt.where(Property.property_type == PropertyType.TORPAQ)
        cat_name = "🌍 Torpaq Sahələri"
    elif category_slug == "obyekt":
        stmt = stmt.where(Property.property_type == PropertyType.OBYEKT)
        cat_name = "🏢 Obyekt / Ofis"
        
    stmt = stmt.limit(30)
    result = await db.execute(stmt)
    properties = result.scalars().all()
    
    await callback.answer()
    
    if not properties:
        return await callback.message.answer(f"Sizin hələ heç bir aktiv <b>{cat_name}</b> elanınız yoxdur.", parse_mode="HTML")
        
    await callback.message.answer(f"Seçim: <b>{cat_name}</b>\nTapılan əmlak sayı: <b>{len(properties)}</b>", parse_mode="HTML")
    
    for prop in properties:
        text = (
            f"📌 <b>{prop.title}</b> (ID: {prop.id})\n"
            f"🏷 <b>{prop.deal_type.value}</b> - {prop.property_type.value}\n"
            f"📍 {prop.district}, {prop.address}\n"
            f"🚪 Otaq: {prop.room_count} | 📐 Sahə: {prop.area} kv.m\n"
            f"🏢 Mərtəbə: {prop.floor} / {prop.total_floors}\n"
            f"📄 Sənəd: {prop.document_type}\n"
            f"📞 Sahib: <code>{prop.owner_phone}</code>\n"
            f"💰 Qiymət: <b>{prop.price:,.2f} AZN</b>\n"
            f"📊 Status: <b>{prop.status.value.upper()}</b>"
        )
        
        if prop.images:
            try:
                photos = json.dumps(prop.images) if isinstance(prop.images, list) else json.loads(prop.images)
                if photos and len(photos) > 0:
                    await callback.message.answer_photo(photos[0], caption=text, parse_mode="HTML", reply_markup=property_actions_kb(prop.id))
                    continue
            except Exception:
                pass
                
        await callback.message.answer(text, parse_mode="HTML", reply_markup=property_actions_kb(prop.id))


# ======================== CALLBACK QUERIES ========================
@router.callback_query(F.data.startswith("prop_del_"))
async def delete_property(callback: CallbackQuery, **kwargs):
    db: AsyncSession = kwargs.get("db")
    prop_id = int(callback.data.split("_")[-1])
    await property_repo.delete(db, prop_id)
    await callback.message.edit_text(f"✅ Əmlak (ID: {prop_id}) sistemdən tamamilə silindi.")

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
        await PropertyService.change_status(db, prop_id, new_status, actor)
        
        status_text = {
            "active": "AKTİV 🟢",
            "reserved": "REZERV 🟡",
            "rented": "KİRAYƏ VERİLDİ 🔵",
            "sold": "SATILDI 🔴"
        }
        await callback.message.edit_text(
            f"✅ Əmlakın statusu uğurla dəyişdirildi: <b>{status_text.get(new_status, new_status.upper())}</b>\n\n"
            f"<i>Geri qayıtmaq üçün yuxarıdakı menyudan istifadə edin.</i>", 
            parse_mode="HTML"
        )
    except Exception as e:
        await callback.answer(f"Xəta: {e}", show_alert=True)

@router.callback_query(F.data.startswith("prop_view_"))
async def back_to_property_view(callback: CallbackQuery, **kwargs):
    db: AsyncSession = kwargs.get("db")
    prop_id = int(callback.data.split("_")[-1])
    prop = await property_repo.get_by_id(db, prop_id)
    if not prop:
        return await callback.answer("Əmlak tapılmadı.", show_alert=True)
        
    text = (
        f"📌 <b>{prop.title}</b> (ID: {prop.id})\n"
        f"🏷 <b>{prop.deal_type.value}</b> - {prop.property_type.value}\n"
        f"📍 {prop.district}, {prop.address}\n"
        f"🚪 Otaq: {prop.room_count} | 📐 Sahə: {prop.area} kv.m\n"
        f"🏢 Mərtəbə: {prop.floor} / {prop.total_floors}\n"
        f"📄 Sənəd: {prop.document_type}\n"
        f"📞 Sahib: <code>{prop.owner_phone}</code>\n"
        f"💰 Qiymət: <b>{prop.price:,.2f} AZN</b>\n"
        f"📊 Status: <b>{prop.status.value.upper()}</b>"
    )
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=property_actions_kb(prop.id))
