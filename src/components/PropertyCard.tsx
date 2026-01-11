"use client";

import Link from "next/link";
import Image from "next/image";
import { Propiedad } from "@/lib/types";
import { formatPrice, isNewProperty, getFuenteLogo, getFuenteColor } from "@/lib/api";

interface PropertyCardProps {
  propiedad: Propiedad;
}

export default function PropertyCard({ propiedad }: PropertyCardProps) {
  const isNew = isNewProperty(propiedad.fechaPrimerVisto);
  const fuenteColor = getFuenteColor(propiedad.fuente);
  const fuenteLogo = getFuenteLogo(propiedad.fuente);

  return (
    <Link href={`/propiedad/${propiedad._id}`}>
      <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-200 cursor-pointer h-full flex flex-col">
        {/* Image */}
        <div className="relative h-48 bg-gray-200">
          {propiedad.fotos.length > 0 ? (
            <img
              src={propiedad.fotos[0]}
              alt={propiedad.titulo}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-gray-400">
              <svg
                className="w-16 h-16"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
                />
              </svg>
            </div>
          )}

          {/* Badges */}
          <div className="absolute top-2 left-2 flex gap-2">
            {isNew && (
              <span className="bg-green-500 text-white text-xs font-bold px-2 py-1 rounded">
                NUEVO
              </span>
            )}
            <span className={`${fuenteColor} text-xs font-bold px-2 py-1 rounded`}>
              {fuenteLogo}
            </span>
          </div>

          {/* Property type badge */}
          <div className="absolute bottom-2 right-2">
            <span className="bg-black/70 text-white text-xs px-2 py-1 rounded capitalize">
              {propiedad.tipo}
            </span>
          </div>
        </div>

        {/* Content */}
        <div className="p-4 flex-1 flex flex-col">
          {/* Price */}
          <div className="text-xl font-bold text-gray-900 mb-2">
            {formatPrice(propiedad.precio, propiedad.moneda)}
          </div>

          {/* Title */}
          <h3 className="text-sm text-gray-600 mb-2 line-clamp-2 flex-1">
            {propiedad.titulo}
          </h3>

          {/* Location */}
          <div className="flex items-center text-sm text-gray-500 mb-3">
            <svg
              className="w-4 h-4 mr-1"
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
            {propiedad.barrio}, CABA
          </div>

          {/* Features */}
          <div className="flex flex-wrap gap-3 text-sm text-gray-600 border-t pt-3">
            {propiedad.ambientes && (
              <div className="flex items-center gap-1">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
                <span>{propiedad.ambientes} amb</span>
              </div>
            )}
            {propiedad.dormitorios && (
              <div className="flex items-center gap-1">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                </svg>
                <span>{propiedad.dormitorios} dorm</span>
              </div>
            )}
            {propiedad.metrosCuadrados && (
              <div className="flex items-center gap-1">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
                </svg>
                <span>{propiedad.metrosCuadrados} m²</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </Link>
  );
}
