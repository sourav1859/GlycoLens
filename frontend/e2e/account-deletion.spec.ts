import { expect, test } from "@playwright/test";
import { login, mockAccount } from "./account-fixture";

test("deletion requires password, exact confirmation and acknowledgement; cancellation discards secrets", async ({ page }) => {
  await mockAccount(page); await login(page); await page.goto("/settings/privacy");
  await page.getByRole("button", { name: "Review account deletion" }).click();
  const remove = page.getByRole("button", { name: "Permanently delete my account", exact: true });
  await expect(remove).toBeDisabled();
  await page.getByLabel("Current password", { exact: true }).fill("synthetic current passphrase");
  await page.getByLabel("Type DELETE to confirm").fill("delete");
  await page.getByRole("checkbox").check(); await expect(remove).toBeDisabled();
  await page.getByLabel("Type DELETE to confirm").fill("DELETE"); await expect(remove).toBeEnabled();
  await page.getByRole("button", { name: "Cancel", exact: true }).click();
  await page.getByRole("button", { name: "Review account deletion" }).click();
  await expect(page.getByLabel("Current password", { exact: true })).toHaveValue("");
  await expect(remove).toBeDisabled();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await page.evaluate(() => {
    const key = Object.keys(localStorage).find(key => key.endsWith("-auth-token"))!;
    const value = JSON.parse(localStorage.getItem(key)!); value.user.is_anonymous = true;
    localStorage.setItem(key, JSON.stringify(value));
  });
  await page.reload();
  await expect(page.getByText(/Anonymous demo deletion is not supported yet/)).toBeVisible();
  await expect(page.getByRole("button", { name: "Review account deletion" })).toHaveCount(0);
});

test("wrong password preserves account; successful deletion clears both tabs and private navigation", async ({ page, context }) => {
  await mockAccount(page); await login(page); await expect(page).toHaveURL(/\/home$/);
  const other = await context.newPage(); await mockAccount(other); await other.goto("/settings");
  await expect(other.getByRole("heading", { name: "Your preferences", exact: true })).toBeVisible();
  await page.goto("/settings/privacy"); await page.getByRole("button", { name: "Review account deletion" }).click();
  await page.getByLabel("Current password", { exact: true }).fill("synthetic wrong password");
  await page.getByLabel("Type DELETE to confirm").fill("DELETE"); await page.getByRole("checkbox").check();
  let accepted = false;
  await page.route("**/api/v1/me", async route => {
    expect(route.request().method()).toBe("DELETE");
    expect(Object.keys(route.request().postDataJSON()).sort()).toEqual(["confirmation", "password"]);
    await route.fulfill(accepted ? { json: { deleted: true, file_cleanup_pending: true } } : { status: 403, json: { detail: "Current password could not be verified" } });
  });
  const remove = page.getByRole("button", { name: "Permanently delete my account", exact: true });
  await remove.click(); await expect(page.getByRole("alert").filter({ hasText: "Current password could not be verified" })).toBeVisible();
  await expect(page).toHaveURL(/\/settings\/privacy$/);
  await expect(page.getByLabel("Current password", { exact: true })).toHaveValue("");
  accepted = true; await page.getByLabel("Current password", { exact: true }).fill("synthetic current passphrase");
  await page.route("**/auth/v1/logout**", route => route.fulfill({ status: 503, json: { msg: "Synthetic logout outage" } }));
  await remove.click(); await expect(page).toHaveURL(/\/account-deleted\?cleanup=pending$/);
  await expect(page.getByRole("heading", { name: "Your account has been deleted" })).toBeVisible();
  await expect(page.getByRole("status")).toContainText("cleanup is pending");
  await expect(other).toHaveURL(/\/auth\/sign-in/);
  expect(await page.evaluate(() => Object.keys(localStorage).filter(key => key.endsWith("-auth-token")))).toEqual([]);
  await page.goto("/home"); await expect(page).toHaveURL(/\/auth\/sign-in/);
});
