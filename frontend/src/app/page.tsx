import { ForecastDemo } from "../features/forecast/ForecastDemo";

export default function Home() {
  return (
    <main>
      <section className="hero" aria-labelledby="page-title">
        <p className="eyebrow">Milestone 1 API + visualization</p>
        <h1 id="page-title">GlycoLens</h1>
        <p>
          Explore how a probabilistic glucose forecast can be presented clearly while the full
          meal workflow is still under development.
        </p>
      </section>
      <ForecastDemo />
    </main>
  );
}
