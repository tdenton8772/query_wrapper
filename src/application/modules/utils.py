import redis

def create_redis_client():
    """Initialize and return a Redis client."""
    return redis.StrictRedis(
        host='localhost',
        port=6379,
        db=0,
        decode_responses=True
    )