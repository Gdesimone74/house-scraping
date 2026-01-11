from http.server import BaseHTTPRequestHandler
import json
import re
from urllib.request import Request, urlopen
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
            SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

            # Extract property ID from path (UUID format)
            match = re.search(r"/api/historial/([a-fA-F0-9-]{36})", self.path)
            if not match:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Invalid property ID"}).encode())
                return

            property_id = match.group(1)

            # Build URL
            url = f"{SUPABASE_URL}/rest/v1/historial_precios?propiedad_id=eq.{property_id}&select=*&order=fecha_cambio.desc"

            # Make request
            req = Request(url)
            req.add_header("apikey", SUPABASE_KEY)
            req.add_header("Authorization", f"Bearer {SUPABASE_KEY}")

            with urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode())

            historial = []
            for row in data:
                historial.append({
                    "id": row["id"],
                    "precioAnterior": float(row["precio_anterior"]) if row["precio_anterior"] else None,
                    "precioNuevo": float(row["precio_nuevo"]) if row["precio_nuevo"] else None,
                    "moneda": row["moneda"],
                    "variacionPorcentaje": float(row["variacion_porcentaje"]) if row["variacion_porcentaje"] else None,
                    "fechaCambio": row["fecha_cambio"]
                })

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"historial": historial}).encode())

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
