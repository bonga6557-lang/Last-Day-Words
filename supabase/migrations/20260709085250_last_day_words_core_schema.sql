-- Core schema: profiles, scores, online teams (initial RLS)
create extension if not exists pgcrypto;

create table if not exists public.profiles (
  id uuid primary key references auth.users (id) on delete cascade,
  display_name text not null unique,
  created_at timestamptz not null default now(),
  constraint display_name_length check (char_length(display_name) between 2 and 24)
);

alter table public.profiles enable row level security;

drop policy if exists "Profiles are viewable by everyone" on public.profiles;
create policy "Profiles are viewable by everyone"
  on public.profiles for select
  using (true);

drop policy if exists "Users can insert own profile" on public.profiles;
create policy "Users can insert own profile"
  on public.profiles for insert
  with check (auth.uid() = id);

drop policy if exists "Users can update own profile" on public.profiles;
create policy "Users can update own profile"
  on public.profiles for update
  using (auth.uid() = id)
  with check (auth.uid() = id);

create table if not exists public.speed_scores (
  id bigserial primary key,
  user_id uuid not null references auth.users (id) on delete cascade,
  week_key text not null,
  score integer not null check (score >= 0),
  words_solved integer not null default 0 check (words_solved >= 0),
  updated_at timestamptz not null default now(),
  unique (user_id, week_key)
);

alter table public.speed_scores enable row level security;

drop policy if exists "Speed scores readable by all" on public.speed_scores;
create policy "Speed scores readable by all"
  on public.speed_scores for select
  using (true);

drop policy if exists "Users upsert own speed scores" on public.speed_scores;
create policy "Users upsert own speed scores"
  on public.speed_scores for insert
  with check (auth.uid() = user_id);

drop policy if exists "Users update own speed scores" on public.speed_scores;
create policy "Users update own speed scores"
  on public.speed_scores for update
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

create table if not exists public.daily_scores (
  id bigserial primary key,
  user_id uuid not null references auth.users (id) on delete cascade,
  day_key text not null,
  score integer not null check (score >= 0),
  updated_at timestamptz not null default now(),
  unique (user_id, day_key)
);

alter table public.daily_scores enable row level security;

drop policy if exists "Daily scores readable by all" on public.daily_scores;
create policy "Daily scores readable by all"
  on public.daily_scores for select
  using (true);

drop policy if exists "Users insert own daily scores" on public.daily_scores;
create policy "Users insert own daily scores"
  on public.daily_scores for insert
  with check (auth.uid() = user_id);

drop policy if exists "Users update own daily scores" on public.daily_scores;
create policy "Users update own daily scores"
  on public.daily_scores for update
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

create table if not exists public.game_rooms (
  id uuid primary key default gen_random_uuid(),
  code text not null unique,
  host_id uuid not null references auth.users (id) on delete cascade,
  status text not null default 'waiting' check (status in ('waiting', 'playing', 'finished')),
  white_score integer not null default 0,
  black_score integer not null default 0,
  payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists public.room_members (
  room_id uuid not null references public.game_rooms (id) on delete cascade,
  user_id uuid not null references auth.users (id) on delete cascade,
  team text not null check (team in ('white', 'black')),
  joined_at timestamptz not null default now(),
  primary key (room_id, user_id)
);

alter table public.game_rooms enable row level security;

drop policy if exists "Rooms readable by authenticated" on public.game_rooms;
create policy "Rooms readable by authenticated"
  on public.game_rooms for select
  to authenticated
  using (true);

drop policy if exists "Authenticated can create rooms" on public.game_rooms;
create policy "Authenticated can create rooms"
  on public.game_rooms for insert
  to authenticated
  with check (auth.uid() = host_id);

drop policy if exists "Authenticated can update rooms" on public.game_rooms;
create policy "Authenticated can update rooms"
  on public.game_rooms for update
  to authenticated
  using (auth.uid() = host_id)
  with check (auth.uid() = host_id);

alter table public.room_members enable row level security;

drop policy if exists "Members readable by authenticated" on public.room_members;
create policy "Members readable by authenticated"
  on public.room_members for select
  to authenticated
  using (true);

drop policy if exists "Users join rooms as themselves" on public.room_members;
create policy "Users join rooms as themselves"
  on public.room_members for insert
  to authenticated
  with check (auth.uid() = user_id);

drop policy if exists "Users update their own room membership" on public.room_members;
create policy "Users update their own room membership"
  on public.room_members for update
  to authenticated
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

drop policy if exists "Users leave rooms" on public.room_members;
create policy "Users leave rooms"
  on public.room_members for delete
  to authenticated
  using (auth.uid() = user_id);

create index if not exists speed_scores_week_score_idx on public.speed_scores (week_key, score desc);
create index if not exists daily_scores_day_score_idx on public.daily_scores (day_key, score desc);
create index if not exists game_rooms_code_idx on public.game_rooms (code);
