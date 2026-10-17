import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  timeout: 60000,
  fullyParallel: false,
  workers: 1,
  use: { baseURL: "http://127.0.0.1:3001", trace: "retain-on-failure" },
  webServer: [{
    command: "pnpm dev --port 3001",
    url: "http://127.0.0.1:3001",
    reuseExistingServer: false,
    timeout: 120000,
    env: { NEXT_PUBLIC_API_URL: "http://127.0.0.1:8001" },
  }, ...(process.env.GLYCOLENS_LIVE_E2E ? [{
    command: "..\\.venv\\Scripts\\python.exe -m uvicorn backend.app.main:app --app-dir .. --port 8001",
    url: "http://127.0.0.1:8001/health",
    reuseExistingServer: false,
    timeout: 120000,
    env: { GLYCOLENS_CORS_ORIGINS: "http://127.0.0.1:3001" },
  }] : [])],
  projects: [{ name: "desktop", use: { viewport: { width: 1280, height: 900 } } },
             { name: "mobile", use: { viewport: { width: 390, height: 844 } } }],
});
