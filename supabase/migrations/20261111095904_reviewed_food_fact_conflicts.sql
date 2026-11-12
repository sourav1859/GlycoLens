begin;
-- Compare the reviewed facts inside the authoritative calculation transaction.
create or replace function private.meal_facts(p_items jsonb,p_prior jsonb)
returns jsonb language plpgsql security invoker set search_path='' as $$
declare item record; fact jsonb; food public.foods; facts jsonb := '[]'; totals jsonb; expected jsonb; reviewed jsonb;
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
    reviewed:=jsonb_build_object('nutrient_basis_g',fact->'nutrient_basis_g','calories',fact->'calories',
      'carbs_g',fact->'carbs_g','protein_g',fact->'protein_g','fat_g',fact->'fat_g','fiber_g',fact->'fiber_g');
    for expected in select value->'expected_facts' from jsonb_array_elements(p_items)
        where (value->>'food_id')::uuid=item.food_id and jsonb_typeof(value->'expected_facts')='object' loop
      if expected is distinct from reviewed then raise exception 'reviewed food facts changed' using errcode='23505'; end if;
    end loop;
    facts := facts || jsonb_build_array(fact || jsonb_build_object('grams',item.grams));
  end loop;
  select jsonb_object_agg(nutrient,amount) into totals from (
    select nutrient,case when bool_and(value->>nutrient is not null) then
      sum((value->>nutrient)::numeric*(value->>'grams')::numeric/(value->>'nutrient_basis_g')::numeric) else null end amount
    from jsonb_array_elements(facts) cross join unnest(array['calories','carbs_g','protein_g','fat_g','fiber_g']) nutrient
    group by nutrient) calculated;
  return jsonb_build_object('totals',totals,'food_snapshots',facts,'confirmed',true,'calculation','frozen_food_facts_v2');
end $$;
commit;
