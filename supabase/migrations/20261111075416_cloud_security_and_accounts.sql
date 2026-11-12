begin;

-- Keep legacy migration history intact. Browser reads remain owner-scoped;
-- authoritative facts/results/context are written only by the verified API.
revoke all on public.users, public.cgm_readings, public.insulin_events,
    public.activity_events, public.foods, public.meals, public.meal_items,
    public.forecasts, public.forecast_points, public.meal_outcomes from public, authenticated, anon;
grant select on public.users, public.cgm_readings, public.insulin_events,
    public.activity_events, public.foods, public.meals, public.meal_items,
    public.forecasts, public.forecast_points, public.meal_outcomes to authenticated;
grant select, insert, update, delete on public.users, public.cgm_readings, public.insulin_events,
    public.activity_events, public.foods, public.meals, public.meal_items,
    public.forecasts, public.forecast_points, public.meal_outcomes to service_role;

revoke all on function public.initialize_demo() from public, anon, authenticated;
revoke all on function public.save_meal(text,timestamptz,uuid,jsonb,jsonb) from public, anon, authenticated;
revoke all on function public.save_forecast(uuid,uuid,text,text,text,timestamptz,numeric,jsonb,jsonb) from public, anon, authenticated;

-- This pre-existing platform helper is an event-trigger function, not an app RPC.
do $$ begin
    if to_regprocedure('public.rls_auto_enable()') is not null then
        revoke execute on function public.rls_auto_enable() from public, anon, authenticated;
    end if;
end $$;

create schema if not exists private;
revoke all on schema private from public, anon;
grant usage on schema private to authenticated, service_role;
create function private.valid_timezone(p_name text) returns boolean
language sql stable security invoker set search_path = '' as $$
    select exists(select 1 from pg_catalog.pg_timezone_names where name = p_name);
$$;
revoke all on function private.valid_timezone(text) from public, anon;
grant execute on function private.valid_timezone(text) to authenticated, service_role;

create table public.user_preferences (
    user_id uuid primary key references public.users(id) on delete cascade,
    timezone text not null default 'UTC' check(private.valid_timezone(timezone)),
    glucose_unit text not null default 'mg/dL' check(glucose_unit in ('mg/dL','mmol/L')),
    source_mode text not null default 'simulation' check(source_mode in ('simulation','replay')),
    food_preferences jsonb not null default '[]'::jsonb check(jsonb_typeof(food_preferences)='array' and jsonb_array_length(food_preferences)<=20),
    revision integer not null default 0 check(revision>=0),
    updated_at timestamptz not null default now()
);
create table public.onboarding_state (
    user_id uuid primary key references public.users(id) on delete cascade,
    flow_version integer not null default 1 check(flow_version=1),
    step text not null default 'preferences' check(step in ('preferences','source','optional','review','complete')),
    revision integer not null default 0 check(revision>=0),
    notice_version text,
    completed_at timestamptz,
    check((step='complete' and completed_at is not null and notice_version is not null) or (step<>'complete' and completed_at is null))
);
create table public.notice_acknowledgements (
    user_id uuid not null references public.users(id) on delete cascade,
    notice_version text not null check(char_length(notice_version) between 1 and 100),
    acknowledged_at timestamptz not null default now(),
    primary key(user_id,notice_version)
);
create table public.nutrition_goals (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references public.users(id) on delete cascade,
    nutrient text not null check(nutrient in ('calories','carbs_g','protein_g','fat_g','fiber_g')),
    target numeric(10,3) not null check(target>0 and target<=10000),
    unit text not null check(unit in ('kcal','g')),
    effective_date date not null,
    check((nutrient='calories' and unit='kcal') or (nutrient<>'calories' and unit='g')),
    unique(user_id,nutrient,effective_date)
);
alter table public.user_preferences enable row level security;
alter table public.onboarding_state enable row level security;
alter table public.notice_acknowledgements enable row level security;
alter table public.nutrition_goals enable row level security;
revoke all on public.user_preferences, public.onboarding_state, public.notice_acknowledgements,
    public.nutrition_goals from public, anon, authenticated;
grant select on public.user_preferences, public.onboarding_state, public.notice_acknowledgements,
    public.nutrition_goals to authenticated;
grant select,insert,update,delete on public.user_preferences, public.onboarding_state,
    public.notice_acknowledgements, public.nutrition_goals to service_role;
-- Preference changes use API revision checks; the browser cannot bypass onboarding.
create policy preferences_read_own on public.user_preferences for select to authenticated using(user_id=(select auth.uid()));
create policy onboarding_read_own on public.onboarding_state for select to authenticated using(user_id=(select auth.uid()));
create policy acknowledgements_read_own on public.notice_acknowledgements for select to authenticated using(user_id=(select auth.uid()));
create policy goals_read_own on public.nutrition_goals for select to authenticated using(user_id=(select auth.uid()));

create function public.app_initialize_user(p_user uuid) returns uuid
language plpgsql security invoker set search_path = '' as $$
begin
    if p_user is null then raise exception 'verified user required'; end if;
    insert into public.users(id,display_name,mode) values(p_user,'GlycoLens member','demo') on conflict(id) do nothing;
    insert into public.user_preferences(user_id) values(p_user) on conflict(user_id) do nothing;
    insert into public.onboarding_state(user_id) values(p_user) on conflict(user_id) do nothing;
    return p_user;
end;
$$;
revoke all on function public.app_initialize_user(uuid) from public,anon,authenticated;
grant execute on function public.app_initialize_user(uuid) to service_role;

-- Server-only atomic meal/forecast functions follow, retaining deterministic
-- calculation, food snapshots, parent ownership, grid validation and idempotency.

create function public.app_save_meal(p_user uuid, p_name text, p_recorded_at timestamptz, p_key uuid, p_items jsonb, p_snapshot jsonb)
returns uuid language plpgsql security invoker set search_path = '' as $$
declare
    meal uuid; item jsonb; food public.foods; grams numeric;
    total_cal numeric := 0; total_c numeric := 0; total_p numeric := 0; total_f numeric := 0; total_fiber numeric := 0;
    fact_snapshots jsonb := '[]'::jsonb;
begin
    if p_user is null or p_key is null or jsonb_typeof(p_items) <> 'array'
       or jsonb_array_length(p_items) < 1 or jsonb_array_length(p_items) > 100 then raise exception 'invalid meal'; end if;
    perform pg_advisory_xact_lock(hashtextextended(p_user::text || p_key::text, 0));
    select id into meal from public.meals where user_id = p_user and idempotency_key = p_key;
    if meal is not null then return meal; end if;
    insert into public.meals (user_id, recorded_at, name, idempotency_key, input_snapshot)
        values (p_user, p_recorded_at, p_name, p_key, p_snapshot) returning id into meal;
    for item in select value from jsonb_array_elements(p_items) loop
        select * into strict food from public.foods where id = (item->>'food_id')::uuid;
        grams := (item->>'grams')::numeric;
        if grams is null or grams <= 0 or grams > 10000 then raise exception 'invalid grams'; end if;
        if food.calories is null or food.carbs_g is null or food.protein_g is null
           or food.fat_g is null or food.fiber_g is null then raise exception 'nutrition requires review'; end if;
        total_cal := total_cal + food.calories * grams / food.nutrient_basis_g;
        total_c := total_c + food.carbs_g * grams / food.nutrient_basis_g;
        total_p := total_p + food.protein_g * grams / food.nutrient_basis_g;
        total_f := total_f + food.fat_g * grams / food.nutrient_basis_g;
        total_fiber := total_fiber + food.fiber_g * grams / food.nutrient_basis_g;
        fact_snapshots := fact_snapshots || jsonb_build_array(jsonb_build_object(
            'food_id', food.id, 'source', food.source, 'source_food_id', food.source_food_id,
            'fetched_at', food.fetched_at, 'nutrient_basis_g', food.nutrient_basis_g, 'grams', grams,
            'calories', food.calories, 'carbs_g', food.carbs_g, 'protein_g', food.protein_g,
            'fat_g', food.fat_g, 'fiber_g', food.fiber_g));
        insert into public.meal_items (meal_id, food_id, quantity, unit, grams)
            values (meal, food.id, grams, 'g', grams)
            on conflict (meal_id, food_id) do update set quantity = meal_items.quantity + excluded.quantity, grams = meal_items.grams + excluded.grams;
    end loop;
    update public.meals set calories = total_cal, carbs_g = total_c, protein_g = total_p,
        fat_g = total_f, fiber_g = total_fiber,
        nutrition_provenance = jsonb_build_object('calculation', 'food_facts_by_grams_v1', 'confirmed', true, 'food_snapshots', fact_snapshots)
        where id = meal;
    return meal;
end;
$$;

create function public.app_save_forecast(p_user uuid, p_meal uuid, p_key uuid, p_model text, p_version text,
    p_context text, p_origin timestamptz, p_latency numeric, p_provenance jsonb, p_points jsonb)
returns uuid language plpgsql security invoker set search_path = '' as $$
declare forecast uuid; point jsonb; step integer := 0;
begin
    if p_user is null or p_key is null or p_origin is null or jsonb_typeof(p_points) <> 'array'
       or jsonb_array_length(p_points) <> 24 then raise exception 'invalid forecast'; end if;
    if not exists (select 1 from public.meals where id = p_meal and user_id = p_user) then raise exception 'meal not owned'; end if;
    perform pg_advisory_xact_lock(hashtextextended(p_user::text || p_key::text, 0));
    select id into forecast from public.forecasts where user_id = p_user and idempotency_key = p_key;
    if forecast is not null then return forecast; end if;
    insert into public.forecasts (user_id, meal_id, model_id, model_version, context_config, horizon_minutes,
        quantiles_json, latency_ms, forecast_origin, context_provenance, idempotency_key)
        values (p_user, p_meal, p_model, p_version, p_context, 120, '[0.1,0.5,0.9]'::jsonb,
            p_latency, p_origin, p_provenance, p_key) returning id into forecast;
    for point in select value from jsonb_array_elements(p_points) loop
        step := step + 1;
        if (point->>'minute')::int is distinct from step * 5 then raise exception 'invalid forecast grid'; end if;
        insert into public.forecast_points (forecast_id, forecast_at, q10, q50, q90)
        values (forecast, p_origin + ((point->>'minute')::int * interval '1 minute'),
            (point->>'q10_mg_dl')::numeric, (point->>'q50_mg_dl')::numeric, (point->>'q90_mg_dl')::numeric);
    end loop;
    return forecast;
end;
$$;

revoke all on function public.app_save_meal(uuid,text,timestamptz,uuid,jsonb,jsonb) from public,anon,authenticated;
revoke all on function public.app_save_forecast(uuid,uuid,uuid,text,text,text,timestamptz,numeric,jsonb,jsonb) from public,anon,authenticated;
grant execute on function public.app_save_meal(uuid,text,timestamptz,uuid,jsonb,jsonb) to service_role;
grant execute on function public.app_save_forecast(uuid,uuid,uuid,text,text,text,timestamptz,numeric,jsonb,jsonb) to service_role;
commit;
