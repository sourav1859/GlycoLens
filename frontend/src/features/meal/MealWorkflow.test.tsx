import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, expect, test, vi } from "vitest";
import { MealWorkflow } from "./MealWorkflow";
import { WorkspaceProvider } from "../simulation/Workspace";
import { MealDrafts } from "./MealDrafts";

vi.mock("next/navigation",()=>({usePathname:()=>"/demo"}));
vi.mock("../auth/AccountProvider", () => ({ useAccount: () => ({ session: { user: { id: "owner" } },account:{user_id:"owner",preferences:{timezone:"UTC"}} }) }));
vi.mock("../../components/ForecastChart", () => ({ ForecastChart: () => null }));
vi.mock("../forecast/ForecastModelPicker", () => ({ ForecastModelPicker: () => null }));
vi.mock("../../lib/application-api", () => ({
  enterDemo: async () => ({ user_id: "owner" }),
  api: async (path: string) => {
    if (path === "/simulation/scenario") return {source_session_id:"source", forecast_origin: "2026-01-01T12:00:00Z", sample_count: 24, execution: "live", notice: "Synthetic unit fixture" };
    if (path.startsWith("/timeline?")) return { cgm: [] };
    if (path.startsWith("/simulation/sources/")) return {id:"source",clock_at:"2026-01-01T12:00:00Z",metadata:{}};
    if (path === "/meals/parse-recipe") return { ingredients: [{ name: "rice", quantity: 100, unit: "g", needs_review: true }], servings: 1 };
    if (path.startsWith("/foods/search")) return { foods: [{ id: "food", name: "Synthetic rice", source: "fixture", source_food_id: "rice", nutrient_basis_g: 100, calories: 100, carbs_g: 20, protein_g: 2, fat_g: 1, fiber_g: 0 }] };
    if (path === "/meals") return { meal_id: "meal" };
    throw new Error("Unexpected test request");
  },
}));

beforeEach(() => vi.stubGlobal("crypto", { randomUUID: () => "operation" }));

test.each([
  ["Ingredient 1", "brown rice"],
  ["Ingredient 1 quantity", "200"],
  ["Ingredient 1 unit", "cup"],
])("editing %s clears review and saved forecast eligibility", async (label, value) => {
  render(<WorkspaceProvider><MealDrafts><MealWorkflow /></MealDrafts></WorkspaceProvider>);
  await screen.findByRole("button", { name: "Run new simulation" });
  fireEvent.click(screen.getByRole("button", { name: "Run new simulation" }));
  await screen.findByText(/New simulation completed/);
  fireEvent.click(screen.getByRole("button", { name: "Recipe text" }));
  fireEvent.change(screen.getByLabelText("Home recipe"), { target: { value: "100 g rice" } });
  fireEvent.click(screen.getByRole("button", { name: "Extract ingredients" }));
  await screen.findByLabelText("Ingredient 1");
  fireEvent.click(screen.getByRole("button", { name: "Find food facts" }));
  fireEvent.click(screen.getByRole("button", { name: "Search foods" }));
  await screen.findByRole("button", { name: "Add ingredient" });
  fireEvent.click(screen.getByRole("button", { name: "Add ingredient" }));
  await screen.findByLabelText("Ingredient grams");
  fireEvent.click(screen.getByRole("checkbox"));
  await waitFor(() => expect(screen.getByRole("button", { name: "Save meal" })).toBeEnabled());
  fireEvent.click(screen.getByRole("button", { name: "Save meal" }));
  await waitFor(() => expect(screen.getByRole("button", { name: "Run forecast" })).toBeEnabled());
  fireEvent.click(screen.getByRole("button", { name: "Recipe text" }));
  fireEvent.change(screen.getByLabelText(label, { exact: true }), { target: { value } });
  expect(screen.getByRole("checkbox")).not.toBeChecked();
  expect(screen.getByRole("button", { name: "Run forecast" })).toBeDisabled();
});
