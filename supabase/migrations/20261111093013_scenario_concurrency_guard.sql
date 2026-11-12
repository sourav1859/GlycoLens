begin;
create or replace function public.app_save_scenario(p_user uuid,p_forecast uuid,p_multiplier numeric,p_key uuid,p_response jsonb)
returns uuid language plpgsql security invoker set search_path='' as $$
declare existing public.portion_scenarios; saved uuid;
begin
  -- Lock the owned parent so the per-forecast bound also holds across API processes.
  perform 1 from public.forecasts where id=p_forecast and user_id=p_user and input_snapshot is not null for update;
  if not found then raise exception 'forecast unavailable' using errcode='22023'; end if;
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
commit;
