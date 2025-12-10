from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

booking_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Просмотр текущих бронирований📋')],
        [KeyboardButton(text='Добавить бронь➕')],
        [KeyboardButton(text='Изменить бронь✏️')],
        [KeyboardButton(text='Отменить бронь❌')],
        [KeyboardButton(text='Проверка загруженности номеров📊')],
        [KeyboardButton(text='Назад в главное меню⬅️')]
    ],
    resize_keyboard=True
)
