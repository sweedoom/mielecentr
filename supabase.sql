-- ============================================================
--  Supabase — таблица заявок для сайта ХОЛОД-ОК
--  Выполнить один раз: Supabase -> SQL Editor -> New query -> вставить -> Run
-- ============================================================

create table if not exists public.leads (
  id          uuid primary key default gen_random_uuid(),
  created_at  timestamptz not null default now(),
  name        text default '',
  phone       text not null,
  message     text default '',
  source      text default 'Заявка с сайта',
  page        text default '',
  status      text not null default 'new',   -- new | work | done | cancel
  comment     text default '',
  utm         text default ''
);

-- индекс на дату (админка сортирует по ней)
create index if not exists leads_created_at_idx on public.leads (created_at desc);

-- ---------- миграция: тег сайта (к боту привязано несколько сайтов) ----------
alter table public.leads add column if not exists site text default '';
create index if not exists leads_site_idx on public.leads (site);

-- ---------- RLS: доступ по анонимному ключу ----------
alter table public.leads enable row level security;

-- любой посетитель может ДОБАВИТЬ заявку (читать таблицу нельзя)
drop policy if exists "anon insert" on public.leads;
drop policy if exists "public insert" on public.leads;
create policy "public insert" on public.leads
  for insert to public with check (true);

-- сервисный ключ (service_role) обходит RLS автоматически
drop policy if exists "service all" on public.leads;
create policy "service all" on public.leads
  for all to service_role using (true) with check (true);

-- ---------- закрытый API админки ----------
-- Админка не читает таблицу напрямую. Она вызывает эту функцию и передаёт пароль.
-- Поэтому anon-ключ можно безопасно использовать в браузере: SELECT/UPDATE/DELETE закрыты RLS.
create or replace function public.admin_leads(
  p_password text,
  p_action text default 'list',
  p_id uuid default null,
  p_value text default null
) returns jsonb
language plpgsql security definer set search_path = public
as $$
declare rows jsonb; n integer;
begin
  -- пароль хранилища. ОДИН на все сайты (бот-то один).
  -- Старый SQL мог быть с 'holodok2026' — админка пробует оба варианта, так что
  -- если не будешь перевыполнять этот файл, всё продолжит работать как раньше.
  if p_password is null or p_password <> 'K9#mR2$vLp7!zQx4' then
    return jsonb_build_object('ok', false, 'error', 'Неверный пароль');
  end if;
  if p_action = 'list' then
    select coalesce(jsonb_agg(to_jsonb(x) order by x.created_at desc), '[]'::jsonb)
      into rows from public.leads x;
    return jsonb_build_object('ok', true, 'leads', rows);
  elsif p_action = 'status' then
    update public.leads set status = coalesce(p_value, 'new') where id = p_id;
  elsif p_action = 'comment' then
    update public.leads set comment = coalesce(p_value, '') where id = p_id;
  elsif p_action = 'delete' then
    delete from public.leads where id = p_id;
  else
    return jsonb_build_object('ok', false, 'error', 'unknown action');
  end if;
  get diagnostics n = row_count;
  return jsonb_build_object('ok', true, 'done', (n > 0));
end;
$$;

grant execute on function public.admin_leads(text, text, uuid, text) to anon, authenticated;
