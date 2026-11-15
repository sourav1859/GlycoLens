import { defineConfig } from "@playwright/test";
if(process.env.GLYCOLENS_LIVE_WORKSPACE_TEST!=="1")throw new Error("Live workspace tests require explicit opt-in and tagged cloud fixtures");
export default defineConfig({testDir:"./e2e-live",workers:1,retries:0,timeout:90000,use:{baseURL:"http://127.0.0.1:3000",viewport:{width:1440,height:1000},trace:"off",screenshot:"off"}});
