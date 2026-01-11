import os
from supabase import create_client, Client
from typing import Optional

_client: Optional[Client] = None

def get_supabase() -> Client:
    """Get Supabase client (singleton pattern)"""
    global _client

    if _client is None:
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables are required")

        _client = create_client(supabase_url, supabase_key)

    return _client
