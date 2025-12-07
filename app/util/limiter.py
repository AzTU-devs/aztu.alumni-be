from fastapi import Depends, Request, HTTPException
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import redis.asyncio as redis

# Startup init
async def init_ddos_limiter():
    redis_client = await redis.from_url(
        "redis://localhost:6379",
        encoding="utf-8",
        decode_responses=True
    )
    await FastAPILimiter.init(redis_client)


# Strong IP extractor (handles proxies like Cloudflare / Nginx)
async def get_real_ip(request: Request) -> str:
    if "cf-connecting-ip" in request.headers:
        return request.headers["cf-connecting-ip"]

    if "x-forwarded-for" in request.headers:
        return request.headers["x-forwarded-for"].split(",")[0].strip()

    return request.client.host


from fastapi import Depends, Request, Response
from fastapi_limiter.depends import RateLimiter

def create_limiter(times: int = 10, seconds: int = 60):
    """
    Returns a RateLimiter dependency for FastAPI routes.
    Handles request and response correctly.
    """
    async def limiter_dependency(request: Request, response: Response):
        return await RateLimiter(times=times, seconds=seconds)(request, response)

    return Depends(limiter_dependency)


# DDoS protection limiter
def ddos_protector(times: int = 20, seconds: int = 60):
    """
    Protect against DoS attack

    Default:
      - 20 requests per minute PER IP
    """
    return Depends(
        RateLimiter(
            times=times,
            seconds=seconds,
            identifier=get_real_ip
        )
    )


# Very strict limiter (login, signup, OTP)
def brute_force_protector():
    """
    For login / sensitive routes
    - 5 requests per 5 minutes
    """
    return Depends(
        RateLimiter(
            times=5,
            seconds=300,
            identifier=get_real_ip
        )
    )