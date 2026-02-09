# Telegram-бот для продажи VPN (Remnawave)

Реализовано:
- Личный кабинет пользователя.
- Админ-панель внутри бота.
- Проверка обязательной подписки на основной Telegram-канал.
- Управление балансом пользователей через админ-панель.
- Покупка VPN-подписки с попыткой создания подписки через API Remnawave.

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
- `/start` — меню и личный кабинет.
- `/admin` — админ-панель (только для `ADMIN_IDS`).

## Примечание по Remnawave
В `app/remnawave_api.py` использован базовый пример запроса `POST /api/subscriptions`.
Если ваша версия панели использует другой endpoint или формат payload, скорректируйте метод `create_vpn_subscription` по вашей документации.
