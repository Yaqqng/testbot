# Telegram-бот для продажи VPN (Remnawave)

Реализовано:
- Личный кабинет пользователя.
- Админ-панель внутри бота.
- Проверка обязательной подписки на основной Telegram-канал.
- Управление балансом пользователей через админ-панель.
- Покупка VPN-подписки с созданием подписки через API Remnawave.
- Поддержка как slash-команд (`/start`, `/admin`), так и текстовых команд (`старт`, `админ`).

## Запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# заполните .env
python bot.py
```

## Команды
- `/start` или `старт` — меню и личный кабинет.
- `/admin` или `админ` — админ-панель (только для `ADMIN_IDS`).

## Переменные окружения
- `MAIN_CHANNEL` — username канала (`@channel`) или числовой chat id.
- `MAIN_CHANNEL_URL` — ссылка для пользователя (`https://t.me/...`) в тексте подсказок.
- `REMNAWAVE_SUBSCRIPTION_ENDPOINT` — endpoint создания подписки (по умолчанию `/api/subscriptions`).
- `PLAN_DAYS` — длительность VPN-подписки в днях.
- `PLAN_COST` — стоимость VPN-подписки в рублях.

## Примечание по Remnawave
В клиенте добавлены 2 варианта payload и 2 заголовка авторизации (`Authorization: Bearer ...` и `X-API-Key`), чтобы повысить совместимость с разными версиями панели.
Если ваша панель использует другой формат, скорректируйте `create_vpn_subscription` в `app/remnawave_api.py`.
