import os
import requests
from typing import Optional, Dict, Any, List

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

def supabase_request(
    table: str,
    method: str = "GET",
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    headers_extra: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """Make a request to Supabase REST API"""

    url = f"{SUPABASE_URL}/rest/v1/{table}"

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

    if headers_extra:
        headers.update(headers_extra)

    response = requests.request(
        method=method,
        url=url,
        headers=headers,
        params=params,
        json=data,
        timeout=30
    )

    response.raise_for_status()

    result = {
        "data": response.json() if response.text else [],
        "count": None
    }

    # Get count from header if present
    content_range = response.headers.get("Content-Range")
    if content_range and "/" in content_range:
        total = content_range.split("/")[-1]
        if total != "*":
            result["count"] = int(total)

    return result

def get_propiedades(
    barrio: Optional[str] = None,
    tipo: Optional[str] = None,
    fuente: Optional[str] = None,
    precio_min: Optional[float] = None,
    precio_max: Optional[float] = None,
    ordenar: str = "fecha",
    page: int = 1,
    limit: int = 20
) -> Dict[str, Any]:
    """Get properties with filters"""

    params = {
        "activo": "eq.true",
        "select": "*"
    }

    # Apply filters
    if barrio:
        params["barrio"] = f"eq.{barrio}"
    if tipo and tipo in ["departamento", "casa"]:
        params["tipo"] = f"eq.{tipo}"
    if fuente and fuente in ["mercadolibre", "zonaprop", "argenprop"]:
        params["fuente"] = f"eq.{fuente}"
    if precio_min:
        params["precio"] = f"gte.{precio_min}"
    if precio_max:
        if "precio" in params:
            params["precio"] = f"gte.{precio_min}&precio=lte.{precio_max}"
        else:
            params["precio"] = f"lte.{precio_max}"

    # Apply sorting
    if ordenar == "precio_asc":
        params["order"] = "precio.asc.nullslast"
    elif ordenar == "precio_desc":
        params["order"] = "precio.desc.nullslast"
    else:
        params["order"] = "fecha_primer_visto.desc"

    # Apply pagination
    offset = (page - 1) * limit
    params["offset"] = offset
    params["limit"] = limit

    # Request with count
    headers_extra = {"Prefer": "count=exact"}

    return supabase_request("propiedades", params=params, headers_extra=headers_extra)

def get_propiedad(id: str) -> Optional[Dict[str, Any]]:
    """Get a single property by ID"""
    params = {
        "id": f"eq.{id}",
        "select": "*"
    }

    result = supabase_request("propiedades", params=params)

    if result["data"]:
        return result["data"][0]
    return None

def get_historial(propiedad_id: str) -> List[Dict[str, Any]]:
    """Get price history for a property"""
    params = {
        "propiedad_id": f"eq.{propiedad_id}",
        "select": "*",
        "order": "fecha_cambio.desc"
    }

    result = supabase_request("historial_precios", params=params)
    return result["data"]
