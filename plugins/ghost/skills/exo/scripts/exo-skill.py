#!/usr/bin/env python3
"""
exo-skill: download and upload exo skill bundles by folder.

Sidesteps the token cost of serializing skill content as MCP tool-call
arguments. The improvement loop downloads the active version into a local
folder, edits files with normal text-editing tools, and uploads the folder
as a new SkillVersion (optionally activating it).

Settings, read from the process environment first and then from the
profile named by --profile (or EXO_PROFILE), which is the file
$XDG_CONFIG_HOME/exo/<name>.env, defaulting to ~/.config. Name a
profile after the MCP server holding
the same workspace, so the two cannot drift apart:

  EXO_API_URL       required, the workspace endpoint without a path
  EXO_API_KEY       required, the same bearer key used by the MCP server
  EXO_WORKSPACE_ID  sent as X-Workspace-Id. Remote gateways require it, and
                    a local dev gateway may infer it from the key instead.

Subcommands:
  create   --folder DIR [--name NAME] [--force]
  download SKILL [--version VID] [--out DIR]
  upload   SKILL --folder DIR [--activate] [--no-base]

create bootstraps a brand-new skill from a folder via the multipart
import route (POST /skills/upload). The skill name defaults to the
folder's basename; pass --name to override. The first version is
created and auto-activated, and a meta file is written into the folder
so a later `upload <id> --folder DIR` chains as a patch. Unlike upload,
create can carry binary files because the import route is multipart.
The import route upserts by name, so create refuses an existing name
unless --force is passed.

SKILL may be a skill ID or a skill name. When a name is supplied and
multiple skills match by case-insensitive exact-or-substring rules, the
candidates are printed and the command exits non-zero so the caller can
disambiguate.
"""

from __future__ import annotations

import argparse
import binascii
import json
import os
import pathlib
import sys
import urllib.error
import urllib.parse
import urllib.request


META_FILE = ".exo-skill-meta.json"
API_PREFIX = "/api/v1"


CONFIG_DIR = pathlib.Path(
    os.environ.get("XDG_CONFIG_HOME") or pathlib.Path.home() / ".config"
) / "exo"

_profile: dict[str, str] = {}


def load_profile(name: str | None) -> None:
    """Populate _profile from CONFIG_DIR/<name>.env. Process env still wins."""
    if not name:
        return
    path = CONFIG_DIR / f"{name}.env"
    if not path.is_file():
        available = sorted(p.stem for p in CONFIG_DIR.glob("*.env"))
        sys.exit(
            f"error: no profile {name!r} at {path}"
            + (f"\navailable: {', '.join(available)}" if available else "")
        )
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        _profile[key.strip()] = val.strip().strip("\"'")


def setting(name: str) -> str | None:
    return os.environ.get(name) or _profile.get(name)


def setting_or_die(name: str) -> str:
    val = setting(name)
    if not val:
        sys.exit(f"error: {name} is required. Set it, or pass --profile.")
    return val


def env_or_die(name: str) -> str:
    return setting_or_die(name)


def api_url() -> str:
    return setting_or_die("EXO_API_URL").rstrip("/")


def request(method: str, path: str, body: dict | None = None) -> dict:
    url = api_url() + API_PREFIX + path
    data = None
    headers = {"Authorization": "Bearer " + env_or_die("EXO_API_KEY")}
    workspace_id = setting("EXO_WORKSPACE_ID")
    if workspace_id:
        headers["X-Workspace-Id"] = workspace_id
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read()
            if not raw:
                return {}
            return json.loads(raw)
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        sys.exit(f"error: {method} {path} -> HTTP {e.code}: {detail}")
    except urllib.error.URLError as e:
        sys.exit(f"error: {method} {path} -> {e.reason}")


def post_multipart(path: str, fields: list[tuple], file_parts: list[tuple]) -> dict:
    """POST a multipart/form-data body.

    fields is a list of (name, str_value) pairs; file_parts is a list of
    (field_name, filename, content_bytes, content_type) tuples. Mirrors
    request()'s auth headers and error handling.
    """
    boundary = "----exo-skill-" + binascii.hexlify(os.urandom(16)).decode()
    crlf = b"\r\n"
    buf = bytearray()

    def emit(text: str) -> None:
        buf.extend(text.encode("utf-8"))

    for name, value in fields:
        emit(f"--{boundary}\r\n")
        emit(f'Content-Disposition: form-data; name="{name}"\r\n\r\n')
        buf.extend(value.encode("utf-8"))
        buf.extend(crlf)
    for field_name, filename, content, content_type in file_parts:
        emit(f"--{boundary}\r\n")
        emit(f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"\r\n')
        emit(f"Content-Type: {content_type}\r\n\r\n")
        buf.extend(content)
        buf.extend(crlf)
    emit(f"--{boundary}--\r\n")

    url = api_url() + API_PREFIX + path
    headers = {
        "Authorization": "Bearer " + env_or_die("EXO_API_KEY"),
        "Content-Type": f"multipart/form-data; boundary={boundary}",
    }
    workspace_id = setting("EXO_WORKSPACE_ID")
    if workspace_id:
        headers["X-Workspace-Id"] = workspace_id
    req = urllib.request.Request(url, data=bytes(buf), method="POST", headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read()
            if not raw:
                return {}
            return json.loads(raw)
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        sys.exit(f"error: POST {path} -> HTTP {e.code}: {detail}")
    except urllib.error.URLError as e:
        sys.exit(f"error: POST {path} -> {e.reason}")


def list_skills() -> list[dict]:
    return request("GET", "/skills").get("skills", [])


def resolve_skill(skill_ref: str) -> dict:
    """Resolve a skill name or ID to its summary dict."""
    skills = list_skills()
    by_id = next((s for s in skills if s["id"] == skill_ref), None)
    if by_id:
        return by_id

    ref_lower = skill_ref.lower()
    exact = [s for s in skills if s["name"].lower() == ref_lower]
    if len(exact) == 1:
        return exact[0]
    if len(exact) > 1:
        _print_candidates(exact, skill_ref)

    substr = [s for s in skills if ref_lower in s["name"].lower()]
    if len(substr) == 1:
        return substr[0]
    if len(substr) > 1:
        _print_candidates(substr, skill_ref)

    sys.exit(f"error: no skill matched '{skill_ref}'")


def _print_candidates(candidates: list[dict], skill_ref: str) -> None:
    print(f"error: multiple skills matched '{skill_ref}':", file=sys.stderr)
    for s in candidates:
        print(f"  {s['id']}  {s['name']}", file=sys.stderr)
    sys.exit(2)


def get_version(skill_id: str, version_id: str) -> dict:
    versions = request("GET", f"/skills/{skill_id}/versions").get("versions", [])
    match = next((v for v in versions if v["id"] == version_id), None)
    if not match:
        sys.exit(f"error: version {version_id} not found for skill {skill_id}")
    return match


def _collect_folder_files(folder: pathlib.Path) -> list[tuple]:
    """Walk a folder into (rel_path, content_bytes, content_type) tuples.

    Skips the meta file and any dotted path component. UTF-8-decodable
    files are sent as text/plain so the runtime classifies them as
    text-editable regardless of extension; everything else is binary.
    """
    parts: list[tuple] = []
    for entry in sorted(folder.rglob("*")):
        if entry.is_dir():
            continue
        if entry.name == META_FILE:
            continue
        rel_parts = entry.relative_to(folder).parts
        if any(part.startswith(".") for part in rel_parts):
            continue
        rel = entry.relative_to(folder).as_posix()
        raw = entry.read_bytes()
        try:
            raw.decode("utf-8")
            content_type = "text/plain; charset=utf-8"
        except UnicodeDecodeError:
            content_type = "application/octet-stream"
        parts.append((rel, raw, content_type))
    return parts


def cmd_create(args: argparse.Namespace) -> None:
    folder = pathlib.Path(args.folder)
    if not folder.is_dir():
        sys.exit(f"error: {folder} is not a directory")

    name = (args.name or folder.resolve().name).strip()
    if not name:
        sys.exit("error: could not derive a skill name from the folder; pass --name")

    existing = next(
        (s for s in list_skills() if s["name"].lower() == name.lower()), None
    )
    if existing and not args.force:
        sys.exit(
            f"error: a skill named '{existing['name']}' already exists ({existing['id']}). "
            f"Use 'upload {existing['id']} --folder {folder}' to add a version, "
            "or pass --force to upsert a new version under it via the import key."
        )

    file_parts = _collect_folder_files(folder)
    if not file_parts:
        sys.exit(f"error: no files to upload under {folder}")
    if not any(rel == "SKILL.md" for rel, _, _ in file_parts):
        print(
            "note: no SKILL.md at the folder root; the runtime expects "
            "'SKILL.md' as the skill entrypoint.",
            file=sys.stderr,
        )

    fields = [("folder_name", name)]
    fields += [("paths", rel) for rel, _, _ in file_parts]
    files = [("files", rel, content, content_type) for rel, content, content_type in file_parts]

    resp = post_multipart("/skills/upload", fields, files)
    skill_id = resp.get("id")
    if not skill_id:
        sys.exit(f"error: create response missing skill id: {resp}")

    version_id = resp.get("active_version_id") or resp.get("latest_version_id")
    print(f"created skill {skill_id} ('{resp.get('name', name)}') with {len(file_parts)} file(s)")
    if version_id:
        print(f"active version {version_id}")

    meta = {
        "skill_id": skill_id,
        "skill_name": resp.get("name", name),
        "version_id": version_id,
        "binary_files": [
            rel for rel, _, content_type in file_parts
            if content_type == "application/octet-stream"
        ],
    }
    (folder / META_FILE).write_text(json.dumps(meta, indent=2), encoding="utf-8")


def cmd_download(args: argparse.Namespace) -> None:
    skill = resolve_skill(args.skill)
    skill_id = skill["id"]
    version_id = args.version or skill.get("active_version_id")
    if not version_id:
        sys.exit(f"error: skill {skill_id} has no active version; pass --version")

    version = get_version(skill_id, version_id)
    out = pathlib.Path(args.out or f"./{skill['name']}-{version_id[-8:]}")
    out.mkdir(parents=True, exist_ok=True)

    text_files: list[dict] = []
    binary_files: list[dict] = []
    for f in version.get("files", []):
        if f.get("previewable_as_text"):
            text_files.append(f)
        else:
            binary_files.append(f)

    for f in text_files:
        path = f["path"]
        query = urllib.parse.urlencode({"path": path})
        body = request("GET", f"/skills/{skill_id}/versions/{version_id}/content?{query}")
        dest = out / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(body.get("content", ""), encoding="utf-8")
        print(f"  wrote {dest}")

    meta = {
        "skill_id": skill_id,
        "skill_name": skill["name"],
        "version_id": version_id,
        "binary_files": [f["path"] for f in binary_files],
    }
    (out / META_FILE).write_text(json.dumps(meta, indent=2), encoding="utf-8")

    print(f"downloaded {len(text_files)} text file(s) to {out}")
    if binary_files:
        paths = ", ".join(f["path"] for f in binary_files)
        print(
            f"note: {len(binary_files)} binary file(s) skipped ({paths}). "
            "Upload will preserve them via base_version_id unless --no-base is passed.",
            file=sys.stderr,
        )


def cmd_upload(args: argparse.Namespace) -> None:
    folder = pathlib.Path(args.folder)
    if not folder.is_dir():
        sys.exit(f"error: {folder} is not a directory")

    skill = resolve_skill(args.skill)
    skill_id = skill["id"]

    base_version_id = None
    meta_path = folder / META_FILE
    if not args.no_base and meta_path.is_file():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if meta.get("skill_id") and meta["skill_id"] != skill_id:
            sys.exit(
                f"error: folder's meta file is for skill {meta['skill_id']}, "
                f"but upload target is {skill_id}"
            )
        base_version_id = meta.get("version_id")

    files = []
    for entry in sorted(folder.rglob("*")):
        if entry.is_dir():
            continue
        if entry.name == META_FILE:
            continue
        rel_parts = entry.relative_to(folder).parts
        if any(part.startswith(".") for part in rel_parts):
            continue
        rel = entry.relative_to(folder).as_posix()
        try:
            content = entry.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            sys.exit(
                f"error: {rel} is not text. The /skills/:id/versions endpoint "
                "only accepts text content; binary files must be preserved via "
                "base_version_id (do not pass --no-base)."
            )
        files.append({"path": rel, "content": content})

    if not files:
        sys.exit(f"error: no files to upload under {folder}")

    body: dict = {"files": files}
    if base_version_id:
        body["base_version_id"] = base_version_id

    resp = request("POST", f"/skills/{skill_id}/versions", body=body)
    new_version_id = resp.get("new_version_id")
    if not new_version_id:
        sys.exit(f"error: upload response missing new_version_id: {resp}")

    print(f"created version {new_version_id} (base: {base_version_id or 'none'})")

    if args.activate:
        request(
            "PUT",
            f"/skills/{skill_id}/active-version",
            body={"version_id": new_version_id},
        )
        print(f"activated version {new_version_id}")

    # Refresh local meta so a subsequent edit + upload chains correctly.
    if meta_path.is_file():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        meta["version_id"] = new_version_id
        meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(prog="exo-skill")
    parser.add_argument(
        "--profile",
        default=os.environ.get("EXO_PROFILE"),
        help="credential profile in $XDG_CONFIG_HOME/exo (default ~/.config), named after the MCP server",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    cr = sub.add_parser("create", help="create a new skill from a folder")
    cr.add_argument("--folder", required=True, help="folder to upload as the new skill")
    cr.add_argument("--name", help="skill name; defaults to the folder's basename")
    cr.add_argument(
        "--force",
        action="store_true",
        help="upsert a new version even if a skill with this name already exists",
    )
    cr.set_defaults(func=cmd_create)

    dl = sub.add_parser("download", help="download a skill version's bundle into a folder")
    dl.add_argument("skill", help="skill ID or name")
    dl.add_argument("--version", help="version ID; defaults to the active version")
    dl.add_argument("--out", help="output folder; defaults to ./<name>-<version-suffix>")
    dl.set_defaults(func=cmd_download)

    up = sub.add_parser("upload", help="upload a folder as a new skill version")
    up.add_argument("skill", help="skill ID or name")
    up.add_argument("--folder", required=True, help="folder to upload")
    up.add_argument("--activate", action="store_true", help="set the new version active")
    up.add_argument(
        "--no-base",
        action="store_true",
        help="upload without using the folder's meta file as base_version_id; drops any binary files that were not redownloaded",
    )
    up.set_defaults(func=cmd_upload)

    args = parser.parse_args()
    load_profile(args.profile)
    args.func(args)


if __name__ == "__main__":
    main()
