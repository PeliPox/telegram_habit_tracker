from aiogram import Router, types
from aiogram.filters import Command
from db.base import SessionLocal
import db.crud as crud

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    db = SessionLocal()

    user = crud.get_user(db, message.from_user.id)
    if not user:
        user = crud.create_user(db, message.from_user.id, message.from_user.first_name)

    await message.answer(f'Привет, {user.name}! Я - твой личный трекер привычек.')

