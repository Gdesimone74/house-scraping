import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "**.mercadolibre.com",
      },
      {
        protocol: "https",
        hostname: "**.mlstatic.com",
      },
      {
        protocol: "https",
        hostname: "**.zonaprop.com.ar",
      },
      {
        protocol: "https",
        hostname: "**.argenprop.com",
      },
      {
        protocol: "http",
        hostname: "**",
      },
    ],
  },
};

export default nextConfig;
