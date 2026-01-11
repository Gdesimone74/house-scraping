from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import parse_qs, urlparse, urlencode
from urllib.request import Request, urlopen
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
            SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

            if not SUPABASE_URL or not SUPABASE_KEY:
                raise Exception(f"Missing env vars")

            # Parse query parameters
            parsed_url = urlparse(self.path)
            params = parse_qs(parsed_url.query)

            # Get filter parameters
            barrio = params.get("barrio", [None])[0]
            tipo = params.get("tipo", [None])[0]
            fuente = params.get("fuente", [None])[0]
            ordenar = params.get("ordenar", ["fecha"])[0]
            page = int(params.get("page", ["1"])[0])
            limit = min(int(params.get("limit", ["20"])[0]), 100)

            # Build query params for Supabase
            query_params = [
                ("activo", "eq.true"),
                ("select", "*"),
                ("offset", str((page - 1) * limit)),
                ("limit", str(limit))
            ]

            # Apply filters
            if barrio:
                query_params.append(("barrio", f"eq.{barrio}"))
            if tipo and tipo in ["departamento", "casa"]:
                query_params.append(("tipo", f"eq.{tipo}"))
            if fuente and fuente in ["mercadolibre", "zonaprop", "argenprop"]:
                query_params.append(("fuente", f"eq.{fuente}"))

            # Apply sorting
            if ordenar == "precio_asc":
                query_params.append(("order", "precio.asc.nullslast"))
            elif ordenar == "precio_desc":
                query_params.append(("order", "precio.desc.nullslast"))
            else:
                query_params.append(("order", "fecha_primer_visto.desc"))

            # Build URL
            url = f"{SUPABASE_URL}/rest/v1/propiedades?{urlencode(query_params)}"

            # Make request
            req = Request(url)
            req.add_header("apikey", SUPABASE_KEY)
            req.add_header("Authorization", f"Bearer {SUPABASE_KEY}")
            req.add_header("Content-Type", "application/json")
            req.add_header("Prefer", "count=exact")

            with urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode())

                # Get count from header
                total = 0
                content_range = response.headers.get("Content-Range")
                if content_range and "/" in content_range:
                    total_str = content_range.split("/")[-1]
                    if total_str != "*":
                        total = int(total_str)
                if total == 0:
                    total = len(data)

            total_pages = (total + limit - 1) // limit if total > 0 else 1

            # Transform response
            propiedades = []
            for row in data:
                propiedades.append({
                    "_id": row["id"],
                    "externalId": row["external_id"],
                    "url": row["url"],
                    "titulo": row["titulo"],
                    "precio": float(row["precio"]) if row["precio"] else None,
                    "moneda": row["moneda"],
                    "barrio": row["barrio"],
                    "tipo": row["tipo"],
                    "ambientes": row["ambientes"],
                    "dormitorios": row["dormitorios"],
                    "banos": row["banos"],
                    "metrosCuadrados": float(row["metros_cuadrados"]) if row["metros_cuadrados"] else None,
                    "metrosTotales": float(row["metros_totales"]) if row["metros_totales"] else None,
                    "fotos": row["fotos"] or [],
                    "descripcion": row["descripcion"],
                    "fuente": row["fuente"],
                    "operacion": row["operacion"],
                    "fechaPrimerVisto": row["fecha_primer_visto"],
                    "fechaUltimaActualizacion": row["fecha_ultima_actualizacion"],
                    "activo": row["activo"]
                })

            result = {
                "propiedades": propiedades,
                "total": total,
                "page": page,
                "limit": limit,
                "totalPages": total_pages
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
