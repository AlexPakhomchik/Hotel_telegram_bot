from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from menu import main_menu

staff_router = Router()

class StaffCheckStates(StatesGroup):
    staff_id = State()
    action = State()

staff_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='📋 Список сотрудников на смене')],
        [KeyboardButton(text='🕒 График работы и смен')],
        [KeyboardButton(text='✅ Отметка прихода/ухода')],
        [KeyboardButton(text='📢 Внутренние объявления')],
        [KeyboardButton(text='Назад в главное меню⬅️')]
    ],
    resize_keyboard=True
)

@staff_router.message(lambda m: m.text == 'Управление персоналом🧑‍💼')
async def staff_main(message: types.Message):
    await message.answer('Управление персоналом🧑‍💼', reply_markup=staff_menu)

@staff_router.message(lambda m: m.text == '📋 Список сотрудников на смене')
async def staff_list(message: types.message, db_pool):
    async with db_pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT id, full_name, role
            FROM staff
            WHERE status = 'на смене'
            ORDER BY full_name;
        """)
    if rows:
        text = "\n".join([f"#{r['id']} | {r['full_name']} | {r['role']}" for r in rows])
    else:
        text = 'Сотрудников на смене нет 📭'
    await message.answer(text)
    await message.answer('1')

@staff_router.message(lambda m: m.text == '🕒 График работы и смен')
async def staff_schedule(message: types.Message, db_pool):
    async with db_pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT full_name, role, shift_start, shift_end
            FROM staff
            ORDER BY shift_start;
        """)
    if rows:
        text = "\n".join([f"{r['full_name']} ({r['role']}) | {r['shift_start']} - {r['shift_end']}" for r in rows])
    else:
        text = 'График пока пуст 🗓️'
    await message.answer(text)



@staff_router.message(lambda m: m.text == '✅ Отметка прихода/ухода')
async def start_checkin(message: types.Message, state: FSMContext):
    await message.answer("Введите ID сотрудника:")
    await state.set_state(StaffCheckStates.staff_id)

@staff_router.message(StaffCheckStates.staff_id)
async def get_staff_id(message: types.Message, state: FSMContext):
    try:
        staff_id = int(message.text)
    except ValueError:
        await message.answer("ID должен быть числом. Попробуйте ещё раз:")
        return
    await state.update_data(staff_id=staff_id)
    await message.answer("Введите действие: 'пришёл' или 'ушёл'")
    await state.set_state(StaffCheckStates.action)

@staff_router.message(StaffCheckStates.action)
async def process_action(message: types.Message, state: FSMContext, db_pool):
    data = await state.get_data()
    staff_id = data.get("staff_id")
    action = message.text.strip().lower()

    if action == 'пришёл':
        new_status = 'на смене'
    elif action == 'ушёл':
        new_status = 'не на смене'
    else:
        await message.answer("Неверное действие. Введите 'пришёл' или 'ушёл'.")
        return

    async with db_pool.acquire() as conn:
        result = await conn.execute(
            "UPDATE staff SET status=$1 WHERE id=$2",
            new_status, staff_id
        )

    if result.startswith('UPDATE'):
        await message.answer(f"Сотрудник #{staff_id} отмечен как '{new_status}' ✅")
    else:
        await message.answer(f"Сотрудник #{staff_id} не найден ⚠️")

    await state.clear()
@staff_router.message(lambda m: m.text == '✅ Отметка прихода/ухода')
async def process_action(message: types.Message, state: FSMContext, db_pool):
    data = await state.get_data()
    staff_id = int(data["staff_id"])
    action = message.text.strip().lower()

    if action == 'пришёл':
        new_status = 'на смене'
    elif action == 'ушёл':
        new_status = 'не на смене'
    else:
        await message.answer("Неверное действие. Введите 'пришёл' или 'ушёл'.")
        return

    async with db_pool.acquire() as conn:
        result = await conn.execute("""
            UPDATE staff
            SET status = $1
            WHERE id = $2
        """, new_status, staff_id)

    if result.startswith('UPDATE'):
        await message.answer(f"Сотрудник #{staff_id} отмечен как '{new_status}' ✅")
    else:
        await message.answer(f"Сотрудник #{staff_id} не найден ⚠️")

    await state.clear()

@staff_router.message(lambda m: m.text == '📢 Внутренние объявления')
async def staff_announcements(message: types.Message, db_pool):
    async with db_pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT id, title, body, created_at
            FROM announcements
            ORDER BY created_at DESC
            LIMIT 5;
        """)
    if rows:
        text = "\n\n".join([f"📢 {r['title']}\n{r['body']}\n🕒 {r['created_at']:%Y-%m-%d %H:%M}" for r in rows])
    else:
        text = "Объявлений пока нет 📭"
    await message.answer(text, reply_markup=main_menu)

@staff_router.message(lambda m: m.text == "Назад в главное меню⬅️")
async def back_to_main(message: types.Message):
    await message.answer("Главное меню⬅️", reply_markup=main_menu)