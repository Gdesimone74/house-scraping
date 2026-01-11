from http.server import BaseHTTPRequestHandler
import json
import re
import sys
import os
from bson import ObjectId

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from api._lib.database import get_propiedades_collection

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Extract ID from path
            match = re.search(r"/api/propiedad/([a-fA-F0-9]{24})", self.path)
            if not match:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Invalid property ID"}).encode())
                return

            property_id = match.group(1)

            # Get collection and find property
            collection = get_propiedades_collection()
            propiedad = collection.find_one({"_id": ObjectId(property_id)})

            if not propiedad:
                self.send_response(404)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Property not found"}).encode())
                return

            # Convert ObjectId and dates
            propiedad["_id"] = str(propiedad["_id"])
            for date_field in ["fechaPrimerVisto", "fechaUltimaActualizacion", "fechaPublicacion"]:
                if date_field in propiedad and propiedad[date_field]:
                    propiedad[date_field] = propiedad[date_field].isoformat()

            # Send response
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
