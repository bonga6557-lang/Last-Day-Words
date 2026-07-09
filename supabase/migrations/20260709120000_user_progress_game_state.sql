alter table public.user_progress
  add column if not exists game_state jsonb not null default '{}'::jsonb;
