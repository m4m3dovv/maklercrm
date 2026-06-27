from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from app.models.user import User

router = Router(name="common_router")

@router.message(CommandStart())
async def cmd_start(message: Message):
    # Birbaşa cavab verməsini sınaqdan keçiririk. Middleware, Actor vs ehtiyac yoxdur.
    await message.answer("Salam! Mən işləyirəm! 🚀")

@router.message()
async def echo_all(message: Message):
    # Əgər adam başqa bir söz yazsa (Məsələn: "salam")
    await message.answer(f"Siz bunu yazdınız: {message.text}")
