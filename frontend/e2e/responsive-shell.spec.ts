import { expect,test } from "@playwright/test";
import { login,mockAccount } from "./account-fixture";

test("shared navigation, reload and dialog focus work across mobile/tablet/desktop widths",async({page})=>{
  await mockAccount(page);await login(page);await expect(page).toHaveURL(/\/home$/);
  const widths=test.info().project.name==="desktop"?[320,360,390,430,768,820,1024,1280,1440,1920]:[390];
  for(const width of widths){
    await page.setViewportSize({width,height:width<500?760:900});
    const nav=page.getByRole("navigation",{name:width<768?"Mobile navigation":"Main navigation",exact:true});
    await expect(nav).toBeVisible();
    for(const name of ["Home","Search","Meal log","Forecasts","Nutrition"]){await expect(nav.getByRole("link",{name,exact:true})).toBeVisible();}
    expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBe(true);
    const add=page.getByRole("button",{name:width<768?"Add a meal":"Add meal",exact:true});
    await add.click();const dialog=page.getByRole("dialog",{name:"How would you like to add a meal?"});
    await expect(dialog).toBeVisible();await page.keyboard.press("Escape");await expect(dialog).not.toBeVisible();await expect(add).toBeFocused();
  }
  await page.setViewportSize({width:1280,height:900});
  await page.getByRole("navigation",{name:"Main navigation",exact:true}).getByRole("link",{name:"Nutrition",exact:true}).click();
  await expect(page).toHaveURL(/\/nutrition$/);await page.reload();await expect(page).toHaveURL(/\/nutrition$/);
  await page.screenshot({path:`../.cache/p02-shell-${test.info().project.name}.png`,fullPage:true});
});

test("required onboarding persists across reload and optional information can be skipped",async({page})=>{
  const me=await mockAccount(page,false);await login(page);await expect(page).toHaveURL(/\/onboarding$/);
  await page.getByLabel(/^Timezone/).fill("Asia/Kolkata");await page.getByLabel("Glucose display unit").selectOption("mmol/L");
  await page.getByRole("button",{name:"Save and continue",exact:true}).click();await expect(page.getByRole("heading",{name:"Choose your starting data source"})).toBeVisible();
  await page.reload();await expect(page.getByRole("heading",{name:"Choose your starting data source"})).toBeVisible();
  await page.getByRole("button",{name:"Save and continue",exact:true}).click();await page.getByRole("button",{name:"Skip optional details",exact:true}).click();
  await expect(page.getByRole("heading",{name:"Everything look right?"})).toBeVisible();
  await expect(page.getByRole("button",{name:"Open my Home"})).toBeDisabled();await page.getByRole("checkbox").check();await page.getByRole("button",{name:"Open my Home"}).click();
  await expect(page).toHaveURL(/\/home$/);expect(me.onboarding.completed_steps).toContain("preferences");expect(me.preferences.timezone).toBe("Asia/Kolkata");
  await page.screenshot({path:`../.cache/p03-onboarding-complete-${test.info().project.name}.png`,fullPage:true});
});

test("protected pages require sign-in and unavailable email recovery is explicit",async({page})=>{
  await mockAccount(page);await page.goto("/settings");await expect(page).toHaveURL(/\/auth\/sign-in\?next=/);
  await page.goto("/auth/forgot-password");await expect(page.getByRole("button",{name:"Request reset link"})).toBeDisabled();
});
