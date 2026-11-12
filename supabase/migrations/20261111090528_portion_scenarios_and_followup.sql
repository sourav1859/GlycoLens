begin;
create table public.portion_scenarios (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.users(id) on delete cascade,
  forecast_id uuid not null references public.forecasts(id) on delete cascade,
  multiplier numeric not null check(multiplier between 0.1 and 2),
  idempotency_key uuid not null,
  response jsonb not null check(jsonb_typeof(response)='object'),
  created_at timestamptz not null default now(),
  unique(user_id,idempotency_key)
);
create index portion_forecast_idx on public.portion_scenarios(forecast_id);
alter table public.portion_scenarios enable row level security;
revoke all on public.portion_scenarios from public,anon,authenticated;
grant select on public.portion_scenarios to authenticated;
grant select,insert,delete on public.portion_scenarios to service_role;
create policy owner_read on public.portion_scenarios for select to authenticated using((select auth.uid())=user_id);
create policy active_session_gate on public.portion_scenarios as restrictive for all to authenticated using((select private.session_is_active()));
create function public.app_save_scenario(p_user uuid,p_forecast uuid,p_multiplier numeric,p_key uuid,p_response jsonb)
returns uuid language plpgsql security invoker set search_path='' as $$
declare existing public.portion_scenarios; saved uuid;
begin
  if not exists(select 1 from public.forecasts where id=p_forecast and user_id=p_user and input_snapshot is not null) then
    raise exception 'forecast unavailable' using errcode='22023'; end if;
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
revoke all on function public.app_save_scenario(uuid,uuid,numeric,uuid,jsonb) from public,anon,authenticated;
grant execute on function public.app_save_scenario(uuid,uuid,numeric,uuid,jsonb) to service_role;

create function public.app_advance_source(p_user uuid,p_session uuid,p_previous timestamptz,p_clock timestamptz,p_cgm jsonb,p_insulin jsonb)
returns void language plpgsql security invoker set search_path='' as $$
declare source public.source_sessions; point jsonb;
begin
  select * into strict source from public.source_sessions where id=p_session and user_id=p_user for update;
  if source.clock_at is distinct from p_previous then raise exception 'source changed' using errcode='23505'; end if;
  if p_clock<=p_previous or p_clock>p_previous+interval '2 hours' then raise exception 'invalid clock advance' using errcode='22023'; end if;
  for point in select value from jsonb_array_elements(p_cgm) loop
    if (point->>'recorded_at')::timestamptz<=p_previous or (point->>'recorded_at')::timestamptz>p_clock then raise exception 'invalid reading time' using errcode='22023'; end if;
    insert into public.cgm_readings(user_id,source_session_id,recorded_at,glucose_mg_dl,source)
      values(p_user,p_session,(point->>'recorded_at')::timestamptz,(point->>'glucose_mg_dl')::numeric,'simulation');
  end loop;
  for point in select value from jsonb_array_elements(p_insulin) loop
    if (point->>'recorded_at')::timestamptz<=p_previous or (point->>'recorded_at')::timestamptz>p_clock then raise exception 'invalid insulin time' using errcode='22023'; end if;
    insert into public.insulin_events(user_id,source_session_id,recorded_at,event_type,units,insulin_kind,source_unit,source)
      values(p_user,p_session,(point->>'recorded_at')::timestamptz,point->>'event_type',(point->>'units')::numeric,point->>'insulin_kind',point->>'source_unit','simulation');
  end loop;
  update public.source_sessions set clock_at=p_clock where id=p_session;
end $$;
revoke all on function public.app_advance_source(uuid,uuid,timestamptz,timestamptz,jsonb,jsonb) from public,anon,authenticated;
grant execute on function public.app_advance_source(uuid,uuid,timestamptz,timestamptz,jsonb,jsonb) to service_role;

create function public.app_store_actuals(p_user uuid,p_forecast uuid,p_values jsonb)
returns void language plpgsql security invoker set search_path='' as $$
declare forecast public.forecasts; meal public.meals; clock timestamptz;
begin
  select * into strict forecast from public.forecasts where id=p_forecast and user_id=p_user;
  select * into strict meal from public.meals where id=forecast.meal_id and user_id=p_user for update;
  select clock_at into clock from public.source_sessions where id=forecast.source_session_id and user_id=p_user;
  if meal.revision is distinct from forecast.meal_revision or meal.state<>'logged' or clock<forecast.forecast_origin+interval '2 hours'
     or (p_values->>'available_at')::timestamptz>clock then raise exception 'actuals not yet eligible' using errcode='22023'; end if;
  insert into public.meal_outcomes(meal_id,actual_30,actual_60,actual_120,available_at,trajectory_metrics_json)
    values(meal.id,(p_values->>'actual_30')::numeric,(p_values->>'actual_60')::numeric,(p_values->>'actual_120')::numeric,
      (p_values->>'available_at')::timestamptz,p_values->'metrics')
    on conflict(meal_id) do update set actual_30=excluded.actual_30,actual_60=excluded.actual_60,actual_120=excluded.actual_120,
      available_at=excluded.available_at,trajectory_metrics_json=excluded.trajectory_metrics_json;
end $$;
revoke all on function public.app_store_actuals(uuid,uuid,jsonb) from public,anon,authenticated;
grant execute on function public.app_store_actuals(uuid,uuid,jsonb) to service_role;
commit;
