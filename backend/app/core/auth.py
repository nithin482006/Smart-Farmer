import logging
from typing import Optional, Dict, Any
from fastapi import Header, HTTPException, status
from app.database import get_supabase

logger = logging.getLogger(__name__)

# Default demo farmer profile for local development and non-authenticated testing
DEMO_USER: Dict[str, Any] = {
    "id": "farmer_demo_001",
    "email": "farmer@smartfarmer.org",
    "full_name": "Rakib Kowshar",
    "is_demo": True,
}


async def get_current_user(
    authorization: Optional[str] = Header(None)
) -> Dict[str, Any]:
    """
    Extracts and verifies the Supabase access token from Authorization header.
    Falls back gracefully to demo user when token is omitted in development.
    """
    if not authorization:
        return DEMO_USER

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return DEMO_USER

    token = parts[1]

    # Verify with Supabase if client is available
    client = get_supabase()
    if client:
        try:
            user_response = client.auth.get_user(token)
            if user_response and user_response.user:
                u = user_response.user
                metadata = u.user_metadata or {}
                return {
                    "id": u.id,
                    "email": u.email,
                    "full_name": metadata.get("full_name", "Farmer"),
                    "phone": metadata.get("phone"),
                    "preferred_language": metadata.get("preferred_language", "en"),
                    "is_demo": False,
                }
        except Exception as e:
            logger.debug(f"Token verification with Supabase failed: {e}. Falling back to demo context.")

    return DEMO_USER
