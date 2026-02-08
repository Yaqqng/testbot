import logging
import os
import random
import string

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


def generate_digits(length: int = 8) -> str:
    """Return a random string that contains only digits."""
    return "".join(random.choices(string.digits, k=length))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Привет! Я генерирую случайный набор цифр.\n"
        "Используй команду /digits или /digits 12, чтобы задать длину."
    )


async def digits(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    length = 8

    if context.args:
        try:
            length = int(context.args[0])
        except ValueError:
            await update.message.reply_text("Длина должна быть числом, например: /digits 10")
            return

    if length < 1 or length > 128:
        await update.message.reply_text("Выбери длину от 1 до 128.")
        return

    code = generate_digits(length)
    await update.message.reply_text(f"Случайные цифры: {code}")


def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("Не найден TELEGRAM_BOT_TOKEN в переменных окружения")

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("digits", digits))

    app.run_polling()


if __name__ == "__main__":
    main()
