create index if not exists game_rooms_host_id_idx on public.game_rooms (host_id);
create index if not exists room_members_user_id_idx on public.room_members (user_id);

-- RLS: wrap auth.uid() in subselect to avoid per-row re-evaluation (Supabase advisor)

drop policy if exists "Users can insert own profile" on public.profiles;
create policy "Users can insert own profile"
  on public.profiles for insert
  with check ((select auth.uid()) = id);

drop policy if exists "Users can update own profile" on public.profiles;
create policy "Users can update own profile"
  on public.profiles for update
  using ((select auth.uid()) = id)
  with check ((select auth.uid()) = id);

drop policy if exists "Users upsert own speed scores" on public.speed_scores;
create policy "Users upsert own speed scores"
  on public.speed_scores for insert
  with check ((select auth.uid()) = user_id);

drop policy if exists "Users update own speed scores" on public.speed_scores;
create policy "Users update own speed scores"
  on public.speed_scores for update
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

drop policy if exists "Users insert own daily scores" on public.daily_scores;
create policy "Users insert own daily scores"
  on public.daily_scores for insert
  with check ((select auth.uid()) = user_id);

drop policy if exists "Users update own daily scores" on public.daily_scores;
create policy "Users update own daily scores"
  on public.daily_scores for update
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

drop policy if exists "Authenticated can create rooms" on public.game_rooms;
create policy "Authenticated can create rooms"
  on public.game_rooms for insert
  to authenticated
  with check ((select auth.uid()) = host_id);

drop policy if exists "Members or host can update rooms" on public.game_rooms;
create policy "Members or host can update rooms"
  on public.game_rooms for update
  to authenticated
  using (
    (select auth.uid()) = host_id
    or exists (
      select 1 from public.room_members m
      where m.room_id = game_rooms.id and m.user_id = (select auth.uid())
    )
  )
  with check (
    (select auth.uid()) = host_id
    or exists (
      select 1 from public.room_members m
      where m.room_id = game_rooms.id and m.user_id = (select auth.uid())
    )
  );

drop policy if exists "Users join rooms as themselves" on public.room_members;
create policy "Users join rooms as themselves"
  on public.room_members for insert
  to authenticated
  with check ((select auth.uid()) = user_id);

drop policy if exists "Users update their own room membership" on public.room_members;
create policy "Users update their own room membership"
  on public.room_members for update
  to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

drop policy if exists "Users leave rooms" on public.room_members;
create policy "Users leave rooms"
  on public.room_members for delete
  to authenticated
  using ((select auth.uid()) = user_id);

drop policy if exists "Users read own progress" on public.user_progress;
create policy "Users read own progress"
  on public.user_progress for select
  to authenticated
  using ((select auth.uid()) = user_id);

drop policy if exists "Users insert own progress" on public.user_progress;
create policy "Users insert own progress"
  on public.user_progress for insert
  to authenticated
  with check ((select auth.uid()) = user_id);

drop policy if exists "Users update own progress" on public.user_progress;
create policy "Users update own progress"
  on public.user_progress for update
  to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);
