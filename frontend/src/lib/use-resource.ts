"use client";
import { useEffect, useState } from "react";
import { useAccount } from "../features/auth/AccountProvider";
import { useWorkspace } from "../features/simulation/Workspace";
import { api } from "./application-api";

export function useResource<T>(path: string, validate: (value: unknown) => value is T, refreshScope="") {
  const {session,account}=useAccount(),{workspace}=useWorkspace();
  const identity=`${session?.user.id??"guest"}:${workspace}:${account?.preferences.timezone??"UTC"}:${path}:${refreshScope}`;
  const [result, setResult] = useState<{path:string; data?:T; error?:string}>();
  const [version, setVersion] = useState(0);
  useEffect(() => {
    let active = true;
    void api(path).then(value => {
      if (!validate(value)) throw new Error("The returned data could not be validated");
      if (active) setResult({path:identity,data:value});
    }).catch(reason => { if (active) setResult({path:identity,error:reason instanceof Error ? reason.message : "Data unavailable"}); });
    return () => { active=false; };
  }, [path,validate,version,identity]);
  return {data:result?.path===identity ? result.data : undefined,error:result?.path===identity ? result.error : undefined,reload:()=>setVersion(v=>v+1)};
}
