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
    database_dsn = f"postgres://postgres:postgres@localhost:5432/{name}?sslmode=disable" if database == "postgres" else ""
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
