from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from .base import BaseScraper
import re
import json

class ZonapropScraper(BaseScraper):
    """Scraper for Zonaprop"""

    BASE_URL = "https://www.zonaprop.com.ar"
    use_playwright = True  # Use Playwright to bypass bot detection

    @property
    def fuente(self) -> str:
        return "zonaprop"

    def get_search_url(self, barrio: str, page: int = 1) -> str:
        """Build Zonaprop search URL"""
        # Normalize barrio name for URL
        barrio_url = barrio.lower().replace(" ", "-")

        pagina = f"-pagina-{page}" if page > 1 else ""

        return f"{self.BASE_URL}/casas-departamentos-venta-{barrio_url}-capital-federal{pagina}.html"

    def get_listings_from_page(self, soup: BeautifulSoup) -> List[BeautifulSoup]:
        """Extract listing elements from search results"""
        listings = soup.select("[data-qa='posting PROPERTY']")
        if not listings:
            listings = soup.select(".postingCard, .posting-card")
        if not listings:
            listings = soup.select("[class*='postingCard']")
        return listings

    def parse_listing(self, element: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """Parse a Zonaprop listing"""
        try:
            # Get link
            link_elem = element.select_one("a[data-qa='posting PROPERTY'], a[href*='/propiedades/']")
            if not link_elem:
                link_elem = element.select_one("a[href]")
            if not link_elem:
                return None

            href = link_elem.get("href", "")
            url = href if href.startswith("http") else f"{self.BASE_URL}{href}"

            # Extract external ID from URL
            external_id_match = re.search(r"-(\d+)\.html", url)
            if not external_id_match:
                external_id_match = re.search(r"/(\d+)", url)
            external_id = f"zp-{external_id_match.group(1)}" if external_id_match else url

            # Title
            title_elem = element.select_one("[data-qa='POSTING_CARD_LOCATION'], .postingAddress, h2")
            titulo = title_elem.get_text(strip=True) if title_elem else "Sin título"

            # Price
            price_elem = element.select_one("[data-qa='POSTING_CARD_PRICE'], .firstPrice, .price")
            precio = None
            moneda = "USD"

            if price_elem:
                price_text = price_elem.get_text(strip=True)
                precio, moneda = self.clean_price(price_text)

            # Images
            fotos = []
            img_elem = element.select_one("img[data-src], img[src*='zonaprop']")
            if img_elem:
                img_url = img_elem.get("data-src") or img_elem.get("src", "")
                if img_url and not img_url.startswith("data:"):
                    fotos.append(img_url)

            # Attributes
            ambientes = None
            dormitorios = None
            banos = None
            metros_cuadrados = None
            metros_totales = None

            # Look for feature spans
            features = element.select("[data-qa='POSTING_CARD_FEATURES'] span, .postingCardMainFeatures span, .mainFeatures span")
            for feature in features:
                text = feature.get_text(strip=True).lower()

                # Check for icons/labels nearby
                if "m²" in text or "m2" in text:
                    area = self.clean_area(text)
                    if "tot" in text:
                        metros_totales = area
                    elif "cub" in text:
                        metros_cuadrados = area
                    elif metros_cuadrados is None:
                        metros_cuadrados = area
                elif "amb" in text:
                    ambientes = self.clean_number(text)
                elif "dorm" in text:
                    dormitorios = self.clean_number(text)
                elif "baño" in text:
                    banos = self.clean_number(text)

            # Also try direct attribute spans
            for attr in element.select("span"):
                text = attr.get_text(strip=True)
                if re.match(r"^\d+\s*(m²|m2)", text, re.IGNORECASE):
                    area = self.clean_area(text)
                    if metros_cuadrados is None:
                        metros_cuadrados = area

            # Property type from title or features
            titulo_lower = titulo.lower()
            tipo = "casa" if any(word in titulo_lower for word in ["casa", "chalet", "ph"]) else "departamento"

            return {
                "externalId": external_id,
                "url": url,
                "titulo": titulo,
                "precio": precio,
                "moneda": moneda,
                "tipo": tipo,
                "ambientes": ambientes,
                "dormitorios": dormitorios,
                "banos": banos,
                "metrosCuadrados": metros_cuadrados,
                "metrosTotales": metros_totales,
                "fotos": fotos,
                "descripcion": None,
            }

        except Exception as e:
            print(f"Error parsing Zonaprop listing: {e}")
            return None
