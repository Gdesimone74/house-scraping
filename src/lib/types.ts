export interface Propiedad {
  _id: string;
  externalId: string;
  url: string;
  titulo: string;
  precio: number | null;
  moneda: "USD" | "ARS";
  barrio: string;
  tipo: "departamento" | "casa";
  ambientes: number | null;
  dormitorios: number | null;
  banos: number | null;
  metrosCuadrados: number | null;
  metrosTotales: number | null;
  fotos: string[];
  descripcion: string | null;
  fuente: "mercadolibre" | "zonaprop" | "argenprop";
  operacion: "venta";
  fechaPublicacion: string | null;
  fechaPrimerVisto: string;
  fechaUltimaActualizacion: string;
  activo: boolean;
}

export interface PropiedadListResponse {
  propiedades: Propiedad[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

export interface BarriosResponse {
  barrios: string[];
}

export interface Filters {
  barrio: string | null;
  tipo: "departamento" | "casa" | null;
  precioMin: number | null;
  precioMax: number | null;
  fuente: "mercadolibre" | "zonaprop" | "argenprop" | null;
  ordenar: "fecha" | "precio_asc" | "precio_desc";
}
