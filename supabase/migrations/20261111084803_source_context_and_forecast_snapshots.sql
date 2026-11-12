begin;
alter table public.cgm_readings drop constraint cgm_readings_user_id_recorded_at_source_key;
alter table public.cgm_readings add column source_session_id uuid,
    add constraint cgm_owned_source foreign key(user_id,source_session_id) references public.source_sessions(user_id,id),
    add constraint cgm_partition_time unique nulls not distinct(user_id,source_session_id,recorded_at,source);
alter table public.insulin_events add column source_session_id uuid,
    add constraint insulin_owned_source foreign key(user_id,source_session_id) references public.source_sessions(user_id,id);
alter table public.activity_events add column source_session_id uuid,
    add constraint activity_owned_source foreign key(user_id,source_session_id) references public.source_sessions(user_id,id);
create index cgm_partition_idx on public.cgm_readings(user_id,source_session_id,recorded_at desc);
create index insulin_partition_idx on public.insulin_events(user_id,source_session_id,recorded_at);
create index activity_partition_idx on public.activity_events(user_id,source_session_id,recorded_at);
alter table public.forecasts add column source_session_id uuid,
    add column meal_revision integer,
    add column input_snapshot jsonb,
    add constraint forecast_owned_source foreign key(user_id,source_session_id) references public.source_sessions(user_id,id),
    add constraint forecast_revision foreign key(meal_id,meal_revision) references public.meal_revisions(meal_id,revision);
create index forecast_partition_idx on public.forecasts(user_id,source_session_id,created_at desc,id);

-- Replacing a context creates a new partition; it never rewrites existing readings.
create function public.app_store_source_context(p_user uuid,p_session uuid,p_mode text,p_clock timestamptz,
    p_cgm jsonb,p_insulin jsonb,p_metadata jsonb)
returns uuid language plpgsql security invoker set search_path='' as $$
declare point jsonb;
begin
  if p_clock is null or p_session is null or p_mode not in ('simulation','replay') or jsonb_array_length(p_cgm) not between 24 and 300
      or jsonb_array_length(p_insulin) not between 1 and 600 then raise exception 'invalid context' using errcode='22023'; end if;
  perform 1 from public.user_preferences where user_id=p_user for update;
  if not found then raise exception 'profile required' using errcode='22023'; end if;
  insert into public.source_sessions(id,user_id,mode,clock_at,metadata) values(p_session,p_user,p_mode,p_clock,p_metadata);
  for point in select value from jsonb_array_elements(p_cgm) loop
    if (point->>'recorded_at')::timestamptz > p_clock then raise exception 'future reading' using errcode='22023'; end if;
    insert into public.cgm_readings(user_id,source_session_id,recorded_at,glucose_mg_dl,source)
      values(p_user,p_session,(point->>'recorded_at')::timestamptz,(point->>'glucose_mg_dl')::numeric,'simulation');
  end loop;
  for point in select value from jsonb_array_elements(p_insulin) loop
    if (point->>'recorded_at')::timestamptz > p_clock then raise exception 'future insulin' using errcode='22023'; end if;
    insert into public.insulin_events(user_id,source_session_id,recorded_at,event_type,units,insulin_kind,source_unit,source)
      values(p_user,p_session,(point->>'recorded_at')::timestamptz,point->>'event_type',(point->>'units')::numeric,
        point->>'insulin_kind',point->>'source_unit','simulation');
  end loop;
  update public.user_preferences set source_session_id=p_session,source_mode=p_mode,revision=revision+1,updated_at=now() where user_id=p_user;
  return p_session;
end $$;

create function public.app_commit_forecast(p_user uuid,p_meal uuid,p_revision integer,p_key uuid,p_model text,p_version text,
    p_context text,p_origin timestamptz,p_latency numeric,p_provenance jsonb,p_points jsonb,p_input jsonb)
returns uuid language plpgsql security invoker set search_path='' as $$
declare meal public.meals; forecast uuid; existing public.forecasts;
begin
  select * into strict meal from public.meals where id=p_meal and user_id=p_user for update;
  if meal.revision<>p_revision or meal.state='cancelled' then raise exception 'meal changed' using errcode='23505'; end if;
  if meal.source_session_id is null or meal.recorded_at<>p_origin or jsonb_array_length(p_input->'history')<>24
      or p_input->'meal'->>'id' is distinct from p_meal::text then raise exception 'invalid frozen input' using errcode='22023'; end if;
  select * into existing from public.forecasts where user_id=p_user and idempotency_key=p_key;
  if found then
    if existing.meal_id<>p_meal or existing.meal_revision<>p_revision then raise exception 'request key reused' using errcode='23505'; end if;
    return existing.id;
  end if;
  forecast:=public.app_save_forecast(p_user,p_meal,p_key,p_model,p_version,p_context,p_origin,p_latency,p_provenance,p_points);
  update public.forecasts set source_session_id=meal.source_session_id,meal_revision=p_revision,input_snapshot=p_input where id=forecast;
  return forecast;
end $$;
revoke all on function public.app_store_source_context(uuid,uuid,text,timestamptz,jsonb,jsonb,jsonb) from public,anon,authenticated;
revoke all on function public.app_commit_forecast(uuid,uuid,integer,uuid,text,text,text,timestamptz,numeric,jsonb,jsonb,jsonb) from public,anon,authenticated;
grant execute on function public.app_store_source_context(uuid,uuid,text,timestamptz,jsonb,jsonb,jsonb) to service_role;
grant execute on function public.app_commit_forecast(uuid,uuid,integer,uuid,text,text,text,timestamptz,numeric,jsonb,jsonb,jsonb) to service_role;

-- A preference change cannot leave the prior mode's source selected.
create function private.clear_changed_source() returns trigger language plpgsql security invoker set search_path='' as $$
begin
  if old.source_mode<>new.source_mode and old.source_session_id is not distinct from new.source_session_id then
    new.source_session_id:=null;
  end if;
  return new;
end $$;
revoke all on function private.clear_changed_source() from public,anon,authenticated;
create trigger clear_changed_source before update on public.user_preferences for each row execute function private.clear_changed_source();
create or replace function public.similar_meal_candidates(p_meal uuid)
returns table(id uuid,name text,recorded_at timestamptz,carbs_g numeric,protein_g numeric,fat_g numeric,fiber_g numeric,
    actual_30 numeric,actual_60 numeric,actual_120 numeric)
language sql stable security invoker set search_path='' as $$
    select m.id,m.name,m.recorded_at,m.carbs_g,m.protein_g,m.fat_g,m.fiber_g,o.actual_30,o.actual_60,o.actual_120
    from public.meals target
    join public.meals m on m.user_id=target.user_id and m.source_session_id=target.source_session_id
        and m.recorded_at<target.recorded_at and m.id<>target.id and m.state='logged'
    join public.meal_outcomes o on o.meal_id=m.id
    where target.id=p_meal and target.user_id=(select auth.uid()) and target.source_session_id is not null
        and o.available_at is not null and o.available_at<=target.recorded_at
        and o.actual_30 is not null and o.actual_60 is not null and o.actual_120 is not null
    order by m.recorded_at desc limit 100;
$$;
commit;
