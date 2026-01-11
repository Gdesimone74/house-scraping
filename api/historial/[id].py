from http.server import BaseHTTPRequestHandler
import json
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from api._lib.database import get_supabase

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
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

            # Get Supabase client and query price history
            supabase = get_supabase()
            result = supabase.table("historial_precios") \
                .select("*") \
                .eq("propiedad_id", property_id) \
                .order("fecha_cambio", desc=True) \
                .execute()

            historial = []
            for row in result.data:
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
