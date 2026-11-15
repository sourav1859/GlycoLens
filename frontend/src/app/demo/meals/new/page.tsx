import { MealComposer } from "../../../../features/meal/MealComposer";
export default async function Page({searchParams}:{searchParams:Promise<{copy?:string}>}){const {copy}=await searchParams;return <MealComposer copyId={copy}/>;}
