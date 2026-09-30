begin;

create extension if not exists vector with schema extensions;

create table public.users (
    id uuid primary key references auth.users (id) on delete cascade,
    display_name text not null check (char_length(display_name) between 1 and 100),
    mode text not null default 'demo' check (mode in ('demo', 'sandbox')),
    created_at timestamptz not null default now()
);

create table public.cgm_readings (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references public.users (id) on delete cascade,
    recorded_at timestamptz not null,
    glucose_mg_dl numeric(7, 2) not null check (glucose_mg_dl > 0 and glucose_mg_dl <= 1000),
    trend text,
    source text not null check (char_length(source) between 1 and 50),
    created_at timestamptz not null default now(),
    unique (user_id, recorded_at, source)
);

create table public.insulin_events (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references public.users (id) on delete cascade,
    recorded_at timestamptz not null,
    event_type text not null check (event_type in ('bolus', 'basal')),
    units numeric(8, 3) not null check (units > 0 and units <= 1000),
    source text not null check (char_length(source) between 1 and 50),
    created_at timestamptz not null default now()
);

create table public.activity_events (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references public.users (id) on delete cascade,
    recorded_at timestamptz not null,
    steps integer check (steps is null or steps >= 0),
    met numeric(7, 3) check (met is null or (met >= 0 and met <= 100)),
    intensity text,
    source text not null check (char_length(source) between 1 and 50),
    created_at timestamptz not null default now()
);

create table public.foods (
    id uuid primary key default gen_random_uuid(),
    name text not null check (char_length(name) between 1 and 200),
    barcode text,
    source text not null check (char_length(source) between 1 and 50),
    source_food_id text,
    serving_size numeric(10, 3) check (serving_size is null or serving_size > 0),
    calories numeric(10, 3) check (calories is null or calories >= 0),
    carbs_g numeric(10, 3) check (carbs_g is null or carbs_g >= 0),
    protein_g numeric(10, 3) check (protein_g is null or protein_g >= 0),
    fat_g numeric(10, 3) check (fat_g is null or fat_g >= 0),
    fiber_g numeric(10, 3) check (fiber_g is null or fiber_g >= 0),
    raw_payload jsonb not null default '{}'::jsonb check (jsonb_typeof(raw_payload) = 'object'),
    created_at timestamptz not null default now()
);

create table public.meals (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references public.users (id) on delete cascade,
    recorded_at timestamptz not null,
    name text not null check (char_length(name) between 1 and 200),
    meal_type text,
    portion_multiplier numeric(8, 3) not null default 1 check (portion_multiplier > 0),
    calories numeric(10, 3) check (calories is null or calories >= 0),
    carbs_g numeric(10, 3) check (carbs_g is null or carbs_g >= 0),
    protein_g numeric(10, 3) check (protein_g is null or protein_g >= 0),
    fat_g numeric(10, 3) check (fat_g is null or fat_g >= 0),
    fiber_g numeric(10, 3) check (fiber_g is null or fiber_g >= 0),
    nutrition_provenance jsonb not null default '{}'::jsonb
        check (jsonb_typeof(nutrition_provenance) = 'object'),
    embedding extensions.vector,
    created_at timestamptz not null default now()
);

create table public.meal_items (
    meal_id uuid not null references public.meals (id) on delete cascade,
    food_id uuid not null references public.foods (id) on delete restrict,
    quantity numeric(10, 3) not null check (quantity > 0),
    unit text not null check (char_length(unit) between 1 and 50),
    grams numeric(10, 3) check (grams is null or grams > 0),
    primary key (meal_id, food_id)
);

create table public.forecasts (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references public.users (id) on delete cascade,
    meal_id uuid references public.meals (id) on delete set null,
    model_id text not null check (char_length(model_id) between 1 and 100),
    model_version text not null check (char_length(model_version) between 1 and 100),
    context_config text not null check (char_length(context_config) between 1 and 100),
    horizon_minutes integer not null check (horizon_minutes between 1 and 1440),
    quantiles_json jsonb not null check (jsonb_typeof(quantiles_json) = 'array'),
    latency_ms numeric(12, 3) check (latency_ms is null or latency_ms >= 0),
    created_at timestamptz not null default now()
);

create table public.forecast_points (
    forecast_id uuid not null references public.forecasts (id) on delete cascade,
    forecast_at timestamptz not null,
    q10 numeric(7, 2) not null check (q10 > 0 and q10 <= 1000),
    q50 numeric(7, 2) not null check (q50 > 0 and q50 <= 1000),
    q90 numeric(7, 2) not null check (q90 > 0 and q90 <= 1000),
    primary key (forecast_id, forecast_at),
    check (q10 <= q50 and q50 <= q90)
);

create table public.meal_outcomes (
    meal_id uuid primary key references public.meals (id) on delete cascade,
    actual_30 numeric(7, 2) check (actual_30 is null or (actual_30 > 0 and actual_30 <= 1000)),
    actual_60 numeric(7, 2) check (actual_60 is null or (actual_60 > 0 and actual_60 <= 1000)),
    actual_120 numeric(7, 2) check (actual_120 is null or (actual_120 > 0 and actual_120 <= 1000)),
    trajectory_metrics_json jsonb not null default '{}'::jsonb
        check (jsonb_typeof(trajectory_metrics_json) = 'object'),
    created_at timestamptz not null default now()
);

create index cgm_readings_user_recorded_at_idx
    on public.cgm_readings (user_id, recorded_at desc);
create index insulin_events_user_recorded_at_idx
    on public.insulin_events (user_id, recorded_at desc);
create index activity_events_user_recorded_at_idx
    on public.activity_events (user_id, recorded_at desc);
create unique index foods_barcode_uidx on public.foods (barcode) where barcode is not null;
create unique index foods_source_id_uidx
    on public.foods (source, source_food_id) where source_food_id is not null;
create index meals_user_recorded_at_idx on public.meals (user_id, recorded_at desc);
create index forecasts_user_created_at_idx on public.forecasts (user_id, created_at desc);
create index forecasts_meal_id_idx on public.forecasts (meal_id) where meal_id is not null;

alter table public.users enable row level security;
alter table public.cgm_readings enable row level security;
alter table public.insulin_events enable row level security;
alter table public.activity_events enable row level security;
alter table public.foods enable row level security;
alter table public.meals enable row level security;
alter table public.meal_items enable row level security;
alter table public.forecasts enable row level security;
alter table public.forecast_points enable row level security;
alter table public.meal_outcomes enable row level security;

revoke all on table public.users from anon;
revoke all on table public.cgm_readings from anon;
revoke all on table public.insulin_events from anon;
revoke all on table public.activity_events from anon;
revoke all on table public.foods from anon;
revoke all on table public.meals from anon;
revoke all on table public.meal_items from anon;
revoke all on table public.forecasts from anon;
revoke all on table public.forecast_points from anon;
revoke all on table public.meal_outcomes from anon;

grant select, insert, update, delete on table public.users to authenticated;
grant select, insert, update, delete on table public.cgm_readings to authenticated;
grant select, insert, update, delete on table public.insulin_events to authenticated;
grant select, insert, update, delete on table public.activity_events to authenticated;
grant select on table public.foods to authenticated;
grant select, insert, update, delete on table public.meals to authenticated;
grant select, insert, update, delete on table public.meal_items to authenticated;
grant select, insert, update, delete on table public.forecasts to authenticated;
grant select, insert, update, delete on table public.forecast_points to authenticated;
grant select, insert, update, delete on table public.meal_outcomes to authenticated;

create policy users_select_own on public.users
    for select to authenticated
    using (id = (select auth.uid()));
create policy users_insert_own on public.users
    for insert to authenticated
    with check (id = (select auth.uid()));
create policy users_update_own on public.users
    for update to authenticated
    using (id = (select auth.uid()))
    with check (id = (select auth.uid()));
create policy users_delete_own on public.users
    for delete to authenticated
    using (id = (select auth.uid()));

create policy cgm_readings_select_own on public.cgm_readings
    for select to authenticated
    using (user_id = (select auth.uid()));
create policy cgm_readings_insert_own on public.cgm_readings
    for insert to authenticated
    with check (user_id = (select auth.uid()));
create policy cgm_readings_update_own on public.cgm_readings
    for update to authenticated
    using (user_id = (select auth.uid()))
    with check (user_id = (select auth.uid()));
create policy cgm_readings_delete_own on public.cgm_readings
    for delete to authenticated
    using (user_id = (select auth.uid()));

create policy insulin_events_select_own on public.insulin_events
    for select to authenticated
    using (user_id = (select auth.uid()));
create policy insulin_events_insert_own on public.insulin_events
    for insert to authenticated
    with check (user_id = (select auth.uid()));
create policy insulin_events_update_own on public.insulin_events
    for update to authenticated
    using (user_id = (select auth.uid()))
    with check (user_id = (select auth.uid()));
create policy insulin_events_delete_own on public.insulin_events
    for delete to authenticated
    using (user_id = (select auth.uid()));

create policy activity_events_select_own on public.activity_events
    for select to authenticated
    using (user_id = (select auth.uid()));
create policy activity_events_insert_own on public.activity_events
    for insert to authenticated
    with check (user_id = (select auth.uid()));
create policy activity_events_update_own on public.activity_events
    for update to authenticated
    using (user_id = (select auth.uid()))
    with check (user_id = (select auth.uid()));
create policy activity_events_delete_own on public.activity_events
    for delete to authenticated
    using (user_id = (select auth.uid()));

create policy foods_select_authenticated on public.foods
    for select to authenticated
    using (true);

create policy meals_select_own on public.meals
    for select to authenticated
    using (user_id = (select auth.uid()));
create policy meals_insert_own on public.meals
    for insert to authenticated
    with check (user_id = (select auth.uid()));
create policy meals_update_own on public.meals
    for update to authenticated
    using (user_id = (select auth.uid()))
    with check (user_id = (select auth.uid()));
create policy meals_delete_own on public.meals
    for delete to authenticated
    using (user_id = (select auth.uid()));

create policy meal_items_select_own on public.meal_items
    for select to authenticated
    using (
        exists (
            select 1 from public.meals
            where meals.id = meal_items.meal_id
              and meals.user_id = (select auth.uid())
        )
    );
create policy meal_items_insert_own on public.meal_items
    for insert to authenticated
    with check (
        exists (
            select 1 from public.meals
            where meals.id = meal_items.meal_id
              and meals.user_id = (select auth.uid())
        )
    );
create policy meal_items_update_own on public.meal_items
    for update to authenticated
    using (
        exists (
            select 1 from public.meals
            where meals.id = meal_items.meal_id
              and meals.user_id = (select auth.uid())
        )
    )
    with check (
        exists (
            select 1 from public.meals
            where meals.id = meal_items.meal_id
              and meals.user_id = (select auth.uid())
        )
    );
create policy meal_items_delete_own on public.meal_items
    for delete to authenticated
    using (
        exists (
            select 1 from public.meals
            where meals.id = meal_items.meal_id
              and meals.user_id = (select auth.uid())
        )
    );

create policy forecasts_select_own on public.forecasts
    for select to authenticated
    using (user_id = (select auth.uid()));
create policy forecasts_insert_own on public.forecasts
    for insert to authenticated
    with check (
        user_id = (select auth.uid())
        and (
            meal_id is null
            or exists (
                select 1 from public.meals
                where meals.id = forecasts.meal_id
                  and meals.user_id = (select auth.uid())
            )
        )
    );
create policy forecasts_update_own on public.forecasts
    for update to authenticated
    using (user_id = (select auth.uid()))
    with check (
        user_id = (select auth.uid())
        and (
            meal_id is null
            or exists (
                select 1 from public.meals
                where meals.id = forecasts.meal_id
                  and meals.user_id = (select auth.uid())
            )
        )
    );
create policy forecasts_delete_own on public.forecasts
    for delete to authenticated
    using (user_id = (select auth.uid()));

create policy forecast_points_select_own on public.forecast_points
    for select to authenticated
    using (
        exists (
            select 1 from public.forecasts
            where forecasts.id = forecast_points.forecast_id
              and forecasts.user_id = (select auth.uid())
        )
    );
create policy forecast_points_insert_own on public.forecast_points
    for insert to authenticated
    with check (
        exists (
            select 1 from public.forecasts
            where forecasts.id = forecast_points.forecast_id
              and forecasts.user_id = (select auth.uid())
        )
    );
create policy forecast_points_update_own on public.forecast_points
    for update to authenticated
    using (
        exists (
            select 1 from public.forecasts
            where forecasts.id = forecast_points.forecast_id
              and forecasts.user_id = (select auth.uid())
        )
    )
    with check (
        exists (
            select 1 from public.forecasts
            where forecasts.id = forecast_points.forecast_id
              and forecasts.user_id = (select auth.uid())
        )
    );
create policy forecast_points_delete_own on public.forecast_points
    for delete to authenticated
    using (
        exists (
            select 1 from public.forecasts
            where forecasts.id = forecast_points.forecast_id
              and forecasts.user_id = (select auth.uid())
        )
    );

create policy meal_outcomes_select_own on public.meal_outcomes
    for select to authenticated
    using (
        exists (
            select 1 from public.meals
            where meals.id = meal_outcomes.meal_id
              and meals.user_id = (select auth.uid())
        )
    );
create policy meal_outcomes_insert_own on public.meal_outcomes
    for insert to authenticated
    with check (
        exists (
            select 1 from public.meals
            where meals.id = meal_outcomes.meal_id
              and meals.user_id = (select auth.uid())
        )
    );
create policy meal_outcomes_update_own on public.meal_outcomes
    for update to authenticated
    using (
        exists (
            select 1 from public.meals
            where meals.id = meal_outcomes.meal_id
              and meals.user_id = (select auth.uid())
        )
    )
    with check (
        exists (
            select 1 from public.meals
            where meals.id = meal_outcomes.meal_id
              and meals.user_id = (select auth.uid())
        )
    );
create policy meal_outcomes_delete_own on public.meal_outcomes
    for delete to authenticated
    using (
        exists (
            select 1 from public.meals
            where meals.id = meal_outcomes.meal_id
              and meals.user_id = (select auth.uid())
        )
    );

comment on table public.users is 'Application profiles linked one-to-one with Supabase Auth users.';
comment on table public.cgm_readings is 'Application or synthetic CGM readings; not a research dataset store.';
comment on table public.meal_outcomes is 'Observed post-meal summaries used only after the prediction horizon.';

commit;
