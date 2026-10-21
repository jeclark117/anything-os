#!/usr/bin/env python3
"""OKF v0.2 conformance check. Stdlib only, no pyyaml.

The frontmatter here is deliberately shallow, so a line scanner is enough
and avoids a dependency. If the frontmatter ever grows nested structures
beyond `sources` and inline flow mappings, swap this for a real parser.
"""

import os
import re
import sys
from datetime import date

# Default bundle root is the folder above scripts/. Pass a path to check a
# different one, for example an example: ./scripts/check.sh examples/personal
ROOT = os.path.abspath(
    sys.argv[1] if len(sys.argv) > 1
    else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
RESERVED = {"index.md", "log.md"}
# Each folder in examples/ is a separate bundle, checked on its own. Skipping a
# name during the walk never blocks checking it directly, because the root
# passed in is never filtered.
SKIP_DIRS = {".git", ".obsidian", "node_modules", "examples"}
# README.md at the root is the template's GitHub landing page. It carries no
# frontmatter on purpose, because GitHub would render it as a table, and
# onboarding deletes it. It is the one file the check ignores.
SKIP_ROOT_FILES = {"README.md"}

# §7 actor convention: human:<id> | process:<id> | <producer>/<version>
ACTOR = re.compile(r"^(human:[\w.\-]+|process:[\w.\-]+|[\w.\-]+/[\w.\-]+)$")

# generated.at must be a real instant. ISO 8601 with a Z or a +/-HH:MM offset.
AT_SHAPE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})$")
# Midnight-Z is the placeholder the schema example used to teach. It records a
# date wearing a timestamp's clothes, and in Pacific time it is the wrong day.
AT_PLACEHOLDER = re.compile(r"^\d{4}-\d{2}-\d{2}T00:00:00Z$")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

errors, warnings = [], []


def err(path, msg):
    errors.append(f"ERROR  {path}: {msg}")


def warn(path, msg):
    warnings.append(f"WARN   {path}: {msg}")


def md_files():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in sorted(filenames):
            if fn.endswith(".md"):
                yield os.path.join(dirpath, fn)


def strip_fences(text):
    """Blank out fenced code blocks. A footnote or link inside a fence is an
    example of the format, not a use of it."""
    out, in_fence = [], False
    for ln in text.split("\n"):
        if ln.lstrip().startswith("```"):
            in_fence = not in_fence
            out.append("")
            continue
        out.append("" if in_fence else ln)
    return "\n".join(out)


def split_frontmatter(text):
    """Return (frontmatter_lines, body_lines, had_block)."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return [], lines, False
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[1:i], lines[i + 1:], True
    return [], lines, None  # None = opened but never closed


def top_level(fm_lines):
    """Map top-level `key: value` pairs. Indented lines belong to the parent."""
    out = {}
    for ln in fm_lines:
        if not ln.strip() or ln.lstrip().startswith("#"):
            continue
        if ln[:1] in (" ", "\t", "-"):
            continue
        m = re.match(r"^([A-Za-z_][\w-]*)\s*:\s*(.*)$", ln)
        if m:
            out[m.group(1)] = m.group(2).strip()
    return out


def check_concept(path, rel, text):
    fm, body, had = split_frontmatter(text)
    if had is None:
        err(rel, "frontmatter block opened with --- but never closed")
        return
    if not had:
        err(rel, "no YAML frontmatter block (SPEC §11.1)")
        return

    keys = top_level(fm)

    # §11.2 the only hard requirement
    if "type" not in keys:
        err(rel, "frontmatter has no `type` (SPEC §11.2)")
    elif not keys["type"].strip():
        err(rel, "`type` is empty (SPEC §11.2)")

    # §7 actor convention
    for raw in fm:
        for m in re.finditer(r"\bby\s*:\s*([^,}\n]+)", raw):
            actor = m.group(1).strip().strip("\"'")
            if not ACTOR.match(actor):
                err(rel, f"actor '{actor}' does not match the §7 convention")

    # generated.at is a real instant, not a placeholder date
    for raw in fm:
        for m in re.finditer(r"\bat\s*:\s*([^,}\n]+)", raw):
            at = m.group(1).strip().strip("\"'")
            if AT_PLACEHOLDER.match(at):
                warn(rel, f"generated.at '{at}' is midnight-Z, a date not an instant")
            elif not AT_SHAPE.match(at):
                warn(rel, f"generated.at '{at}' is not ISO 8601 with Z or an offset")

    # §5.5 staleness
    if "stale_after" in keys:
        v = keys["stale_after"].strip().strip("\"'")
        if not ISO_DATE.match(v):
            err(rel, f"stale_after '{v}' is not YYYY-MM-DD")
        elif date.fromisoformat(v) <= date.today():
            warn(rel, f"stale as of {v}, needs review")

    # §5.4 lifecycle
    if "status" in keys and keys["status"].strip() not in (
        "draft", "stable", "deprecated",
    ):
        err(rel, f"status '{keys['status']}' is not draft|stable|deprecated")

    # §5.1 footnote labels must join to a sources[].id
    source_ids = set(re.findall(r"^\s*-?\s*id:\s*(\S+)", "\n".join(fm), re.M))
    body_text = strip_fences("\n".join(body))
    cited = set(re.findall(r"\[\^([\w.\-]+)\]", body_text))
    defined = set(re.findall(r"^\[\^([\w.\-]+)\]:", body_text, re.M))
    for label in sorted(cited - source_ids):
        err(rel, f"footnote [^{label}] has no matching sources[].id")
    for label in sorted(cited - defined):
        err(rel, f"footnote [^{label}] is cited but never defined")
    for sid in sorted(source_ids - cited):
        warn(rel, f"sources entry '{sid}' is never cited in the body")


def check_index(path, rel, text):
    fm, _, had = split_frontmatter(text)
    is_root = os.path.dirname(path) == ROOT
    if had and not is_root:
        err(rel, "index.md carries frontmatter; only the bundle root may (SPEC §8)")
    if is_root:
        if not had:
            err(rel, "bundle-root index.md must declare okf_version (SPEC §12)")
        elif "okf_version" not in top_level(fm):
            err(rel, "bundle-root index.md frontmatter lacks okf_version")


def check_log(path, rel, text):
    headings = re.findall(r"^##\s+(.+)$", text, re.M)
    if not headings:
        warn(rel, "log.md has no date headings (SPEC §9)")
    for h in headings:
        if not ISO_DATE.match(h.strip()):
            err(rel, f"log heading '{h.strip()}' is not YYYY-MM-DD (SPEC §9)")


def check_links(path, rel, text):
    _, body, _ = split_frontmatter(text)
    here = os.path.dirname(path)
    for m in re.finditer(r"\[[^\]]*\]\(([^)]+)\)", strip_fences("\n".join(body))):
        target = m.group(1).split("#")[0].strip()
        if not target or target.startswith(("http://", "https://", "mailto:")):
            continue
        if target.startswith("/"):
            warn(rel, f"bundle-absolute link '{target}' breaks in Obsidian and GitHub")
            continue
        if not os.path.exists(os.path.join(here, target)):
            err(rel, f"broken link '{target}'")


def main():
    concepts = 0
    for path in md_files():
        rel = os.path.relpath(path, ROOT)
        name = os.path.basename(path)
        if rel in SKIP_ROOT_FILES:
            continue
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        if name == "index.md":
            check_index(path, rel, text)
        elif name == "log.md":
            check_log(path, rel, text)
        else:
            concepts += 1
            check_concept(path, rel, text)
        check_links(path, rel, text)

    for line in warnings:
        print(line)
    for line in errors:
        print(line)

    print()
    print(f"{concepts} concepts checked, {len(errors)} errors, {len(warnings)} warnings")
    if errors:
        print("NOT CONFORMANT with OKF v0.2")
        return 1
    print("CONFORMANT with OKF v0.2")
    return 0


if __name__ == "__main__":
    sys.exit(main())
