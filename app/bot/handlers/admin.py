from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole
from app.services.stats_service import StatsService

router = Router(name="admin_router")

@router.message(F.text == "📊 Statistika")
async def show_statistics(message: Message, db: AsyncSession, actor: User):
    if actor.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        return await message.answer("⚠️ Bu bölməyə giriş icazəniz yoxdur.")
        
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
