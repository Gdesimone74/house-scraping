# Database utilities for GitHub Actions scraper only
# Vercel endpoints use urllib directly

import os
from typing import Optional, Dict, Any, List

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

def get_supabase():
    """Get Supabase client for scraper (uses requests)"""
    # Only import when actually called (not at module load)
    import requests

    class SupabaseClient:
        def __init__(self, url, key):
            self.url = url
            self.key = key
            self.session = requests.Session()
            self.session.headers.update({
                "apikey": key,
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            })

        def table(self, name):
            return SupabaseTable(self, name)

    class SupabaseTable:
        def __init__(self, client, name):
            self.client = client
            self.name = name
            self.url = f"{client.url}/rest/v1/{name}"

        def upsert(self, data, on_conflict=None):
            headers = {"Prefer": "resolution=merge-duplicates"}
            response = self.client.session.post(self.url, json=data, headers=headers)
            response.raise_for_status()
            return type('Result', (), {'data': response.json() if response.text else []})()

        def update(self, data):
            return SupabaseQuery(self, "PATCH", data)

        def select(self, columns="*"):
            return SupabaseQuery(self, "GET", select=columns)

    class SupabaseQuery:
        def __init__(self, table, method, data=None, select="*"):
            self.table = table
            self.method = method
            self.data = data
            self.params = {"select": select} if method == "GET" else {}
            self.filters = []

        def eq(self, column, value):
            self.filters.append(f"{column}=eq.{value}")
            return self

        def lt(self, column, value):
            self.filters.append(f"{column}=lt.{value}")
            return self

        def execute(self):
            url = self.table.url
            if self.filters:
                url += "?" + "&".join(self.filters)
                if self.params:
                    url += "&" + "&".join(f"{k}={v}" for k, v in self.params.items())
            elif self.params:
                url += "?" + "&".join(f"{k}={v}" for k, v in self.params.items())

            if self.method == "GET":
                response = self.table.client.session.get(url)
            else:
                response = self.table.client.session.patch(url, json=self.data)

            response.raise_for_status()
            return type('Result', (), {'data': response.json() if response.text else []})()

    return SupabaseClient(SUPABASE_URL, SUPABASE_KEY)
