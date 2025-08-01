import aioredis
import os

class RedisPubSub:
    def __init__(self, redis_url: str, redis_port: int, redis_username: str, redis_password: str):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost")
        self.redis_port = os.getenv("REDIS_PORT", 6379)
        self.redis_username = os.getenv("REDIS_USERNAME", "default")
        self.redis_password = os.getenv("REDIS_PASSWORD", "default")
        self.redis = None

    async def connect(self):
        self.redis = await aioredis.from_url(
            f"redis://{self.redis_username}:{self.redis_password}@{self.redis_url}:{self.redis_port}",
            decode_responses=True
        )

    async def publish(self, channel: str, message: str):
        if self.redis:
            await self.redis.publish(channel, message)

    async def subscribe(self, channel: str):
        if self.redis:
            pubsub = self.redis.pubsub()
            await pubsub.subscribe(channel)
            return pubsub

    async def close(self):
        if self.redis:
            await self.redis.close()