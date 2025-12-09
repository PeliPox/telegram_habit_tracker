from aiogram import Router, types, F
from sqlalchemy.orm import Session
from db.base import get_db
from db.crud import get_habits_by_user, get_user, delete_habit, update_habit, get_habit_by_id, complete_habit, is_habit_completed_today
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext


class UpdateHabitState(StatesGroup):
    waiting_for_title = State()
    waiting_for_periodicity = State()

router = Router()

@router.message(Command("habits"))
async def list_habits(message: types.Message):
    db_gen = get_db()
    db: Session = next(db_gen)

    user = get_user(db, message.from_user.id)
    habits = get_habits_by_user(db, user.id)

    if not habits:
        await message.answer("У тебя пока нет привычек. Добавь через команду /add_habit")
        return

    text = "Твои привычки:\n\n"
    keyboard = InlineKeyboardBuilder()

    for h in habits:
        completed = is_habit_completed_today(db, h.id)
        mark = "✅" if completed else "❌"

        if h.periodicity == 1:
            text += f"{mark}• *{h.title}* — каждый день\n"
        elif 2 <= h.periodicity <= 5:
            text += f"{mark}• *{h.title}* — каждые {h.periodicity} дня\n"
        elif 6 <= h.periodicity <= 7:
            text += f"{mark}• *{h.title}* — каждые {h.periodicity} дней\n"

    keyboard.row(
        InlineKeyboardButton(
            text=f"✏️",
            callback_data=f"update_habit:{h.id}"
        ),
        InlineKeyboardButton(
            text=f"🗑",
            callback_data=f"delete_habit:{h.id}"
        ),
        InlineKeyboardButton(
            text=f"✅",
            callback_data=f"complete_habit:{h.id}"
        )
    )

    await message.answer(
        text=text,
        parse_mode="Markdown",
        reply_markup=keyboard.as_markup()
    )

    next(db_gen, None)

@router.callback_query(F.data.startswith("complete_habit"))
async def complete_habit_handler(callback: types.CallbackQuery):
    habit_id = int(callback.data.split(":")[1])

    db_gen = get_db()
    db: Session = next(db_gen)

    habit = get_habit_by_id(db, habit_id)
    if not habit:
        await callback.answer("Привычка не найдена!", show_alert=True)
        return

    complete_habit(db, habit_id)

    await callback.answer("Отмечено как выполнено! 🔥")
    next(db_gen, None)

@router.callback_query(F.data.startswith("delete_habit:"))
async def delete_habit_handler(callback: types.CallbackQuery):
    habit_id = int(callback.data.split(":")[1])

    db_gen = get_db()
    db: Session = next(db_gen)

    delete_habit(db, habit_id)

    next(db_gen, None)

    await callback.answer("Привычка удалена!")
    await callback.message.edit_text("Привычка удалена ✔️")


@router.callback_query(F.data.startswith("update_habit"))
async def update_habit_start(callback: types.CallbackQuery, state: FSMContext):
    habit_id = int(callback.data.split(":")[1])
    await state.update_data(habit_id=habit_id)

    await callback.message.answer(
        "Что хочешь изменить?\n"
        "Отправь новое название или напиши `skip` чтобы пропустить."
    )

    await state.set_state(UpdateHabitState.waiting_for_title)


@router.message(UpdateHabitState.waiting_for_title)
async def update_title(message: types.Message, state: FSMContext):
    title = message.text.strip()
    await state.update_data(title=None if title.lower() == "skip" else title)

    await message.answer("Теперь отправь новый периодичность (в днях) или напиши `skip`.")
    await state.set_state(UpdateHabitState.waiting_for_periodicity)


@router.message(UpdateHabitState.waiting_for_periodicity)
async def update_period(message: types.Message, state: FSMContext):
    data = await state.get_data()
    period_text = message.text.strip()

    if period_text.lower() == "skip":
        period = None
    else:
        period = int(period_text)

    db_gen = get_db()
    db = next(db_gen)

    updated = update_habit(
        db,
        habit_id=data["habit_id"],
        title=data.get("title"),
        periodicity=period,
    )

    next(db_gen, None)
    await state.clear()

    if updated:
        await message.answer("Готово! Привычка обновлена ✅")
    else:
        await message.answer("Ошибка: привычка не найдена ❌")