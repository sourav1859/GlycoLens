import { expect, test, type Page } from "@playwright/test";
import { login, mockAccount } from "./account-fixture";

async function fixture(page:Page) {
 await mockAccount(page);
 const food={id:"20000000-0000-4000-8000-000000000001",name:"Synthetic reviewed food with a long descriptive source name",source:"synthetic_fixture",source_food_id:"fixture",nutrient_basis_g:100,calories:180,carbs_g:30,protein_g:6,fat_g:4,fiber_g:null};
 const meal={workspace:"personal",id:"30000000-0000-4000-8000-000000000001",name:"Fixture meal",state:"logged",recorded_at:"2026-01-01T12:00:00Z",consumed_at:"2026-01-01T12:00:00Z",revision:1,source_session_id:null,meal_type:null,meal_items:[{food_id:food.id,grams:125,foods:food}],nutrition_provenance:{food_snapshots:[{...food,food_id:food.id,grams:125}]},calories:225,carbs_g:37.5,protein_g:7.5,fat_g:5,fiber_g:null};
 let saved:Record<string,unknown>|undefined;
 const summary={workspace:"personal",available:true,timezone:"UTC",day:"2026-01-01",source:null,days:[{day:"2026-01-01",meal_count:1,nutrients:Object.fromEntries(["calories","carbs_g","protein_g","fat_g","fiber_g"].map(f=>[f,{total:f==="fiber_g"?null:f==="calories"?225:f==="carbs_g"?37.5:f==="protein_g"?7.5:5,known_total:f==="fiber_g"?0:225,known_meals:f==="fiber_g"?0:1,missing_meals:f==="fiber_g"?1:0}]))}],meals:[meal],goals:[],latest_glucose:[],forecasts:[]};
 await page.route("**/api/v1/**",async route=>{
   const path=new URL(route.request().url()).pathname;
   if(path==="/api/v1/home"||path==="/api/v1/nutrition"){await route.fulfill({json:summary});return;}
   if(path==="/api/v1/foods/search"){await route.fulfill({json:{foods:[food],candidates:[]}});return;}
   if(path==="/api/v1/meals"&&route.request().method()==="POST"){
     saved=route.request().postDataJSON();Object.assign(meal,saved,{revision:1});
     const grams=(saved!.items as {grams:number}[])[0].grams;
     meal.calories=grams*1.8;meal.carbs_g=grams*.3;meal.nutrition_provenance.food_snapshots[0].grams=grams;
     await route.fulfill({json:{meal_id:meal.id,revision:1}});return;
   }
   if(path===`/api/v1/meals/${meal.id}`){await route.fulfill({json:[meal]});return;}
   if(path==="/api/v1/meals"){await route.fulfill({json:{meals:[meal],has_more:false}});return;}
   await route.fallback();
 });
 return {meal,summary,saved:()=>saved};
}

test("common composer reviews fractional yield and preserves unknown nutrients",async({page})=>{
 const f=await fixture(page);await login(page);await page.goto("/meals/new");
 await page.getByLabel("Food name",{exact:true}).fill("synthetic");await page.getByRole("button",{name:"Search foods",exact:true}).click();
 await page.getByRole("button",{name:"Add food",exact:true}).click();await page.getByLabel("Ingredient grams in recipe").fill("125");
 await page.getByLabel("Recipe yield in servings").fill("2");await page.getByLabel("Servings in this meal").fill("0.5");
 await expect(page.getByRole("button",{name:"Save reviewed meal"})).toBeDisabled();
 const nav=page.getByRole("navigation",{name:test.info().project.name==="mobile"?"Mobile navigation":"Main navigation",exact:true});
 await nav.getByRole("link",{name:"Search",exact:true}).click();await nav.getByRole("link",{name:"Meal log",exact:true}).click();
 await page.locator(".page-intro").getByRole("link",{name:"Add a meal",exact:true}).click();
 await expect(page.getByLabel("Ingredient grams in recipe")).toHaveValue("125");await expect(page.getByLabel("Servings in this meal")).toHaveValue("0.5");
 await expect(page.locator("dd").filter({hasText:/^Unknown/})).toBeVisible();await page.getByRole("checkbox").check();
 await page.getByRole("button",{name:"Save reviewed meal"}).click();await expect(page).toHaveURL(new RegExp(`/meals/${f.meal.id}$`));
 expect(f.saved()?.items).toMatchObject([{food_id:"20000000-0000-4000-8000-000000000001",grams:31.25}]);expect(f.saved()?.state).toBe("planned");expect(f.saved()?.consumed_at).toBeNull();
 await expect(page.getByText("This meal is excluded from eaten totals.",{exact:false})).toBeVisible();
 await expect(page.getByRole("button",{name:"Run selected forecast"})).toHaveCount(0);
});

test("populated Home and Nutrition reflow with unknown facts and no prescribed goals",async({page})=>{
 await fixture(page);await login(page);await page.goto("/home");await expect(page.getByRole("heading",{name:"Eaten today"})).toBeVisible();
 for(const width of [320,390,768,1024,1440]){
  await page.setViewportSize({width,height:800});expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  await expect(page.locator("dd").filter({hasText:/^Unknown/})).toBeVisible();
 }
 await page.goto("/nutrition");await expect(page.getByRole("table")).toBeVisible();await expect(page.getByText("No nutrition targets set.",{exact:false})).toBeVisible();
 await page.setViewportSize({width:320,height:760});expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
 await page.screenshot({path:`../.cache/p06-nutrition-${test.info().project.name}.png`,fullPage:true});
});

test("copied draft reviews current facts and does not inherit eaten status",async({page})=>{
 const f=await fixture(page);f.meal.nutrition_provenance.food_snapshots[0].calories=100;f.meal.calories=125;
 await login(page);await page.goto(`/meals/new?copy=${f.meal.id}`);
 await expect(page.getByText("225 kcal",{exact:true})).toBeVisible();
 await expect(page.getByRole("combobox",{name:/^Status/})).toHaveValue("planned");
 await expect(page.getByRole("button",{name:"Save reviewed meal"})).toBeDisabled();
});
