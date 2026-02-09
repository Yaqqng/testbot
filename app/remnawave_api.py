from __future__ import annotations

import httpx


class RemnawaveClient:
    def __init__(self, base_url: str, api_key: str, subscription_endpoint: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.subscription_endpoint = "/" + subscription_endpoint.strip("/")
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "X-API-Key": api_key,
            "Content-Type": "application/json",
        }

    async def create_vpn_subscription(self, telegram_user_id: int, days: int) -> dict:
        payload_variants = [
            {
                "external_id": str(telegram_user_id),
                "duration_days": days,
                "note": "Telegram bot purchase",
            },
            {
                "userExternalId": str(telegram_user_id),
                "days": days,
                "comment": "Telegram bot purchase",
            },
        ]

        async with httpx.AsyncClient(timeout=20) as client:
            for payload in payload_variants:
                response = await client.post(
                    f"{self.base_url}{self.subscription_endpoint}",
                    headers=self.headers,
                    json=payload,
                )
                if response.is_success:
                    return response.json()

            response.raise_for_status()
            return response.json()
