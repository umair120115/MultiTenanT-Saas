# debug_redis.py
import os
import redis
import ssl
from dotenv import load_dotenv
load_dotenv()
# Load your URL (hardcode it here temporarily if os.getenv fails)
redis_url = os.getenv("REDIS_URL")

print(f"Testing connection to: {redis_url}")

try:
    # 1. Parse the URL to see if python reads it correctly
    r = redis.from_url(
        redis_url, 
        ssl_cert_reqs=ssl.CERT_NONE # This matches your settings config
    )
    
    # 2. Try a ping
    print("Attempting PING...")
    response = r.ping()
    print(f"Success! Redis responded with: {response}")
    
    # 3. Try a write
    r.set("debug_key", "debug_value")
    print(f"Write successful: {r.get('debug_key')}")

except Exception as e:
    print("\n--- CONNECTION FAILED ---")
    print(e)