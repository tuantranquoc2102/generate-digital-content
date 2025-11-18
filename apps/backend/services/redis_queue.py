import os
from redis import Redis
from rq import Queue

REDIS_HOST=os.getenv("REDIS_HOST","localhost")
REDIS_PORT=int(os.getenv("REDIS_PORT","6379"))

# Job timeout: 2 hours for very long videos (up to 1 hour content)
JOB_TIMEOUT = int(os.getenv("JOB_TIMEOUT", "7200"))  # 2 hours

redis_conn = Redis(host=REDIS_HOST, port=REDIS_PORT)
q = Queue("transcribe", connection=redis_conn, default_timeout=JOB_TIMEOUT)