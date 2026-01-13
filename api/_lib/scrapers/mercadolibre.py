from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from .base import BaseScraper
import requests
import re

class MercadoLibreScraper(BaseScraper):
    """Scraper for MercadoLibre Inmuebles"""

    BASE_URL = "https://inmuebles.mercadolibre.com.ar"
    use_playwright = True  # Use Playwright to bypass bot detection

    @property
    def fuente(self) -> str:
        return "mercadolibre"

    def get_search_url(self, barrio: str, page: int = 1) -> str:
        """Build MercadoLibre search URL"""
        # Normalize barrio name for URL
        barrio_url = barrio.lower().replace(" ", "-")

        # Calculate offset (48 items per page)
        offset = (page - 1) * 48
        desde = f"_Desde_{offset + 1}" if offset > 0 else ""

        return f"{self.BASE_URL}/departamentos-o-casas/venta/capital-federal/{barrio_url}{desde}_NoIndex_True"

    def get_listings_from_page(self, soup: BeautifulSoup) -> List[BeautifulSoup]:
        """Extract listing elements from search results"""
        # MercadoLibre uses different selectors, try multiple
        listings = soup.select("li.ui-search-layout__item")
        if not listings:
            listings = soup.select("div.ui-search-result")
        if not listings:
            listings = soup.select("[class*='ui-search-layout__item']")
        return listings

    def parse_listing(self, element: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """Parse a MercadoLibre listing"""
        try:
            # Get link and ID
            link_elem = element.select_one("a.ui-search-link, a[href*='inmueble']")
            if not link_elem:
                link_elem = element.select_one("a[href*='MLA']")
            if not link_elem:
                return None

            url = link_elem.get("href", "")
            if not url:
                return None

            # Extract external ID from URL
            external_id_match = re.search(r"MLA-?(\d+)", url)
            external_id = external_id_match.group(0) if external_id_match else url

            # Title - get from link text since ML changed structure
            titulo = link_elem.get_text(strip=True) if link_elem else "Sin título"

            # Price
            price_elem = element.select_one(".andes-money-amount__fraction, .price-tag-fraction")
            currency_elem = element.select_one(".andes-money-amount__currency-symbol")

            precio = None
            moneda = "USD"

            if price_elem:
                price_text = price_elem.get_text(strip=True)
                currency_text = currency_elem.get_text(strip=True) if currency_elem else ""
                full_price = f"{currency_text} {price_text}"
                precio, moneda = self.clean_price(full_price)

            # Images
            fotos = []
            img_elem = element.select_one("img")
            if img_elem:
                img_url = img_elem.get("src") or img_elem.get("data-src", "")
                if img_url and not img_url.startswith("data:"):
                    # Get higher resolution version (works for jpg and webp)
                    img_url = re.sub(r"-[A-Z]\.(jpg|webp)", r"-O.\1", img_url)
                    fotos.append(img_url)

            # Attributes (rooms, bathrooms, area)
            ambientes = None
            dormitorios = None
            banos = None
            metros_cuadrados = None
            metros_totales = None

            attrs = element.select(".ui-search-card-attributes__attribute, .ui-search-item__attributes li")
            for attr in attrs:
                text = attr.get_text(strip=True).lower()
                if "dormitorio" in text or "dorm" in text:
                    dormitorios = self.clean_number(text)
                elif "ambiente" in text or "amb" in text:
                    ambientes = self.clean_number(text)
                elif "baño" in text:
                    banos = self.clean_number(text)
                elif "m²" in text or "m2" in text:
                    area = self.clean_area(text)
                    if "total" in text:
                        metros_totales = area
                    elif "cubierto" in text or "cub" in text:
                        metros_cuadrados = area
                    elif metros_cuadrados is None:
                        metros_cuadrados = area

            # Determine property type from title
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
            print(f"Error parsing MercadoLibre listing: {e}")
            return None

    def get_photos_from_detail(self, url: str) -> List[str]:
        """Get all photos from MercadoLibre detail page"""
        try:
            # Use fresh headers for detail page
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "es-AR,es;q=0.9",
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "lxml")

            photos = []
            seen = set()

            # Find all images from mlstatic
            for img in soup.select("img[src*='mlstatic']"):
                src = img.get("src", "")
                if src and "mlstatic" in src and src not in seen:
                    # Convert to high quality version
                    # Replace size indicators like -F, -V, -W with -O (original)
                    high_quality = re.sub(r"-[A-Z](-null)?\.(jpg|webp)", r"-O.\2", src)
                    high_quality = re.sub(r"_[A-Z]\.(jpg|webp)", r"_O.\1", high_quality)
                    if high_quality not in seen:
                        seen.add(high_quality)
                        photos.append(high_quality)

            # Also check data-zoom attributes
            for img in soup.select("img[data-zoom]"):
                src = img.get("data-zoom", "")
                if src and src not in seen:
                    seen.add(src)
                    photos.append(src)

            return photos[:20]  # Limit to 20 photos

        except Exception as e:
            return []
