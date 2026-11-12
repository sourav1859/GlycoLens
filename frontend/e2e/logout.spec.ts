import { expect, test } from "@playwright/test";
import { login, mockAccount } from "./account-fixture";

test("header logout clears credentials, other tabs and protected back navigation", async ({ page, context }) => {
  await mockAccount(page);
  await login(page);
  await expect(page).toHaveURL(/\/home$/);
  const other = await context.newPage();
  await mockAccount(other);
  await other.goto("/settings");
  await expect(other.getByRole("heading", { name: "Your preferences" })).toBeVisible();
  const logout = page.waitForRequest(request => new URL(request.url()).pathname.endsWith("/auth/v1/logout"));
  await page.getByRole("button", { name: "Sign out", exact: true }).click();
  expect((await logout).method()).toBe("POST");
  await expect(page).toHaveURL(/\/auth\/sign-in/);
  await expect(other).toHaveURL(/\/auth\/sign-in/);
  expect(await page.evaluate(() => Object.keys(localStorage).filter(key => key.endsWith("-auth-token")))).toEqual([]);
  await page.goto("/profile");
  await expect(page).toHaveURL(/\/auth\/sign-in/);
  await expect(page.getByRole("heading", { name: "Your profile" })).toHaveCount(0);
});

test("anonymous demo logout requires confirmation and clears the draft across tabs", async ({ page, context }) => {
  await mockAccount(page);
  await login(page);
  await expect(page).toHaveURL(/\/home$/);
  await page.evaluate(() => {
    const key = Object.keys(localStorage).find(key => key.endsWith("-auth-token"))!;
    const session = JSON.parse(localStorage.getItem(key)!);
    session.user.is_anonymous = true;
    localStorage.setItem(key, JSON.stringify(session));
  });
  await page.goto("/demo");
  const other = await context.newPage();
  await mockAccount(other);
  await other.goto("/demo");
  await other.getByRole("button", { name: "Choose virtual patient" }).click();
  await other.getByLabel("Meal name").fill("Private synthetic draft");
  page.once("dialog", dialog => dialog.dismiss());
  await page.getByRole("button", { name: "Sign out", exact: true }).click();
  await expect(page).toHaveURL(/\/demo$/);
  page.once("dialog", dialog => dialog.accept());
  await page.getByRole("button", { name: "Sign out", exact: true }).click();
  await expect(page).toHaveURL(/\/auth\/sign-in/);
  await expect(other.getByRole("button", { name: "Choose virtual patient" })).toBeVisible();
  await expect(other.getByLabel("Meal name")).toHaveCount(0);
});
