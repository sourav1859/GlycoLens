import { MealComposer } from "../../../../../features/meal/MealComposer";
export default async function Page({params}:{params:Promise<{id:string}>}){const {id}=await params;return <MealComposer mealId={id}/>;}
