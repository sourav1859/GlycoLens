import { afterEach, beforeEach, expect, it, vi } from "vitest";
const mocks=vi.hoisted(()=>({getSession:vi.fn(),signOut:vi.fn()}));
vi.mock("./supabase",()=>({supabase:()=>({auth:mocks})}));
import { api } from "./application-api";
beforeEach(()=>{vi.clearAllMocks();mocks.signOut.mockResolvedValue({error:null});});
afterEach(()=>vi.unstubAllGlobals());

it("discards an earlier owner's response after account switching without signing out the new owner", async()=>{
  mocks.getSession.mockResolvedValueOnce({data:{session:{access_token:"token-a",user:{id:"a"}}}}).mockResolvedValueOnce({data:{session:{access_token:"token-b",user:{id:"b"}}}});
  vi.stubGlobal("fetch",vi.fn().mockResolvedValue(new Response(JSON.stringify({private:"owner-a-record"}),{status:200})));
  await expect(api("/me")).rejects.toThrow("account changed");
  expect(mocks.signOut).not.toHaveBeenCalled();
});
it("uses no-store, overwrites an untrusted bearer header and clears a revoked local session",async()=>{
  mocks.getSession.mockResolvedValue({data:{session:{access_token:"verified-session",user:{id:"a"}}}});
  const fetcher=vi.fn().mockResolvedValue(new Response(JSON.stringify({detail:"Session is invalid or expired"}),{status:401}));vi.stubGlobal("fetch",fetcher);
  await expect(api("/me",{headers:{Authorization:"Bearer forged"}})).rejects.toThrow("Session is invalid");
  expect(fetcher.mock.calls[0][1].cache).toBe("no-store");
  expect(fetcher.mock.calls[0][1].headers.get("Authorization")).toBe("Bearer verified-session");
  expect(mocks.signOut).toHaveBeenCalledWith({scope:"local"});
});
