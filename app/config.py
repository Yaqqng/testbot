from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(slots=True)
class Settings:
    bot_token: str
    main_channel: str
    admin_ids: set[int]
    remnawave_base_url: str
    remnawave_api_key: str
    db_path: str = "bot.sqlite3"



def load_settings() -> Settings:
    admin_raw = os.getenv("ADMIN_IDS", "")
    admin_ids = {int(x.strip()) for x in admin_raw.split(",") if x.strip()}

    return Settings(
        bot_token=os.getenv("BOT_TOKEN", ""),
        main_channel=os.getenv("MAIN_CHANNEL", ""),
        admin_ids=admin_ids,
        remnawave_base_url=os.getenv("REMNAWAVE_BASE_URL", ""),
        remnawave_api_key=os.getenv("REMNAWAVE_API_KEY", ""),
        db_path=os.getenv("DB_PATH", "bot.sqlite3"),
    )
