import { MealWorkflow } from "../features/meal/MealWorkflow";

export default function Home() {
  return (
    <main>
      <section className="hero" aria-labelledby="page-title">
        <p className="eyebrow">Meal understanding · Virtual-patient research prototype</p>
        <h1 id="page-title">GlycoLens</h1>
        <p>
          Review meal nutrition and explore an uncertain glucose forecast with a simulated patient.
        </p>
      </section>
      <MealWorkflow />
    </main>
  );
}
