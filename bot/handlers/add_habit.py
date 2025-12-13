from aiogram import Router, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from db.crud import create_habit
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
router = Router()

class HabitCreate(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_period = State()


def cancel_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
        ]
    )

#  start habit creation
@router.message(lambda message: message.text == "➕ Создать привычку")
async def habit_add_start(message: types.Message, state: FSMContext):
    await message.answer(
        "✏️ Введите название привычки:",
        reply_markup=cancel_kb()
    )
    await state.set_state(HabitCreate.waiting_for_title)

# habit title
@router.message(HabitCreate.waiting_for_title)
async def habit_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("📄 Введите описание привычки:")
    await state.set_state(HabitCreate.waiting_for_description)


# description
@router.message(HabitCreate.waiting_for_description)
async def habit_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("📆 Как часто выполнять?\nНапример: 1 - каждый день, 2 - каждые 2 дня")
    await state.set_state(HabitCreate.waiting_for_period)


# habit period
@router.message(HabitCreate.waiting_for_period)
async def habit_period(message: types.Message, state: FSMContext):
    try:
        period = int(message.text)
        if period < 1:
            raise ValueError
    except:
        return await message.answer('Введите число! Например 1, 2, 3, ...')

    data = await state.get_data()
    title = data["title"]
    description = data["description"]

    create_habit(
        user_id=message.from_user.id,
        title=title,
        periodicity=period,
        description=description
    )

    await message.answer(f"Привычка добавлена!\n"
                         f"\n✏️ Название - {title}\n"
                         f"📄 Описание - {description}\n"
                         f"📆 Периодичность - {period} д.")
    await state.clear()


@router.callback_query(lambda c: c.data == "cancel")
async def cancel_action(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Создание привычки отменено")
    await callback.answer()
