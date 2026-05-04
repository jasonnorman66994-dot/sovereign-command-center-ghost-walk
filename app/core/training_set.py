# app/core/training_set.py
import redis

r = redis.Redis(host='localhost', port=6379, db=0)

async def update_training_set(incident_id: str, label: str = "FALSE_POSITIVE"):
    """
    Adds the incident_id to a Redis set for negative training examples.
    Handles Redis connection errors gracefully.
    """
    key = f"training_set:{label}"
    try:
        r.sadd(key, incident_id)
    except Exception as e:
        # Log or print the error, but do not crash the app
        print(f"[WARNING] Could not update Redis training set: {e}")
