from redis.asyncio import Redis
from src.app.utils.config import Config

JTI_EXPIRY = 3600

# to run the Redis on docker
# docker run -d --name my-redis -p 6379:6379 redis:7-alpine
token_blocklist: Redis = Redis.from_url(
    Config.REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
)


async def add_jti_to_blocklist(jti: str) -> None:
    await token_blocklist.set(name=jti, value="", ex=JTI_EXPIRY)


async def is_token_in_blocklist(jti: str) -> bool:
    return await token_blocklist.get(jti) is not None
