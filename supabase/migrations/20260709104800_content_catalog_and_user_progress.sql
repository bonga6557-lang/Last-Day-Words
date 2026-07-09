-- Content catalog (public read) + signed-in progression
-- Matches supabase/schema.sql lines 229-346

create table if not exists public.seasons (
  id text primary key,
  title text not null,
  description text not null default '',
  starts_on date,
  ends_on date
);

create table if not exists public.chapters (
  id text primary key,
  title text not null,
  description text not null default '',
  sort_order integer not null default 0,
  season_id text references public.seasons (id) on delete set null
);

create table if not exists public.words (
  id text primary key,
  chapter_id text not null references public.chapters (id) on delete cascade,
  word text not null,
  clue text not null,
  expert_clue text,
  verse text not null default '',
  scripture text not null default '',
  summary text not null default '',
  sort_order integer not null default 0
);

create table if not exists public.season_chapters (
  season_id text not null references public.seasons (id) on delete cascade,
  chapter_id text not null references public.chapters (id) on delete cascade,
  primary key (season_id, chapter_id)
);

create table if not exists public.content_featured (
  week_key text primary key,
  word_id text references public.words (id) on delete set null,
  announcement text
);

create table if not exists public.user_progress (
  user_id uuid primary key references auth.users (id) on delete cascade,
  xp integer not null default 0 check (xp >= 0),
  rank text not null default 'novice',
  unlocked_cosmetics text[] not null default '{}',
  selected_candle text not null default 'candle-classic',
  selected_banner text not null default '',
  updated_at timestamptz not null default now()
);

alter table public.seasons enable row level security;
alter table public.chapters enable row level security;
alter table public.words enable row level security;
alter table public.season_chapters enable row level security;
alter table public.content_featured enable row level security;
alter table public.user_progress enable row level security;

drop policy if exists "Seasons public read" on public.seasons;
create policy "Seasons public read"
  on public.seasons for select
  using (true);

drop policy if exists "Chapters public read" on public.chapters;
create policy "Chapters public read"
  on public.chapters for select
  using (true);

drop policy if exists "Words public read" on public.words;
create policy "Words public read"
  on public.words for select
  using (true);

drop policy if exists "Season chapters public read" on public.season_chapters;
create policy "Season chapters public read"
  on public.season_chapters for select
  using (true);

drop policy if exists "Featured public read" on public.content_featured;
create policy "Featured public read"
  on public.content_featured for select
  using (true);

drop policy if exists "Users read own progress" on public.user_progress;
create policy "Users read own progress"
  on public.user_progress for select
  to authenticated
  using (auth.uid() = user_id);

drop policy if exists "Users insert own progress" on public.user_progress;
create policy "Users insert own progress"
  on public.user_progress for insert
  to authenticated
  with check (auth.uid() = user_id);

drop policy if exists "Users update own progress" on public.user_progress;
create policy "Users update own progress"
  on public.user_progress for update
  to authenticated
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

create index if not exists words_chapter_sort_idx on public.words (chapter_id, sort_order);
create index if not exists chapters_sort_idx on public.chapters (sort_order);
create index if not exists user_progress_xp_idx on public.user_progress (xp desc);

insert into public.seasons (id, title, description, starts_on, ends_on)
values
  ('daniel', 'Daniel Track', 'Prophetic milestones from the book of Daniel — image, beasts, little horn, sanctuary, and Michael.', null, null),
  ('revelation', 'Revelation Track', 'Prophetic milestones from Revelation — churches, seals, trumpets, beast system, and the millennium.', null, null)
on conflict (id) do update set
  title = excluded.title,
  description = excluded.description;
