# Frontend End-to-End Tests

The responsive-shell, meal-pages and retained demo suites use synthetic Auth/API
fixtures. `playwright.config.ts` supplies fake Supabase configuration. They never
prove real cloud, email, provider, model or phone-camera acceptance. The historical
unscoped live application test stays skipped; use guarded cloud runners instead.

Install the pinned Chromium runtime, then run `pnpm --dir frontend exec playwright
test e2e/responsive-shell.spec.ts e2e/meal-pages.spec.ts e2e/meal-workflow.spec.ts`.
On this machine set `PLAYWRIGHT_BROWSERS_PATH` to the ignored project cache.
See the implementation report for the final run and earlier selector corrections.
