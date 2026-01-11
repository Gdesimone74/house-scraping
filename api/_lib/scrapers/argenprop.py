from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from .base import BaseScraper
import re

class ArgenpropScraper(BaseScraper):
    """Scraper for Argenprop"""

    BASE_URL = "https://www.argenprop.com"

    @property
    def fuente(self) -> str:
        return "argenprop"

    def get_search_url(self, barrio: str, page: int = 1) -> str:
        """Build Argenprop search URL"""
        # Normalize barrio name for URL
        barrio_url = barrio.lower().replace(" ", "-")

        pagina = f"?pagina-{page}" if page > 1 else ""

        return f"{self.BASE_URL}/casas-o-departamentos/venta/capital-federal/{barrio_url}{pagina}"

    def get_listings_from_page(self, soup: BeautifulSoup) -> List[BeautifulSoup]:
        """Extract listing elements from search results"""
        listings = soup.select(".listing__item, .card--listing")
        if not listings:
            listings = soup.select("[class*='listing']")
        if not listings:
            listings = soup.select("article.card")
        return listings

    def parse_listing(self, element: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """Parse an Argenprop listing"""
        try:
            # Get link
            link_elem = element.select_one("a.card, a[href*='/propiedad/'], a.listing__item")
            if not link_elem:
                link_elem = element.select_one("a[href]")
            if not link_elem:
                return None

            href = link_elem.get("href", "")
            url = href if href.startswith("http") else f"{self.BASE_URL}{href}"

            # Extract external ID from URL
            external_id_match = re.search(r"--(\d+)$", url)
            if not external_id_match:
                external_id_match = re.search(r"/(\d+)", url)
            external_id = f"ap-{external_id_match.group(1)}" if external_id_match else url

            # Title/Address
            title_elem = element.select_one(".card__address, .listing__item__address, h2, .card__title")
            titulo = title_elem.get_text(strip=True) if title_elem else "Sin título"

            # Price
            price_elem = element.select_one(".card__price, .listing__item__price, .price")
            precio = None
            moneda = "USD"

            if price_elem:
                price_text = price_elem.get_text(strip=True)
                precio, moneda = self.clean_price(price_text)

            # Images
            fotos = []
            img_elem = element.select_one("img[data-src], img[src*='argenprop'], img.card__image")
            if img_elem:
                img_url = img_elem.get("data-src") or img_elem.get("src", "")
                if img_url and not img_url.startswith("data:"):
                    fotos.append(img_url)

            # Also check for background-image style
            if not fotos:
                bg_elem = element.select_one("[style*='background-image']")
                if bg_elem:
                    style = bg_elem.get("style", "")
                    match = re.search(r"url\(['\"]?([^'\"]+)['\"]?\)", style)
                    if match:
                        fotos.append(match.group(1))

            # Attributes
            ambientes = None
            dormitorios = None
            banos = None
            metros_cuadrados = None
            metros_totales = None

            # Look for feature elements
            features = element.select(".card__main-features li, .card__features li, .listing__item__features span")
            for feature in features:
                text = feature.get_text(strip=True).lower()

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

            # Property type
            tipo_elem = element.select_one(".card__type, .listing__item__type")
            tipo = "departamento"
            if tipo_elem:
                tipo_text = tipo_elem.get_text(strip=True).lower()
                if any(word in tipo_text for word in ["casa", "chalet", "ph"]):
                    tipo = "casa"
            elif any(word in titulo.lower() for word in ["casa", "chalet", "ph"]):
                tipo = "casa"

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
            print(f"Error parsing Argenprop listing: {e}")
            return None
