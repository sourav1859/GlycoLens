begin;

alter table public.foods add column nutrient_basis_g numeric not null default 100 check (nutrient_basis_g > 0);
alter table public.foods add column fetched_at timestamptz not null default now();
alter table public.insulin_events add column insulin_kind text;
alter table public.insulin_events add column source_unit text not null default 'unknown';
alter table public.insulin_events drop constraint insulin_events_units_check;
alter table public.insulin_events add constraint insulin_events_units_check check (units >= 0 and units <= 1000);
alter table public.meals add column input_snapshot jsonb not null default '{}'::jsonb;
alter table public.meals add column idempotency_key uuid;
create unique index meals_user_idempotency_uidx on public.meals (user_id, idempotency_key) where idempotency_key is not null;
alter table public.forecasts add column forecast_origin timestamptz;
alter table public.forecasts add column context_provenance jsonb not null default '{}'::jsonb;
alter table public.forecasts add column idempotency_key uuid;
create unique index forecasts_user_idempotency_uidx on public.forecasts (user_id, idempotency_key) where idempotency_key is not null;

create function public.initialize_demo() returns uuid language plpgsql security invoker set search_path = public as $$
begin
    if auth.uid() is null then raise exception 'session required'; end if;
    insert into public.users (id, display_name, mode) values (auth.uid(), 'Virtual patient', 'demo') on conflict (id) do nothing;
    return auth.uid();
end;
$$;

-- Meal totals are recalculated from stored food facts. Client-supplied totals are ignored.
create function public.save_meal(p_name text, p_recorded_at timestamptz, p_key uuid, p_items jsonb, p_snapshot jsonb)
returns uuid language plpgsql security invoker set search_path = public as $$
declare
    meal uuid; item jsonb; food public.foods; grams numeric;
    total_cal numeric := 0; total_c numeric := 0; total_p numeric := 0; total_f numeric := 0; total_fiber numeric := 0;
    fact_snapshots jsonb := '[]'::jsonb;
begin
    if auth.uid() is null or p_key is null or jsonb_typeof(p_items) <> 'array'
       or jsonb_array_length(p_items) < 1 or jsonb_array_length(p_items) > 100 then raise exception 'invalid meal'; end if;
    perform pg_advisory_xact_lock(hashtextextended(auth.uid()::text || p_key::text, 0));
    select id into meal from public.meals where user_id = auth.uid() and idempotency_key = p_key;
    if meal is not null then return meal; end if;
    insert into public.meals (user_id, recorded_at, name, idempotency_key, input_snapshot)
        values (auth.uid(), p_recorded_at, p_name, p_key, p_snapshot) returning id into meal;
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

create function public.save_forecast(p_meal uuid, p_key uuid, p_model text, p_version text,
    p_context text, p_origin timestamptz, p_latency numeric, p_provenance jsonb, p_points jsonb)
returns uuid language plpgsql security invoker set search_path = public as $$
declare forecast uuid; point jsonb; step integer := 0;
begin
    if auth.uid() is null or p_key is null or p_origin is null or jsonb_typeof(p_points) <> 'array'
       or jsonb_array_length(p_points) <> 24 then raise exception 'invalid forecast'; end if;
    if not exists (select 1 from public.meals where id = p_meal and user_id = auth.uid()) then raise exception 'meal not owned'; end if;
    perform pg_advisory_xact_lock(hashtextextended(auth.uid()::text || p_key::text, 0));
    select id into forecast from public.forecasts where user_id = auth.uid() and idempotency_key = p_key;
    if forecast is not null then return forecast; end if;
    insert into public.forecasts (user_id, meal_id, model_id, model_version, context_config, horizon_minutes,
        quantiles_json, latency_ms, forecast_origin, context_provenance, idempotency_key)
        values (auth.uid(), p_meal, p_model, p_version, p_context, 120, '[0.1,0.5,0.9]'::jsonb,
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

revoke all on function public.initialize_demo() from public, anon;
revoke all on function public.save_meal(text, timestamptz, uuid, jsonb, jsonb) from public, anon;
revoke all on function public.save_forecast(uuid, uuid, text, text, text, timestamptz, numeric, jsonb, jsonb) from public, anon;
grant execute on function public.initialize_demo() to authenticated;
grant execute on function public.save_meal(text, timestamptz, uuid, jsonb, jsonb) to authenticated;
grant execute on function public.save_forecast(uuid, uuid, text, text, text, timestamptz, numeric, jsonb, jsonb) to authenticated;
commit;
