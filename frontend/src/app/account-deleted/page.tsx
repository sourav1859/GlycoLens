import Link from "next/link";
export default async function Page({ searchParams }: { searchParams: Promise<{ cleanup?: string }> }) {
  const pending = (await searchParams).cleanup === "pending";
  return <main className="public-main"><article className="surface"><p className="eyebrow">YOUR DATA CONTROLS</p><h1>Your account has been deleted</h1><p>There is no recovery window. Your account and active application records have been removed.</p>{pending && <p role="status">Private source file cleanup is pending and will retry automatically. Your account cannot be restored during cleanup.</p>}<p>Provider backups and security logs follow provider retention. Keep or remove any exports you downloaded yourself.</p><Link className="button" href="/">Return to GlycoLens</Link></article></main>;
}
