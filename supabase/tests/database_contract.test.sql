begin;

select plan(20);

select ok(
    exists (select 1 from pg_extension where extname = 'vector'),
    'pgvector extension is installed'
);

select has_table('public', 'users', 'users table exists');
select has_table('public', 'cgm_readings', 'cgm_readings table exists');
select has_table('public', 'insulin_events', 'insulin_events table exists');
select has_table('public', 'activity_events', 'activity_events table exists');
select has_table('public', 'foods', 'foods table exists');
select has_table('public', 'meals', 'meals table exists');
select has_table('public', 'meal_items', 'meal_items table exists');
select has_table('public', 'forecasts', 'forecasts table exists');
select has_table('public', 'forecast_points', 'forecast_points table exists');
select has_table('public', 'meal_outcomes', 'meal_outcomes table exists');

select is(
    (
        select count(*)::integer
        from pg_class
        join pg_namespace on pg_namespace.oid = pg_class.relnamespace
        where pg_namespace.nspname = 'public'
          and pg_class.relname in (
              'users', 'cgm_readings', 'insulin_events', 'activity_events', 'foods',
              'meals', 'meal_items', 'forecasts', 'forecast_points', 'meal_outcomes'
          )
          and pg_class.relrowsecurity
    ),
    10,
    'RLS is enabled on every exposed application table'
);

insert into auth.users (instance_id, id, aud, role, created_at, updated_at)
values
    ('00000000-0000-0000-0000-000000000000', '10000000-0000-4000-8000-000000000001', 'authenticated', 'authenticated', now(), now()),
    ('00000000-0000-0000-0000-000000000000', '20000000-0000-4000-8000-000000000002', 'authenticated', 'authenticated', now(), now());

insert into public.users (id, display_name, mode)
values
    ('10000000-0000-4000-8000-000000000001', 'Synthetic User One', 'demo'),
    ('20000000-0000-4000-8000-000000000002', 'Synthetic User Two', 'demo');

set local role authenticated;
select set_config('request.jwt.claim.sub', '10000000-0000-4000-8000-000000000001', true);
select set_config(
    'request.jwt.claims',
    '{"sub":"10000000-0000-4000-8000-000000000001","role":"authenticated"}',
    true
);

select lives_ok(
    $$
        insert into public.cgm_readings (user_id, recorded_at, glucose_mg_dl, source)
        values (
            '10000000-0000-4000-8000-000000000001',
            '2026-01-01T12:00:00Z',
            120,
            'synthetic'
        )
    $$,
    'an authenticated user can insert their own CGM row'
);

select throws_ok(
    $$
        insert into public.cgm_readings (user_id, recorded_at, glucose_mg_dl, source)
        values (
            '20000000-0000-4000-8000-000000000002',
            '2026-01-01T12:00:00Z',
            120,
            'synthetic'
        )
    $$,
    '42501',
    null,
    'an authenticated user cannot insert another user''s CGM row'
);

select throws_ok(
    $$
        insert into public.cgm_readings (user_id, recorded_at, glucose_mg_dl, source)
        values (
            '10000000-0000-4000-8000-000000000001',
            '2026-01-01T12:05:00Z',
            -1,
            'synthetic'
        )
    $$,
    '23514',
    null,
    'invalid glucose values fail the database constraint'
);

select results_eq(
    $$select count(*)::bigint from public.cgm_readings$$,
    $$values (1::bigint)$$,
    'the owner can read their own CGM row'
);

reset role;
set local role authenticated;
select set_config('request.jwt.claim.sub', '20000000-0000-4000-8000-000000000002', true);
select set_config(
    'request.jwt.claims',
    '{"sub":"20000000-0000-4000-8000-000000000002","role":"authenticated"}',
    true
);

select results_eq(
    $$select count(*)::bigint from public.cgm_readings$$,
    $$values (0::bigint)$$,
    'another authenticated user cannot read the first user''s CGM row'
);

select results_eq(
    $$select count(*)::bigint from public.foods where source = 'synthetic'$$,
    $$values (1::bigint)$$,
    'authenticated users can read the shared synthetic food catalog'
);

reset role;
set local role anon;

select throws_ok(
    $$select count(*) from public.foods$$,
    '42501',
    null,
    'anonymous users have no table access'
);

reset role;

insert into public.meals (
    id, user_id, recorded_at, name, carbs_g, nutrition_provenance
)
values (
    '30000000-0000-4000-8000-000000000003',
    '10000000-0000-4000-8000-000000000001',
    '2026-01-01T12:00:00Z',
    'Synthetic meal',
    30,
    '{"data_mode":"synthetic_demo"}'::jsonb
);

insert into public.forecasts (
    id, user_id, meal_id, model_id, model_version, context_config,
    horizon_minutes, quantiles_json
)
values (
    '40000000-0000-4000-8000-000000000004',
    '10000000-0000-4000-8000-000000000001',
    '30000000-0000-4000-8000-000000000003',
    'synthetic-demo',
    '1.0',
    'cgm_only',
    120,
    '[0.1, 0.5, 0.9]'::jsonb
);

select throws_ok(
    $$
        insert into public.forecast_points (forecast_id, forecast_at, q10, q50, q90)
        values (
            '40000000-0000-4000-8000-000000000004',
            '2026-01-01T12:05:00Z',
            140,
            130,
            150
        )
    $$,
    '23514',
    null,
    'crossing forecast quantiles fail the database constraint'
);

select * from finish();
rollback;
