"""Separate Node/browser/container acceptance runner for installed frontend artifacts."""

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import re
import shlex
import shutil
import signal
import subprocess
import sys
import time
import uuid


ROOT = Path(__file__).resolve().parents[1]
MODES = ("csr", "ssg", "ssr")
SITE_URL = "https://frontend.example"


def clean_environment():
    environment = dict(os.environ)
    for key in ("PYTHONPATH", "PYTHONHOME", "PLAYWRIGHT_BASE_URL", "PLAYWRIGHT_CHANNEL", "NODE_ENV",
                "PLAYWRIGHT_HOST_PLATFORM_OVERRIDE", "PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS"):
        environment.pop(key, None)
    environment["SITE_URL"] = SITE_URL
    environment["SSR_PRIVATE_TOKEN"] = "private-smoke-sentinel"
    return environment


def fresh_workspace(path):
    path = path.resolve()
    if path == ROOT or ROOT in path.parents:
        raise ValueError("work directory must be outside the source checkout")
    path.mkdir(parents=True, exist_ok=False)
    return path


class Audit:
    def __init__(self, work, environment):
        self.work = work
        self.environment = environment
        self.reports = work / "reports"
        self.reports.mkdir()
        self.summary = {"schema_version": 1, "started_at": datetime.now(timezone.utc).isoformat(),
                        "ok": False, "stages": []}

    def run(self, label, command, *, cwd=None, env=None, timeout=1800):
        """Persist logs; terminate the entire owned subprocess group on interruption."""
        print(f"[{label}] {shlex.join(map(str, command))}", flush=True)
        started = time.monotonic()
        entry = {"name": label, "ok": False, "log": label + ".log"}
        self.summary["stages"].append(entry)
        self.save()
        path = self.reports / entry["log"]
        try:
            with path.open("w") as log:
                process = subprocess.Popen(command, cwd=cwd or self.work,
                                           env=env or self.environment, stdout=log,
                                           stderr=subprocess.STDOUT, start_new_session=True)
                try:
                    code = process.wait(timeout=timeout)
                except (subprocess.TimeoutExpired, KeyboardInterrupt):
                    try:
                        os.killpg(process.pid, signal.SIGTERM)
                    except ProcessLookupError:
                        pass
                    try:
                        process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        try:
                            os.killpg(process.pid, signal.SIGKILL)
                        except ProcessLookupError:
                            pass
                        process.wait()
                    raise
            if code:
                raise subprocess.CalledProcessError(code, command)
            entry["ok"] = True
            return path.read_text(errors="replace")
        except BaseException:
            if path.exists():
                print(path.read_text(errors="replace")[-12_000:], file=sys.stderr)
            raise
        finally:
            entry["duration_seconds"] = round(time.monotonic() - started, 3)
            self.save()

    def save(self):
        (self.reports / "summary.json").write_text(json.dumps(self.summary, indent=2) + "\n")

    def browser(self, label, project, script, environment):
        try:
            self.run(label, ["pnpm", script], cwd=project, env=environment)
        finally:
            # Playwright clears its results for the next invocation; preserve each phase.
            for folder in ("test-results", "playwright-report"):
                source = project / folder
                if source.exists():
                    shutil.copytree(source, self.reports / label / folder)


def runtime_acceptance(audit, mode, project, environment):
    identity = f"biucing-audit-{mode}-{uuid.uuid4().hex[:12]}"
    image = identity + ":test"
    container = None
    built = False
    try:
        audit.run(f"{mode}-docker-build", ["docker", "build", "--build-arg", f"SITE_URL={SITE_URL}",
                                         "-t", image, "."], cwd=project, timeout=3600)
        built = True
        port = "3000" if mode == "ssr" else "80"
        started = audit.run(f"{mode}-docker-start", ["docker", "run", "--detach", "--name", identity,
            "--publish", f"127.0.0.1::{port}", "--env", "SSR_PRIVATE_TOKEN=private-smoke-sentinel", image])
        # Docker warnings may share the captured log; remove only its exact ID.
        identifiers = [line for line in started.splitlines() if re.fullmatch(r"[0-9a-f]{64}", line)]
        if len(identifiers) != 1:
            raise AssertionError("unexpected container identity")
        container = identifiers[0]
        deadline = time.monotonic() + 60
        while True:
            state = json.loads(subprocess.check_output(
                ["docker", "inspect", "--format", "{{json .State}}", container],
                env=environment, text=True, timeout=15))
            health = state.get("Health", {}).get("Status")
            if health == "healthy":
                break
            if not state["Running"] or health == "unhealthy" or time.monotonic() >= deadline:
                raise AssertionError(f"{mode} runtime failed readiness: {state}")
            time.sleep(1)
        bindings = json.loads(audit.run(f"{mode}-docker-port", ["docker", "inspect", "--format",
            f'{{{{json (index .NetworkSettings.Ports "{port}/tcp")}}}}', container]))
        runtime_env = dict(environment, PLAYWRIGHT_BASE_URL=f"http://127.0.0.1:{bindings[0]['HostPort']}")
        audit.browser(f"{mode}-production-browser", project, "browser:smoke:production", runtime_env)
        if mode == "ssr":
            audit.run("ssr-runtime-boundaries", ["docker", "exec", container, "node", "-e",
                'const fs=require("node:fs"),a=require("node:assert/strict");'
                'a.notEqual(process.getuid(),0);'
                'for(const p of ["app",".env","node_modules/vite","node_modules/@react-router/dev"])'
                'a.ok(!fs.existsSync(p),p);'])
        else:
            audit.run(f"{mode}-runtime-boundaries", ["docker", "exec", container, "sh", "-c",
                '! command -v node && test ! -d /app/node_modules && test ! -d /app/build/server'])
        audit.run(f"{mode}-docker-stop", ["docker", "stop", "--time", "15", container])
        code = audit.run(f"{mode}-docker-exit", ["docker", "inspect", "--format", "{{.State.ExitCode}}", container])
        if code.strip() != "0":
            raise AssertionError(f"{mode} container did not exit cleanly: {code.strip()}")
    finally:
        # Exact UUID-scoped resources only: never global prune, user images or volumes.
        try:
            if container:
                try:
                    audit.run(f"{mode}-docker-logs", ["docker", "logs", container])
                finally:
                    audit.run(f"{mode}-docker-remove", ["docker", "rm", "--force", container])
        finally:
            if built:
                audit.run(f"{mode}-image-remove", ["docker", "image", "rm", image])


def verify_mode(audit, biucing, mode, args):
    # Same package identity allows one frozen Docker dependency layer across modes.
    name = "frontend-check"
    output = audit.work / "projects" / mode
    output.mkdir(parents=True)
    audit.run(f"{mode}-generate", [str(biucing), "create", "frontend", name, "--non-interactive",
        "--output-dir", str(output), "--set", f"rendering={mode}",
        "--display-name", 'R&D "引号" <研发> \\ $HOME {{PROJECT_NAME}}'])
    project = output / name
    environment = dict(audit.environment)
    if args.browser_channel:
        environment["PLAYWRIGHT_CHANNEL"] = args.browser_channel
    audit.run(f"{mode}-install", ["pnpm", "install", "--frozen-lockfile"], cwd=project, env=environment)
    audit.run(f"{mode}-peers", ["pnpm", "peers", "check"], cwd=project, env=environment)
    audit.run(f"{mode}-verify", ["pnpm", "verify"], cwd=project, env=environment)
    if not args.browser_channel:
        install = ["pnpm", "exec", "playwright", "install", "chromium", "--only-shell"]
        if args.install_browser_deps:
            install.append("--with-deps")
        audit.run(f"{mode}-browser-install", install, cwd=project, env=environment)
    audit.browser(f"{mode}-development-browser", project, "browser:smoke", environment)
    audit.browser(f"{mode}-built-browser", project, "browser:smoke:build", environment)
    if args.docker:
        runtime_acceptance(audit, mode, project, environment)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist-dir", type=Path, required=True, help="Directory with exactly one wheel")
    parser.add_argument("--work-dir", type=Path, required=True, help="New directory outside checkout; retained for diagnosis")
    parser.add_argument("--mode", choices=MODES, action="append", help="Repeat to select modes; default: all")
    parser.add_argument("--docker", action="store_true", help="Also test each actual production image")
    parser.add_argument("--browser-channel", choices=["chrome", "chromium"], help="Explicit existing browser; default installs Headless Shell")
    parser.add_argument("--install-browser-deps", action="store_true", help="Allow Playwright system package setup on Linux CI")
    args = parser.parse_args()
    if os.name != "posix":
        parser.error("frontend acceptance currently supports Linux and macOS")
    wheels = list(args.dist_dir.resolve().glob("*.whl"))
    if len(wheels) != 1:
        parser.error("expected exactly one wheel in --dist-dir")
    for executable in ("uv", "node", "pnpm", *(["docker"] if args.docker else [])):
        if not shutil.which(executable):
            parser.error(f"missing executable: {executable}")
    work = fresh_workspace(args.work_dir)
    environment = clean_environment()
    environment["PNPM_STORE_DIR"] = str(work / "pnpm-store")
    audit = Audit(work, environment)
    audit.summary.update(wheel=wheels[0].name, wheel_sha256=sha256(wheels[0].read_bytes()).hexdigest(),
                         modes=list(dict.fromkeys(args.mode or MODES)), docker=args.docker,
                         platform=sys.platform, machine=platform.machine(), python_version=platform.python_version(),
                         browser_channel=args.browser_channel or "default-headless-shell")
    try:
        audit.run("node-version", ["node", "--version"])
        audit.run("pnpm-version", ["pnpm", "--version"])
        venv = work / "venv"
        audit.run("create-venv", ["uv", "venv", "--python", sys.executable, str(venv)])
        python = venv / "bin/python"
        audit.run("install-wheel", ["uv", "pip", "install", "--python", str(python), "--no-deps", str(wheels[0])])
        audit.run("installed-origin", [str(python), "-I", "-c",
            'import biucingcli,sys; from pathlib import Path; '
            'p=Path(biucingcli.__file__).resolve(); '
            'assert Path(sys.prefix).resolve() in p.parents, p; print(p)'])
        biucing = venv / "bin/biucing"
        audit.run("installed-validate", [str(biucing), "validate"])
        for mode in audit.summary["modes"]:
            verify_mode(audit, biucing, mode, args)
        audit.summary["ok"] = True
    except BaseException as error:
        audit.summary["error"] = f"{type(error).__name__}: {error}"
        raise
    finally:
        audit.save()
        print(f"Acceptance report: {audit.reports / 'summary.json'}", flush=True)


if __name__ == "__main__":
    main()
