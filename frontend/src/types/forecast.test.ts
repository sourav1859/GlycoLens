import { isForecastResponse } from "./forecast";

function fixture() {
  const provenance={model_key:"lightgbm",model_id:"metabonet_lightgbm_direct",model_version:"metabonet_tabular_v1:"+"a".repeat(64),feature_version:"metabonet_tabular_v1",bundle_sha256:"a".repeat(64),calibration_sha256:"b".repeat(64),history_samples:288,interval_kind:"calibrated_marginal_80",inputs:["current carbohydrates"]};
  return {schema_version:"2.0",data_mode:"simulated",model_id:provenance.model_id,model_version:provenance.model_version,context_configuration:"cgm_insulin_carbohydrates",unit:"mg/dL",provenance,interval_kind:provenance.interval_kind,
    history:Array.from({length:288},(_,i)=>({minute:-1435+5*i,value_mg_dl:120})),
    forecast:Array.from({length:24},(_,i)=>({minute:5*(i+1),q10_mg_dl:-5,q50_mg_dl:40,q90_mg_dl:85})),
    summary:{minute_30_mg_dl:40,minute_60_mg_dl:40,minute_120_mg_dl:40},notice:"Synthetic transfer coverage unverified"};
}

test("signed marginal bands require the full versioned model identity",()=>{
  const value=fixture();expect(isForecastResponse(value)).toBe(true);
  expect(isForecastResponse({...value,schema_version:"1.0"})).toBe(false);
  expect(isForecastResponse({...value,provenance:{...value.provenance,calibration_sha256:null}})).toBe(false);
  expect(isForecastResponse({...value,history:value.history.slice(1)})).toBe(false);
  expect(isForecastResponse({...value,history:[null]})).toBe(false);
  expect(isForecastResponse({...value,forecast:[null]})).toBe(false);
});

test("nonfinite endpoints and model-version mismatch are rejected",()=>{
  const value=fixture();value.forecast[0].q10_mg_dl=Number.NaN;
  expect(isForecastResponse(value)).toBe(false);
  expect(isForecastResponse({...fixture(),model_version:"another"})).toBe(false);
});
