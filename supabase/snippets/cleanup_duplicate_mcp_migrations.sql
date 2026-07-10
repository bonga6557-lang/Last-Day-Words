-- Housekeeping for Supabase migration history noise from chunked MCP retries.
-- Safe for data: does NOT touch public.words / chapters / seasons.
-- Remote-only workflow: local `supabase/config.toml` is not used.
--
-- COMPLETED 2026-07-10: removed 3 duplicate history rows (kept earliest per name):
--   20260709123427  seed_expansion_words_batch_1  (kept 20260709122251)
--   20260710110154  seed_batch2_words_part3       (kept 20260710105813)
--   20260710110334  seed_batch2_part3             (redundant retry)
-- Result: 18 migration rows, no duplicate names.

-- 1) Inspect current history
select version, name
from supabase_migrations.schema_migrations
order by version;

-- 2) Find duplicate names (should return empty after cleanup)
select name, count(*) as n, array_agg(version order by version) as versions
from supabase_migrations.schema_migrations
group by name
having count(*) > 1;

-- 3) If new MCP retries create duplicates, keep earliest version per name:
-- delete from supabase_migrations.schema_migrations
-- where version in ('<duplicate_version_to_remove>');
