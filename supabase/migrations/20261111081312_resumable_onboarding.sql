begin;
alter table public.onboarding_state add column completed_steps text[] not null default '{}'
    check(completed_steps <@ array['preferences','source','optional']::text[]);

create function public.app_update_preferences(p_user uuid,p_revision integer,p_values jsonb) returns void
language plpgsql security invoker set search_path = '' as $$
declare current_preferences public.user_preferences;
begin
    select * into strict current_preferences from public.user_preferences where user_id=p_user for update;
    if current_preferences.revision <> p_revision then raise exception 'preferences changed; reload' using errcode='PT409'; end if;
    if p_values is null or jsonb_typeof(p_values)<>'object' then raise exception 'invalid preferences' using errcode='22023'; end if;
    update public.user_preferences set
        timezone=coalesce(p_values->>'timezone',timezone),
        glucose_unit=coalesce(p_values->>'glucose_unit',glucose_unit),
        source_mode=coalesce(p_values->>'source_mode',source_mode),
        food_preferences=coalesce(p_values->'food_preferences',food_preferences),
        revision=revision+1,updated_at=now() where user_id=p_user;
    if p_values ? 'display_name' then
        update public.users set display_name=trim(p_values->>'display_name') where id=p_user;
    end if;
end;
$$;

create function public.app_save_onboarding(p_user uuid,p_revision integer,p_step text,p_values jsonb) returns void
language plpgsql security invoker set search_path = '' as $$
declare state public.onboarding_state; pref_revision integer; next_step text;
begin
    select * into strict state from public.onboarding_state where user_id=p_user for update;
    if state.revision<>p_revision or state.completed_at is not null then raise exception 'onboarding changed; reload' using errcode='PT409'; end if;
    if p_step not in ('preferences','source','optional') then raise exception 'invalid step' using errcode='22023'; end if;
    if p_step='preferences' and (not (p_values ? 'timezone') or not (p_values ? 'glucose_unit')) then raise exception 'preferences required' using errcode='22023'; end if;
    if p_step='source' and (not ('preferences'=any(state.completed_steps)) or not (p_values ? 'source_mode')) then raise exception 'confirm preferences first' using errcode='22023'; end if;
    if p_step='optional' and not ('source'=any(state.completed_steps)) then raise exception 'confirm source first' using errcode='22023'; end if;
    select revision into pref_revision from public.user_preferences where user_id=p_user for update;
    perform public.app_update_preferences(p_user,pref_revision,p_values);
    next_step := case p_step when 'preferences' then 'source' when 'source' then 'optional' else 'review' end;
    -- Editing an earlier confirmed step from review never erases later progress.
    if state.step='review' then next_step := 'review'; end if;
    update public.onboarding_state set
        step=next_step,revision=revision+1,
        completed_steps=case when p_step=any(completed_steps) then completed_steps else array_append(completed_steps,p_step) end
        where user_id=p_user;
end;
$$;

create function public.app_complete_onboarding(p_user uuid,p_revision integer,p_notice text,p_acknowledged boolean) returns void
language plpgsql security invoker set search_path = '' as $$
declare state public.onboarding_state;
begin
    select * into strict state from public.onboarding_state where user_id=p_user for update;
    if p_notice is distinct from 'research-v1' or p_acknowledged is distinct from true then raise exception 'current notice acknowledgement required' using errcode='22023'; end if;
    if state.completed_at is not null and state.notice_version=p_notice then return; end if;
    if state.revision<>p_revision then raise exception 'onboarding changed; reload' using errcode='PT409'; end if;
    if not (array['preferences','source']::text[] <@ state.completed_steps) then raise exception 'required setup incomplete' using errcode='22023'; end if;
    insert into public.notice_acknowledgements(user_id,notice_version) values(p_user,p_notice) on conflict do nothing;
    update public.onboarding_state set step='complete',notice_version=p_notice,completed_at=now(),revision=revision+1 where user_id=p_user;
end;
$$;
revoke all on function public.app_update_preferences(uuid,integer,jsonb),
    public.app_save_onboarding(uuid,integer,text,jsonb),
    public.app_complete_onboarding(uuid,integer,text,boolean) from public,anon,authenticated;
grant execute on function public.app_update_preferences(uuid,integer,jsonb),
    public.app_save_onboarding(uuid,integer,text,jsonb),
    public.app_complete_onboarding(uuid,integer,text,boolean) to service_role;

-- A signed access JWT can outlive logout. Check the caller's own managed Auth
-- session without exposing auth.sessions or granting browser access to that table.
create function private.session_is_active() returns boolean
language sql stable security definer set search_path = '' as $$
    select exists(select 1 from auth.sessions s
        where s.user_id=(select auth.uid()) and s.id=(
            case when (select auth.jwt()->>'session_id') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
            then (select auth.jwt()->>'session_id')::uuid else null end)
        and (s.not_after is null or s.not_after>now()));
$$;
revoke all on function private.session_is_active() from public,anon;
grant execute on function private.session_is_active() to authenticated;
create function public.current_session_active() returns boolean
language sql stable security invoker set search_path = '' as $$ select private.session_is_active(); $$;
revoke all on function public.current_session_active() from public,anon;
grant execute on function public.current_session_active() to authenticated;
do $$ declare item record; begin
    for item in select tablename from pg_catalog.pg_tables where schemaname='public' and tablename in
        ('users','cgm_readings','insulin_events','activity_events','foods','meals','meal_items','forecasts','forecast_points','meal_outcomes',
         'user_preferences','onboarding_state','notice_acknowledgements','nutrition_goals') loop
        execute format('create policy active_session_gate on public.%I as restrictive for all to authenticated using ((select private.session_is_active())) with check ((select private.session_is_active()))',item.tablename);
    end loop;
end $$;
commit;
