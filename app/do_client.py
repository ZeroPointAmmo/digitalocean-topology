import asyncio
from typing import Any

import httpx

API_BASE = "https://api.digitalocean.com"


class DOAPIError(Exception):
    def __init__(self, status_code: int, message: str, path: str):
        super().__init__(f"{status_code} on {path}: {message}")
        self.status_code = status_code
        self.message = message
        self.path = path


class DOClient:
    def __init__(self, token: str, *, timeout: float = 15.0):
        self._client = httpx.AsyncClient(
            base_url=API_BASE,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            timeout=timeout,
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "DOClient":
        return self

    async def __aexit__(self, *_exc: Any) -> None:
        await self.aclose()

    async def get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return await self._request("GET", path, params=params)

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        backoffs = [0.0, 1.0, 2.0]
        last_exc: Exception | None = None
        for delay in backoffs:
            if delay:
                await asyncio.sleep(delay)
            try:
                resp = await self._client.request(method, path, params=params)
            except httpx.RequestError as e:
                last_exc = e
                continue
            if resp.status_code in (429, 500, 502, 503, 504):
                last_exc = DOAPIError(resp.status_code, resp.text[:300], path)
                continue
            if resp.status_code >= 400:
                raise DOAPIError(resp.status_code, resp.text[:500], path)
            if not resp.content:
                return {}
            return resp.json()
        if last_exc:
            raise last_exc
        raise DOAPIError(0, "request failed without explicit error", path)

    async def paginate(
        self,
        path: str,
        key: str,
        *,
        per_page: int = 200,
        params: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        page_params = dict(params or {})
        page_params["per_page"] = per_page
        page_params["page"] = 1
        while True:
            data = await self.get(path, params=page_params)
            items.extend(data.get(key, []) or [])
            links = (data.get("links") or {}).get("pages") or {}
            if not links.get("next"):
                break
            page_params["page"] += 1
        return items
