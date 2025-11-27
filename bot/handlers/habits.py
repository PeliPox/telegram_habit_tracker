from aiogram import Router, types
from sqlalchemy.orm import Session
from db.base import get_db
from db.crud import get_habits_by_user, get_user
from aiogram.filters import Command

router = Router()

@router.message(Command("habits"))
async def list_habits(message: types.Message):
    db_gen = get_db()
    db: Session = next(db_gen) # получаем сессию

    user = get_user(db, message.from_user.id)
    habits = get_habits_by_user(db, user.id)

    text = " \bТвои привычки: \n\n"

    if not habits:
        await message.answer("У тебя пока нет привычек.")
    else:
        for h in habits:
            text += f"•{h.title} - каждые {h.periodicity} дней\n"
        await message.answer(text=text, parse_mode="Markdown")

    next(db_gen, None)