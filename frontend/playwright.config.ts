import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  timeout: 60000,
  fullyParallel: false,
  workers: 1,
  use: { baseURL: "http://127.0.0.1:3001", trace: "retain-on-failure", channel: process.env.GLYCOLENS_BROWSER_CHANNEL === "chrome" ? "chrome" : undefined },
  webServer: [{
    command: "pnpm dev --port 3001",
    url: "http://127.0.0.1:3001",
    reuseExistingServer: false,
    timeout: 120000,
    env: { GLYCOLENS_E2E:"1", NEXT_PUBLIC_API_URL: "http://127.0.0.1:8001", NEXT_PUBLIC_SUPABASE_URL:"https://synthetic-supabase.example.invalid", NEXT_PUBLIC_SUPABASE_ANON_KEY:"synthetic-public-fixture",NEXT_PUBLIC_AUTH_EMAIL_DELIVERY_ENABLED:"false" },
  }],
  projects: [{ name: "desktop", use: { viewport: { width: 1280, height: 900 } } },
             { name: "mobile", use: { viewport: { width: 390, height: 844 } } }],
});
