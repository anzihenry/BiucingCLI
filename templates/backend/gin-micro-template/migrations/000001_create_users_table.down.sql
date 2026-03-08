-- Drop indexes
DROP INDEX IF EXISTS idx_users_deleted_at ON users;
DROP INDEX IF EXISTS idx_profiles_user_id ON profiles;

-- Drop tables
DROP TABLE IF EXISTS profiles;
DROP TABLE IF EXISTS users;
