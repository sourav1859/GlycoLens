import { expect,test,type Page } from "@playwright/test";
import { mockAccount,login } from "./account-fixture";

const source="40000000-0000-4000-8000-000000000001";
const oldSource="40000000-0000-4000-8000-000000000002";
const food={id:"20000000-0000-4000-8000-000000000001",name:"Synthetic workspace food",source:"synthetic_fixture",source_food_id:"fixture",nutrient_basis_g:100,calories:180,carbs_g:30,protein_g:8,fat_g:4,fiber_g:5};
const today=()=>new Intl.DateTimeFormat("en-CA",{timeZone:"America/New_York"}).format(new Date());

async function fixture(page:Page){
 const me=await mockAccount(page);me.preferences.timezone="America/New_York";
 const now=new Date().toISOString();
 const personal={workspace:"personal",id:"30000000-0000-4000-8000-000000000001",name:"Personal meal today",recorded_at:now,consumed_at:now,state:"logged",revision:1,source_session_id:null,meal_type:null,calories:180,carbs_g:30,protein_g:8,fat_g:4,fiber_g:5,nutrition_provenance:{food_snapshots:[{...food,food_id:food.id,grams:100}]},meal_items:[{food_id:food.id,grams:100,foods:food}]};
 const simulated=[{...personal,workspace:"simulation",id:"30000000-0000-4000-8000-000000000002",name:"Earlier virtual meal",source_session_id:oldSource,recorded_at:"2026-01-01T13:35:00Z",consumed_at:null,state:"planned"},{...personal,workspace:"simulation",id:"30000000-0000-4000-8000-000000000003",name:"Later virtual meal",source_session_id:source,recorded_at:"2026-01-02T12:10:00Z",consumed_at:null,state:"planned"}];
 const rows=[personal,...simulated];
 const summary={available:true,workspace:"personal",timezone:"America/New_York",clock_at:now,day:today(),source:null,days:[{day:today(),meal_count:1,nutrients:Object.fromEntries(["calories","carbs_g","protein_g","fat_g","fiber_g"].map(f=>[f,{total:personal[f as keyof typeof personal],known_total:180,known_meals:1,missing_meals:0}]))}],meals:[personal],goals:[],latest_glucose:[],forecasts:[]};
 await page.route("**/api/v1/**",async route=>{
  const url=new URL(route.request().url()),path=url.pathname;
  if(path.endsWith("/home")||path.endsWith("/nutrition")){await route.fulfill({json:summary});return;}
  if(path.endsWith("/simulation/scenario")){await route.fulfill({json:{source_session_id:source,forecast_origin:"2026-01-02T12:10:00Z",sample_count:288,execution:"live",notice:"Synthetic browser fixture"}});return;}
  if(path.includes("/simulation/sources/")){await route.fulfill({json:{id:path.split("/").at(-1),mode:"simulation",clock_at:"2026-01-02T12:10:00Z",created_at:now,metadata:{}}});return;}
  if(path.endsWith("/timeline")){expect(url.searchParams.get("source_session_id")).toBeTruthy();await route.fulfill({json:{cgm:Array.from({length:288},()=>({recorded_at:"2026-01-02T12:10:00Z",glucose_mg_dl:118,source:"simulation"}))}});return;}
  if(path.endsWith("/forecasts/models")){await route.fulfill({json:{models:[{key:"chronos",label:"Chronos",available:true},{key:"lightgbm",label:"LightGBM",available:true}]}});return;}
  if(path.endsWith("/foods/search")){await route.fulfill({json:{foods:[food]}});return;}
  if(path.endsWith("/meals")){await route.fulfill({json:{meals:url.searchParams.get("workspace")==="simulation"?simulated:[personal],has_more:false}});return;}
  const meal=rows.find(m=>path.endsWith(`/meals/${m.id}`));
  if(meal){await route.fulfill({json:[meal]});return;}
  await route.fallback();
 });
 return {personal,simulated,summary};
}

test("personal screens reject a response from the simulation partition",async({page})=>{
 const f=await fixture(page);
 await page.route("**/api/v1/home",route=>route.fulfill({json:{...f.summary,workspace:"simulation",source:{id:source,clock_at:"2026-01-01T12:00:00Z"},meals:f.simulated}}));
 await login(page);await page.goto("/home");
 await expect(page.getByRole("alert").filter({hasText:"Daily data unavailable"})).toBeVisible();
 await expect(page.getByText("Earlier virtual meal",{exact:true})).toHaveCount(0);
 await page.route("**/api/v1/meals?**",route=>route.fulfill({json:{meals:f.simulated,has_more:false}}));
 await page.goto("/meals");await expect(page.getByRole("alert").filter({hasText:"Meal history unavailable"})).toBeVisible();
 await expect(page.getByText("Earlier virtual meal",{exact:true})).toHaveCount(0);
});

test("personal app uses current local day and no virtual controls",async({page})=>{
 await fixture(page);await login(page);await page.goto("/home");
 await expect(page.getByRole("heading",{name:"Your local time"})).toBeVisible();
 await expect(page.getByLabel("Local day")).toHaveValue(today());
 await expect(page.getByRole("button",{name:"Run virtual patient"})).toHaveCount(0);
 await expect(page.getByText("Personal meal today",{exact:true})).toBeVisible();
 await expect(page.getByText("Earlier virtual meal",{exact:true})).toHaveCount(0);
 for(const width of [320,390,768,1024,1440,1920]){await page.setViewportSize({width,height:850});expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);}
});

test("exit, browser back and refresh restore personal date and context",async({page})=>{
 await fixture(page);await login(page);await page.goto("/home");
 await page.getByLabel("Local day").fill("2026-01-01");
 await expect(page.getByLabel("Local day")).toHaveValue("2026-01-01");
 await page.getByRole("link",{name:"Open virtual simulation",exact:true}).click();
 await page.getByRole("button",{name:"Run new simulation",exact:true}).click();
 await expect(page.getByText(/Latest simulated glucose/)).toBeVisible();
 await page.getByRole("link",{name:"Exit simulation",exact:true}).click();
 await expect(page.getByLabel("Local day")).toHaveValue(today());
 await page.goBack();await expect(page.getByRole("link",{name:"Exit simulation",exact:true})).toBeVisible();
 await page.getByRole("link",{name:"Exit simulation",exact:true}).click();await expect(page).toHaveURL(/\/home$/);await page.reload();
 await expect(page.getByLabel("Local day")).toHaveValue(today());
 await expect(page.getByText(/Latest simulated glucose/)).toHaveCount(0);
});

test("earlier simulation meals remain visible and old detail links resolve scope",async({page})=>{
 const f=await fixture(page);await login(page);await page.goto("/demo/meals");
 await expect(page.getByText("Earlier virtual meal",{exact:true})).toBeVisible();
 await expect(page.getByText("Later virtual meal",{exact:true})).toBeVisible();
 await expect(page.getByText("Personal meal today",{exact:true})).toHaveCount(0);
 await page.goto(`/meals/${f.simulated[0].id}`);
 await expect(page).toHaveURL(new RegExp(`/demo/meals/${f.simulated[0].id}$`));
 await expect(page.getByRole("heading",{name:"Earlier virtual meal"})).toBeVisible();
 await page.goto("/meals");await expect(page.getByText("Personal meal today",{exact:true})).toBeVisible();
});

test("simulation in another tab does not switch personal day",async({page,context})=>{
 await fixture(page);await login(page);await page.goto("/home");
 const other=await context.newPage();await fixture(other);await other.goto("/demo");
 await other.getByRole("button",{name:"Run new simulation",exact:true}).click();
 await expect(other.getByText(/Latest simulated glucose/)).toBeVisible();
 await expect(page.getByLabel("Local day")).toHaveValue(today());
 await page.reload();await expect(page.getByLabel("Local day")).toHaveValue(today());
 await other.close();
});

test("slow simulation response after exit cannot select a hidden source",async({page})=>{
 await fixture(page);await login(page);await page.goto("/demo");
 let release=()=>{};
 await page.route("**/api/v1/simulation/scenario",async route=>{
  await new Promise<void>(resolve=>{release=resolve;});
  await route.fulfill({json:{source_session_id:source,forecast_origin:"2026-01-01T12:00:00Z",sample_count:24,execution:"live",notice:"Late fixture"}}).catch(()=>{});
 });
 const request=page.waitForRequest("**/api/v1/simulation/scenario");
 await page.getByRole("button",{name:"Run new simulation",exact:true}).click();await request;
 await page.getByRole("link",{name:"Exit simulation",exact:true}).click();await expect(page).toHaveURL(/\/home$/);release();
 await expect(page.getByLabel("Local day")).toHaveValue(today());
 await page.getByRole("link",{name:"Open virtual simulation",exact:true}).click();
 await expect(page.getByText(/Run the scenario to begin/)).toBeVisible();
});

test("personal draft survives entering and leaving simulation",async({page})=>{
 await fixture(page);await login(page);await page.goto("/meals/new");
 await page.getByLabel("Food name",{exact:true}).fill("synthetic");await page.getByRole("button",{name:"Search foods",exact:true}).click();
 await page.getByRole("button",{name:"Add food",exact:true}).click();
 await page.getByLabel("Ingredient grams in recipe").fill("137");
 const nav=page.getByRole("navigation",{name:test.info().project.name==="mobile"?"Mobile navigation":"Main navigation",exact:true});
 await nav.getByRole("link",{name:"Home",exact:true}).click();
 await page.getByRole("link",{name:"Open virtual simulation",exact:true}).click();
 await page.getByRole("link",{name:"Exit simulation",exact:true}).click();
 await page.getByRole("link",{name:"Add a meal",exact:true}).first().click();
 await expect(page.getByLabel("Ingredient grams in recipe")).toHaveValue("137");
});
