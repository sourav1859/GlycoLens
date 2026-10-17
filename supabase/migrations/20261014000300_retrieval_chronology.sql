begin;
alter table public.meal_outcomes add column available_at timestamptz;
create function public.similar_meal_candidates(p_meal uuid)
returns table(id uuid, name text, recorded_at timestamptz, carbs_g numeric, protein_g numeric,
    fat_g numeric, fiber_g numeric, actual_30 numeric, actual_60 numeric, actual_120 numeric)
language sql stable security invoker set search_path = public as $$
    select m.id, m.name, m.recorded_at, m.carbs_g, m.protein_g, m.fat_g, m.fiber_g,
        o.actual_30, o.actual_60, o.actual_120
    from public.meals target
    join public.meals m on m.user_id = target.user_id and m.recorded_at < target.recorded_at and m.id <> target.id
    join public.meal_outcomes o on o.meal_id = m.id
    where target.id = p_meal and target.user_id = auth.uid()
        and o.available_at is not null and o.available_at <= target.recorded_at
        and o.actual_30 is not null and o.actual_60 is not null and o.actual_120 is not null
    order by m.recorded_at desc limit 100;
$$;
revoke all on function public.similar_meal_candidates(uuid) from public, anon;
grant execute on function public.similar_meal_candidates(uuid) to authenticated;
commit;
