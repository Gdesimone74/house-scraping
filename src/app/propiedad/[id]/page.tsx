"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { Propiedad } from "@/lib/types";
import { fetchPropiedad, formatPrice, isNewProperty, getFuenteLogo, getFuenteColor } from "@/lib/api";
import ImageGallery from "@/components/ImageGallery";

export default function PropiedadDetail() {
  const params = useParams();
  const router = useRouter();
  const [propiedad, setPropiedad] = useState<Propiedad | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadPropiedad = async () => {
      if (!params.id || typeof params.id !== "string") {
        setError("ID de propiedad inválido");
        setLoading(false);
        return;
      }

      try {
        const data = await fetchPropiedad(params.id);
        setPropiedad(data);
      } catch (err) {
        setError("No se pudo cargar la propiedad");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    loadPropiedad();
  }, [params.id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100">
        <div className="max-w-5xl mx-auto px-4 py-8">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-300 rounded w-1/4 mb-6" />
            <div className="h-96 bg-gray-300 rounded-lg mb-6" />
            <div className="h-6 bg-gray-300 rounded w-1/2 mb-4" />
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-2" />
            <div className="h-4 bg-gray-200 rounded w-2/3" />
          </div>
        </div>
      </div>
    );
  }

  if (error || !propiedad) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            {error || "Propiedad no encontrada"}
          </h1>
          <Link
            href="/"
            className="text-blue-600 hover:text-blue-800 font-medium"
          >
            Volver al inicio
          </Link>
        </div>
      </div>
    );
  }

  const isNew = isNewProperty(propiedad.fechaPrimerVisto);
  const fuenteColor = getFuenteColor(propiedad.fuente);
  const fuenteLogo = getFuenteLogo(propiedad.fuente);

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-5xl mx-auto px-4 py-4">
          <button
            onClick={() => router.back()}
            className="flex items-center text-gray-600 hover:text-gray-900"
          >
            <svg
              className="w-5 h-5 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 19l-7-7 7-7"
              />
            </svg>
            Volver
          </button>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-5xl mx-auto px-4 py-6">
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          {/* Image Gallery */}
          <div className="p-4 md:p-6">
            <ImageGallery images={propiedad.fotos} title={propiedad.titulo} />
          </div>

          {/* Content */}
          <div className="p-4 md:p-6 border-t">
            {/* Badges */}
            <div className="flex flex-wrap gap-2 mb-4">
              {isNew && (
                <span className="bg-green-500 text-white text-sm font-bold px-3 py-1 rounded">
                  NUEVO
                </span>
              )}
              <span className={`${fuenteColor} text-sm font-bold px-3 py-1 rounded`}>
                {fuenteLogo}
              </span>
              <span className="bg-gray-200 text-gray-700 text-sm px-3 py-1 rounded capitalize">
                {propiedad.tipo}
              </span>
            </div>

            {/* Price */}
            <div className="text-3xl font-bold text-gray-900 mb-4">
              {formatPrice(propiedad.precio, propiedad.moneda)}
            </div>

            {/* Title */}
            <h1 className="text-xl font-semibold text-gray-900 mb-2">
              {propiedad.titulo}
            </h1>

            {/* Location */}
            <div className="flex items-center text-gray-600 mb-6">
              <svg
                className="w-5 h-5 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
              {propiedad.barrio}, Capital Federal
            </div>

            {/* Features */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
              {propiedad.ambientes && (
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900">
                    {propiedad.ambientes}
                  </div>
                  <div className="text-sm text-gray-600">Ambientes</div>
                </div>
              )}
              {propiedad.dormitorios && (
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900">
                    {propiedad.dormitorios}
                  </div>
                  <div className="text-sm text-gray-600">Dormitorios</div>
                </div>
              )}
              {propiedad.banos && (
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900">
                    {propiedad.banos}
                  </div>
                  <div className="text-sm text-gray-600">Baños</div>
                </div>
              )}
              {propiedad.metrosCuadrados && (
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900">
                    {propiedad.metrosCuadrados}
                  </div>
                  <div className="text-sm text-gray-600">m² cubiertos</div>
                </div>
              )}
              {propiedad.metrosTotales && (
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900">
                    {propiedad.metrosTotales}
                  </div>
                  <div className="text-sm text-gray-600">m² totales</div>
                </div>
              )}
            </div>

            {/* Description */}
            {propiedad.descripcion && (
              <div className="mb-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-2">
                  Descripción
                </h2>
                <p className="text-gray-600 whitespace-pre-line">
                  {propiedad.descripcion}
                </p>
              </div>
            )}

            {/* External link */}
            <div className="border-t pt-6">
              <a
                href={propiedad.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center w-full md:w-auto px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
              >
                Ver publicación original
                <svg
                  className="w-5 h-5 ml-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                  />
                </svg>
              </a>
            </div>

            {/* Metadata */}
            <div className="mt-6 pt-6 border-t text-sm text-gray-500">
              <p>
                Primera vez visto:{" "}
                {new Date(propiedad.fechaPrimerVisto).toLocaleDateString("es-AR", {
                  day: "numeric",
                  month: "long",
                  year: "numeric",
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </p>
              <p>
                Última actualización:{" "}
                {new Date(propiedad.fechaUltimaActualizacion).toLocaleDateString(
                  "es-AR",
                  {
                    day: "numeric",
                    month: "long",
                    year: "numeric",
                    hour: "2-digit",
                    minute: "2-digit",
                  }
                )}
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
