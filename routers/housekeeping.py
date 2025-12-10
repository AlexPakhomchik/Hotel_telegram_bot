from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from menu import main_menu


housekeeping_router = Router()

class AssignCleaning(StatesGroup):
    room = State()
    staff = State()
    notes = State()

class FinishCleaning(StatesGroup):
    task_id = State()

housekeeping_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='📋 Список задач по уборке')],
        [KeyboardButton(text='🧹 Назначить уборку')],
        [KeyboardButton(text='✅ Завершить уборку')],
        [KeyboardButton(text='Назад в главное меню⬅️')]
    ],
    resize_keyboard=True
)

@housekeeping_router.message(lambda m: m.text == 'Служба гостиничного хозяйства🧹')
async def housekeeping_main(message: types.Message):
    await message.answer('Служба гостиничного хозяйства🧹', reply_markup=housekeeping_menu)

@housekeeping_router.message(lambda m: m.text == '📋 Список задач по уборке')
async def housekeeping_list(message: types.Message, db_pool):
    async with db_pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT id, room_number, status, notes
            FROM housekeeping
            ORDER BY assigned_at DESC;
        """)
    if rows:
        text = "\n".join([f"#{r['id']} | Комната {r['room_number']} | {r['status']} | {r['notes'] or ''}" for r in rows])
    else:
        text = "Задач по уборке нет 📭"
    await message.answer(text)

@housekeeping_router.message(lambda m: m.text == '🧹 Назначить уборку')
async def start_assign(message: types.Message, state: FSMContext):
    await message.answer("Введите номер комнаты:")
    await state.set_state(AssignCleaning.room)

@housekeeping_router.message(AssignCleaning.room)
async def assign_room(message: types.Message, state: FSMContext):
    await state.update_data(room=int(message.text))
    await message.answer("Введите ID сотрудника:")
    await state.set_state(AssignCleaning.staff)

@housekeeping_router.message(AssignCleaning.staff)
async def assign_staff(message: types.Message, state: FSMContext):
    await state.update_data(staff=int(message.text))
    await message.answer("Введите комментарий (или '-' если нет):")
    await state.set_state(AssignCleaning.notes)

@housekeeping_router.message(AssignCleaning.notes)
async def assign_notes(message: types.Message, state: FSMContext, db_pool):
    data = await state.get_data()
    notes = None if message.text.strip() == '-' else message.text.strip()
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO housekeeping (room_number, staff_id, notes, status)
            VALUES ($1, $2, $3, 'ожидает')
        """, data["room"], data["staff"], notes)
    await message.answer(f"Задача по уборке комнаты {data['room']} назначена ✅")
    await state.clear()

@housekeeping_router.message(lambda m: m.text == '✅ Завершить уборку')
async def start_finish(message: types.Message, state: FSMContext):
    await message.answer("Введите ID задачи по уборке:")
    await state.set_state(FinishCleaning.task_id)

@housekeeping_router.message(FinishCleaning.task_id)
async def finish_task(message: types.Message, state: FSMContext, db_pool):
    try:
        task_id = int(message.text)
    except ValueError:
        await message.answer("ID должен быть числом. Попробуйте ещё раз:")
        return
    async with db_pool.acquire() as conn:
        result = await conn.execute("""
            UPDATE housekeeping
            SET status='завершено', finished_at=NOW()
            WHERE id=$1
        """, task_id)
    if result.startswith("UPDATE"):
        await message.answer(f"Задача #{task_id} отмечена как завершённая ✅")
    else:
        await message.answer("Задача не найдена ⚠️")
    await state.clear()

@housekeeping_router.message(lambda m: m.text == "Назад в главное меню⬅️")
async def back_to_main(message: types.Message):
    await message.answer("Главное меню⬅️", reply_markup=main_menu)
