begin;
create function public.consumed_nutrition_window(p_source uuid,p_start timestamptz,p_end timestamptz,p_timezone text)
returns jsonb language plpgsql stable security invoker set search_path='' as $$
declare result jsonb;
begin
  if p_start is null or p_end is null or p_end<=p_start or p_end-p_start>interval '8 days' or not private.valid_timezone(p_timezone)
     or not exists(select 1 from public.source_sessions where id=p_source and user_id=(select auth.uid())) then
    raise exception 'invalid owned window' using errcode='22023';
  end if;
  with days as (select d::date as local_day from generate_series((p_start at time zone p_timezone)::date,
      (p_end at time zone p_timezone)::date-1,interval '1 day') d),
  meals as (select * from public.meals where user_id=(select auth.uid()) and source_session_id=p_source
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
revoke all on function public.consumed_nutrition_window(uuid,timestamptz,timestamptz,text) from public,anon;
grant execute on function public.consumed_nutrition_window(uuid,timestamptz,timestamptz,text) to authenticated;

create function private.validate_consumed_clock() returns trigger language plpgsql security invoker set search_path='' as $$
begin
  if new.state='logged' and new.source_session_id is not null and new.consumed_at>
      (select clock_at from public.source_sessions where id=new.source_session_id and user_id=new.user_id) then
    raise exception 'consumption is after source clock' using errcode='22023';
  end if;
  return new;
end $$;
revoke all on function private.validate_consumed_clock() from public,anon,authenticated;
create trigger validate_consumed_clock before insert or update on public.meals for each row execute function private.validate_consumed_clock();
commit;
