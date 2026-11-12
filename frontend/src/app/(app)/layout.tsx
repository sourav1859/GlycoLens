import type { ReactNode } from "react";
import { AppShell } from "../../components/layout/AppShell";
import { AccountGate } from "../../features/auth/AccountProvider";
import { MealDrafts } from "../../features/meal/MealDrafts";

export const dynamic = "force-dynamic";

export default function ApplicationLayout({ children }: { children: ReactNode }) {
  return <AccountGate><MealDrafts><AppShell>{children}</AppShell></MealDrafts></AccountGate>;
}
