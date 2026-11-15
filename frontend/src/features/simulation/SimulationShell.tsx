"use client";
import Link from "next/link";
import type { ReactNode } from "react";
import { SignOutButton } from "../auth/SignOutButton";
import { useWorkspace } from "./Workspace";

export function SimulationShell({children}:{children:ReactNode}) {
  const {exit}=useWorkspace();
  return <main className="public-main"><section className="surface simulation-banner" aria-label="Virtual simulation workspace"><div className="surface-heading"><div><strong>Virtual simulation</strong><p className="small muted">Synthetic research data and a virtual clock. Personal meals and current dates stay in your regular app.</p></div><Link className="button" href="/home" onClick={exit}>Exit simulation</Link></div><nav className="intro-actions" aria-label="Simulation navigation"><Link href="/demo">Run simulation</Link><Link href="/demo/sessions">Saved sessions</Link><Link href="/demo/meals">Simulation meals</Link><Link href="/demo/forecasts">Simulation forecasts</Link><Link href="/demo/legacy">Legacy history</Link><SignOutButton /></nav></section>{children}</main>;
}
