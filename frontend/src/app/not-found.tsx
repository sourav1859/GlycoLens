import Link from "next/link";
export default function NotFound() { return <main className="public-main"><section className="surface empty-panel"><p className="eyebrow">404 · A different path</p><h1>We couldn’t find that page</h1><p>The link may have changed or the item may no longer be available.</p><Link className="button" href="/home">Go to Home</Link></section></main>; }
