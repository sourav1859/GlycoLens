import { describe, expect, it } from "vitest";
import { portionFacts, type Food } from "./meal-facts";
const food: Food = { id:"fixture", name:"Fixture", source:"synthetic", source_food_id:"fixture", nutrient_basis_g:100, calories:180, carbs_g:30, protein_g:6, fat_g:4, fiber_g:null };
describe("portion preview", () => {
  it("uses grams, fractional yield and chosen servings with no volume guesses", () => {
    expect(portionFacts([{food,grams:100},{food,grams:25}],2,.5)).toMatchObject({calories:56.25,carbs_g:9.375,fiber_g:null});
    expect(portionFacts([{food,grams:100}],.5,1)?.calories).toBe(360);
  });
  it("rejects invalid amounts and never converts unknown to zero", () => {
    expect(portionFacts([{food,grams:NaN}],1,1)).toBeNull();
    expect(portionFacts([{food,grams:100}],0,1)).toBeNull();
    expect(portionFacts([{food,grams:100}],1,1)?.fiber_g).toBeNull();
  });
});
