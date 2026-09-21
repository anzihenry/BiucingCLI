"""Read-only snapshot collector; running this module prints a candidate to stdout."""

import hashlib
import io
import json
from contextlib import redirect_stdout
from pathlib import Path
import tempfile

from biucingcli.cli import main


CASES = {
    "frontend": ["frontend"],
    "frontend-ssg": ["frontend", "--set", "rendering=ssg"],
    "web-service": ["web-service", "--module-name", "example.com/demo"],
    "worker": ["worker", "--module-name", "example.com/demo"],
    "android": ["android", "--package-name", "com.example.demo"],
    "harmonyos": ["harmonyos", "--bundle-name", "com.example.demo"],
}
for platform in ("ios", "macos", "watchos", "tvos"):
    CASES[f"apple-{platform}"] = ["apple", "--bundle-identifier", "com.example.demo",
                                 "--platform", platform]
for store in ("postgres", "redis"):
    CASES[f"microservice-{store}"] = ["microservice", "--module-name", "example.com/demo",
                                     "--proto-package", "demo.v1", "--dependency-store", store]


def inventory(root):
    """Hash exact bytes, record directories and portable executable bits only."""
    result = {}
    for path in sorted(root.rglob("*")):
        name = path.relative_to(root).as_posix()
        if path.is_symlink():
            result[name] = {"kind": "symlink", "target": str(path.readlink())}
        elif path.is_dir():
            result[name] = {"kind": "directory"}
        else:
            result[name] = {"kind": "file", "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                            "execute_bits": oct(path.stat().st_mode & 0o111)}
    return result


def collect_case(name):
    template, *options = CASES[name]
    if template in {"frontend", "apple", "android", "harmonyos"}:
        options += ["--display-name", 'R&D "引号" <研发> \\ $HOME {{PROJECT_NAME}}']
    with tempfile.TemporaryDirectory() as tmp:
        output = io.StringIO()
        with redirect_stdout(output):
            main(["create", template, "demo", "--output-dir", tmp,
                  "--non-interactive", "--json", *options])
        manifest = json.loads(output.getvalue())
        # Normalize only environment/release identity, never generated file bytes.
        manifest["output_path"] = "<OUTPUT>/demo"
        manifest["generator_version"] = "<VERSION>"
        return {"manifest": manifest, "entries": inventory(Path(tmp) / "demo")}


if __name__ == "__main__":
    print(json.dumps({name: collect_case(name) for name in CASES}, ensure_ascii=False, indent=2))
