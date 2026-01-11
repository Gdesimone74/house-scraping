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

            # Get Supabase client and query
            supabase = get_supabase()
            result = supabase.table("propiedades").select("*").eq("id", property_id).single().execute()

            if not result.data:
                self.send_response(404)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Property not found"}).encode())
                return

            row = result.data

            # Transform to match frontend expectations
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
