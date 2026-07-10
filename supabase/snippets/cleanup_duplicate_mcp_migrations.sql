-- Optional housekeeping for Supabase Dashboard migration history noise.
-- Safe for data: does NOT touch public.words / chapters / seasons.
-- Only removes duplicate rows in the migration history table from chunked MCP retries
-- (e.g. seed_batch2_words_part3 applied 3 times). Keep one row per distinct name.
--
-- Run in Supabase SQL Editor after reviewing the SELECT results.
-- Remote-only workflow: local `supabase/config.toml` is not used.

-- 1) Inspect history (column names can vary by project age)
select *
from supabase_migrations.schema_migrations
order by version;

-- 2) Find duplicate names if a "name" column exists (MCP-style history).
-- If this errors, use only step 1 and delete by version list from the dashboard.
/*
select name, count(*) as n
from supabase_migrations.schema_migrations
group by name
having count(*) > 1;
*/

-- 3) Example: keep the earliest version for a repeated MCP name, drop the rest.
-- Uncomment and adjust after inspecting versions from step 1.
/*
delete from supabase_migrations.schema_migrations
where version in (
  -- list duplicate version ids to remove (keep one)
  -- '20260710xxxxxx_dup2',
  -- '20260710xxxxxx_dup3'
);
*/

-- Prefer: Supabase Dashboard → Database → Migrations → remove noise manually
-- if schema_migrations layout differs. Content is already correct via ON CONFLICT upserts.
