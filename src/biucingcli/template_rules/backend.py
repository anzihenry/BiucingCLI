"""Independent backend components; no runtime dependency on the generator."""
import json

from biucingcli.template_rules.common import RuleResult

DERIVED = frozenset({"database_dsn", "cache_dsn"})
SNIPPETS = frozenset({"component_environment", "component_services", "component_dependencies"})


def components(values: dict[str, str], *, web: bool = False) -> RuleResult:
    database = values.get("database", "postgres" if web else "none")
    cache = values.get("cache", "none")
    if database not in (("postgres",) if web else ("none", "postgres")):
        raise ValueError("Unsupported database; web-service requires postgres; micro-service supports none, postgres")
    if cache not in ("none", "redis"):
        raise ValueError("Unsupported cache. Expected one of: none, redis")
    name = values.get("service_name", values["project_name"])
    if database == "postgres" and len(name) > 54:
        raise ValueError("PostgreSQL service_name must be at most 54 characters to keep role names within 63 bytes")
    database_dsn = f"postgres://{name}_app:local-app-only@localhost:5432/{name}?sslmode=disable" if database == "postgres" else ""
    cache_dsn = "redis://localhost:6379/0" if cache == "redis" else ""
    services = []
    if database == "postgres":
        services.append(f"""  postgres:
    image: postgres:16.13-alpine
    environment:
      POSTGRES_DB: {name}
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./deploy/postgres-init.sql:/docker-entrypoint-initdb.d/10-roles.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d {name}"]
      interval: 2s
      timeout: 2s
      retries: 30
""")
    if cache == "redis":
        services.append("""  redis:
    image: redis:7.4.2-alpine
""")
    # Container-only endpoints: these snippets contain validated slugs/choices only.
    environment = f'      DATABASE_DSN: "{database_dsn.replace("@localhost:", "@postgres:")}"\n'
    environment += f'      CACHE_DSN: "{cache_dsn.replace("localhost", "redis")}"'
    block = "\n".join(services)
    return RuleResult({"database_dsn": database_dsn, "cache_dsn": cache_dsn},
                      {"component_environment": environment, "component_services": block, "component_dependencies": json.dumps((["postgres"] if database == "postgres" else []) + (["redis"] if cache == "redis" else []))})


def derive(values: dict[str, str]) -> RuleResult:
    return components(values, web=True)
