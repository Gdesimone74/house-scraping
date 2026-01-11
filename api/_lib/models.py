from pydantic import BaseModel
from typing import List, Optional, Literal
from datetime import datetime

class PropiedadBase(BaseModel):
    externalId: str
    url: str
    titulo: str
    precio: Optional[float] = None
    moneda: Literal["USD", "ARS"] = "USD"
    barrio: str
    tipo: Literal["departamento", "casa"]
    ambientes: Optional[int] = None
    dormitorios: Optional[int] = None
    banos: Optional[int] = None
    metrosCuadrados: Optional[float] = None
    metrosTotales: Optional[float] = None
    fotos: List[str] = []
    descripcion: Optional[str] = None
    fuente: Literal["mercadolibre", "zonaprop", "argenprop"]
    operacion: Literal["venta"] = "venta"

class Propiedad(PropiedadBase):
    id: str
    fechaPublicacion: Optional[datetime] = None
    fechaPrimerVisto: datetime
    fechaUltimaActualizacion: datetime
    activo: bool = True

class PropiedadListResponse(BaseModel):
    propiedades: List[Propiedad]
    total: int
    page: int
    limit: int
    totalPages: int

# Lista de barrios de Capital Federal
BARRIOS_CABA = [
    "Agronomia", "Almagro", "Balvanera", "Barracas", "Belgrano", "Boedo",
    "Caballito", "Chacarita", "Coghlan", "Colegiales", "Constitucion",
    "Flores", "Floresta", "La Boca", "La Paternal", "Liniers", "Mataderos",
    "Monte Castro", "Montserrat", "Nueva Pompeya", "Nunez", "Palermo",
    "Parque Avellaneda", "Parque Chacabuco", "Parque Chas", "Parque Patricios",
    "Puerto Madero", "Recoleta", "Retiro", "Saavedra", "San Cristobal",
    "San Nicolas", "San Telmo", "Velez Sarsfield", "Versalles", "Villa Crespo",
    "Villa del Parque", "Villa Devoto", "Villa General Mitre", "Villa Lugano",
    "Villa Luro", "Villa Ortuzar", "Villa Pueyrredon", "Villa Real",
    "Villa Riachuelo", "Villa Santa Rita", "Villa Soldati", "Villa Urquiza"
]
