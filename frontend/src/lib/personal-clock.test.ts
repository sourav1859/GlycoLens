import { act, renderHook } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";
import { localDay,usePersonalClock } from "./personal-clock";

afterEach(()=>vi.useRealTimers());
test.each([
 ["2026-11-14T12:00:00Z","Pacific/Kiritimati","2026-11-15"],
 ["2026-11-14T04:00:00Z","Pacific/Honolulu","2026-11-13"],
 ["2026-03-08T06:59:59Z","America/New_York","2026-03-08"],
 ["2026-03-08T07:00:00Z","America/New_York","2026-03-08"],
 ["2026-11-01T05:30:00Z","America/New_York","2026-11-01"],
 ["2026-11-01T06:30:00Z","America/New_York","2026-11-01"],
])("%s groups in %s",(instant,zone,day)=>expect(localDay(new Date(instant),zone)).toBe(day));
test("personal default day rolls over at local midnight and timezone changes regroup it",async()=>{
 vi.useFakeTimers();vi.setSystemTime(new Date("2026-11-15T04:59:59Z"));
 const hook=renderHook(({zone})=>usePersonalClock(zone),{initialProps:{zone:"America/New_York"}});
 await act(async()=>{vi.runAllTicks();});
 expect(hook.result.current.day).toBe("2026-11-14");
 act(()=>vi.advanceTimersByTime(2000));expect(hook.result.current.day).toBe("2026-11-15");
 hook.rerender({zone:"Pacific/Honolulu"});expect(hook.result.current.day).toBe("2026-11-14");
});
