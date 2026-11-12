export function AsyncState({ title, message, error = false, retry }: { title: string; message?: string; error?: boolean; retry?: () => void }) {
  return <div className={`async-state ${error ? "is-error" : ""}`} role={error ? "alert" : "status"} aria-live="polite"><strong>{title}</strong>{message && <p>{message}</p>}{retry && <button type="button" className="button secondary" onClick={retry}>Try again</button>}</div>;
}
