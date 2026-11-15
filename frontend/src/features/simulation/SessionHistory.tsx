"use client";
import Link from "next/link";
import { useState } from "react";
import { useResource } from "../../lib/use-resource";
import { AsyncState } from "../../components/ui/AsyncState";
import { useAccount } from "../auth/AccountProvider";

type Source={id:string;mode:string;clock_at:string;created_at:string};
function valid(value:unknown):value is {sources:Source[];has_more:boolean} {
  const v=value as {sources:Source[];has_more:boolean};
  return !!v&&Array.isArray(v.sources)&&v.sources.every(s=>typeof s.id==="string"&&typeof s.clock_at==="string")&&typeof v.has_more==="boolean";
}
export function SessionHistory(){
  const [offset,setOffset]=useState(0),{account}=useAccount();
  const {data,error,reload}=useResource(`/simulation/sources?offset=${offset}`,valid);
  return <section className="surface"><h1>Saved simulation sessions</h1><p>Each run and replay has its own history. Opening one never changes your personal app.</p>{error?<AsyncState title="Sessions unavailable" message={error} retry={reload} error/>:!data?<AsyncState title="Loading sessions…"/>:!data.sources.length?<p>No saved simulation sessions.</p>:data.sources.map(s=><article className="food-result" key={s.id}><div><strong>{s.mode} · {s.id.slice(0,8)}</strong><p>Virtual clock: {new Date(s.clock_at).toLocaleString(undefined,{timeZone:account?.preferences.timezone??"UTC"})}</p><p className="small muted">Created: {new Date(s.created_at).toLocaleString(undefined,{timeZone:account?.preferences.timezone??"UTC"})}</p></div><Link className="button secondary" href={`/demo/sessions/${s.id}`}>Open session</Link></article>)}<div className="intro-actions"><button className="button secondary" disabled={!offset} onClick={()=>setOffset(Math.max(0,offset-20))}>Previous</button><button className="button secondary" disabled={!data?.has_more} onClick={()=>setOffset(offset+20)}>Next</button></div></section>;
}
