export const nutrientFields = ["calories", "carbs_g", "protein_g", "fat_g", "fiber_g"] as const;
export type Nutrient = typeof nutrientFields[number];
export type Food = { id?: string; food_id?: string; name: string; source: string; source_food_id: string; nutrient_basis_g: number } & Partial<Record<Nutrient, number | null>>;
export type DraftItem = { food: Food; grams: number };
export function expectedFacts(food:Food){return {nutrient_basis_g:food.nutrient_basis_g,...Object.fromEntries(nutrientFields.map(f=>[f,food[f]??null]))};}
export type Meal = { workspace: "personal"|"simulation"|"legacy_unclassified"; id: string; name: string; state: "planned" | "logged" | "cancelled"; recorded_at: string; consumed_at: string | null; revision: number; source_session_id: string | null; meal_type: string | null; meal_items?:{food_id:string;grams:number;foods:Food}[]; nutrition_provenance: { food_snapshots: (Food & { grams: number })[] } } & Record<Nutrient, number | null>;

export function portionFacts(items: DraftItem[], servings: number, portion: number) {
  if (!Number.isFinite(servings) || servings <= 0 || !Number.isFinite(portion) || portion <= 0 || items.some(i => !Number.isFinite(i.grams) || i.grams <= 0 || !Number.isFinite(i.food.nutrient_basis_g) || i.food.nutrient_basis_g <= 0)) return null;
  return Object.fromEntries(nutrientFields.map(field => [field, items.some(item => item.food[field] == null) ? null : items.reduce((total,item) => total + Number(item.food[field])*item.grams/item.food.nutrient_basis_g/servings*portion,0)])) as Record<Nutrient, number|null>;
}
export function isFood(value: unknown): value is Food {
  if (!value || typeof value !== "object") return false;
  const v = value as Food;
  return typeof v.name === "string" && typeof v.source === "string" && typeof v.source_food_id === "string" && (v.id === undefined || typeof v.id === "string") && (v.nutrient_basis_g === undefined || typeof v.nutrient_basis_g === "number" && v.nutrient_basis_g > 0) && nutrientFields.every(f => v[f] == null || typeof v[f] === "number" && Number.isFinite(v[f]) && v[f]! >= 0);
}
export function isMeal(value: unknown): value is Meal {
  if (!value || typeof value !== "object") return false;
  const v = value as Meal;
  const scoped=["personal","simulation","legacy_unclassified"].includes(v.workspace)&&(v.workspace==="personal"?v.source_session_id===null:v.workspace==="simulation"?typeof v.source_session_id==="string"&&!!v.source_session_id:v.source_session_id===null||typeof v.source_session_id==="string");
  return scoped && typeof v.id === "string" && typeof v.name === "string" && ["planned","logged","cancelled"].includes(v.state) && typeof v.recorded_at === "string" && Number.isInteger(v.revision) && Array.isArray(v.nutrition_provenance?.food_snapshots) && nutrientFields.every(f => v[f] === null || typeof v[f] === "number");
}
export function displayNutrient(value: number | null | undefined) { return value == null ? "Unknown" : value.toLocaleString(undefined, { maximumFractionDigits: 1 }); }
