-- Synthetic catalog fixture only. Never place participant or real-user health data in this file.
insert into public.foods (
    id,
    name,
    source,
    source_food_id,
    serving_size,
    calories,
    carbs_g,
    protein_g,
    fat_g,
    fiber_g,
    raw_payload
)
values (
    '00000000-0000-4000-8000-000000000001',
    'Synthetic demonstration meal component',
    'synthetic',
    'synthetic-food-001',
    100,
    180,
    30,
    8,
    4,
    5,
    '{"data_mode":"synthetic_demo"}'::jsonb
)
on conflict (id) do nothing;
