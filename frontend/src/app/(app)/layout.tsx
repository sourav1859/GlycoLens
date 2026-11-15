import type { ReactNode } from "react";
import { AppShell } from "../../components/layout/AppShell";
import { AccountGate } from "../../features/auth/AccountProvider";

export const dynamic = "force-dynamic";

export default function ApplicationLayout({ children }: { children: ReactNode }) {
  return <AccountGate><AppShell>{children}</AppShell></AccountGate>;
}
