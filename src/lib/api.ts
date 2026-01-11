import { PropiedadListResponse, Propiedad, BarriosResponse, Filters } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

export async function fetchPropiedades(
  filters: Partial<Filters> = {},
  page: number = 1,
  limit: number = 20
): Promise<PropiedadListResponse> {
  const params = new URLSearchParams();

  if (filters.barrio) params.set("barrio", filters.barrio);
  if (filters.tipo) params.set("tipo", filters.tipo);
  if (filters.precioMin) params.set("precio_min", filters.precioMin.toString());
  if (filters.precioMax) params.set("precio_max", filters.precioMax.toString());
  if (filters.fuente) params.set("fuente", filters.fuente);
  if (filters.ordenar) params.set("ordenar", filters.ordenar);

  params.set("page", page.toString());
  params.set("limit", limit.toString());

  const response = await fetch(`${API_BASE}/api/propiedades?${params.toString()}`);

  if (!response.ok) {
    throw new Error("Failed to fetch properties");
  }

  return response.json();
}

export async function fetchPropiedad(id: string): Promise<Propiedad> {
  const response = await fetch(`${API_BASE}/api/propiedad/${id}`);

  if (!response.ok) {
    throw new Error("Failed to fetch property");
  }

  return response.json();
}

export async function fetchBarrios(): Promise<string[]> {
  const response = await fetch(`${API_BASE}/api/barrios`);

  if (!response.ok) {
    throw new Error("Failed to fetch barrios");
  }

  const data: BarriosResponse = await response.json();
  return data.barrios;
}

export function formatPrice(precio: number | null, moneda: "USD" | "ARS"): string {
  if (precio === null) return "Consultar";

  const formatter = new Intl.NumberFormat("es-AR", {
    style: "currency",
    currency: moneda,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  });

  return formatter.format(precio);
}

export function isNewProperty(fechaPrimerVisto: string): boolean {
  const date = new Date(fechaPrimerVisto);
  const now = new Date();
  const diffHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);
  return diffHours < 24;
}

export function getFuenteLogo(fuente: string): string {
  switch (fuente) {
    case "mercadolibre":
      return "ML";
    case "zonaprop":
      return "ZP";
    case "argenprop":
      return "AP";
    default:
      return fuente.toUpperCase().slice(0, 2);
  }
}

export function getFuenteColor(fuente: string): string {
  switch (fuente) {
    case "mercadolibre":
      return "bg-yellow-400 text-black";
    case "zonaprop":
      return "bg-orange-500 text-white";
    case "argenprop":
      return "bg-blue-600 text-white";
    default:
      return "bg-gray-500 text-white";
  }
}
