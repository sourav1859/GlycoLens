import type { Metadata } from "next";
import type { ReactNode } from "react";

import "./globals.css";
import "./responsive.css";
import { AccountProvider } from "../features/auth/AccountProvider";

export const metadata: Metadata = {
  title: "GlycoLens",
  description: "Research prototype for meal-centered glucose forecasting",
  manifest: "/manifest.webmanifest",
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en">
      <body><AccountProvider>{children}</AccountProvider></body>
    </html>
  );
}
