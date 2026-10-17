-- A full unique index supports provider upserts; PostgreSQL still allows multiple NULL IDs.
begin;
drop index public.foods_source_id_uidx;
create unique index foods_source_id_uidx on public.foods (source, source_food_id);
commit;
