begin;
-- Forward-only, reviewed classification. No timestamp or frozen snapshot rewriting.
create temp table workspace_before on commit drop as
 select id, md5(to_jsonb(m)::text) fingerprint from public.meals m;
alter table public.meals add column workspace text not null default 'legacy_unclassified';
update public.meals m set workspace='simulation' where exists
 (select 1 from public.source_sessions s where s.id=m.source_session_id and s.user_id=m.user_id and s.mode in ('simulation','replay'));
alter table public.meals add constraint meal_workspace_source check(
 (workspace='personal' and source_session_id is null) or
 (workspace='simulation' and source_session_id is not null) or
 (workspace='legacy_unclassified'));
do $$ begin
 if exists(select 1 from workspace_before b full join public.meals m on m.id=b.id
   where b.id is null or m.id is null or b.fingerprint<>md5((to_jsonb(m)-'workspace')::text)) then
   raise exception 'workspace migration changed preserved meal evidence';
 end if;
end $$;
create index meals_workspace_time_idx on public.meals(user_id,workspace,recorded_at desc,id);
create index meals_workspace_consumed_idx on public.meals(user_id,workspace,consumed_at) where state='logged';
alter table public.user_preferences drop constraint user_preferences_source_mode_check;
alter table public.user_preferences add constraint user_preferences_source_mode_check check(source_mode in ('personal','simulation','replay'));
alter table public.user_preferences alter column source_mode set default 'personal';
create function private.validate_meal_workspace() returns trigger language plpgsql security invoker set search_path='' as $$
begin
 if tg_op='INSERT' and new.workspace='legacy_unclassified' then raise exception 'explicit workspace required' using errcode='22023'; end if;
 if tg_op='UPDATE' and (old.workspace='legacy_unclassified' or old.workspace is distinct from new.workspace or old.source_session_id is distinct from new.source_session_id) then
   raise exception 'meal workspace immutable; legacy history is read-only' using errcode='22023';
 end if;
 return new;
end $$;
revoke all on function private.validate_meal_workspace() from public,anon,authenticated;
create trigger validate_meal_workspace before insert or update on public.meals for each row execute function private.validate_meal_workspace();
create or replace function public.app_commit_meal(p_user uuid,p_meal uuid,p_revision integer,p_key uuid,p_values jsonb)
returns jsonb language plpgsql security invoker set search_path='' as $$
declare old public.meals; current_source uuid; fact jsonb; totals jsonb; saved public.meals; receipt private.meal_requests;
  request jsonb := jsonb_build_object('meal',p_meal,'revision',p_revision,'values',p_values); result jsonb;
  new_state text := p_values->>'state'; at_time timestamptz := (p_values->>'recorded_at')::timestamptz;
begin
  if p_user is null or p_key is null or new_state not in ('planned','logged','cancelled')
      or at_time is null or p_values->>'confirmed' is distinct from 'true' then
    raise exception 'review required' using errcode='22023';
  end if;
  if p_values->>'workspace' is null or p_values->>'workspace' not in ('personal','simulation') then
    raise exception 'explicit workspace required; reload the application' using errcode='22023';
  end if;
  current_source := (p_values->>'source_session_id')::uuid;
  if ((p_values->>'workspace'='simulation') <> (current_source is not null)) then
    raise exception 'workspace/source mismatch' using errcode='22023';
  end if;
  if current_source is not null and not exists(select 1 from public.source_sessions where id=current_source and user_id=p_user) then
    raise exception 'owned source required' using errcode='22023';
  end if;
  perform pg_advisory_xact_lock(hashtextextended(p_user::text||p_key::text,0));
  select * into receipt from private.meal_requests where user_id=p_user and key=p_key;
  if found then
    if receipt.request is distinct from request then raise exception 'request key reused' using errcode='23505'; end if;
    return receipt.result;
  end if;
  if p_meal is not null then
    select * into strict old from public.meals where id=p_meal and user_id=p_user for update;
    if old.revision is distinct from p_revision then raise exception 'stale revision' using errcode='23505'; end if;
    if old.state='cancelled' then raise exception 'cancelled meal is immutable; copy it' using errcode='22023'; end if;
    if old.workspace is distinct from p_values->>'workspace' or old.source_session_id is distinct from current_source then
      raise exception 'meal workspace is immutable' using errcode='22023';
    end if;
  elsif p_revision<>0 or new_state='cancelled' then raise exception 'invalid initial state' using errcode='22023';
  end if;
  fact := private.meal_facts(p_values->'items',old.nutrition_provenance->'food_snapshots'); totals := fact->'totals';
  if p_meal is null then
    insert into public.meals(user_id,recorded_at,name,idempotency_key,source_session_id,workspace)
      values(p_user,at_time,p_values->>'name',p_key,current_source,p_values->>'workspace') returning * into saved;
  else saved:=old;
  end if;
  update public.meals set recorded_at=at_time,name=p_values->>'name',state=new_state,
    consumed_at=case when new_state='logged' then (p_values->>'consumed_at')::timestamptz else null end,
    meal_type=p_values->>'meal_type',revision=case when p_meal is null then 1 else old.revision+1 end,updated_at=now(),
    calories=(totals->>'calories')::numeric,carbs_g=(totals->>'carbs_g')::numeric,protein_g=(totals->>'protein_g')::numeric,
    fat_g=(totals->>'fat_g')::numeric,fiber_g=(totals->>'fiber_g')::numeric,nutrition_provenance=fact,
    input_snapshot=coalesce(p_values->'input_snapshot','{}')
    where id=saved.id returning * into saved;
  delete from public.meal_items where meal_id=saved.id;
  insert into public.meal_items(meal_id,food_id,quantity,unit,grams)
    select saved.id,(value->>'food_id')::uuid,(value->>'grams')::numeric,'g',(value->>'grams')::numeric
      from jsonb_array_elements(fact->'food_snapshots');
  insert into public.meal_revisions(meal_id,revision,user_id,snapshot) values(saved.id,saved.revision,p_user,to_jsonb(saved)-'embedding');
  result:=jsonb_build_object('meal_id',saved.id,'revision',saved.revision);
  insert into private.meal_requests values(p_user,p_key,request,result);
  return result;
end $$;

create or replace function public.app_store_source_context(p_user uuid,p_session uuid,p_mode text,p_clock timestamptz,
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
  -- Tab-local selection is explicit; never change personal application preferences.
  return p_session;
end $$;
create function public.workspace_nutrition_window(p_workspace text,p_source uuid,p_start timestamptz,p_end timestamptz,p_timezone text)
returns jsonb language plpgsql stable security invoker set search_path='' as $$
declare result jsonb;
begin
  if p_start is null or p_end is null or p_end<=p_start or p_end-p_start>interval '8 days' or not private.valid_timezone(p_timezone)
     or p_workspace is null or p_workspace not in ('personal','simulation')
     or (p_workspace='personal' and p_source is not null)
     or (p_workspace='simulation' and (p_source is null or not exists(select 1 from public.source_sessions where id=p_source and user_id=(select auth.uid())))) then
    raise exception 'invalid owned window' using errcode='22023';
  end if;
  with days as (select d::date as local_day from generate_series((p_start at time zone p_timezone)::date,
      (p_end at time zone p_timezone)::date-1,interval '1 day') d),
  meals as (select * from public.meals where user_id=(select auth.uid()) and workspace=p_workspace and source_session_id is not distinct from p_source
      and state='logged' and consumed_at>=p_start and consumed_at<p_end),
  counts as (select days.local_day,count(m.id) meal_count from days left join meals m on (m.consumed_at at time zone p_timezone)::date=days.local_day group by days.local_day),
  values_by_nutrient as (
    select days.local_day,nutrient,count(m.id) meal_count,count(m.id) filter(where to_jsonb(m)->>nutrient is not null) known_count,
      coalesce(sum((to_jsonb(m)->>nutrient)::numeric),0) known_total
    from days cross join unnest(array['calories','carbs_g','protein_g','fat_g','fiber_g']) nutrient
    left join meals m on (m.consumed_at at time zone p_timezone)::date=days.local_day group by days.local_day,nutrient),
  nutrients as (select local_day,jsonb_object_agg(nutrient,jsonb_build_object('total',case when known_count=meal_count then known_total else null end,
      'known_total',known_total,'known_meals',known_count,'missing_meals',meal_count-known_count)) nutrients
    from values_by_nutrient group by local_day)
  select jsonb_agg(jsonb_build_object('day',counts.local_day,'meal_count',counts.meal_count,'nutrients',nutrients.nutrients) order by counts.local_day)
    into result from counts join nutrients using(local_day);
  return coalesce(result,'[]');
end $$;
revoke all on function public.workspace_nutrition_window(text,uuid,timestamptz,timestamptz,text) from public,anon;
grant execute on function public.workspace_nutrition_window(text,uuid,timestamptz,timestamptz,text) to authenticated;


revoke all on function public.app_commit_meal(uuid,uuid,integer,uuid,jsonb),public.app_store_source_context(uuid,uuid,text,timestamptz,jsonb,jsonb,jsonb) from public,anon,authenticated;
grant execute on function public.app_commit_meal(uuid,uuid,integer,uuid,jsonb),public.app_store_source_context(uuid,uuid,text,timestamptz,jsonb,jsonb,jsonb) to service_role;
commit;
