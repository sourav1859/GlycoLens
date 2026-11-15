import { SavedForecast } from "../../../../features/forecast/SavedForecast";
export default async function Page({params}:{params:Promise<{id:string}>}){const {id}=await params;return <SavedForecast id={id}/>;}
