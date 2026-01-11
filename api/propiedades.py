from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import parse_qs, urlparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api._lib.database import get_propiedades

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Parse query parameters
            parsed_url = urlparse(self.path)
            params = parse_qs(parsed_url.query)

            # Get filter parameters
            barrio = params.get("barrio", [None])[0]
            tipo = params.get("tipo", [None])[0]
            precio_min = params.get("precio_min", [None])[0]
            precio_max = params.get("precio_max", [None])[0]
            fuente = params.get("fuente", [None])[0]
            ordenar = params.get("ordenar", ["fecha"])[0]
            page = int(params.get("page", ["1"])[0])
            limit = min(int(params.get("limit", ["20"])[0]), 100)

            # Get properties
            result = get_propiedades(
                barrio=barrio,
                tipo=tipo,
                fuente=fuente,
                precio_min=float(precio_min) if precio_min else None,
                precio_max=float(precio_max) if precio_max else None,
                ordenar=ordenar,
                page=page,
                limit=limit
            )

            # Calculate pagination
            total = result["count"] or len(result["data"])
            total_pages = (total + limit - 1) // limit if total > 0 else 1

            # Transform response
            propiedades = []
            for row in result["data"]:
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

            response = {
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
            self.wfile.write(json.dumps(response).encode())

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
