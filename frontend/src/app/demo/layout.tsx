import type { ReactNode } from "react";
import { SimulationShell } from "../../features/simulation/SimulationShell";
export default function Layout({children}:{children:ReactNode}) {return <SimulationShell>{children}</SimulationShell>;}
