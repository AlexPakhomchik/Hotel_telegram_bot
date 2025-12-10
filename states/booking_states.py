from aiogram.fsm.state import StatesGroup, State

class BookingStates(StatesGroup):
    room_number = State()
    guest_name = State()
    check_in = State()
    check_out = State()
    status = State()

class EditBookingStates(StatesGroup):
    booking_id = State()
    room_number = State()
    guest_name = State()
    check_in = State()
    check_out = State()
    status = State()

class CancelBookingStates(StatesGroup):
    booking_id = State()