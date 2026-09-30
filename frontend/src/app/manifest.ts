import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "GlycoLens",
    short_name: "GlycoLens",
    description: "Research prototype for meal-centered glucose forecasting",
    start_url: "/",
    display: "standalone",
    background_color: "#f5f7fb",
    theme_color: "#176b5d",
  };
}
