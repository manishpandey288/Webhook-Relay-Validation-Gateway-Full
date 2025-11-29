import time
from collections import defaultdict
from typing import Optional
from config import settings

class RateLimiter:
    """
    Simple in-memory rate limiter using sliding window
    """
    def __init__(self):
        # Store request timestamps per tenant
        # Format: {tenant_id: [timestamp1, timestamp2, ...]}
        self.requests = defaultdict(list)
        self.last_cleanup = time.time()
        self.cleanup_interval = 60  # Clean up old entries every 60 seconds
    
    def _cleanup_old_entries(self, now: float, window: int = 1):
        """Remove entries older than the window"""
        cutoff = now - window
        for tenant_id in list(self.requests.keys()):
            self.requests[tenant_id] = [
                ts for ts in self.requests[tenant_id] if ts > cutoff
            ]
            # Remove empty entries
            if not self.requests[tenant_id]:
                del self.requests[tenant_id]
    
    def check_rate_limit(
        self,
        tenant_id: str,
        limit: int = None,
        window: int = 1
    ) -> tuple:
        """
        Simple sliding window rate limiting
        
        Args:
            tenant_id: Tenant identifier
            limit: Events per window (default from settings)
            window: Time window in seconds (default 1)
            
        Returns:
            (is_allowed, remaining_tokens)
        """
        if limit is None:
            limit = settings.DEFAULT_RATE_LIMIT
        
        now = time.time()
        
        # Periodic cleanup
        if now - self.last_cleanup > self.cleanup_interval:
            self._cleanup_old_entries(now, window)
            self.last_cleanup = now
        
        # Get requests in current window
        cutoff = now - window
        tenant_requests = [
            ts for ts in self.requests[tenant_id] if ts > cutoff
        ]
        
        # Check if limit exceeded
        if len(tenant_requests) >= limit:
            return False, 0
        
        # Add current request
        tenant_requests.append(now)
        self.requests[tenant_id] = tenant_requests
        
        remaining = limit - len(tenant_requests)
        return True, remaining
