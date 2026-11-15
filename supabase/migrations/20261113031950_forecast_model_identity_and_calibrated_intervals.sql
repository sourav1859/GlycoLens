-- Approved cloud development target only. Forward-compatible; no row rewrite/reset.
begin;

-- Preserve finite signed calibrated tails. Median/history constraints stay separate.
alter table public.forecast_points drop constraint forecast_points_q10_check;
alter table public.forecast_points drop constraint forecast_points_q90_check;
alter table public.forecast_points add constraint forecast_points_q10_check check(q10 between -99999 and 99999);
alter table public.forecast_points add constraint forecast_points_q90_check check(q90 between -99999 and 99999);

create or replace function public.app_commit_forecast(p_user uuid,p_meal uuid,p_revision integer,p_key uuid,p_model text,p_version text,
    p_context text,p_origin timestamptz,p_latency numeric,p_provenance jsonb,p_points jsonb,p_input jsonb)
returns uuid language plpgsql security invoker set search_path='' as $$
declare meal public.meals; forecast uuid; existing public.forecasts; identity jsonb; source_meta jsonb;
    required_count integer:=24; item jsonb; is_tabular boolean:=false; step integer:=0;
begin
  select * into strict meal from public.meals where id=p_meal and user_id=p_user for update;
  if meal.revision is distinct from p_revision or meal.state='cancelled' then raise exception 'meal changed' using errcode='23505'; end if;
  identity:=p_input->'model_identity';
  is_tabular:=p_model='metabonet_lightgbm_direct';
  if is_tabular then
    required_count:=288;
    if identity->>'model_key' is distinct from 'lightgbm'
      or identity->>'feature_version' is distinct from 'metabonet_tabular_v1'
      or identity->>'interval_kind' is distinct from 'calibrated_marginal_80'
      or (identity->>'history_samples')::integer is distinct from 288
      or coalesce(identity->>'bundle_sha256','') !~ '^[a-f0-9]{64}$'
      or coalesce(identity->>'calibration_sha256','') !~ '^[a-f0-9]{64}$'
      or p_version is distinct from 'metabonet_tabular_v1:'||(identity->>'bundle_sha256')
      or p_context is distinct from 'cgm_insulin_carbohydrates'
      or p_input->'source_metadata'->>'scenario' is distinct from 'lightgbm_warmup_48h_v1'
      or p_input->'response'->>'schema_version' is distinct from '2.0'
    then raise exception 'invalid tabular model identity' using errcode='22023'; end if;
    select metadata into source_meta from public.source_sessions where id=meal.source_session_id and user_id=p_user;
    if source_meta is distinct from p_input->'source_metadata' then raise exception 'source metadata differs' using errcode='22023'; end if;
  end if;
  if meal.source_session_id is null or meal.recorded_at is distinct from p_origin
      or jsonb_array_length(p_input->'history') is distinct from required_count
      or p_input->'meal'->>'id' is distinct from p_meal::text
  then raise exception 'invalid frozen input' using errcode='22023'; end if;
  if p_input->'response'->>'schema_version'='2.0' then
    if identity->>'model_id' is distinct from p_model or identity->>'model_version' is distinct from p_version
      or identity is distinct from p_provenance->'model_identity'
      or identity is distinct from p_input->'response'->'provenance'
      or p_input->'response'->'forecast' is distinct from p_points
      or p_input->'response'->>'model_id' is distinct from p_model
      or p_input->'response'->>'model_version' is distinct from p_version
    then raise exception 'forecast identity or payload differs' using errcode='22023'; end if;
  end if;
  if is_tabular then
    -- All model-input readings must be authentic past readings in the owned source.
    if (select count(distinct value->>'recorded_at') from jsonb_array_elements(p_input->'history'))<>288 then
      raise exception 'duplicate history' using errcode='22023'; end if;
    for item in select value from jsonb_array_elements(p_input->'history') loop
      if (item->>'recorded_at')::timestamptz > p_origin
        or (item->>'recorded_at')::timestamptz < p_origin-interval '1435 minutes'
        or extract(epoch from (p_origin-(item->>'recorded_at')::timestamptz))::integer % 300<>0
        or not exists(select 1 from public.cgm_readings c where c.user_id=p_user and c.source_session_id=meal.source_session_id
          and c.recorded_at=(item->>'recorded_at')::timestamptz and c.glucose_mg_dl=(item->>'glucose_mg_dl')::numeric)
      then raise exception 'unverified tabular history' using errcode='22023'; end if;
    end loop;
  end if;
  if jsonb_array_length(p_points) is distinct from 24 then raise exception 'invalid forecast grid' using errcode='22023'; end if;
  for item in select value from jsonb_array_elements(p_points) loop
    step:=step+1;
    if (item->>'minute')::integer is distinct from step*5
      or (not is_tabular and ((item->>'q10_mg_dl')::numeric not between 20 and 600
        or (item->>'q50_mg_dl')::numeric not between 20 and 600 or (item->>'q90_mg_dl')::numeric not between 20 and 600))
    then raise exception 'invalid model output grid or bounds' using errcode='22023'; end if;
  end loop;
  perform pg_advisory_xact_lock(hashtextextended(p_user::text||p_key::text,0));
  select * into existing from public.forecasts where user_id=p_user and idempotency_key=p_key;
  if found then
    if existing.meal_id is distinct from p_meal or existing.meal_revision is distinct from p_revision
      or existing.model_id is distinct from p_model or existing.model_version is distinct from p_version
      or existing.input_snapshot->'model_identity' is distinct from identity
    then raise exception 'request key reused' using errcode='23505'; end if;
    return existing.id;
  end if;
  forecast:=public.app_save_forecast(p_user,p_meal,p_key,p_model,p_version,p_context,p_origin,p_latency,p_provenance,p_points);
  update public.forecasts set source_session_id=meal.source_session_id,meal_revision=p_revision,input_snapshot=p_input where id=forecast;
  return forecast;
end $$;

-- A scenario response must retain the baseline's complete frozen model identity.
create or replace function public.app_save_scenario(p_user uuid,p_forecast uuid,p_multiplier numeric,p_key uuid,p_response jsonb)
returns uuid language plpgsql security invoker set search_path='' as $$
declare existing public.portion_scenarios; saved uuid; parent public.forecasts; point jsonb; step integer:=0;
begin
  select * into parent from public.forecasts where id=p_forecast and user_id=p_user and input_snapshot is not null for update;
  if not found then raise exception 'forecast unavailable' using errcode='22023'; end if;
  if parent.input_snapshot->'model_identity' is not null and (p_response->'provenance' is distinct from parent.input_snapshot->'model_identity'
      or p_response->>'model_id' is distinct from parent.model_id or p_response->>'model_version' is distinct from parent.model_version) then
    raise exception 'scenario model identity differs' using errcode='22023'; end if;
  if p_multiplier is null or p_multiplier not between 0.1 and 2 or jsonb_array_length(p_response->'forecast') is distinct from 24 then
    raise exception 'invalid scenario' using errcode='22023'; end if;
  for point in select value from jsonb_array_elements(p_response->'forecast') loop
    step:=step+1;
    if (point->>'minute')::integer is distinct from step*5
      or point->>'q10_mg_dl' is null or point->>'q50_mg_dl' is null or point->>'q90_mg_dl' is null
      or (point->>'q10_mg_dl')::numeric not between -99999 and 99999
      or (point->>'q50_mg_dl')::numeric not between 0.01 and 1000
      or (point->>'q90_mg_dl')::numeric not between -99999 and 99999
      or (point->>'q10_mg_dl')::numeric > (point->>'q50_mg_dl')::numeric
      or (point->>'q50_mg_dl')::numeric > (point->>'q90_mg_dl')::numeric then
      raise exception 'invalid scenario grid or interval' using errcode='22023'; end if;
  end loop;
  perform pg_advisory_xact_lock(hashtextextended(p_user::text||p_key::text,0));
  select * into existing from public.portion_scenarios where user_id=p_user and idempotency_key=p_key;
  if found then
    if existing.forecast_id<>p_forecast or existing.multiplier<>p_multiplier then raise exception 'key reused' using errcode='23505'; end if;
    return existing.id;
  end if;
  if (select count(*) from public.portion_scenarios where user_id=p_user and forecast_id=p_forecast)>=10 then
    raise exception 'scenario limit reached' using errcode='PT429'; end if;
  insert into public.portion_scenarios(user_id,forecast_id,multiplier,idempotency_key,response)
    values(p_user,p_forecast,p_multiplier,p_key,p_response) returning id into saved;
  return saved;
end $$;
revoke all on function public.app_commit_forecast(uuid,uuid,integer,uuid,text,text,text,timestamptz,numeric,jsonb,jsonb,jsonb) from public,anon,authenticated;
revoke all on function public.app_save_scenario(uuid,uuid,numeric,uuid,jsonb) from public,anon,authenticated;
grant execute on function public.app_commit_forecast(uuid,uuid,integer,uuid,text,text,text,timestamptz,numeric,jsonb,jsonb,jsonb) to service_role;
grant execute on function public.app_save_scenario(uuid,uuid,numeric,uuid,jsonb) to service_role;
commit;
