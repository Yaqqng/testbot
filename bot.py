from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.enums.chat_member_status import ChatMemberStatus
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from dotenv import load_dotenv

from app.config import load_settings
from app.db import Database
from app.keyboards import admin_menu, user_menu
from app.remnawave_api import RemnawaveClient

class AdminBalanceState(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_delta = State()


load_dotenv()
settings = load_settings()

db = Database(settings.db_path)
remnawave = RemnawaveClient(
    settings.remnawave_base_url,
    settings.remnawave_api_key,
    settings.remnawave_subscription_endpoint,
)

bot = Bot(token=settings.bot_token)
dp = Dispatcher()


START_TEXTS = {"старт", "start", "/start"}
ADMIN_TEXTS = {"админ", "admin", "/admin"}


def is_admin(user_id: int) -> bool:
    return user_id in settings.admin_ids


def _channel_hint() -> str:
    if settings.main_channel_url:
        return settings.main_channel_url
    return settings.main_channel


async def check_channel_subscription(user_id: int) -> tuple[bool, str | None]:
    if not settings.main_channel:
        return True, None

    try:
        member = await bot.get_chat_member(settings.main_channel, user_id)
    except (TelegramBadRequest, TelegramForbiddenError):
        return False, "Бот не может проверить подписку. Проверьте MAIN_CHANNEL и права бота в канале."

    is_member = member.status in {
        ChatMemberStatus.MEMBER,
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.CREATOR,
    }
    if is_member:
        return True, None
    return False, None


async def send_start(message: Message) -> None:
    user = db.get_or_create_user(message.from_user.id, message.from_user.username)
    sub_ok, error_text = await check_channel_subscription(user.user_id)

    if error_text:
        await message.answer(error_text)

    if not sub_ok:
        await message.answer(
            f"Чтобы пользоваться ботом, подпишитесь на канал: {_channel_hint()}\n"
            "После подписки нажмите «Проверить подписку на канал».",
            reply_markup=user_menu(),
        )
        return

    await message.answer(
        f"Привет, @{message.from_user.username or message.from_user.id}!\n"
        f"Ваш баланс: {user.balance}₽",
        reply_markup=user_menu(),
    )


@dp.message(CommandStart())
async def start_command_handler(message: Message) -> None:
    await send_start(message)


@dp.message(F.text.func(lambda text: bool(text) and text.strip().lower() in START_TEXTS))
async def start_text_handler(message: Message) -> None:
    await send_start(message)


@dp.message(Command("admin"))
async def admin_command_handler(message: Message) -> None:
    if not is_admin(message.from_user.id):
        await message.answer("Недостаточно прав.")
        return
    await message.answer("Админ-панель", reply_markup=admin_menu())


@dp.message(F.text.func(lambda text: bool(text) and text.strip().lower() in ADMIN_TEXTS))
async def admin_text_handler(message: Message) -> None:
    await admin_command_handler(message)


@dp.callback_query(F.data == "check_sub")
async def check_sub_handler(callback: CallbackQuery) -> None:
    ok, error_text = await check_channel_subscription(callback.from_user.id)
    if error_text:
        await callback.message.answer(error_text)
    elif ok:
        await callback.message.answer("Подписка подтверждена ✅")
    else:
        await callback.message.answer(f"Вы ещё не подписаны на {_channel_hint()}")
    await callback.answer()


@dp.callback_query(F.data == "cabinet")
async def cabinet_handler(callback: CallbackQuery) -> None:
    user = db.get_or_create_user(callback.from_user.id, callback.from_user.username)
    subscriptions = db.get_subscriptions(user.user_id)
    await callback.message.answer(
        f"Личный кабинет\nБаланс: {user.balance}₽\nАктивных/исторических подписок: {len(subscriptions)}"
    )
    await callback.answer()


@dp.callback_query(F.data == "my_subs")
async def my_subs_handler(callback: CallbackQuery) -> None:
    subs = db.get_subscriptions(callback.from_user.id)
    if not subs:
        await callback.message.answer("У вас пока нет подписок.")
    else:
        text = ["Ваши подписки:"]
        for row in subs[:10]:
            text.append(
                f"#{row['id']} • {row['plan_days']} дн. • {row['status']} • remnawave_id={row['remnawave_id'] or '-'}"
            )
        await callback.message.answer("\n".join(text))
    await callback.answer()


@dp.callback_query(F.data == "buy_30")
async def buy_handler(callback: CallbackQuery) -> None:
    is_subscribed, error_text = await check_channel_subscription(callback.from_user.id)
    if not is_subscribed:
        await callback.message.answer(
            error_text or "Сначала подпишитесь на канал и подтвердите подписку."
        )
        await callback.answer()
        return

    user = db.get_or_create_user(callback.from_user.id, callback.from_user.username)
    if user.balance < settings.plan_cost:
        await callback.message.answer(
            f"Недостаточно средств. Стоимость {settings.plan_cost}₽, ваш баланс {user.balance}₽"
        )
        await callback.answer()
        return

    try:
        created = await remnawave.create_vpn_subscription(user.user_id, settings.plan_days)
        remnawave_id = str(created.get("id") or created.get("uuid") or created.get("subscriptionId") or "")
    except Exception as error:  # noqa: BLE001
        await callback.message.answer(f"Ошибка при создании подписки в Remnawave: {error}")
        await callback.answer()
        return

    db.update_balance(user.user_id, -settings.plan_cost, callback.from_user.username)
    db.create_subscription(user.user_id, settings.plan_days, remnawave_id)

    await callback.message.answer(
        f"Покупка успешна ✅\nСписано: {settings.plan_cost}₽\nПериод: {settings.plan_days} дней\nID в панели: {remnawave_id or '-'}"
    )
    await callback.answer()


@dp.callback_query(F.data == "admin_balance")
async def admin_balance_start(callback: CallbackQuery, state: FSMContext) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer("Недостаточно прав", show_alert=True)
        return
    await state.set_state(AdminBalanceState.waiting_for_user_id)
    await callback.message.answer("Введите ID пользователя, которому изменить баланс:")
    await callback.answer()


@dp.message(AdminBalanceState.waiting_for_user_id)
async def admin_balance_user_id(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        await state.clear()
        return
    if not message.text or not message.text.isdigit():
        await message.answer("Нужен числовой user_id.")
        return
    await state.update_data(target_user_id=int(message.text))
    await state.set_state(AdminBalanceState.waiting_for_delta)
    await message.answer("Введите сумму изменения, например +500 или -200")


@dp.message(AdminBalanceState.waiting_for_delta)
async def admin_balance_delta(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        await state.clear()
        return

    raw = (message.text or "").strip()
    try:
        delta = int(raw)
    except ValueError:
        await message.answer("Неверный формат суммы. Пример: 300 или -150")
        return

    data = await state.get_data()
    target_user_id = data["target_user_id"]
    new_balance = db.update_balance(target_user_id, delta)
    await state.clear()

    await message.answer(
        f"Баланс пользователя {target_user_id} изменён на {delta:+d}₽. Текущий баланс: {new_balance}₽"
    )


async def main() -> None:
    if not settings.bot_token:
        raise RuntimeError("BOT_TOKEN is not set")
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
