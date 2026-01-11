from http.server import BaseHTTPRequestHandler
import json
import re
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
            SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

            # Extract ID from path (UUID format)
            match = re.search(r"/api/propiedad/([a-fA-F0-9-]{36})", self.path)
            if not match:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Invalid property ID"}).encode())
                return

            property_id = match.group(1)

            # Build URL
            url = f"{SUPABASE_URL}/rest/v1/propiedades?id=eq.{property_id}&select=*"

            # Make request
            req = Request(url)
            req.add_header("apikey", SUPABASE_KEY)
            req.add_header("Authorization", f"Bearer {SUPABASE_KEY}")

            with urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode())

            if not data:
                self.send_response(404)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Property not found"}).encode())
                return

            row = data[0]

            propiedad = {
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
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(propiedad).encode())

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
