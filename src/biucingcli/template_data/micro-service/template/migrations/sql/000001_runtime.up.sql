BEGIN;
-- Shared infrastructure only; each generated service owns a separate database.
CREATE TABLE runtime_metadata (key text PRIMARY KEY, value text NOT NULL);
INSERT INTO runtime_metadata VALUES ('schema', '1');
DO $$ BEGIN EXECUTE format('REVOKE INSERT, UPDATE, DELETE ON schema_migrations FROM %I', current_setting('app.runtime_role')); END $$;
COMMIT;
