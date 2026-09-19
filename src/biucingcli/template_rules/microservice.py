"""Microservice dependency-store and service-type derivations."""

from biucingcli.template_rules.common import RuleResult, default_type_name


def microservice_dependency_config(store: str | None, service_name: str) -> dict[str, str]:
    """Return derived local dependency values for the microservice template."""
    selected = (store or "postgres").lower()
    supported = {
        "postgres": {
            "dependency_store": "postgres",
            "dependency_store_image": "postgres:16-alpine",
            "dependency_store_port": "5432",
            "dependency_store_dsn": f"postgres://postgres:postgres@localhost:5432/{service_name}?sslmode=disable",
            "dependency_store_container_dsn": (
                f"postgres://postgres:postgres@postgres:5432/{service_name}?sslmode=disable"
            ),
            "dependency_store_env_block": "\n".join(
                [
                    "    environment:",
                    f"      POSTGRES_DB: {service_name}",
                    "      POSTGRES_USER: postgres",
                    "      POSTGRES_PASSWORD: postgres",
                ]
            ),
        },
        "redis": {
            "dependency_store": "redis",
            "dependency_store_image": "redis:7-alpine",
            "dependency_store_port": "6379",
            "dependency_store_dsn": "redis://localhost:6379/0",
            "dependency_store_container_dsn": "redis://redis:6379/0",
            "dependency_store_env_block": "",
        },
    }
    if selected not in supported:
        raise ValueError("Unsupported dependency store. Expected one of: postgres, redis")
    return dict(supported[selected])


def derive(values: dict[str, str]) -> RuleResult:
    derived = microservice_dependency_config(
        values.get("dependency_store"), values.get("service_name", values["project_name"]),
    )
    derived["service_type_name"] = default_type_name(values["project_name"])
    return RuleResult(derived)
