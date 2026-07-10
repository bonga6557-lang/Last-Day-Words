# Supabase remote-only workflow

Local Supabase CLI (`supabase/config.toml`, `supabase start`) is **not** used.
Production content and schema live on the linked remote project.

## Canonical content snapshot

- **Full catalog upsert:** `supabase/seed_content.sql` (76 chapters / 380 words; includes batch-2).
- **Versioned migrations (DDL + seeds):** `supabase/migrations/*.sql`  
  Latest content migrations:
  - `20260709150000_seed_expansion_content.sql`
  - `20260710120000_seed_batch2_content.sql`

## Housekeeping notes

- Temp `supabase/_*` MCP apply chunks are gitignored; delete if recreated.
- Chunked MCP applies can leave **duplicate names** in Dashboard migration history
  (e.g. `seed_batch2_words_part3` ×3). Data is fine (`ON CONFLICT` upserts).
  Optional cleanup SQL: `supabase/snippets/cleanup_duplicate_mcp_migrations.sql`.
