import hmac
import hashlib
from typing import Optional

def verify_hmac_signature(
    body: bytes,
    signature: Optional[str],
    secret: str
) -> bool:
    """
    Verify HMAC signature from webhook payload
    
    Args:
        body: Raw request body bytes
        signature: Signature from header (format: sha256=...)
        secret: Shared secret key
        
    Returns:
        True if signature is valid, False otherwise
    """
    if not signature:
        return False
    
    # Remove 'sha256=' prefix if present
    if signature.startswith('sha256='):
        signature = signature[7:]
    
    # Calculate expected signature
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        body,
        hashlib.sha256
    ).hexdigest()
    
    # Constant-time comparison to prevent timing attacks
    return hmac.compare_digest(expected_signature, signature)

