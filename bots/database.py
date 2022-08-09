import os

import redis

from dotenv import load_dotenv


def connect_to_db():
    load_dotenv()
    redis_host = os.environ["REDIS_HOST"]
    redis_port = os.environ["REDIS_PORT"]
    redis_password = os.environ["REDIS_PASSWORD"]
    database = redis.Redis(
        host=redis_host,
        port=redis_port,
        password=redis_password
    )
    return database
