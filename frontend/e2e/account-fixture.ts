import type { Page } from "@playwright/test";

export async function mockAccount(page: Page, completed = true) {
  const id="10000000-0000-4000-8000-000000000001";
  const me={user_id:id,display_name:"GlycoLens member",notice_version:"research-v1",preferences:{user_id:id,timezone:"UTC",glucose_unit:"mg/dL",source_mode:"simulation",revision:0,food_preferences:[] as string[]},onboarding:{user_id:id,flow_version:1,step:completed?"complete":"preferences",completed_steps:completed?["preferences","source","optional"]:[] as string[],revision:0,completed_at:completed?"2026-01-01T00:00:00Z":null,notice_version:completed?"research-v1":null},goals:[]};
  await page.route("**/auth/v1/**",async route=>{
    const path=new URL(route.request().url()).pathname;
    if(path.endsWith("/logout")){await route.fulfill({status:204});return;}
    const now=Math.floor(Date.now()/1000);
    const token=`${Buffer.from('{"alg":"HS256"}').toString("base64url")}.${Buffer.from(JSON.stringify({sub:id,session_id:"90000000-0000-4000-8000-000000000001",exp:now+3600,iat:now,role:"authenticated"})).toString("base64url")}.synthetic`;
    const user={id,email:"synthetic@example.invalid",aud:"authenticated",role:"authenticated",is_anonymous:false,app_metadata:{provider:"email",providers:["email"]},user_metadata:{},created_at:"2026-01-01T00:00:00Z"};
    await route.fulfill({json:path.endsWith("/user")?user:{access_token:token,refresh_token:"synthetic-refresh",token_type:"bearer",expires_in:3600,user}});
  });
  await page.route("**/api/v1/**",async route=>{
    const path=new URL(route.request().url()).pathname;
    if(path==="/api/v1/demo/session"){await route.fulfill({json:{user_id:id}});return;}
    if(path==="/api/v1/me" || path==="/api/v1/me/bootstrap"){await route.fulfill({json:me});return;}
    if(path==="/api/v1/me/onboarding"){
      const body=route.request().postDataJSON();
      if(body.revision!==me.onboarding.revision){await route.fulfill({status:409,json:{detail:"changed"}});return;}
      Object.assign(me.preferences,body.values);me.preferences.revision++;me.onboarding.revision++;
      if(body.values.display_name)me.display_name=body.values.display_name;
      if(!me.onboarding.completed_steps.includes(body.step))me.onboarding.completed_steps.push(body.step);
      me.onboarding.step=me.onboarding.step==="review"?"review":body.step==="preferences"?"source":body.step==="source"?"optional":"review";
      await route.fulfill({json:me});return;
    }
    if(path==="/api/v1/me/onboarding/complete"){
      me.onboarding.step="complete";me.onboarding.completed_at="2026-01-01T00:00:00Z";me.onboarding.notice_version="research-v1";me.onboarding.revision++;
      await route.fulfill({json:me});return;
    }
    if(path==="/api/v1/me/preferences"){
      const body=route.request().postDataJSON();if(body.display_name)me.display_name=body.display_name;
      Object.assign(me.preferences,body);me.preferences.revision++;
      await route.fulfill({json:me});return;
    }
    await route.fulfill({status:503,json:{detail:"This feature is unavailable in the isolated browser fixture"}});
  });
  return me;
}

export async function login(page: Page) {
  await page.goto("/auth/sign-in");
  await page.getByLabel("Email address").fill("synthetic@example.invalid");
  await page.getByLabel("Password",{exact:true}).fill("synthetic passphrase only");
  await page.getByRole("button",{name:"Sign in",exact:true}).click();
}
