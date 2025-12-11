from aiogram import Router, types
from db.base import get_db
from db.crud import get_habits_stats_for_user, get_user
from sqlalchemy.orm import Session

router = Router()


@router.message(lambda msg: msg.text == "📊 Статистика")
async def show_stats(message: types.Message):
    db_gen = get_db()
    db: Session = next(db_gen)

    user = get_user(db, message.from_user.id)
    stats = get_habits_stats_for_user(db, user.id)

    next(db_gen, None)

    if not stats:
        await message.answer("У тебя пока нет привычек, поэтому статистика пустая.")
        return

    text = "📊 *Твоя статистика по привычкам:*\n\n"

    for s in stats:
        habit = s["habit"]
        text += (
            f"• *{habit.title}*\n"
            f"   ├ Всего выполнений: *{s['total']}*\n"
            f"   ├ Выполнено сегодня: *{s['today']}*\n"
            f"   ├ Последний раз: *{s['last'] if s['last'] else '—'}*\n"
            f"   ├ Текущий стрик: *{s['streak']}*\n"
            f"   └ Максимальный стрик: *{s['max_streak']}*\n\n"
        )

    await message.answer(text, parse_mode="Markdown")