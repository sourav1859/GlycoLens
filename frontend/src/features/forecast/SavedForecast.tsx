"use client";
import Link from "next/link";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useWorkspace } from "../simulation/Workspace";
import { useResource } from "../../lib/use-resource";
import { isForecastResponse, type ForecastResponse } from "../../types/forecast";
import { ForecastChart } from "../../components/ForecastChart";
import { AsyncState } from "../../components/ui/AsyncState";
import { useAccount } from "../auth/AccountProvider";
import { ScenarioPanel } from "./ScenarioPanel";
type Saved={workspace?:string;forecast_id:string;meal_id:string;meal_revision:number;forecast_origin:string;forecast:ForecastResponse};
function valid(value:unknown):value is Saved {const v=value as Saved;return !!v&&typeof v.forecast_id==="string"&&Number.isInteger(v.meal_revision)&&isForecastResponse(v.forecast);}
export function SavedForecast({id,compact=false}:{id:string;compact?:boolean}) {
 const {data,error,reload}=useResource(`/forecasts/${id}`,valid),{account}=useAccount();
 const {simulation}=useWorkspace(),router=useRouter();
 const move=!!data&&!simulation;
 useEffect(()=>{if(move)router.replace(`/demo/forecasts/${id}`);},[move,router,id]);
 if(move)return <AsyncState title="Opening simulation forecast…"/>;
 if(error)return <AsyncState title="Forecast unavailable" message={error} error retry={reload}/>;
 if(!data)return <AsyncState title="Loading saved forecast…"/>;
 return <section><p className="muted small">Frozen meal revision {data.meal_revision} · origin {new Date(data.forecast_origin).toLocaleString(undefined,{timeZone:account?.preferences.timezone??"UTC"})} · {account?.preferences.glucose_unit}</p><ForecastChart data={data.forecast} unit={account?.preferences.glucose_unit}/><p className="small muted">Chart, summaries and table use your display unit; saved values remain canonical mg/dL. {data.forecast.interval_kind==="calibrated_marginal_80"?"Bands are symmetric marginal calibration intervals with unverified synthetic/personal coverage.":"q10–q90 is a model interval, not a clinical guarantee."}</p><div className="table-scroll" role="region" aria-label="Data table; scroll horizontally for all columns" tabIndex={0}><table><caption>Median and model interval</caption><thead><tr><th>Minutes</th><th>{data.forecast.interval_kind==="calibrated_marginal_80"?"Lower band":"q10"}</th><th>Median</th><th>{data.forecast.interval_kind==="calibrated_marginal_80"?"Upper band":"q90"}</th><th>Unit</th></tr></thead><tbody>{data.forecast.forecast.filter(p=>!compact||[30,60,120].includes(p.minute)).map(p=><tr key={p.minute}><th>+{p.minute}</th>{[p.q10_mg_dl,p.q50_mg_dl,p.q90_mg_dl].map((n,i)=><td key={i}>{(n/(account?.preferences.glucose_unit==="mmol/L"?18.0182:1)).toFixed(1)}</td>)}<td>{account?.preferences.glucose_unit}</td></tr>)}</tbody></table></div><div className="intro-actions"><Link className="button secondary" href={`/demo/meals/${data.meal_id}`}>View meal</Link>{compact&&<Link className="button secondary" href={`/demo/forecasts/${id}`}>Full forecast</Link>}</div>{!compact&&<ScenarioPanel id={id}/>}</section>;
}
