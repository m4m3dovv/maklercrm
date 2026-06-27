import json
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from app.models.user import User
from app.bot.states.property_states import AddPropertyStates
from app.bot.keyboards.reply import get_cancel_menu, get_main_menu
from app.bot.keyboards.inline import property_actions_kb, property_status_kb
from app.schemas.property import PropertyCreate
from app.services.property_service import PropertyService
from app.models.property import PropertyStatus, PropertyType, DealType
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
    kb.button(text="✅ Şəkillər bitdi (Yadda saxla)")
    kb.button(text="❌ Ləğv et")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)

# "Evlər" düyməsinin dinləyicisi (Sizin dediyiniz açılmayan düymə)
@router.message(F.text == "🏠 Evlər")
async def property_menu(message: Message):
    text = (
        "🏠 <b>Evlər bölməsi</b>\n\n"
        "Yeni ev əlavə etmək üçün: /add_property\n"
        "Aktiv evlərinizi görmək üçün: /my_properties"
    )
    await message.answer(text, parse_mode="HTML")

# ======================== EV ƏLAVƏ ETMƏK FSM ========================
@router.message(Command("add_property"))
async def start_add_property(message: Message, state: FSMContext):
    await state.set_state(AddPropertyStates.waiting_for_deal_type)
    await message.answer("Ev satılır, yoxsa kirayə verilir?", reply_markup=get_deal_type_kb())

@router.message(AddPropertyStates.waiting_for_deal_type, F.text.in_(["Satılır", "Kirayə verilir"]))
async def process_deal_type(message: Message, state: FSMContext):
    deal = DealType.SATIS if message.text == "Satılır" else DealType.KIRAYE
    await state.update_data(deal_type=deal)
    await state.set_state(AddPropertyStates.waiting_for_property_type)
    await message.answer("Əmlakın növünü seçin:", reply_markup=get_property_type_kb())

@router.message(AddPropertyStates.waiting_for_property_type, F.text)
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

@router.message(AddPropertyStates.waiting_for_title, F.text)
async def process_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(AddPropertyStates.waiting_for_district)
    await message.answer("Əmlakın yerləşdiyi rayonu daxil edin:")

@router.message(AddPropertyStates.waiting_for_district, F.text)
async def process_district(message: Message, state: FSMContext):
    await state.update_data(district=message.text)
    await state.set_state(AddPropertyStates.waiting_for_address)
    await message.answer("Dəqiq ünvanı daxil edin:")

@router.message(AddPropertyStates.waiting_for_address, F.text)
async def process_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await state.set_state(AddPropertyStates.waiting_for_room_count)
    await message.answer("Otaq sayını daxil edin (Torpaqdırsa 0 yazın):")

@router.message(AddPropertyStates.waiting_for_room_count, F.text)
async def process_room(message: Message, state: FSMContext):
    await state.update_data(room_count=int(message.text) if message.text.isdigit() else 0)
    await state.set_state(AddPropertyStates.waiting_for_floor)
    await message.answer("Neçənci mərtəbədə yerləşir? (Bina evi deyilsə 1 yazın):")

@router.message(AddPropertyStates.waiting_for_floor, F.text)
async def process_floor(message: Message, state: FSMContext):
    await state.update_data(floor=int(message.text) if message.text.isdigit() else 1)
    await state.set_state(AddPropertyStates.waiting_for_total_floors)
    await message.answer("Binanın ümumi mərtəbə sayını daxil edin:")

@router.message(AddPropertyStates.waiting_for_total_floors, F.text)
async def process_total_floors(message: Message, state: FSMContext):
    await state.update_data(total_floors=int(message.text) if message.text.isdigit() else 1)
    await state.set_state(AddPropertyStates.waiting_for_area)
    await message.answer("Sahəsini daxil edin (kv.m və ya sot):")

@router.message(AddPropertyStates.waiting_for_area, F.text)
async def process_area(message: Message, state: FSMContext):
    await state.update_data(area=float(message.text.replace(',', '.')))
    await state.set_state(AddPropertyStates.waiting_for_document_type)
    await message.answer("Sənədin növünü yazın (Çıxarış, Müqavilə və s.):")

@router.message(AddPropertyStates.waiting_for_document_type, F.text)
async def process_doc(message: Message, state: FSMContext):
    await state.update_data(document_type=message.text)
    await state.set_state(AddPropertyStates.waiting_for_owner_phone)
    await message.answer("Sahibin əlaqə nömrəsini daxil edin:")

@router.message(AddPropertyStates.waiting_for_owner_phone, F.text)
async def process_owner(message: Message, state: FSMContext):
    await state.update_data(owner_phone=message.text)
    await state.set_state(AddPropertyStates.waiting_for_price)
    await message.answer("Əmlakın qiymətini (AZN) daxil edin:")

@router.message(AddPropertyStates.waiting_for_price, F.text)
async def process_price(message: Message, state: FSMContext):
    try:
        price = float(message.text.replace(',', '.'))
    except ValueError:
        return await message.answer("Xahiş olunur, düzgün məbləğ daxil edin:")
        
    await state.update_data(price=price)
    await state.update_data(photo_ids=[])
    
    await state.set_state(AddPropertyStates.waiting_for_photos)
    await message.answer("Əla! İndi mənə əmlakın şəkillərini göndərin (Maks 30 ədəd).\n\n"
                         "Bütün şəkilləri atıb qurtardıqdan sonra aşağıdakı <b>'✅ Şəkillər bitdi'</b> düyməsini sıxın.", 
                         reply_markup=get_finish_photo_kb(), parse_mode="HTML")

@router.message(AddPropertyStates.waiting_for_photos, F.photo)
async def collect_photos(message: Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photo_ids", [])
    photos.append(message.photo[-1].file_id)
    await state.update_data(photo_ids=photos)

@router.message(AddPropertyStates.waiting_for_photos, F.text == "✅ Şəkillər bitdi (Yadda saxla)")
async def save_all_property_data(message: Message, state: FSMContext, **kwargs):
    db: AsyncSession = kwargs.get("db")
    actor: User = kwargs.get("actor")
    data = await state.get_data()
    photos = data.get("photo_ids", [])
    
    try:
        prop_create = PropertyCreate(
            title=data["title"],
            property_type=data["property_type"],
            deal_type=data["deal_type"],
            district=data["district"],
            address=data["address"],
            room_count=data["room_count"],
            floor=data.get("floor"),
            total_floors=data.get("total_floors"),
            area=data["area"],
            document_type=data.get("document_type"),
            owner_phone=data.get("owner_phone"),
            price=data["price"],
            images=json.dumps(photos) if photos else None,
            agent_id=actor.id,
            status=PropertyStatus.ACTIVE
        )
        
        property_obj = await PropertyService.create_property(db, prop_create, actor)
        await state.clear()
        
        text = (
            f"✅ <b>Əmlak uğurla bazaya əlavə edildi!</b> (ID: {property_obj.id})\n\n"
            f"🏷 {property_obj.deal_type.value} - {property_obj.property_type.value}\n"
            f"📌 {property_obj.title}\n"
            f"📍 Ünvan: {property_obj.district}, {property_obj.address}\n"
            f"🚪 Otaq: {property_obj.room_count} | 📐 Sahə: {property_obj.area} kv.m\n"
            f"🏢 Mərtəbə: {property_obj.floor} / {property_obj.total_floors}\n"
            f"📄 Sənəd: {property_obj.document_type}\n"
            f"📞 Sahib: {property_obj.owner_phone}\n"
            f"💰 Qiymət: {property_obj.price:,.2f} AZN\n"
            f"📸 Yüklənən şəkil sayı: {len(photos)}"
        )
        
        if photos:
            await message.answer_photo(photos[0], caption=text, parse_mode="HTML", reply_markup=get_main_menu(actor.role))
        else:
            await message.answer(text, parse_mode="HTML", reply_markup=get_main_menu(actor.role))
            
        await message.answer("İdarəetmə:", reply_markup=property_actions_kb(property_obj.id))
        
    except Exception as e:
        await message.answer(f"Ev yadda saxlanılarkən xəta baş verdi: {str(e)}")
        await state.clear()

# ======================== CALLBACK QUERIES (SİL, STATUS DƏYİŞ) ========================
@router.callback_query(F.data.startswith("prop_del_"))
async def delete_property(callback: CallbackQuery, **kwargs):
    db: AsyncSession = kwargs.get("db")
    prop_id = int(callback.data.split("_")[-1])
    await property_repo.delete(db, prop_id)
    await callback.message.edit_text(f"✅ Əmlak (ID: {prop_id}) sistemdən silindi.")
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
        await callback.message.edit_text(f"✅ Əmlakın statusu dəyişdirildi: <b>{new_status.upper()}</b>", parse_mode="HTML")
    except Exception as e:
        await callback.answer(f"Xəta: {e}", show_alert=True)
