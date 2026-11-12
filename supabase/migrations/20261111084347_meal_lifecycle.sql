begin;

-- Source sessions are immutable partitions, including when virtual clocks overlap.
create table public.source_sessions (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references public.users(id) on delete cascade,
    mode text not null check (mode in ('simulation','replay')),
    clock_at timestamptz not null,
    metadata jsonb not null check (jsonb_typeof(metadata) = 'object'),
    created_at timestamptz not null default now(),
    unique(user_id,id)
);
alter table public.user_preferences add column source_session_id uuid;
alter table public.user_preferences add constraint preferences_owned_source foreign key(user_id,source_session_id)
    references public.source_sessions(user_id,id);
alter table public.meals
    add column source_session_id uuid,
    add column state text not null default 'planned' check(state in ('planned','logged','cancelled')),
    add column consumed_at timestamptz,
    add column revision integer not null default 1 check(revision > 0),
    add column updated_at timestamptz not null default now(),
    add constraint logged_has_time check ((state = 'logged') = (consumed_at is not null)),
    add constraint meals_owned_source foreign key(user_id,source_session_id) references public.source_sessions(user_id,id);
create index meals_consumed_source_idx on public.meals(user_id,source_session_id,consumed_at,id) where state='logged';
create index meals_source_time_idx on public.meals(user_id,source_session_id,recorded_at desc,id);
create table public.meal_revisions (
    meal_id uuid not null references public.meals(id) on delete cascade,
    revision integer not null,
    user_id uuid not null references public.users(id) on delete cascade,
    snapshot jsonb not null check(jsonb_typeof(snapshot)='object'),
    created_at timestamptz not null default now(),
    primary key(meal_id,revision)
);
create index meal_revisions_owner_idx on public.meal_revisions(user_id,meal_id);
create table private.meal_requests (
    user_id uuid not null references public.users(id) on delete cascade,
    key uuid not null,
    request jsonb not null,
    result jsonb not null,
    primary key(user_id,key)
);
alter table private.meal_requests enable row level security;
revoke all on private.meal_requests from public,anon,authenticated;
grant select,insert,delete on private.meal_requests to service_role;
insert into public.meal_revisions(meal_id,revision,user_id,snapshot)
    select id,revision,user_id,to_jsonb(m)-'embedding' from public.meals m;

do $$ declare t text; begin
  foreach t in array array['source_sessions','meal_revisions'] loop
    execute format('alter table public.%I enable row level security',t);
    execute format('revoke all on public.%I from public,anon,authenticated',t);
    execute format('grant select on public.%I to authenticated',t);
    execute format('grant select,insert,update,delete on public.%I to service_role',t);
    execute format('create policy owner_read on public.%I for select to authenticated using ((select auth.uid())=user_id)',t);
    execute format('create policy active_session_gate on public.%I as restrictive for all to authenticated using ((select private.session_is_active()))',t);
  end loop;
end $$;

-- Deterministic calculation from trusted facts. Existing food facts remain frozen on edit.
create function private.meal_facts(p_items jsonb,p_prior jsonb)
returns jsonb language plpgsql security invoker set search_path='' as $$
declare item record; fact jsonb; food public.foods; facts jsonb := '[]'; totals jsonb;
begin
  if jsonb_typeof(p_items) is distinct from 'array' or jsonb_array_length(p_items) not between 1 and 100 then
    raise exception 'invalid items' using errcode='22023';
  end if;
  for item in select (value->>'food_id')::uuid food_id,sum((value->>'grams')::numeric) grams
      from jsonb_array_elements(p_items) group by 1 loop
    if item.grams is null or item.grams <= 0 or item.grams > 10000 or item.grams::text in ('NaN','Infinity','-Infinity') then
      raise exception 'invalid grams' using errcode='22023';
    end if;
    select value into fact from jsonb_array_elements(coalesce(p_prior,'[]')) where value->>'food_id'=item.food_id::text limit 1;
    if fact is null then
      select * into strict food from public.foods where id=item.food_id;
      fact := jsonb_build_object('food_id',food.id,'name',food.name,'source',food.source,'source_food_id',food.source_food_id,
        'fetched_at',food.fetched_at,'nutrient_basis_g',food.nutrient_basis_g,'calories',food.calories,'carbs_g',food.carbs_g,
        'protein_g',food.protein_g,'fat_g',food.fat_g,'fiber_g',food.fiber_g);
    end if;
    facts := facts || jsonb_build_array(fact || jsonb_build_object('grams',item.grams));
  end loop;
  select jsonb_object_agg(nutrient,amount) into totals from (
    select nutrient,case when bool_and(value->>nutrient is not null) then
      sum((value->>nutrient)::numeric*(value->>'grams')::numeric/(value->>'nutrient_basis_g')::numeric) else null end amount
    from jsonb_array_elements(facts) cross join unnest(array['calories','carbs_g','protein_g','fat_g','fiber_g']) nutrient
    group by nutrient) calculated;
  return jsonb_build_object('totals',totals,'food_snapshots',facts,'confirmed',true,'calculation','frozen_food_facts_v2');
end $$;
revoke all on function private.meal_facts(jsonb,jsonb) from public,anon,authenticated;
grant execute on function private.meal_facts(jsonb,jsonb) to service_role;

create function public.app_commit_meal(p_user uuid,p_meal uuid,p_revision integer,p_key uuid,p_values jsonb)
returns jsonb language plpgsql security invoker set search_path='' as $$
declare old public.meals; current_source uuid; fact jsonb; totals jsonb; saved public.meals; receipt private.meal_requests;
  request jsonb := jsonb_build_object('meal',p_meal,'revision',p_revision,'values',p_values); result jsonb;
  new_state text := p_values->>'state'; at_time timestamptz := (p_values->>'recorded_at')::timestamptz;
begin
  if p_user is null or p_key is null or new_state not in ('planned','logged','cancelled')
      or at_time is null or p_values->>'confirmed' is distinct from 'true' then
    raise exception 'review required' using errcode='22023';
  end if;
  perform pg_advisory_xact_lock(hashtextextended(p_user::text||p_key::text,0));
  select * into receipt from private.meal_requests where user_id=p_user and key=p_key;
  if found then
    if receipt.request is distinct from request then raise exception 'request key reused' using errcode='23505'; end if;
    return receipt.result;
  end if;
  select source_session_id into current_source from public.user_preferences where user_id=p_user;
  if p_meal is not null then
    select * into strict old from public.meals where id=p_meal and user_id=p_user for update;
    if old.revision is distinct from p_revision then raise exception 'stale revision' using errcode='23505'; end if;
    if old.state='cancelled' then raise exception 'cancelled meal is immutable; copy it' using errcode='22023'; end if;
    current_source := old.source_session_id;
  elsif p_revision<>0 or new_state='cancelled' then raise exception 'invalid initial state' using errcode='22023';
  end if;
  fact := private.meal_facts(p_values->'items',old.nutrition_provenance->'food_snapshots'); totals := fact->'totals';
  if p_meal is null then
    insert into public.meals(user_id,recorded_at,name,idempotency_key,source_session_id)
      values(p_user,at_time,p_values->>'name',p_key,current_source) returning * into saved;
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
revoke all on function public.app_commit_meal(uuid,uuid,integer,uuid,jsonb) from public,anon,authenticated;
grant execute on function public.app_commit_meal(uuid,uuid,integer,uuid,jsonb) to service_role;
commit;
