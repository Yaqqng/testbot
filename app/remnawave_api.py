from __future__ import annotations

import httpx


class RemnawaveClient:
    """Минимальный клиент для панели Remnawave.

    При необходимости скорректируйте endpoint/поля под вашу версию API из документации.
    """

    def __init__(self, base_url: str, api_key: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    async def create_vpn_subscription(self, telegram_user_id: int, days: int) -> dict:
        payload = {
            "external_id": str(telegram_user_id),
            "duration_days": days,
            "note": "Telegram bot purchase",
        }
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                f"{self.base_url}/api/subscriptions",
                headers=self.headers,
                json=payload,
            )
            response.raise_for_status()
            return response.json()
