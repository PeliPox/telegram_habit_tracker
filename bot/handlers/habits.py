from aiogram import Router, types, F
from sqlalchemy.orm import Session
from db.base import get_db
from db.crud import (get_habits_by_user, get_user, delete_habit, update_habit_title, get_habit_by_id,
                     complete_habit, is_habit_completed_today, update_habit_description, update_habit_periodicity,
                     not_complete_habit)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext


class UpdateHabitState(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_periodicity = State()

router = Router()

@router.message(lambda message: message.text == "📋 Мои привычки")
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
        day_spelling: str = ""
        if h.periodicity == 1:
            day_spelling: str = f"каждый день\n"
        elif  2 <= h.periodicity <= 5:
            day_spelling: str = f"каждые {h.periodicity} дня\n"
        elif 6 <= h.periodicity >= 7:
            day_spelling: str = f"каждые {h.periodicity} дней\n"

        if h.description:
            text += f"{mark}• *{h.title}* — {day_spelling} ({h.description})\n"
        else:
            text += f"{mark}• *{h.title}* — {day_spelling}"

    keyboard.button(
        text=f"✏️ Изменить",
        callback_data="update_habit"
    )
    keyboard.button(
        text=f"🗑 Удалить",
        callback_data="delete_habit"
    )
    keyboard.button(
        text=f"✅ Выполнено",
        callback_data=f"complete_habit"
    )
    keyboard.button(
        text=f"❌ Не выполнено",
        callback_data=f"not_complete_habit"
    )
    keyboard.adjust(2, 1, 2)

    await message.answer(
        text=text,
        parse_mode="Markdown",
        reply_markup=keyboard.as_markup(resize_keyboard=True)
    )
    next(db_gen, None)


@router.callback_query(F.data.startswith("complete_habit"))
async def choose_habit_to_complete(callback: types.CallbackQuery):
    db_gen = get_db()
    db: Session = next(db_gen)

    user = get_user(db, callback.from_user.id)
    habits = get_habits_by_user(db, user.id)

    next(db_gen, None)

    if not habits:
        await callback.answer("У тебя нет привычек.", show_alert=True)
        return

    keyboard = InlineKeyboardBuilder()
    for h in habits:
        keyboard.button(
            text=h.title,
            callback_data=f"habit_completed:{h.id}"
        )
    keyboard.button(text="❌ Отмена", callback_data="cancel_action")
    keyboard.adjust(1)

    await callback.message.edit_text(
        "Выбери привычку, которую хочешь отметить:",
        reply_markup=keyboard.as_markup()
    )

    await callback.answer()


@router.callback_query(F.data.startswith("not_complete_habit"))
async def choose_habit_to_not_complete(callback: types.CallbackQuery):
    db_gen = get_db()
    db: Session = next(db_gen)

    user = get_user(db, callback.from_user.id)
    habits = get_habits_by_user(db, user.id)

    next(db_gen, None)

    if not habits:
        await callback.answer("У тебя нет привычек.", show_alert=True)
        return

    keyboard = InlineKeyboardBuilder()
    for h in habits:
        keyboard.button(
            text=h.title,
            callback_data=f"habit_not_completed:{h.id}"
        )
    keyboard.button(text="❌ Отмена", callback_data="cancel_action")
    keyboard.adjust(1)

    await callback.message.edit_text(
        "Выбери привычку, которую хочешь отменить:",
        reply_markup=keyboard.as_markup()
    )

    await callback.answer()


@router.callback_query(F.data.startswith("habit_completed:"))
async def complete_habit_handler(callback: types.CallbackQuery):
    habit_id = int(callback.data.split(":")[1])

    db_gen = get_db()
    db: Session = next(db_gen)

    complete_habit(db, habit_id)
    next(db_gen, None)

    await callback.answer("Отмечено как выполнено! 🔥")
    await callback.message.edit_text("Отмечено как выполнено!")


@router.callback_query(F.data.startswith("habit_not_completed:"))
async def not_complete_habit_handler(callback: types.CallbackQuery):
    habit_id = int(callback.data.split(":")[1])

    db_gen = get_db()
    db: Session = next(db_gen)

    not_complete_habit(db, habit_id)
    next(db_gen, None)

    await callback.answer("Отмечено как не выполнено! 🔥")
    await callback.message.edit_text("Отмечено как не выполнено!")


@router.callback_query(F.data.startswith("delete_habit"))
async def choose_habit_to_delete(callback: types.CallbackQuery):
    db_gen = get_db()
    db: Session = next(db_gen)

    user = get_user(db, callback.from_user.id)
    habits = get_habits_by_user(db, user.id)

    next(db_gen, None)

    if not habits:
        await callback.answer("У тебя нет привычек.", show_alert=True)
        return

    keyboard = InlineKeyboardBuilder()
    for h in habits:
        keyboard.button(
            text=h.title,
            callback_data=f"habit_to_delete:{h.id}"
        )
    keyboard.button(
        text="❌ Отмена",
        callback_data="cancel_action"
    )
    keyboard.adjust(1)

    await callback.message.edit_text(
        "Выбери привычку, которую хочешь удалить:\u2063",
        reply_markup=keyboard.as_markup()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("habit_to_delete:"))
async def delete_habit_handler(callback: types.CallbackQuery):
    habit_id = int(callback.data.split(":")[1])

    db_gen = get_db()
    db: Session = next(db_gen)

    delete_habit(db, habit_id)

    next(db_gen, None)

    await callback.answer("Привычка удалена!")
    await callback.message.edit_text("Привычка удалена ✔️")


@router.callback_query(F.data.startswith("update_habit"))
async def choose_habit_to_update(callback: types.CallbackQuery):
    db_gen = get_db()
    db: Session = next(db_gen)

    user = get_user(db, callback.from_user.id)
    habits = get_habits_by_user(db, user.id)

    next(db_gen, None)

    if not habits:
        await callback.answer("У тебя нет привычек.", show_alert=True)
        return

    keyboard = InlineKeyboardBuilder()
    for h in habits:
        keyboard.button(
            text=h.title,
            callback_data=f"select_habit_for_update:{h.id}"
        )
    keyboard.button(text="❌ Отмена", callback_data="cancel_action")
    keyboard.adjust(1)

    await callback.message.answer(
        "Выбери привычку, которую хочешь изменить:\u2063",
        reply_markup=keyboard.as_markup()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("select_habit_for_update:"))
async def update_habit_menu(callback: types.CallbackQuery, state: FSMContext):
    habit_id = int(callback.data.split(":")[1])
    await state.update_data(habit_id=habit_id)

    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="✏️ Название", callback_data="edit_title")
    keyboard.button(text="📄 Описание", callback_data="edit_description")
    keyboard.button(text="📆 Периодичность", callback_data="edit_period")
    keyboard.button(text="❌ Отмена", callback_data="cancel_action")
    keyboard.adjust(1)

    await callback.message.edit_text(
        "Что хочешь изменить?",
        reply_markup=keyboard.as_markup()
    )
    await callback.answer()


@router.callback_query(F.data == "edit_title")
async def update_title_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введи новое название:")
    await state.set_state(UpdateHabitState.waiting_for_title)
    await callback.answer()


@router.message(UpdateHabitState.waiting_for_title)
async def process_new_title(message: types.Message, state: FSMContext):
    data = await state.get_data()
    habit_id = data["habit_id"]

    db_gen = get_db()
    db = next(db_gen)
    update_habit_title(db, habit_id, message.text)
    next(db_gen, None)

    await message.answer("Название обновлено ✔️")
    await state.clear()


@router.callback_query(F.data == "edit_description")
async def update_description_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введи новое описание привычки:")
    await state.set_state(UpdateHabitState.waiting_for_description)
    await callback.answer()


@router.message(UpdateHabitState.waiting_for_description)
async def process_new_description(message: types.Message, state: FSMContext):
    data = await state.get_data()
    habit_id = data["habit_id"]

    db_gen = get_db()
    db = next(db_gen)
    update_habit_description(db, habit_id, message.text)
    next(db_gen, None)

    await message.answer("Описание обновлено ✔️")
    await state.clear()


@router.callback_query(F.data == "edit_period")
async def update_period_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введи периодичность (в днях):")
    await state.set_state(UpdateHabitState.waiting_for_periodicity)
    await callback.answer()


@router.message(UpdateHabitState.waiting_for_periodicity)
async def process_new_period(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введите число, пожалуйста")
        return

    data = await state.get_data()
    habit_id = data["habit_id"]

    db_gen = get_db()
    db = next(db_gen)
    update_habit_periodicity(db, habit_id, int(message.text))
    next(db_gen, None)

    await message.answer("Периодичность обновлена ✔️")
    await state.clear()


@router.callback_query(F.data == "cancel_action")
async def cancel_action(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.answer("Отменено ❌")
