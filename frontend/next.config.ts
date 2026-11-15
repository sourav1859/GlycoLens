import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  distDir: process.env.GLYCOLENS_E2E === "1" ? ".next-e2e" : ".next",
  output: "standalone",
  agentRules: false,
  devIndicators: process.env.GLYCOLENS_E2E === "1" ? false : undefined,
  allowedDevOrigins: ["127.0.0.1"],
};

export default nextConfig;
