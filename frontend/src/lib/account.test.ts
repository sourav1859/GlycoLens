import { describe, expect, it } from "vitest";
import { isAccount } from "./account";

function account() { return { user_id:"synthetic-owner",display_name:"Member",notice_version:"research-v1",preferences:{user_id:"synthetic-owner",timezone:"America/New_York",glucose_unit:"mg/dL",source_mode:"simulation",revision:0,food_preferences:[]},onboarding:{user_id:"synthetic-owner",flow_version:1,step:"preferences",revision:0,completed_steps:[],completed_at:null,notice_version:null},goals:[] }; }
describe("account transport validation", () => {
  it("accepts a complete preferences payload without personal health fields", () => { expect(isAccount(account())).toBe(true); });
  it("rejects a foreign-owner child and invalid display/source values", () => {
    const foreign=account(); foreign.preferences.user_id="another-owner"; expect(isAccount(foreign)).toBe(false);
    const unit=account(); unit.preferences.glucose_unit="unknown"; expect(isAccount(unit)).toBe(false);
    const zone=account(); zone.preferences.timezone="Not/AZone"; expect(isAccount(zone)).toBe(false);
  });
  it("rejects false completion without server evidence", () => { const value=account(); value.onboarding.step="complete"; expect(isAccount(value)).toBe(false); });
});
