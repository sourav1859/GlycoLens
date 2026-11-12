"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAccount } from "./AccountProvider";
import { AsyncState } from "../../components/ui/AsyncState";
import { safeReturnPath } from "../../lib/auth-policy";

export function AuthCallback() {
  const { session, initializing, recovery } = useAccount();
  const router = useRouter();
  const [expired, setExpired] = useState(false);
  useEffect(() => {
    if (initializing) return;
    if (session) router.replace(recovery ? "/auth/reset-password" : safeReturnPath(new URLSearchParams(window.location.search).get("next")));
    else { const timer = setTimeout(() => setExpired(true), 3000); return () => clearTimeout(timer); }
  }, [session, initializing, recovery, router]);
  return <main className="public-main"><section className="surface empty-panel">{expired ? <><h1>This link couldn’t be verified</h1><p>It may be expired, already used, or opened on another device. Return to sign in or request a fresh link.</p><Link className="button" href="/auth/sign-in">Return to sign in</Link></> : <AsyncState title="Verifying your account link…" message="Keep this page open while the secure sign-in flow completes." />}</section></main>;
}
