"""Exact template-resource inventories for source, wheel and sdist verification."""

from hashlib import sha256
from pathlib import Path, PurePosixPath
import tarfile
import zipfile
import shutil


RESOURCE_PREFIX = "biucingcli/template_data/"


def fingerprint(content, mode):
    return {"sha256": sha256(content).hexdigest(), "execute_bits": mode & 0o111}


def source_resources(root):
    return {p.relative_to(root).as_posix(): fingerprint(p.read_bytes(), p.stat().st_mode)
            for p in root.rglob("*") if p.is_file()}


def wheel_resources(wheel):
    result = {}
    with zipfile.ZipFile(wheel) as archive:
        for item in archive.infolist():
            if item.is_dir() or not item.filename.startswith(RESOURCE_PREFIX):
                continue
            name = item.filename.removeprefix(RESOURCE_PREFIX)
            if name in result:
                raise AssertionError(f"duplicate wheel resource: {name}")
            result[name] = fingerprint(archive.read(item), item.external_attr >> 16)
    return result


def sdist_resources(sdist):
    result = {}
    with tarfile.open(sdist) as archive:
        for item in archive.getmembers():
            parts = PurePosixPath(item.name).parts
            relative = "/".join(parts[1:])
            prefix = "src/" + RESOURCE_PREFIX
            if not relative.startswith(prefix) or item.isdir():
                continue
            if not item.isfile():
                raise AssertionError(f"non-regular sdist resource: {item.name}")
            name = relative.removeprefix(prefix)
            if name in result:
                raise AssertionError(f"duplicate sdist resource: {name}")
            with archive.extractfile(item) as stream:
                result[name] = fingerprint(stream.read(), item.mode)
    return result


def assert_resources_equal(expected, actual, label):
    if not expected:
        raise AssertionError("empty expected resource inventory")
    missing = sorted(expected.keys() - actual.keys())
    extra = sorted(actual.keys() - expected.keys())
    changed = sorted(k for k in expected.keys() & actual.keys() if expected[k] != actual[k])
    if missing or extra or changed:
        raise AssertionError(f"{label}: missing={missing}, extra={extra}, changed={changed}")


def extract_sdist(sdist, destination):
    """Reject links, special files and traversal before extracting any member."""
    with tarfile.open(sdist) as archive:
        members = archive.getmembers()
        roots = set()
        for item in members:
            path = PurePosixPath(item.name)
            if (path.is_absolute() or ".." in path.parts or "\\" in item.name
                    or not path.parts or not (item.isfile() or item.isdir())):
                raise AssertionError(f"unsafe source archive entry: {item.name}")
            roots.add(path.parts[0])
        if len(roots) != 1:
            raise AssertionError("source archive must have exactly one top-level directory")
        # Python 3.11.0–3.11.7 do not expose tarfile's data filter. Extract only
        # prevalidated regular files into a fresh directory, without ownership,
        # links or setuid modes from the archive. Never overwrite existing data.
        destination = Path(destination)
        destination.mkdir(parents=True, exist_ok=False)
        for item in members:
            target = destination.joinpath(*PurePosixPath(item.name).parts)
            if item.isdir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.extractfile(item) as source, target.open("xb") as output:
                    shutil.copyfileobj(source, output)
                target.chmod(0o644 | (item.mode & 0o111))
    root = Path(destination) / roots.pop()
    if not (root / "pyproject.toml").is_file():
        raise AssertionError("source archive has no pyproject.toml")
    return root
