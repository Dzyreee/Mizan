/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Self-contained server build for Docker (.next/standalone/server.js).
  output: "standalone",
};

export default nextConfig;
