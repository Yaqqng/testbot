from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(slots=True)
class Settings:
    bot_token: str
    main_channel: str
    main_channel_url: str
    admin_ids: set[int]
    remnawave_base_url: str
    remnawave_api_key: str
    remnawave_subscription_endpoint: str
    plan_days: int
    plan_cost: int
    db_path: str = "bot.sqlite3"


def load_settings() -> Settings:
    admin_raw = os.getenv("ADMIN_IDS", "")
    admin_ids = {int(x.strip()) for x in admin_raw.split(",") if x.strip()}

    return Settings(
        bot_token=os.getenv("BOT_TOKEN", ""),
        main_channel=os.getenv("MAIN_CHANNEL", ""),
        main_channel_url=os.getenv("MAIN_CHANNEL_URL", ""),
        admin_ids=admin_ids,
        remnawave_base_url=os.getenv("REMNAWAVE_BASE_URL", ""),
        remnawave_api_key=os.getenv("REMNAWAVE_API_KEY", ""),
        remnawave_subscription_endpoint=os.getenv(
            "REMNAWAVE_SUBSCRIPTION_ENDPOINT", "/api/subscriptions"
        ),
        plan_days=int(os.getenv("PLAN_DAYS", "30")),
        plan_cost=int(os.getenv("PLAN_COST", "299")),
        db_path=os.getenv("DB_PATH", "bot.sqlite3"),
    )
