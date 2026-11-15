import { expect, test } from "@playwright/test";
import { mockAccount } from "./account-fixture";

const food = { id: "00000000-0000-4000-8000-000000000001", name: "Synthetic rice", source: "synthetic", source_food_id: "fixture", nutrient_basis_g: 100, calories: 180, carbs_g: 30, protein_g: 8, fat_g: 4, fiber_g: 5 };
let samples=24;
const origin = "2026-01-01T12:00:00Z";

test.beforeEach(async ({ page }) => {
  await mockAccount(page);
  await page.route("**/auth/v1/**", async route => {
    const now = Math.floor(Date.now() / 1000);
    const token = `${Buffer.from('{"alg":"HS256"}').toString("base64url")}.${Buffer.from(JSON.stringify({ sub: "10000000-0000-4000-8000-000000000001", exp: now + 3600, iat: now, role: "authenticated" })).toString("base64url")}.synthetic`;
    await route.fulfill({ json: { access_token: token, token_type: "bearer", expires_in: 3600, refresh_token: "synthetic", user: { id: "10000000-0000-4000-8000-000000000001", aud: "authenticated", role: "authenticated", is_anonymous: true, app_metadata: {}, user_metadata: {}, created_at: origin } } });
  });
  await page.route("**/api/v1/**", async route => {
    const path = new URL(route.request().url()).pathname;
    let json: unknown = {};
    if(path.endsWith("/me/bootstrap")){await route.fallback();return;}
    if (path.endsWith("/forecasts/models")) json = {models:[{key:"chronos",label:"Chronos",available:true},{key:"lightgbm",label:"LightGBM",available:true}]};
    else if (path.endsWith("/demo/session")) json = { user_id: "10000000-0000-4000-8000-000000000001" };
    else if (path.endsWith("/simulation/scenario")) {samples=route.request().postDataJSON().protocol==="lightgbm_warmup_48h_v1"?288:24;json = {source_session_id:"40000000-0000-4000-8000-000000000001", forecast_origin: origin, execution: "live", sample_count:route.request().postDataJSON().protocol==="lightgbm_warmup_48h_v1"?288:24, notice: "Synthetic browser-test fixture" };}
    else if(path.includes("/simulation/sources/")) json={id:"40000000-0000-4000-8000-000000000001",clock_at:origin,metadata:{}};
    else if (path.endsWith("/timeline")) json = { cgm: Array.from({ length: samples }, (_, i) => ({ recorded_at: new Date(Date.parse(origin) - i * 300000).toISOString(), glucose_mg_dl: 120, source: "simulation" })) };
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
    if(path.endsWith("/forecasts")&&route.request().method()==="POST"&&route.request().postDataJSON().model_key==="lightgbm"){
      const data=(json as {forecast:Record<string,unknown>}).forecast;
      const version="metabonet_tabular_v1:"+"a".repeat(64);
      Object.assign(data,{schema_version:"2.0",model_id:"metabonet_lightgbm_direct",model_version:version,context_configuration:"cgm_insulin_carbohydrates",interval_kind:"calibrated_marginal_80",
        history:Array.from({length:288},(_,i)=>({minute:-1435+i*5,value_mg_dl:120})),
        forecast:Array.from({length:24},(_,i)=>({minute:(i+1)*5,q10_mg_dl:-5,q50_mg_dl:120,q90_mg_dl:245})),
        provenance:{model_key:"lightgbm",model_id:"metabonet_lightgbm_direct",model_version:version,feature_version:"metabonet_tabular_v1",bundle_sha256:"a".repeat(64),calibration_sha256:"b".repeat(64),history_samples:288,interval_kind:"calibrated_marginal_80",inputs:["glucose","recorded insulin","current carbohydrates"]}});
    }
    await route.fulfill({ json });
  });
});

test("confirmed meal reaches a validated forecast and earlier history", async ({ page }) => {
  await page.goto("/demo");
  await page.getByRole("button", { name: "Choose virtual patient" }).click();
  const simulation = page.waitForRequest(request => request.url().endsWith("/simulation/scenario"));
  await page.getByRole("button", { name: "Run new simulation" }).click();
  expect((await simulation).postDataJSON()).toEqual({ replay: false,protocol:"m1_fixed_meal_day" });
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

test("saved simulation replay uses the replay request", async ({ page }) => {
  await page.goto("/demo");
  await page.getByRole("button", { name: "Choose virtual patient" }).click();
  const replay = page.waitForRequest(request => request.url().endsWith("/simulation/scenario"));
  await page.getByRole("button", { name: "Replay saved simulation" }).click();
  expect((await replay).postDataJSON()).toEqual({ replay: true,protocol:"m1_fixed_meal_day" });
  await expect(page.getByText("Latest simulated glucose:")).toBeVisible();
});

test("recipe extraction stays editable and barcode accepts manual fallback", async ({ page }) => {
  await page.goto("/demo");
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

test("research model requires explicit selection and longer protocol, with signed bands readable",async({page})=>{
  await page.goto("/demo");
  await page.getByRole("button",{name:"Choose virtual patient"}).click();
  await expect(page.getByLabel("Forecast model")).toHaveValue("chronos");
  await expect(page.getByRole("option",{name:"LightGBM · research option"})).toBeEnabled();
  await page.getByLabel("Forecast model").selectOption("lightgbm");
  const simulation=page.waitForRequest(r=>r.url().endsWith("/simulation/scenario"));
  await page.getByRole("button",{name:"Start 48-hour research simulation"}).click();
  expect((await simulation).postDataJSON()).toEqual({replay:false,protocol:"lightgbm_warmup_48h_v1"});
  await page.getByRole("button",{name:"Search foods",exact:true}).click();
  await page.getByRole("button",{name:"Add ingredient"}).click();
  await page.getByRole("checkbox").check();
  await page.getByRole("button",{name:"Save meal",exact:true}).click();
  const forecast=page.waitForRequest(r=>r.url().endsWith("/forecasts")&&r.method()==="POST");
  await page.getByRole("button",{name:"Run forecast",exact:true}).click();
  expect((await forecast).postDataJSON().model_key).toBe("lightgbm");
  await expect(page.getByText("Calibrated marginal 80% interval",{exact:true})).toBeVisible();
  await page.getByText("Model inputs and version",{exact:true}).click();
  await expect(page.getByText(/Used 288 history readings/)).toBeVisible();
  await page.getByText("Forecast data table",{exact:true}).click();
  await expect(page.getByRole("cell",{name:"-5",exact:true}).first()).toBeVisible();
  for(const width of [320,390,768,1024,1440,1920]){
    await page.setViewportSize({width,height:900});
    await expect(page.getByLabel("Forecast model")).toBeVisible();
    expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBe(true);
  }
  await page.screenshot({path:`../.cache/lightgbm-fixture-${test.info().project.name}.png`,fullPage:true});
});
