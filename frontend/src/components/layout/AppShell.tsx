"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, type ReactNode } from "react";
import { accountNavigation, primaryNavigation, primaryRouteFor, routeTitle } from "../../lib/navigation";
import { Icon } from "../ui/Icon";
import { AdaptiveDialog } from "../ui/AdaptiveDialog";
import { SignOutButton } from "../../features/auth/SignOutButton";

export function Brand() {
  return <span className="brand"><span className="brand-mark" aria-hidden="true"><Icon name="chart" /></span><span>Glyco<span className="brand-light">Lens</span></span></span>;
}

export function AppShell({ children }: { children: ReactNode }) {
  const path = usePathname();
  const [quickAdd, setQuickAdd] = useState(false);
  const active = primaryRouteFor(path);
  return <div className="app-shell">
    <a href="#app-main" className="skip-link">Skip to content</a>
    <aside className="desktop-sidebar">
      <Link href="/home" className="brand-link" aria-label="GlycoLens Home"><Brand /></Link>
      <p className="nav-section-label">YOUR EVERYDAY</p>
      <nav aria-label="Main navigation">{primaryNavigation.map(item => <Link key={item.href} href={item.href} title={item.label} aria-current={active === item.href ? "page" : undefined}><Icon name={item.icon} /><span className="nav-label">{item.label}</span></Link>)}</nav>
      <div className="sidebar-bottom"><p className="nav-section-label">YOUR SPACE</p><nav aria-label="Account navigation">{accountNavigation.map(item => <Link key={item.href} href={item.href} title={item.label} aria-current={path.startsWith(item.href) ? "page" : undefined}><Icon name={item.icon} /><span className="nav-label">{item.label}</span></Link>)}</nav><p className="sidebar-notice">A clearer view.<br />Research, not treatment advice.</p></div>
    </aside>
    <div className="app-body">
      <header className="app-header"><div className="header-location"><span className="mobile-brand"><Brand /></span><span className="desktop-location">Your space <span aria-hidden="true">/</span> <strong>{routeTitle(path)}</strong></span></div><div className="header-actions"><button className="button compact header-add" onClick={() => setQuickAdd(true)}><Icon name="plus" /><span>Add meal</span></button><Link className="icon-button" href="/notifications" aria-label="Notifications"><Icon name="bell" /></Link><Link className="account-button" href="/profile" aria-label="Profile and settings"><Icon name="profile" /></Link><SignOutButton /></div></header>
      <main id="app-main" className="app-main" tabIndex={-1}>{children}<footer className="app-footer"><span>Made for understanding. Research and education only.</span><span><Link href="/privacy">Privacy</Link><Link href="/help">Help</Link></span></footer></main>
    </div>
    <nav className="mobile-navigation" aria-label="Mobile navigation">{primaryNavigation.map(item => <Link key={item.href} href={item.href} aria-current={active === item.href ? "page" : undefined}><Icon name={item.icon} /><span>{item.label}</span></Link>)}</nav>
    <button className="floating-add" type="button" aria-label="Add a meal" onClick={() => setQuickAdd(true)}><Icon name="plus" /></button>
    <AdaptiveDialog open={quickAdd} title="How would you like to add a meal?" onClose={() => setQuickAdd(false)}><p className="muted">Choose a starting point. You’ll review portions and food facts before saving.</p><div className="quick-add-options">{[
      ["/meals/new", "Search or enter food", "Find food facts and review your portion", "search"],
      ["/scan", "Scan a barcode", "Use your camera or type the code", "scan"],
      ["/recipes/analyze", "Enter a recipe", "Review extracted ingredients and servings", "spark"],
    ].map(([href,title,description,icon]) => <Link href={href} key={href} onClick={() => setQuickAdd(false)}><span className="icon-tile"><Icon name={icon} /></span><span><strong>{title}</strong><small>{description}</small></span><Icon name="arrow" /></Link>)}</div></AdaptiveDialog>
  </div>;
}
