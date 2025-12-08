from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Управление бронированием🏨')],
        [KeyboardButton(text='Управление персоналом🧑‍💼')],
        [KeyboardButton(text='Служба гостиничного хозяйства🧹')],
        [KeyboardButton(text='Техническое обслуживание🛠️')],
        [KeyboardButton(text='Склад и инвентарь📦')],
        [KeyboardButton(text='Внутренние коммуникации💬')],
        [KeyboardButton(text='Отчетность📊')]
    ],
    resize_keyboard=True
)
