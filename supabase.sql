-- ============================================================================
--  ФАЙЛ ОТКЛЮЧЁН. САЙТ: MIELE (Москва).
--
--  Раньше этот файл создавал таблицу заявок и функцию public.admin_leads(...)
--  с ОДНИМ паролем на все сайты, вшитым прямо в текст SQL и выданным роли anon.
--  Этот пароль лежал в открытом виде в HTML админки, а сама функция была
--  SECURITY DEFINER и умела list / status / comment / DELETE по всей таблице.
--  То есть любой, кто знал пароль, читал И УДАЛЯЛ заявки обоих сайтов.
--
--  Такой схемы больше нет. Правильная схема — в backend/supabase/migrations/.
--
--  ЭТОТ ФАЙЛ НИЧЕГО НЕ СОЗДАЁТ, НИЧЕГО НЕ УДАЛЯЕТ И НЕ МЕНЯЕТ ДАННЫЕ.
--  Единственное, что он делает — останавливает выполнение с объяснением.
--  Так сделано намеренно (fail closed): случайный запуск старого SQL не должен
--  ни вернуть дырявую функцию, ни «на всякий случай» что-то перезаписать.
--
--  ЧТО ДЕЛАТЬ ВМЕСТО ЭТОГО
--    1) Выполнить по порядку (Supabase -> SQL Editor, каждый файл отдельно):
--         backend/supabase/migrations/0001_schema.sql
--         backend/supabase/migrations/0002_functions.sql
--         backend/supabase/migrations/0003_scheduler.sql
--       0001 сам снимает права с public.admin_leads и удаляет её вместе со
--       всеми перегрузками; 0002 добавляет лимитер, очередь уведомлений и
--       атомарный приём заявки; 0003 настраивает планировщик (pg_cron+pg_net+Vault).
--    2) Завести пользователей админок и приписать их к сайтам:
--         insert into public.admin_memberships (user_id, site) values
--           ('<uuid пользователя>', 'mielecentr');
--    3) Развернуть Edge-функции и заполнить секреты — см. backend/deploy.txt.
--
--  ДАННЫЕ НЕ ТРОГАЮТСЯ: ни одна строка public.leads не удаляется и не
--  переписывается. Старые заявки без тега сайта 0001 аккуратно складывает в
--  public.leads_legacy_review и НЕ угадывает их принадлежность.
-- ============================================================================

do $$
begin
  raise exception using
    errcode = 'feature_not_supported',
    message = 'Устаревший SQL отключён (fail closed): выполнено ничего, данные не изменены.',
    detail  = 'Здесь раньше создавалась public.admin_leads(...) — SECURITY DEFINER '
              'с общим паролем на все сайты, выданная роли anon, включая удаление заявок.',
    hint    = 'Выполните backend/supabase/migrations/0001_schema.sql, затем 0002_functions.sql '
              'и 0003_scheduler.sql. Порядок развёртывания описан в backend/deploy.txt.';
end
$$;

-- ============================================================================
--  СПРАВКА (не выполняется — здесь только комментарии).
--
--  Проверить, что дырявой функции больше нет (после 0001_schema.sql):
--
--    select count(*) as admin_leads_left
--      from pg_proc p
--      join pg_namespace n on n.oid = p.pronamespace
--     where n.nspname = 'public' and p.proname = 'admin_leads';
--    -- ожидается 0
--
--  Проверить, что anon не имеет доступа к таблице:
--
--    select has_table_privilege('anon', 'public.leads', 'select') as anon_read,
--           has_table_privilege('anon', 'public.leads', 'insert') as anon_write;
--    -- ожидается false, false
--
--  Посмотреть заявки, у которых сайт не определён (их не видит ни одна админка):
--
--    select l.id, l.created_at, l.phone, r.reason
--      from public.leads_legacy_review r
--      join public.leads l on l.id = r.lead_id
--     order by l.created_at desc;
--
--  Осознанно отнести такую заявку к сайту (только вручную, service_role):
--
--    select public.assign_legacy_site('<uuid заявки>', 'mielecentr');
-- ============================================================================
