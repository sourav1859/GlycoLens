-- Immediate hard deletion: account rows cascade; aggregate spend is never refunded.
alter table private.llm_requests add constraint llm_requests_owned_user
  foreign key(user_id) references public.users(id) on delete cascade;

-- No account identity or payload in this outbox. Entries survive only until the
-- exact private source directory has been removed. Never retain an undo snapshot.
create table private.deleted_source_artifacts (
  source_id uuid primary key,
  queued_at timestamptz not null default now()
);
create table private.account_deletion_attempts (
  user_id uuid primary key references public.users(id) on delete cascade,
  window_start timestamptz not null default now(),
  attempts integer not null default 1 check(attempts between 1 and 5)
);
alter table private.deleted_source_artifacts enable row level security;
alter table private.account_deletion_attempts enable row level security;
revoke all on private.deleted_source_artifacts,private.account_deletion_attempts from public,anon,authenticated;
grant select,insert,delete on private.deleted_source_artifacts to service_role;
grant select,insert,update on private.account_deletion_attempts to service_role;

create function private.queue_deleted_source_artifacts() returns trigger
language plpgsql security invoker set search_path = '' as $$
begin
  insert into private.deleted_source_artifacts(source_id) values(old.id) on conflict do nothing;
  return old;
end;
$$;
revoke all on function private.queue_deleted_source_artifacts() from public,anon,authenticated;
grant usage on schema private to supabase_auth_admin;
grant insert on private.deleted_source_artifacts to supabase_auth_admin;
create policy auth_cascade_artifact_queue on private.deleted_source_artifacts for insert
  to supabase_auth_admin with check(true);
create trigger queue_deleted_source_artifacts before delete on public.source_sessions
  for each row execute function private.queue_deleted_source_artifacts();

create function public.app_reserve_deletion_attempt(p_user uuid) returns void
language plpgsql security invoker set search_path = '' as $$
declare accepted uuid;
begin
  insert into private.account_deletion_attempts(user_id) values(p_user)
  on conflict(user_id) do update set
    attempts=case when account_deletion_attempts.window_start<=now()-interval '15 minutes'
      then 1 else account_deletion_attempts.attempts+1 end,
    window_start=case when account_deletion_attempts.window_start<=now()-interval '15 minutes'
      then now() else account_deletion_attempts.window_start end
  where account_deletion_attempts.window_start<=now()-interval '15 minutes' or account_deletion_attempts.attempts<5
  returning user_id into accepted;
  if accepted is null then raise exception using errcode='PT429',message='Deletion reauthentication attempt limit reached'; end if;
end;
$$;

create function public.app_deletion_artifacts(p_complete uuid default null) returns uuid[]
language plpgsql security invoker set search_path = '' as $$
begin
  if p_complete is not null then
    delete from private.deleted_source_artifacts where source_id=p_complete;
    return array[]::uuid[];
  end if;
  return array(select source_id from private.deleted_source_artifacts order by queued_at,source_id limit 100);
end;
$$;
revoke all on function public.app_reserve_deletion_attempt(uuid),public.app_deletion_artifacts(uuid) from public,anon,authenticated;
grant execute on function public.app_reserve_deletion_attempt(uuid),public.app_deletion_artifacts(uuid) to service_role;
