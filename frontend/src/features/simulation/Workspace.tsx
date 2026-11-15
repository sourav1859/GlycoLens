"use client";
import { createContext, useContext, useEffect, useRef, useState, type ReactNode, type RefObject } from "react";
import { usePathname } from "next/navigation";

type Source = { id:string; clock_at:string; sample_count?:number };
const Context=createContext<{source:Source|null;select:(source:Source|null)=>void;generation:RefObject<number>;exit:()=>void}|null>(null);
export function WorkspaceProvider({children}:{children:ReactNode}) {
  const [source,select]=useState<Source|null>(null);
  const generation=useRef(0);
  const path=usePathname();
  useEffect(()=>{if(!path.startsWith("/demo"))generation.current+=1;},[path]);
  function exit(){generation.current+=1;select(null);}
  return <Context.Provider value={{source,select,generation,exit}}>{children}</Context.Provider>;
}
export function useWorkspace() {
  const context=useContext(Context),path=usePathname();
  if(!context)throw new Error("Workspace provider missing");
  const simulation=path.startsWith("/demo");
  return {...context,simulation,workspace:simulation?"simulation" as const:"personal" as const,base:simulation?"/demo":""};
}
