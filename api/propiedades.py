from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import parse_qs, urlparse
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api._lib.database import get_propiedades_collection
from api._lib.models import BARRIOS_CABA

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
            page = int(params.get("page", [1])[0])
            limit = min(int(params.get("limit", [20])[0]), 100)

            # Build query
            query = {"activo": True}

            if barrio:
                query["barrio"] = barrio
            if tipo and tipo in ["departamento", "casa"]:
                query["tipo"] = tipo
            if fuente and fuente in ["mercadolibre", "zonaprop", "argenprop"]:
                query["fuente"] = fuente
            if precio_min:
                query["precio"] = query.get("precio", {})
                query["precio"]["$gte"] = float(precio_min)
            if precio_max:
                query["precio"] = query.get("precio", {})
                query["precio"]["$lte"] = float(precio_max)

            # Determine sort order
            sort_field = "fechaPrimerVisto"
            sort_order = -1  # Descending (newest first)

            if ordenar == "precio_asc":
                sort_field = "precio"
                sort_order = 1
            elif ordenar == "precio_desc":
                sort_field = "precio"
                sort_order = -1

            # Get collection and execute query
            collection = get_propiedades_collection()

            # Get total count
            total = collection.count_documents(query)

            # Calculate pagination
            skip = (page - 1) * limit
            total_pages = (total + limit - 1) // limit

            # Fetch properties
            cursor = collection.find(query).sort(sort_field, sort_order).skip(skip).limit(limit)

            propiedades = []
            for doc in cursor:
                doc["_id"] = str(doc["_id"])
                # Convert datetime objects to ISO strings
                for date_field in ["fechaPrimerVisto", "fechaUltimaActualizacion", "fechaPublicacion"]:
                    if date_field in doc and doc[date_field]:
                        doc[date_field] = doc[date_field].isoformat()
                propiedades.append(doc)

            # Build response
            response = {
                "propiedades": propiedades,
                "total": total,
                "page": page,
                "limit": limit,
                "totalPages": total_pages
            }

            # Send response
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
