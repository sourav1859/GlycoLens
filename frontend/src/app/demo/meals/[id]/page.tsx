import { MealDetail } from "../../../../features/meal/MealDetail";
export default async function Page({params}:{params:Promise<{id:string}>}){const {id}=await params;return <MealDetail id={id}/>;}
