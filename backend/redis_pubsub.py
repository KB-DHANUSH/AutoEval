from redis import asyncio as aioredis
import os

class PubSubManager:
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL","localhost")
        self.redis_port = int(os.getenv("REDIS_PORT", 6379))
        self.redis_username = os.getenv("REDIS_USERNAME", "default")
        self.redis_password = os.getenv("REDIS_PASSWORD", "default")
        self.redis = None

    async def connect(self):
        self.redis = await aioredis.Redis(
            host=self.redis_url,
            username=self.redis_username,
            port=self.redis_port,
            password=self.redis_password,
            decode_responses=True
        )
        await self.redis.ping()

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
    
    def is_subscribed(self, channel: str) -> bool:
        if self.redis:
            return channel in self.redis.pubsub_channels
        return False