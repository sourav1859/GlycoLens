export const primaryNavigation = [
  { href: "/home", label: "Home", icon: "home" },
  { href: "/search", label: "Search", icon: "search" },
  { href: "/meals", label: "Meal log", icon: "meal" },
  { href: "/forecasts", label: "Forecasts", icon: "chart" },
  { href: "/nutrition", label: "Nutrition", icon: "nutrition" },
] as const;

export const accountNavigation = [
  { href: "/favorites", label: "Favorites", icon: "heart" },
  { href: "/profile", label: "Profile", icon: "profile" },
  { href: "/settings", label: "Settings", icon: "settings" },
  { href: "/notifications", label: "Notifications", icon: "bell" },
  { href: "/help", label: "Help & information", icon: "help" },
] as const;

export function primaryRouteFor(path: string) {
  if (path === "/scan" || path === "/recipes/analyze") return "/meals";
  if (path.startsWith("/recipes/") || path.startsWith("/products/")) return "/search";
  return primaryNavigation.find(item => path === item.href || path.startsWith(item.href + "/"))?.href;
}

export function routeTitle(path: string) {
  return [...primaryNavigation, ...accountNavigation].find(item => path === item.href)?.label ?? "GlycoLens";
}
