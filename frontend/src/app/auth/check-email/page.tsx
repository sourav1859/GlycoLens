import Link from "next/link";
export default function Page() { return <main className="public-main"><section className="surface empty-panel"><h1>Check your email</h1><p>If verification is required, open the link in the same browser to continue. Delivery may be unavailable in this development environment.</p><Link className="button" href="/auth/sign-in">Return to sign in</Link></section></main>; }
