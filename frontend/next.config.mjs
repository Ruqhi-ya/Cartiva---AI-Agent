/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "images.unsplash.com" },
      { protocol: "http", hostname: "assets.myntassets.com" },
      { protocol: "https", hostname: "images-static.nykaa.com" },
      { protocol: "https", hostname: "thedermaco.com" },
    ],
  },
};

export default nextConfig;