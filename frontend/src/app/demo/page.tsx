import Link from "next/link";
import { SignOutButton } from "../../features/auth/SignOutButton";
import { MealWorkflow } from "../../features/meal/MealWorkflow";
export default function Demo() { return <main><section className="hero"><div className="demo-account-bar"><Link href="/home">← Back to GlycoLens</Link><SignOutButton /></div><p className="eyebrow">Virtual-patient research workflow</p><h1>GlycoLens demo</h1><p>Simulated data for research and education. Sign in first if anonymous demo access is unavailable.</p></section><MealWorkflow /></main>; }
