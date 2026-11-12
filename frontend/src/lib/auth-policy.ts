export function safeReturnPath(value: string | null | undefined, fallback = "/home") {
  if (!value || !value.startsWith("/") || value.startsWith("//") || /[\\\u0000-\u001f]/.test(value)) return fallback;
  try {
    const decoded = decodeURIComponent(value);
    if (decoded.startsWith("//") || /[\\\u0000-\u001f]/.test(decoded)) return fallback;
    const url = new URL(value, "https://glycolens.invalid");
    if (url.origin !== "https://glycolens.invalid" || url.pathname.startsWith("/auth/")) return fallback;
    return url.pathname + url.search;
  } catch { return fallback; }
}

export function passwordIsValid(value: string) { return value.length >= 12 && value.length <= 128; }
export const emailDeliveryEnabled = process.env.NEXT_PUBLIC_AUTH_EMAIL_DELIVERY_ENABLED === "true";
