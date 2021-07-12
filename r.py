import redis
import os

def connect():
    return redis.from_url(
        url=os.environ.get('REDIS_URL'),
        decode_responses=True,
    )