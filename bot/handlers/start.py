from aiogram import Router, types
from aiogram.filters import Command
from db.base import SessionLocal
import db.crud as crud
from aiogram.utils.keyboard import ReplyKeyboardBuilder, KeyboardButton

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    db = SessionLocal()

    user = crud.get_user(db, message.from_user.id)
    if not user:
        user = crud.create_user(db, message.from_user.id, message.from_user.first_name)

    welcome_text = (f"Привет, {user.name}! Я - твой личный трекер привычек.\n"
                    f"Начнем?")

    keyboard = ReplyKeyboardBuilder()
    keyboard.add(
        KeyboardButton(text="📋 Мои привычки"),
        KeyboardButton(text="➕ Создать привычку"),
        KeyboardButton(text="📊 Статистика"),
        KeyboardButton(text="⚙️ Настройки")
    )
    keyboard.adjust(1)

    await message.answer(
        welcome_text,
        reply_markup=keyboard.as_markup(
            resize_keyboard=True,
            one_time_keyboard=False
        )
    )
    # await message.answer(f'Привет, {user.name}! Я - твой личный трекер привычек.')

