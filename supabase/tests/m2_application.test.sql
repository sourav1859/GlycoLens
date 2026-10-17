begin;
select plan(15);

insert into auth.users (id, instance_id, aud, role, email, encrypted_password, email_confirmed_at, created_at, updated_at)
values ('20000000-0000-4000-8000-000000000001', '00000000-0000-0000-0000-000000000000', 'authenticated', 'authenticated', null, '', now(), now(), now()),
       ('20000000-0000-4000-8000-000000000002', '00000000-0000-0000-0000-000000000000', 'authenticated', 'authenticated', null, '', now(), now(), now());
set local role authenticated;
select set_config('request.jwt.claim.sub', '20000000-0000-4000-8000-000000000001', true);
select set_config('request.jwt.claims', '{"sub":"20000000-0000-4000-8000-000000000001","role":"authenticated"}', true);
select lives_ok('select public.initialize_demo()', 'demo profile initialization works with session');
select lives_ok('select public.initialize_demo()', 'demo initialization is idempotent');

select lives_ok($test$
    select public.save_meal('Synthetic recipe', '2026-01-01T12:00:00Z', '30000000-0000-4000-8000-000000000001',
        '[{"food_id":"00000000-0000-4000-8000-000000000001","grams":100},{"food_id":"00000000-0000-4000-8000-000000000001","grams":50}]'::jsonb,
        '{"fixture":"synthetic"}'::jsonb)
$test$, 'duplicate ingredients aggregate in one atomic meal');
select is((select carbs_g from public.meals where idempotency_key = '30000000-0000-4000-8000-000000000001'), 45::numeric, 'totals are computed from food basis');
select is((select grams from public.meal_items), 150::numeric, 'repeated ingredient grams aggregate');
select lives_ok($test$
    select public.save_meal('Repeated request', '2026-01-01T12:00:00Z', '30000000-0000-4000-8000-000000000001',
        '[{"food_id":"00000000-0000-4000-8000-000000000001","grams":100}]'::jsonb, '{}'::jsonb)
$test$, 'meal retry reuses persisted operation');
select is((select count(*) from public.meals), 1::bigint, 'retry does not duplicate meal');
select throws_ok($test$
    select public.save_meal('Invalid item', '2026-01-01T12:00:00Z', '30000000-0000-4000-8000-000000000002',
        '[{"food_id":"00000000-0000-4000-8000-000000000001","grams":-1}]'::jsonb, '{}'::jsonb)
$test$, 'P0001', 'invalid grams', 'invalid ingredient is rejected');
select is((select count(*) from public.meals), 1::bigint, 'failed item rolls back parent meal');
insert into public.meals (id, user_id, recorded_at, name, carbs_g, protein_g, fat_g, fiber_g)
values ('50000000-0000-4000-8000-000000000001', auth.uid(), '2026-01-01T09:00:00Z', 'Synthetic earlier meal', 30, 10, 5, 2),
       ('50000000-0000-4000-8000-000000000002', auth.uid(), '2026-01-01T10:00:00Z', 'Outcome not yet available', 30, 10, 5, 2);
insert into public.meal_outcomes (meal_id, actual_30, actual_60, actual_120, available_at)
values ('50000000-0000-4000-8000-000000000001', 100, 110, 120, '2026-01-01T11:00:00Z'),
       ('50000000-0000-4000-8000-000000000002', 100, 110, 120, '2026-01-01T13:00:00Z');
select is((select count(*) from public.similar_meal_candidates((select id from public.meals where idempotency_key = '30000000-0000-4000-8000-000000000001'))), 1::bigint, 'retrieval excludes outcomes unavailable at query origin');
select is((select jsonb_array_length(nutrition_provenance->'food_snapshots') from public.meals where idempotency_key = '30000000-0000-4000-8000-000000000001'), 2, 'saved meal preserves source nutrient snapshots');
select throws_ok($test$
    select public.save_forecast((select id from public.meals where idempotency_key = '30000000-0000-4000-8000-000000000001'),
        '60000000-0000-4000-8000-000000000001', 'synthetic', '1', 'cgm_only', '2026-01-01T12:00:00Z', 1, '{}'::jsonb,
        (select jsonb_agg(jsonb_build_object('minute', i * 5, 'q10_mg_dl', 90, 'q50_mg_dl', 100, 'q90_mg_dl', 110)) from generate_series(0,23) i))
$test$, 'P0001', 'invalid forecast grid', 'malformed forecast grid fails atomically');
select is((select count(*) from public.forecasts), 0::bigint, 'malformed points roll back forecast parent');
select set_config('request.jwt.claim.sub', '20000000-0000-4000-8000-000000000002', true);
select set_config('request.jwt.claims', '{"sub":"20000000-0000-4000-8000-000000000002","role":"authenticated"}', true);
select is((select count(*) from public.meals), 0::bigint, 'second demo session cannot read first session meals');
select is((select count(*) from public.similar_meal_candidates('50000000-0000-4000-8000-000000000001')), 0::bigint, 'retrieval cannot traverse another session meal');
select * from finish();
rollback;
