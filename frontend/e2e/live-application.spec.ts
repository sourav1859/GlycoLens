import { expect, test } from "@playwright/test";

test("local real Auth, live simulator and selected pretrained forecast", async ({ page }) => {
  test.skip(true, "Historical local-stack test. Use the explicitly guarded cloud harness; do not enable this unscoped anonymous/model path.");
  test.setTimeout(180000);
  await page.goto("/demo");
  await page.getByRole("button", { name: "Choose virtual patient" }).click();
  await page.getByRole("button", { name: "Run live scenario" }).click();
  await expect(page.getByText("Latest simulated glucose:")).toBeVisible({ timeout: 120000 });
  await page.getByLabel("Search food", { exact: true }).fill("synthetic");
  await page.getByRole("button", { name: "Search foods", exact: true }).click();
  await page.getByRole("button", { name: "Add ingredient" }).first().click();
  await page.getByRole("checkbox").check();
  await page.getByRole("button", { name: "Save meal", exact: true }).click();
  await page.getByRole("button", { name: "Run forecast", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Two-hour glucose forecast" })).toBeVisible({ timeout: 60000 });
  await expect(page.getByText("amazon/chronos-2", { exact: true })).toBeVisible();
  await expect(page.getByText("Virtual-patient earlier meal (illustrative nutrition)", { exact: false })).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await page.screenshot({ path: `../.cache/m2-live-${test.info().project.name}.png`, fullPage: true });
});
