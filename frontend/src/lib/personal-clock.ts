"use client";
import { useEffect, useState } from "react";

export function localDay(at:Date,timezone:string) {
  const parts=new Intl.DateTimeFormat("en-US",{timeZone:timezone,year:"numeric",month:"2-digit",day:"2-digit"}).formatToParts(at);
  const value=(name:string)=>parts.find(p=>p.type===name)!.value;
  return `${value("year")}-${value("month")}-${value("day")}`;
}
export function usePersonalClock(timezone:string) {
  const [now,setNow]=useState<Date|null>(null);
  useEffect(()=>{
    const tick=()=>setNow(new Date());
    queueMicrotask(tick);
    const timer=setInterval(tick,1000);
    window.addEventListener("focus",tick);document.addEventListener("visibilitychange",tick);
    return()=>{clearInterval(timer);window.removeEventListener("focus",tick);document.removeEventListener("visibilitychange",tick);};
  },[]);
  return {now,day:now?localDay(now,timezone):""};
}
