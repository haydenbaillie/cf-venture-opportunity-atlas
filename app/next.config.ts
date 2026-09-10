import type { NextConfig } from "next";

const pages = process.env.GITHUB_PAGES === "true";
const repo = process.env.GITHUB_REPOSITORY?.split("/")[1];

const nextConfig: NextConfig = {
  reactStrictMode: true,
  ...(pages
    ? {
        output: "export" as const,
        images: { unoptimized: true },
        trailingSlash: true,
        basePath: repo ? `/${repo}` : "",
      }
    : {}),
};

export default nextConfig;
