#!/usr/bin/env python3
"""
Script to run all scrapers and save properties to MongoDB.
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

from api._lib.database import get_propiedades_collection, ensure_indexes
from api._lib.scrapers import MercadoLibreScraper, ZonapropScraper, ArgenpropScraper
from api._lib.models import BARRIOS_CABA

def save_properties(properties: list, collection) -> dict:
    """
    Save properties to MongoDB, handling duplicates.
    Returns stats about inserted/updated properties.
    """
    stats = {
        "inserted": 0,
        "updated": 0,
        "errors": 0
    }

    now = datetime.utcnow()

    for prop in properties:
        try:
            # Check if property already exists
            existing = collection.find_one({
                "externalId": prop["externalId"],
                "fuente": prop["fuente"]
            })

            if existing:
                # Update existing property
                collection.update_one(
                    {"_id": existing["_id"]},
                    {
                        "$set": {
                            "precio": prop.get("precio"),
                            "moneda": prop.get("moneda", "USD"),
                            "fotos": prop.get("fotos", []),
                            "fechaUltimaActualizacion": now,
                            "activo": True
                        }
                    }
                )
                stats["updated"] += 1
            else:
                # Insert new property
                prop["fechaPrimerVisto"] = now
                prop["fechaUltimaActualizacion"] = now
                prop["activo"] = True

                collection.insert_one(prop)
                stats["inserted"] += 1

        except Exception as e:
            print(f"Error saving property {prop.get('externalId')}: {e}")
            stats["errors"] += 1

    return stats

def mark_inactive_properties(collection, hours: int = 48):
    """
    Mark properties as inactive if they haven't been updated recently.
    This helps identify properties that were removed from listings.
    """
    cutoff = datetime.utcnow() - timedelta(hours=hours)

    result = collection.update_many(
        {
            "activo": True,
            "fechaUltimaActualizacion": {"$lt": cutoff}
        },
        {"$set": {"activo": False}}
    )

    return result.modified_count

def main():
    print("=" * 50)
    print(f"Starting scraper at {datetime.now().isoformat()}")
    print("=" * 50)

    # Ensure indexes exist
    print("\nEnsuring database indexes...")
    ensure_indexes()

    # Get collection
    collection = get_propiedades_collection()

    # Initialize scrapers
    scrapers = [
        MercadoLibreScraper(),
        ZonapropScraper(),
        ArgenpropScraper()
    ]

    # Select a subset of barrios to scrape (to stay within time limits)
    # Rotate through barrios on different runs
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
                stats = save_properties(properties, collection)
                print(f"Inserted: {stats['inserted']}, Updated: {stats['updated']}, Errors: {stats['errors']}")

                total_stats["inserted"] += stats["inserted"]
                total_stats["updated"] += stats["updated"]
                total_stats["errors"] += stats["errors"]

        except Exception as e:
            print(f"Error running {scraper.fuente} scraper: {e}")
            total_stats["errors"] += 1

    # Mark old properties as inactive
    print("\nMarking inactive properties...")
    inactive_count = mark_inactive_properties(collection)
    print(f"Marked {inactive_count} properties as inactive")

    print("\n" + "=" * 50)
    print("SCRAPER COMPLETE")
    print(f"Total inserted: {total_stats['inserted']}")
    print(f"Total updated: {total_stats['updated']}")
    print(f"Total errors: {total_stats['errors']}")
    print("=" * 50)

if __name__ == "__main__":
    main()
