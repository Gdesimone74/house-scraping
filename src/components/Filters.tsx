"use client";

import { useState, useEffect } from "react";
import { Filters as FiltersType } from "@/lib/types";
import { fetchBarrios } from "@/lib/api";

interface FiltersProps {
  filters: FiltersType;
  onFiltersChange: (filters: FiltersType) => void;
}

export default function Filters({ filters, onFiltersChange }: FiltersProps) {
  const [barrios, setBarrios] = useState<string[]>([]);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    fetchBarrios().then(setBarrios).catch(console.error);
  }, []);

  const handleChange = (key: keyof FiltersType, value: string | number | null) => {
    onFiltersChange({
      ...filters,
      [key]: value === "" ? null : value,
    });
  };

  const clearFilters = () => {
    onFiltersChange({
      barrio: null,
      tipo: null,
      precioMin: null,
      precioMax: null,
      fuente: null,
      ordenar: "fecha",
    });
  };

  const hasActiveFilters =
    filters.barrio ||
    filters.tipo ||
    filters.precioMin ||
    filters.precioMax ||
    filters.fuente;

  return (
    <div className="bg-white rounded-lg shadow-md p-4 mb-6">
      {/* Mobile toggle */}
      <button
        className="md:hidden w-full flex items-center justify-between text-left"
        onClick={() => setIsOpen(!isOpen)}
      >
        <span className="font-semibold">Filtros</span>
        <svg
          className={`w-5 h-5 transition-transform ${isOpen ? "rotate-180" : ""}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Filters content */}
      <div className={`${isOpen ? "block" : "hidden"} md:block mt-4 md:mt-0`}>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
          {/* Barrio */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Barrio
            </label>
            <select
              value={filters.barrio || ""}
              onChange={(e) => handleChange("barrio", e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Todos</option>
              {barrios.map((barrio) => (
                <option key={barrio} value={barrio}>
                  {barrio}
                </option>
              ))}
            </select>
          </div>

          {/* Tipo */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tipo
            </label>
            <select
              value={filters.tipo || ""}
              onChange={(e) => handleChange("tipo", e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Todos</option>
              <option value="departamento">Departamento</option>
              <option value="casa">Casa</option>
            </select>
          </div>

          {/* Precio Min */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Precio Min (USD)
            </label>
            <input
              type="number"
              placeholder="0"
              value={filters.precioMin || ""}
              onChange={(e) =>
                handleChange("precioMin", e.target.value ? Number(e.target.value) : null)
              }
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Precio Max */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Precio Max (USD)
            </label>
            <input
              type="number"
              placeholder="Sin límite"
              value={filters.precioMax || ""}
              onChange={(e) =>
                handleChange("precioMax", e.target.value ? Number(e.target.value) : null)
              }
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Fuente */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Fuente
            </label>
            <select
              value={filters.fuente || ""}
              onChange={(e) => handleChange("fuente", e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Todas</option>
              <option value="mercadolibre">MercadoLibre</option>
              <option value="zonaprop">Zonaprop</option>
              <option value="argenprop">Argenprop</option>
            </select>
          </div>

          {/* Ordenar */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Ordenar
            </label>
            <select
              value={filters.ordenar}
              onChange={(e) => handleChange("ordenar", e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="fecha">Más recientes</option>
              <option value="precio_asc">Menor precio</option>
              <option value="precio_desc">Mayor precio</option>
            </select>
          </div>
        </div>

        {/* Clear filters button */}
        {hasActiveFilters && (
          <div className="mt-4 flex justify-end">
            <button
              onClick={clearFilters}
              className="text-sm text-blue-600 hover:text-blue-800 font-medium"
            >
              Limpiar filtros
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
