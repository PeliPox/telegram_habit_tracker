from aiogram import Router, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from db.crud import create_habit

router = Router()

class HabitCreate(StatesGroup):
    waiting_for_title = State()
    waiting_for_period = State()

#  start habit creation
@router.message(F.text == "/add_habit")
async def habit_add_start(message: types.Message, state: FSMContext):
    await message.answer("Введите название привычки:")
    await state.set_state(HabitCreate.waiting_for_title)

# habit title
@router.message(HabitCreate.waiting_for_title)
async def habit_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Как часто выполнять?\nНапример: 1 - каждый день, 2 - каждые 2 дня")
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

    # почему в БД название колонок такое?
    create_habit(
        user_id=message.from_user.id,
        title=title,
        periodicity=period
    )

    await message.answer(f"Привычка '{title}' добавлена (каждые {period} дн.)!")
    await state.clear()

