"""Rate Limiter based on remoteIP addresses."""


from slowapi import Limiter
from slowapi.util import get_remote_address

DEFAULT_RATE_LIMIT: str = "10 per minute"

# Initialize rate limiter
limiter =Limiter(key_func=get_remote_address, default_limits=[DEFAULT_RATE_LIMIT])


