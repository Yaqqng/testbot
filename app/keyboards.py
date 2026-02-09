from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def user_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🧾 Личный кабинет", callback_data="cabinet")],
            [InlineKeyboardButton(text="🛒 Купить VPN (30 дней / 299₽)", callback_data="buy_30")],
            [InlineKeyboardButton(text="📦 Мои подписки", callback_data="my_subs")],
            [InlineKeyboardButton(text="✅ Проверить подписку на канал", callback_data="check_sub")],
        ]
    )


def admin_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💰 Изменить баланс", callback_data="admin_balance")],
        ]
    )
