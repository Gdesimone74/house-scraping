"use client";

import { useState, useEffect, useCallback } from "react";
import { Propiedad, Filters as FiltersType } from "@/lib/types";
import { fetchPropiedades } from "@/lib/api";
import Filters from "@/components/Filters";
import PropertyGrid from "@/components/PropertyGrid";
import Pagination from "@/components/Pagination";

const defaultFilters: FiltersType = {
  barrio: null,
  tipo: null,
  precioMin: null,
  precioMax: null,
  fuente: null,
  ordenar: "fecha",
};

export default function Home() {
  const [propiedades, setPropiedades] = useState<Propiedad[]>([]);
  const [filters, setFilters] = useState<FiltersType>(defaultFilters);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadPropiedades = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetchPropiedades(filters, page, 20);
      setPropiedades(response.propiedades);
      setTotalPages(response.totalPages);
      setTotal(response.total);
    } catch (err) {
      setError("Error al cargar propiedades. Por favor intenta de nuevo.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [filters, page]);

  useEffect(() => {
    loadPropiedades();
  }, [loadPropiedades]);

  const handleFiltersChange = (newFilters: FiltersType) => {
    setFilters(newFilters);
    setPage(1);
  };

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-2xl font-bold text-gray-900">
            Propiedades en Venta - CABA
          </h1>
          <p className="text-gray-600 mt-1">
            Encuentra departamentos y casas en Capital Federal
          </p>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        {/* Filters */}
        <Filters filters={filters} onFiltersChange={handleFiltersChange} />

        {/* Results count */}
        {!loading && !error && (
          <div className="mb-4 text-sm text-gray-600">
            {total} {total === 1 ? "propiedad encontrada" : "propiedades encontradas"}
          </div>
        )}

        {/* Error message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
            <button
              onClick={loadPropiedades}
              className="ml-4 text-red-800 underline hover:no-underline"
            >
              Reintentar
            </button>
          </div>
        )}

        {/* Property grid */}
        <PropertyGrid propiedades={propiedades} loading={loading} />

        {/* Pagination */}
        {!loading && !error && (
          <Pagination
            currentPage={page}
            totalPages={totalPages}
            onPageChange={handlePageChange}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-12">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <p className="text-center text-sm text-gray-500">
            Datos obtenidos de MercadoLibre, Zonaprop y Argenprop.
            Actualizado cada 6 horas.
          </p>
        </div>
      </footer>
    </div>
  );
}
