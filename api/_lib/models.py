from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime
from bson import ObjectId

class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, handler):
        if isinstance(v, ObjectId):
            return str(v)
        return str(v)

class PropiedadBase(BaseModel):
    externalId: str
    url: str
    titulo: str
    precio: float
    moneda: Literal["USD", "ARS"]
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

class PropiedadCreate(PropiedadBase):
    pass

class Propiedad(PropiedadBase):
    id: str = Field(alias="_id")
    fechaPublicacion: Optional[datetime] = None
    fechaPrimerVisto: datetime
    fechaUltimaActualizacion: datetime
    activo: bool = True

    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }

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
