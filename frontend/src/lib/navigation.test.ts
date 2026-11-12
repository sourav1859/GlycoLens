import { describe, expect, it } from "vitest";
import { accountNavigation, primaryNavigation, primaryRouteFor } from "./navigation";

describe("shared route identity", () => {
  it("has the same five primary destinations and unique accessible names", () => {
    expect(primaryNavigation.map(item => item.label)).toEqual(["Home", "Search", "Meal log", "Forecasts", "Nutrition"]);
    expect(new Set([...primaryNavigation, ...accountNavigation].map(item => item.href)).size).toBe(10);
  });
  it("groups details and entry methods without matching unrelated prefixes", () => {
    expect(primaryRouteFor("/meals/new")).toBe("/meals");
    expect(primaryRouteFor("/recipes/analyze")).toBe("/meals");
    expect(primaryRouteFor("/recipes/catalog-id")).toBe("/search");
    expect(primaryRouteFor("/products/catalog-id")).toBe("/search");
    expect(primaryRouteFor("/forecasts/id/compare")).toBe("/forecasts");
    expect(primaryRouteFor("/home-made")).toBeUndefined();
  });
});
