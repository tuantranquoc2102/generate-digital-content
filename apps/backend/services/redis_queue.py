import os
from redis import Redis
from rq import Queue

REDIS_HOST=os.getenv("REDIS_HOST","localhost")
REDIS_PORT=int(os.getenv("REDIS_PORT","6379"))

redis_conn = Redis(host=REDIS_HOST, port=REDIS_PORT)
q = Queue("transcribe", connection=redis_conn)