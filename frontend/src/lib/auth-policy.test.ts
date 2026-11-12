import { describe, expect, it } from "vitest";
import { passwordIsValid, safeReturnPath } from "./auth-policy";

describe("safe account routing and password boundaries", () => {
  it("preserves valid internal deep links", () => { expect(safeReturnPath("/meals/new?mode=recipe")).toBe("/meals/new?mode=recipe"); });
  it.each(["https://outside.invalid", "//outside.invalid", "/\\outside.invalid", "/%5Coutside.invalid", "/auth/callback", "/bad\nvalue", "%zz"])("rejects unsafe return %s", value => { expect(safeReturnPath(value)).toBe("/home"); });
  it("bounds passwords without forcing health or other personal information", () => { expect(passwordIsValid("short")).toBe(false); expect(passwordIsValid("a sufficiently long passphrase")).toBe(true); expect(passwordIsValid("a".repeat(129))).toBe(false); });
});
