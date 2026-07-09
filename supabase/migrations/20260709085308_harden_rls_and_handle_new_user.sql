-- Signup profile bootstrap + hardened game room updates for members
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer set search_path = public
as $$
declare
  requested_name text;
  fallback_name text;
begin
  requested_name := nullif(
    left(
      trim(
        coalesce(
          new.raw_user_meta_data->>'display_name',
          split_part(new.email, '@', 1),
          'Player'
        )
      ),
      24
    ),
    ''
  );

  if requested_name is null or char_length(requested_name) < 2 then
    requested_name := 'Player';
  end if;

  fallback_name := left(requested_name, 15) || '-' || left(new.id::text, 8);

  insert into public.profiles (id, display_name)
  values (new.id, requested_name)
  on conflict (id) do nothing;

  return new;
exception
  when unique_violation then
    insert into public.profiles (id, display_name)
    values (new.id, fallback_name)
    on conflict (id) do nothing;

    return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

revoke execute on function public.handle_new_user() from public, anon, authenticated;

drop policy if exists "Authenticated can update rooms" on public.game_rooms;
drop policy if exists "Members or host can update rooms" on public.game_rooms;
create policy "Members or host can update rooms"
  on public.game_rooms for update
  to authenticated
  using (
    auth.uid() = host_id
    or exists (
      select 1 from public.room_members m
      where m.room_id = game_rooms.id and m.user_id = auth.uid()
    )
  )
  with check (
    auth.uid() = host_id
    or exists (
      select 1 from public.room_members m
      where m.room_id = game_rooms.id and m.user_id = auth.uid()
    )
  );
