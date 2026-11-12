export type Preferences = { user_id: string; timezone: string; glucose_unit: "mg/dL" | "mmol/L"; source_mode: "simulation" | "replay"; source_session_id?: string | null; revision: number; food_preferences: string[] };
export type Onboarding = { user_id: string; revision: number; flow_version: 1; step: "preferences" | "source" | "optional" | "review" | "complete"; completed_steps: string[]; completed_at: string | null; notice_version: string | null };
export type NutritionGoal = { id: string; user_id: string; nutrient: "calories" | "carbs_g" | "protein_g" | "fat_g" | "fiber_g"; target: number; unit: "kcal" | "g"; effective_date: string };
export type Account = { user_id: string; display_name: string; preferences: Preferences; onboarding: Onboarding; goals: NutritionGoal[]; notice_version: "research-v1" };

function object(value: unknown): value is Record<string, unknown> { return typeof value === "object" && value !== null && !Array.isArray(value); }
function revision(value: unknown): value is number { return typeof value === "number" && Number.isInteger(value) && value >= 0; }
export function isAccount(value: unknown): value is Account {
  if (!object(value) || typeof value.user_id !== "string" || typeof value.display_name !== "string" || !value.display_name.trim() || value.notice_version !== "research-v1") return false;
  const p = value.preferences, o = value.onboarding;
  if (!object(p) || !object(o) || p.user_id !== value.user_id || o.user_id !== value.user_id) return false;
  if (typeof p.timezone !== "string" || !["mg/dL", "mmol/L"].includes(String(p.glucose_unit)) || !["simulation", "replay"].includes(String(p.source_mode)) || !revision(p.revision) || !Array.isArray(p.food_preferences) || !p.food_preferences.every(item => typeof item === "string")) return false;
  try { new Intl.DateTimeFormat("en", { timeZone: p.timezone }); } catch { return false; }
  if (o.flow_version !== 1 || !revision(o.revision) || !["preferences", "source", "optional", "review", "complete"].includes(String(o.step)) || !Array.isArray(o.completed_steps) || !o.completed_steps.every(step => ["preferences", "source", "optional"].includes(String(step)))) return false;
  if (o.step === "complete" && (typeof o.completed_at !== "string" || !Number.isFinite(Date.parse(o.completed_at)) || o.notice_version !== value.notice_version || !o.completed_steps.includes("preferences") || !o.completed_steps.includes("source"))) return false;
  return Array.isArray(value.goals) && value.goals.every(goal => object(goal) && goal.user_id === value.user_id && typeof goal.nutrient === "string" && ["calories", "carbs_g", "protein_g", "fat_g", "fiber_g"].includes(goal.nutrient) && typeof goal.target === "number" && Number.isFinite(goal.target) && goal.target > 0 && goal.unit === (goal.nutrient === "calories" ? "kcal" : "g"));
}
