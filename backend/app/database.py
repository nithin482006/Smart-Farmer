import logging
from typing import Optional
from supabase import create_client, Client
from app.core.config import settings

logger = logging.getLogger(__name__)

supabase: Optional[Client] = None

try:
    if settings.SUPABASE_URL and settings.SUPABASE_KEY and "placeholder" not in settings.SUPABASE_KEY:
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    else:
        logger.warning("Supabase credentials not fully configured. Using fallback local storage mode.")
except Exception as e:
    logger.error(f"Failed to initialize Supabase client: {e}")
    supabase = None


def get_supabase() -> Optional[Client]:
    return supabase
