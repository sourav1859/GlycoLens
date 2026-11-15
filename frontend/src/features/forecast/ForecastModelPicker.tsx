"use client";
import { useEffect, useState } from "react";
import { api } from "../../lib/application-api";

export type ModelKey = "chronos" | "lightgbm";
type Capability = {key:ModelKey;label:string;available:boolean;reason?:string|null};

export function ForecastModelPicker({value,onChange,disabled=false,ready=true,prepareLong}:{
  value:ModelKey;onChange:(value:ModelKey)=>void;disabled?:boolean;ready?:boolean;prepareLong?:()=>void;
}) {
  const [models,setModels]=useState<Capability[]>([]);
  const [failure,setFailure]=useState("");
  useEffect(()=>{
    if(!ready)return;
    let active=true;
    void api("/forecasts/models").then(result=>{
      if(!Array.isArray(result.models)||!result.models.every((m:Capability)=>["chronos","lightgbm"].includes(m.key)&&typeof m.available==="boolean"))throw new Error("Model capabilities unavailable");
      if(active)setModels(result.models);
    }).catch(()=>{if(active)setFailure("Research-model availability could not be checked. Chronos remains the default; retry after the service recovers.");});
    return ()=>{active=false;};
  },[ready]);
  const lightgbm=models.find(m=>m.key==="lightgbm");
  return <div className="model-picker">
    <label className="field">Forecast model<select value={value} disabled={disabled} onChange={event=>onChange(event.target.value as ModelKey)}>
      <option value="chronos">Chronos · default</option>
      <option value="lightgbm" disabled={!lightgbm?.available}>LightGBM · research option</option>
    </select></label>
    <p className="muted small">Chronos was effectively unchanged across the tested synthetic meal and portion changes; its meal-response capability check failed. Forecasts remain research context estimates. Actual meal-response accuracy has not been established.</p>
    {failure&&<p role="status" className="muted small">{failure}</p>}
    {lightgbm&&!lightgbm.available&&<p className="muted small">{lightgbm.reason}</p>}
    {value==="lightgbm"&&<><p className="notice-panel">LightGBM needs 24 hours of simulated glucose history. Its current-meal predictor uses carbohydrates; protein, fat and fiber remain nutrition facts. Its calibrated intervals have unverified coverage in this simulation.</p>
      {prepareLong?<button type="button" disabled={disabled} onClick={prepareLong}>Start 48-hour research simulation</button>:<p className="small">Prepare the 48-hour research source in the demo before saving a new meal. Existing meals keep their original source context.</p>}</>}
  </div>;
}
