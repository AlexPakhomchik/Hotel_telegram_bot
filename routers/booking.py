from aiogram import Router, types
from states.booking_states import BookingStates, EditBookingStates, CancelBookingStates
from aiogram.fsm.context import FSMContext
from menu import main_menu
from keyboards.booking_menu import booking_menu

import datetime



booking_router = Router()



@booking_router.message(lambda m: m.text == 'Управление бронированием🏨')
async def booking_main(message: types.Message):
    await message.answer('Управление бронированием🏨', reply_markup=booking_menu)

@booking_router.message(lambda m: m.text == 'Просмотр текущих бронирований📋')
async def show_bookings(message: types.Message, db_pool):
    async with db_pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM bookings;")
        if rows:
            text = '\n'.join([f"#{r['id']} | Номер {r['room_number']} | {r['guest_name']} | {r['status']}" for r in rows])
        else:
            text = 'Бронирований пока нет'
        await message.answer(text)

@booking_router.message(lambda m: m.text == 'Добавить бронь➕')
async def start_add_booking(message: types.Message, state: FSMContext):
    await message.answer('Введите номер комнаты:')
    await state.set_state(BookingStates.room_number)

@booking_router.message(BookingStates.room_number)
async def process_room(message: types.Message, state: FSMContext):
    await state.update_data(room_number=message.text)
    await message.answer("Введите имя гостя:")
    await state.set_state(BookingStates.guest_name)

@booking_router.message(BookingStates.guest_name)
async def process_guest(message: types.Message, state: FSMContext):
    await state.update_data(guest_name=message.text)
    await message.answer("Введите дату заезда (YYYY-MM-DD):")
    await state.set_state(BookingStates.check_in)

@booking_router.message(BookingStates.check_in)
async def process_checkin(message: types.Message, state: FSMContext):
    await state.update_data(check_in=message.text)
    await message.answer("Введите дату выезда (YYYY-MM-DD):")
    await state.set_state(BookingStates.check_out)

@booking_router.message(BookingStates.check_out)
async def process_checkout(message: types.Message, state: FSMContext):
    await state.update_data(check_out=message.text)
    await message.answer("Введите статус брони (например: подтверждено/ожидание/отменено):")
    await state.set_state(BookingStates.status)

@booking_router.message(BookingStates.status)
async def process_status(message: types.Message, state: FSMContext, db_pool):
    await state.update_data(status=message.text)
    data = await state.get_data()

    check_in = datetime.datetime.strptime(data["check_in"], "%Y-%m-%d").date()
    check_out = datetime.datetime.strptime(data["check_out"], "%Y-%m-%d").date()

    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO bookings (room_number, guest_name, check_in, check_out, status)
            VALUES ($1, $2, $3, $4, $5)
        """, data["room_number"], data["guest_name"], check_in, check_out, data["status"])

    await message.answer("Бронь успешно добавлена ✅")
    await state.clear()

@booking_router.message(lambda m: m.text == "Изменить бронь✏️")
async def start_edit_booking(message: types.Message, state: FSMContext):
    await message.answer("Введите ID брони, которую хотите изменить:")
    await state.set_state(EditBookingStates.booking_id)

@booking_router.message(EditBookingStates.booking_id)
async def process_edit_id(message: types.Message, state: FSMContext):
    await state.update_data(booking_id=message.text)
    await message.answer("Введите новый номер комнаты:")
    await state.set_state(EditBookingStates.room_number)

@booking_router.message(EditBookingStates.room_number)
async def process_edit_room(message: types.Message, state: FSMContext):
    await state.update_data(room_number=message.text)
    await message.answer("Введите новое имя гостя:")
    await state.set_state(EditBookingStates.guest_name)

@booking_router.message(EditBookingStates.guest_name)
async def process_edit_guest(message: types.Message, state: FSMContext):
    await state.update_data(guest_name=message.text)
    await message.answer("Введите новую дату заезда (YYYY-MM-DD):")
    await state.set_state(EditBookingStates.check_in)

@booking_router.message(EditBookingStates.check_in)
async def process_edit_checkin(message: types.Message, state: FSMContext):
    await state.update_data(check_in=message.text)
    await message.answer("Введите новую дату выезда (YYYY-MM-DD):")
    await state.set_state(EditBookingStates.check_out)

@booking_router.message(EditBookingStates.check_out)
async def process_edit_checkout(message: types.Message, state: FSMContext):
    await state.update_data(check_out=message.text)
    await message.answer("Введите новый статус брони:")
    await state.set_state(EditBookingStates.status)

@booking_router.message(EditBookingStates.status)
async def process_edit_status(message: types.Message, state: FSMContext, db_pool):
    await state.update_data(status=message.text)
    data = await state.get_data()

    check_in = datetime.datetime.strptime(data["check_in"], "%Y-%m-%d").date()
    check_out = datetime.datetime.strptime(data["check_out"], "%Y-%m-%d").date()

    async with db_pool.acquire() as conn:
        await conn.execute("""
            UPDATE bookings
            SET room_number=$1, guest_name=$2, check_in=$3, check_out=$4, status=$5
            WHERE id=$6
        """, data["room_number"], data["guest_name"], check_in, check_out, data["status"], int(data["booking_id"]))

    await message.answer("Бронь успешно изменена ✏️✅")
    await state.clear()

@booking_router.message(lambda m: m.text == "Отменить бронь❌")
async def start_cancel_booking(message: types.Message, state: FSMContext):
    await message.answer("Введите ID брони, которую хотите отменить:")
    await state.set_state(CancelBookingStates.booking_id)

@booking_router.message(CancelBookingStates.booking_id)
async def process_cancel_booking(message: types.Message, state: FSMContext, db_pool):
    booking_id = message.text

    async with db_pool.acquire() as conn:
        result = await conn.execute("DELETE FROM bookings WHERE id=$1", int(booking_id))

    if result.startswith("DELETE"):
        await message.answer(f"Бронь #{booking_id} успешно отменена ❌")
    else:
        await message.answer(f"Бронь #{booking_id} не найдена ⚠️")

    await state.clear()

@booking_router.message(lambda m: m.text == "Проверка загруженности номеров📊")
async def check_room_load(message: types.Message, db_pool):
    async with db_pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT room_number, COUNT(*) AS total
            FROM bookings
            WHERE status = 'подтверждено'
            GROUP BY room_number
            ORDER BY room_number;
        """)

    if rows:
        text = "\n".join([f"Номер {r['room_number']} | Бронирований: {r['total']}" for r in rows])
    else:
        text = "Нет подтверждённых броней 📭"

    await message.answer(text)

@booking_router.message(lambda m: m.text == "Назад в главное меню⬅️")
async def back_to_main(message: types.Message):
    await message.answer("Главное меню⬅️", reply_markup=main_menu)
