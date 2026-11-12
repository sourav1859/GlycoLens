"use client";
import { useEffect, useState } from "react";
import { api } from "./application-api";

export function useResource<T>(path: string, validate: (value: unknown) => value is T) {
  const [result, setResult] = useState<{path:string; data?:T; error?:string}>();
  const [version, setVersion] = useState(0);
  useEffect(() => {
    let active = true;
    void api(path).then(value => {
      if (!validate(value)) throw new Error("The returned data could not be validated");
      if (active) setResult({path,data:value});
    }).catch(reason => { if (active) setResult({path,error:reason instanceof Error ? reason.message : "Data unavailable"}); });
    return () => { active=false; };
  }, [path,validate,version]);
  return {data:result?.path===path ? result.data : undefined,error:result?.path===path ? result.error : undefined,reload:()=>setVersion(v=>v+1)};
}
