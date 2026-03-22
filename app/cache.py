import json
from collections.abc import Iterable
from typing import Any

from redis import Redis

from app.config import settings


class CacheClient:
    def __init__(self) -> None:
        self._client = Redis.from_url(settings.redis_url, decode_responses=True)
        self.ttl = settings.redis_cache_ttl

    def ping(self) -> bool:
        return bool(self._client.ping())

    def get_json(self, key: str) -> Any | None:
        value = self._client.get(key)
        if value is None:
            return None
        return json.loads(value)

    def set_json(self, key: str, value: Any) -> None:
        self._client.setex(key, self.ttl, json.dumps(value))

    def delete_keys(self, keys: Iterable[str]) -> None:
        keys = list(keys)
        if not keys:
            return
        self._client.delete(*keys)

    def delete_pattern(self, pattern: str) -> None:
        keys = list(self._client.scan_iter(match=pattern))
        if keys:
            self._client.delete(*keys)


cache_client = CacheClient()
