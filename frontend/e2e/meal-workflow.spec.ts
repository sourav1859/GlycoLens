import { expect, test } from "@playwright/test";

const food = { id: "00000000-0000-4000-8000-000000000001", name: "Synthetic rice", source: "synthetic", source_food_id: "fixture", nutrient_basis_g: 100, calories: 180, carbs_g: 30, protein_g: 8, fat_g: 4, fiber_g: 5 };
const origin = "2026-01-01T12:00:00Z";

test.beforeEach(async ({ page }) => {
  await page.route("**/auth/v1/**", async route => {
    const now = Math.floor(Date.now() / 1000);
    const token = `${Buffer.from('{"alg":"HS256"}').toString("base64url")}.${Buffer.from(JSON.stringify({ sub: "10000000-0000-4000-8000-000000000001", exp: now + 3600, iat: now, role: "authenticated" })).toString("base64url")}.synthetic`;
    await route.fulfill({ json: { access_token: token, token_type: "bearer", expires_in: 3600, refresh_token: "synthetic", user: { id: "10000000-0000-4000-8000-000000000001", aud: "authenticated", role: "authenticated", is_anonymous: true, app_metadata: {}, user_metadata: {}, created_at: origin } } });
  });
  await page.route("**/api/v1/**", async route => {
    const path = new URL(route.request().url()).pathname;
    let json: unknown = {};
    if (path.endsWith("/demo/session")) json = { user_id: "synthetic" };
    else if (path.endsWith("/simulation/scenario")) json = { forecast_origin: origin, execution: "live", notice: "Synthetic browser-test fixture" };
    else if (path.endsWith("/timeline")) json = { cgm: Array.from({ length: 24 }, (_, i) => ({ recorded_at: new Date(Date.parse(origin) - i * 300000).toISOString(), glucose_mg_dl: 120, source: "simulation" })) };
    else if (path.includes("/foods/")) json = path.includes("/search") ? { foods: [food], source: "cache" } : food;
    else if (path.endsWith("/parse-recipe")) json = { ingredients: [{ name: "rice", quantity: 100, unit: "g", needs_review: true }], servings: 2, model: "synthetic-test-parser" };
    else if (path.endsWith("/meals")) json = { meal_id: "20000000-0000-4000-8000-000000000001" };
    else if (path.endsWith("/similar")) json = { meals: [{ id: "prior", name: "Synthetic earlier meal", similarity: 0.8, actual_60: 140 }] };
    else if (path.endsWith("/forecasts")) json = { forecast_id: "synthetic", forecast: {
      schema_version: "1.0", data_mode: "simulated", model_id: "synthetic-browser-test", model_version: "1", context_configuration: "cgm_insulin_nutrition", unit: "mg/dL",
      history: Array.from({ length: 24 }, (_, i) => ({ minute: -115 + i * 5, value_mg_dl: 120 })),
      forecast: Array.from({ length: 24 }, (_, i) => ({ minute: (i + 1) * 5, q10_mg_dl: 100, q50_mg_dl: 120, q90_mg_dl: 140 })),
      summary: { minute_30_mg_dl: 120, minute_60_mg_dl: 120, minute_120_mg_dl: 120 }, notice: "Uncertain synthetic research fixture, not insulin dosing advice",
    } };
    await route.fulfill({ json });
  });
});

test("confirmed meal reaches a validated forecast and earlier history", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Choose virtual patient" }).click();
  await page.getByRole("button", { name: "Run live scenario" }).click();
  await expect(page.getByText("Latest simulated glucose:")).toBeVisible();
  await page.getByRole("button", { name: "Search foods", exact: true }).click();
  await page.getByRole("button", { name: "Add ingredient" }).click();
  await expect(page.getByRole("button", { name: "Save meal" })).toBeDisabled();
  await page.getByRole("checkbox").check();
  await page.getByRole("button", { name: "Save meal" }).click();
  await expect(page.getByRole("button", { name: "Run forecast" })).toBeEnabled();
  await page.getByRole("button", { name: "Run forecast" }).click();
  await expect(page.getByRole("heading", { name: "Two-hour glucose forecast" })).toBeVisible();
  await expect(page.getByText("Synthetic earlier meal", { exact: false })).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await page.screenshot({ path: `../.cache/m2-browser-${test.info().project.name}.png`, fullPage: true });
});

test("recipe extraction stays editable and barcode accepts manual fallback", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Choose virtual patient" }).click();
  await page.getByRole("button", { name: "Recipe text", exact: true }).click();
  await page.getByLabel("Home recipe").fill("100 g rice, two servings");
  await page.getByRole("button", { name: "Extract ingredients" }).click();
  await page.getByRole("textbox", { name: "Ingredient 1", exact: true }).fill("cooked rice");
  await expect(page.getByText("Review required", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Barcode", exact: true }).click();
  await page.getByLabel("Barcode number").fill("12345678");
  await page.getByRole("button", { name: "Look up barcode" }).click();
  await expect(page.getByRole("button", { name: "Add ingredient" })).toBeVisible();
});
