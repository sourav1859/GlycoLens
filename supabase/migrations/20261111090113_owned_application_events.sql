begin;
create table public.notifications (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.users(id) on delete cascade,
  kind text not null check(kind in ('meal_saved','forecast_ready','source_ready')),
  entity_id uuid not null,
  event_key text not null,
  created_at timestamptz not null default now(),
  read_at timestamptz,
  unique(user_id,event_key)
);
create index notification_owner_time_idx on public.notifications(user_id,created_at desc,id);
create index notification_unread_idx on public.notifications(user_id) where read_at is null;
alter table public.notifications enable row level security;
revoke all on public.notifications from public,anon,authenticated;
grant select on public.notifications to authenticated;
grant select,insert,update,delete on public.notifications to service_role;
create policy owner_read on public.notifications for select to authenticated using ((select auth.uid())=user_id);
create policy active_session_gate on public.notifications as restrictive for all to authenticated using((select private.session_is_active()));
create function private.record_application_event() returns trigger language plpgsql security invoker set search_path='' as $$
declare kind text; entity uuid; key text;
begin
  if tg_table_name='meal_revisions' then kind:='meal_saved'; entity:=new.meal_id; key:='meal:'||new.meal_id||':'||new.revision;
  elsif tg_table_name='forecasts' then kind:='forecast_ready'; entity:=new.id; key:='forecast:'||new.id;
  else kind:='source_ready'; entity:=new.id; key:='source:'||new.id;
  end if;
  insert into public.notifications(user_id,kind,entity_id,event_key) values(new.user_id,kind,entity,key) on conflict(user_id,event_key) do nothing;
  return new;
end $$;
revoke all on function private.record_application_event() from public,anon,authenticated;
create trigger meal_event after insert on public.meal_revisions for each row execute function private.record_application_event();
create trigger forecast_event after insert on public.forecasts for each row execute function private.record_application_event();
create trigger source_event after insert on public.source_sessions for each row execute function private.record_application_event();
create function public.app_read_notifications(p_user uuid,p_ids uuid[]) returns integer language plpgsql security invoker set search_path='' as $$
declare affected integer;
begin
  if coalesce(array_length(p_ids,1),0)>100 then raise exception 'too many notifications' using errcode='22023'; end if;
  update public.notifications set read_at=now() where user_id=p_user and id=any(p_ids) and read_at is null;
  get diagnostics affected=row_count; return affected;
end $$;
revoke all on function public.app_read_notifications(uuid,uuid[]) from public,anon,authenticated;
grant execute on function public.app_read_notifications(uuid,uuid[]) to service_role;

-- Conservative reserve, not a provider invoice. Never refunded on timeout.
create table private.llm_budget (name text primary key, reserved_usd numeric not null check(reserved_usd between 0 and 5));
insert into private.llm_budget values('development-test-2026-11-11',0.00763580);
create table private.llm_requests (id uuid primary key default gen_random_uuid(),user_id uuid not null,created_at timestamptz not null default now());
create index llm_request_owner_time_idx on private.llm_requests(user_id,created_at);
alter table private.llm_budget enable row level security;
alter table private.llm_requests enable row level security;
revoke all on private.llm_budget,private.llm_requests from public,anon,authenticated;
grant select,insert,update on private.llm_budget,private.llm_requests to service_role;
create function public.app_reserve_recipe_request(p_user uuid) returns uuid language plpgsql security invoker set search_path='' as $$
declare id uuid; reserved numeric;
begin
  select reserved_usd into strict reserved from private.llm_budget where name='development-test-2026-11-11' for update;
  if reserved+0.01>5 then raise exception 'test budget exhausted' using errcode='PT429'; end if;
  if (select count(*) from private.llm_requests where user_id=p_user and created_at>=now()-interval '1 day')>=10 then
    raise exception 'recipe daily limit reached' using errcode='PT429';
  end if;
  update private.llm_budget set reserved_usd=reserved_usd+0.01 where name='development-test-2026-11-11';
  insert into private.llm_requests(user_id) values(p_user) returning llm_requests.id into id;
  return id;
end $$;
revoke all on function public.app_reserve_recipe_request(uuid) from public,anon,authenticated;
grant execute on function public.app_reserve_recipe_request(uuid) to service_role;

-- Serialize forecast receipt lookup before delegating to the legacy atomic point writer.
create or replace function public.app_commit_forecast(p_user uuid,p_meal uuid,p_revision integer,p_key uuid,p_model text,p_version text,
    p_context text,p_origin timestamptz,p_latency numeric,p_provenance jsonb,p_points jsonb,p_input jsonb)
returns uuid language plpgsql security invoker set search_path='' as $$
declare meal public.meals; forecast uuid; existing public.forecasts;
begin
  select * into strict meal from public.meals where id=p_meal and user_id=p_user for update;
  if meal.revision is distinct from p_revision or meal.state='cancelled' then raise exception 'meal changed' using errcode='23505'; end if;
  if meal.source_session_id is null or meal.recorded_at is distinct from p_origin or jsonb_array_length(p_input->'history') is distinct from 24
      or p_input->'meal'->>'id' is distinct from p_meal::text then raise exception 'invalid frozen input' using errcode='22023'; end if;
  perform pg_advisory_xact_lock(hashtextextended(p_user::text||p_key::text,0));
  select * into existing from public.forecasts where user_id=p_user and idempotency_key=p_key;
  if found then
    if existing.meal_id is distinct from p_meal or existing.meal_revision is distinct from p_revision then raise exception 'request key reused' using errcode='23505'; end if;
    return existing.id;
  end if;
  forecast:=public.app_save_forecast(p_user,p_meal,p_key,p_model,p_version,p_context,p_origin,p_latency,p_provenance,p_points);
  update public.forecasts set source_session_id=meal.source_session_id,meal_revision=p_revision,input_snapshot=p_input where id=forecast;
  return forecast;
end $$;
commit;
