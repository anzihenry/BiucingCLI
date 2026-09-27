BEGIN;
-- Shared infrastructure only; each generated service owns a separate database.
CREATE TABLE runtime_metadata (key text PRIMARY KEY, value text NOT NULL);
INSERT INTO runtime_metadata VALUES ('schema', '1');
DO $$ BEGIN EXECUTE format('REVOKE INSERT, UPDATE, DELETE ON schema_migrations FROM %I', current_setting('app.runtime_role')); END $$;
CREATE TABLE sessions(id_hash text PRIMARY KEY, issuer text NOT NULL, subject text NOT NULL, csrf text NOT NULL, expires_at timestamptz NOT NULL);
CREATE INDEX sessions_expiry ON sessions(expires_at);
CREATE TABLE login_attempts(state_hash text PRIMARY KEY,binding_hash text NOT NULL,nonce text NOT NULL,verifier text NOT NULL,expires_at timestamptz NOT NULL);
CREATE INDEX login_expiry ON login_attempts(expires_at);
COMMIT;
