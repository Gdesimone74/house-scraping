#!/usr/bin/env python3
"""
Script to run all scrapers and save properties to Supabase.
Designed to be run via GitHub Actions cron job.
"""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api._lib.database import get_supabase
from api._lib.scrapers import MercadoLibreScraper, ZonapropScraper, ArgenpropScraper
from api._lib.models import BARRIOS_CABA

def save_properties(properties: list, supabase) -> dict:
    """
    Save properties to Supabase, handling duplicates with upsert.
    Returns stats about inserted/updated properties.
    """
    stats = {
        "inserted": 0,
        "updated": 0,
        "errors": 0
    }

    for prop in properties:
        try:
            # Prepare data for Supabase (snake_case)
            data = {
                "external_id": prop["externalId"],
                "url": prop["url"],
                "titulo": prop["titulo"],
                "precio": prop.get("precio"),
                "moneda": prop.get("moneda", "USD"),
                "barrio": prop["barrio"],
                "tipo": prop["tipo"],
                "ambientes": prop.get("ambientes"),
                "dormitorios": prop.get("dormitorios"),
                "banos": prop.get("banos"),
                "metros_cuadrados": prop.get("metrosCuadrados"),
                "metros_totales": prop.get("metrosTotales"),
                "fotos": prop.get("fotos", []),
                "descripcion": prop.get("descripcion"),
                "fuente": prop["fuente"],
                "operacion": prop.get("operacion", "venta"),
                "activo": True
            }

            # Try to upsert (insert or update on conflict)
            result = supabase.table("propiedades").upsert(
                data,
                on_conflict="external_id,fuente"
            ).execute()

            if result.data:
                stats["inserted"] += 1
            else:
                stats["updated"] += 1

        except Exception as e:
            print(f"Error saving property {prop.get('externalId')}: {e}")
            stats["errors"] += 1

    return stats

def mark_inactive_properties(supabase, hours: int = 48):
    """
    Mark properties as inactive if they haven't been updated recently.
    """
    cutoff = (datetime.utcnow() - timedelta(hours=hours)).isoformat()

    result = supabase.table("propiedades").update(
        {"activo": False}
    ).eq("activo", True).lt("fecha_ultima_actualizacion", cutoff).execute()

    return len(result.data) if result.data else 0

def main():
    print("=" * 50)
    print(f"Starting scraper at {datetime.now().isoformat()}")
    print("=" * 50)

    # Get Supabase client
    supabase = get_supabase()

    # Initialize scrapers
    scrapers = [
        MercadoLibreScraper(),
        ZonapropScraper(),
        ArgenpropScraper()
    ]

    # Select a subset of barrios to scrape (to stay within time limits)
    barrios_to_scrape = BARRIOS_CABA[:10]  # Scrape 10 barrios per run

    total_stats = {"inserted": 0, "updated": 0, "errors": 0}

    for scraper in scrapers:
        print(f"\n{'='*30}")
        print(f"Running {scraper.fuente} scraper")
        print(f"{'='*30}")

        try:
            properties = scraper.scrape_all(barrios_to_scrape, max_pages_per_barrio=2)
            print(f"\nFound {len(properties)} properties from {scraper.fuente}")

            if properties:
                stats = save_properties(properties, supabase)
                print(f"Inserted: {stats['inserted']}, Updated: {stats['updated']}, Errors: {stats['errors']}")

                total_stats["inserted"] += stats["inserted"]
                total_stats["updated"] += stats["updated"]
                total_stats["errors"] += stats["errors"]

        except Exception as e:
            print(f"Error running {scraper.fuente} scraper: {e}")
            total_stats["errors"] += 1

    # Mark old properties as inactive
    print("\nMarking inactive properties...")
    inactive_count = mark_inactive_properties(supabase)
    print(f"Marked {inactive_count} properties as inactive")

    print("\n" + "=" * 50)
    print("SCRAPER COMPLETE")
    print(f"Total inserted: {total_stats['inserted']}")
    print(f"Total updated: {total_stats['updated']}")
    print(f"Total errors: {total_stats['errors']}")
    print("=" * 50)

if __name__ == "__main__":
    main()
