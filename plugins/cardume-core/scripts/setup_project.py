#!/usr/bin/env python3
"""
setup_project.py (cardume-setup)

Installs the Cardume conventions block into a project's CLAUDE.md without touching anything else.

Guarantees:
  - Only the text between <!-- cardume:start --> and <!-- cardume:end --> is ever replaced.
    Everything outside the block is verified byte-for-byte after writing; on mismatch the
    backup is restored.
  - AGENTS.md is never written. When it exists, the block imports it (@AGENTS.md) so both
    files stay a single source of truth.
  - Every file is backed up to .cardume/backups/<timestamp>/ before it changes.
  - Dry run by default: prints the diff. Pass --apply to write.

Usage:
  cardume-setup [project] [--apply]
"""

import argparse
import difflib
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

START = "<!-- cardume:start -->"
END = "<!-- cardume:end -->"
BLOCK_RE = re.compile(re.escape(START) + r".*?" + re.escape(END), re.DOTALL)
TEMPLATE = Path(__file__).resolve().parent.parent / "templates" / "CLAUDE.md"
GITIGNORE_ENTRIES = [".cardume/", ".claude/agent-memory-local/"]
# marker file -> (official LSP plugin, language server binary, install hint)
LSP_HINTS = [
    (("tsconfig.json", "package.json"), "typescript-lsp", "typescript-language-server",
     "npm install -g typescript-language-server typescript"),
    (("pyproject.toml", "requirements.txt", "setup.py"), "pyright-lsp", "pyright-langserver", "npm install -g pyright"),
    (("go.mod",), "gopls-lsp", "gopls", "go install golang.org/x/tools/gopls@latest"),
    (("pom.xml", "build.gradle", "build.gradle.kts"), "jdtls-lsp", "jdtls", "install Eclipse JDT Language Server"),
    (("Cargo.toml",), "rust-analyzer-lsp", "rust-analyzer", "rustup component add rust-analyzer"),
]


def build_block(project: Path, claude_md_text: str) -> str:
    block = TEMPLATE.read_text(encoding="utf-8").strip()
    imports_agents = re.search(r"^@AGENTS\.md\s*$", BLOCK_RE.sub("", claude_md_text), re.MULTILINE)
    if (project / "AGENTS.md").is_file() and not imports_agents:
        block = block.replace(START, f"{START}\n@AGENTS.md\n", 1)
    return block


def new_claude_md(current: str, block: str) -> str:
    if BLOCK_RE.search(current):
        return BLOCK_RE.sub(lambda _: block, current, count=1)
    if not current.strip():
        return block + "\n"
    return current.rstrip("\n") + "\n\n" + block + "\n"


def outside_block(text: str) -> str:
    return BLOCK_RE.sub("", text)


def new_gitignore(current: str) -> str:
    lines = {l.strip() for l in current.splitlines()}
    missing = [e for e in GITIGNORE_ENTRIES if e not in lines and e.rstrip("/") not in lines]
    if not missing:
        return current
    prefix = current if not current or current.endswith("\n") else current + "\n"
    return prefix + "".join(e + "\n" for e in missing)


def print_lsp_hints(project: Path) -> None:
    hints = [h for h in LSP_HINTS if any((project / marker).exists() for marker in h[0])]
    if not hints:
        return
    print("\nRecommended code-intelligence plugins (official, optional):")
    for _, plugin, binary, install in hints:
        status = "found" if shutil.which(binary) else f"missing — {install}"
        print(f"  /plugin install {plugin}@claude-plugins-official   ({binary}: {status})")


def show_diff(path: Path, old: str, new: str) -> None:
    diff = difflib.unified_diff(old.splitlines(keepends=True), new.splitlines(keepends=True),
                                fromfile=f"a/{path.name}", tofile=f"b/{path.name}")
    sys.stdout.writelines(diff)


def main() -> None:
    parser = argparse.ArgumentParser(description="Install the Cardume block into CLAUDE.md safely")
    parser.add_argument("project", nargs="?", default=".", help="Project root")
    parser.add_argument("--apply", action="store_true", help="Write the changes (default: dry run)")
    args = parser.parse_args()

    project = Path(args.project).resolve()
    claude_md = project / "CLAUDE.md"
    gitignore = project / ".gitignore"

    claude_old = claude_md.read_text(encoding="utf-8") if claude_md.exists() else ""
    if claude_old.count(START) > 1 or claude_old.count(START) != claude_old.count(END):
        sys.exit(f"{claude_md}: malformed Cardume markers; fix them by hand before running setup.")
    claude_new = new_claude_md(claude_old, build_block(project, claude_old))
    changes = [(claude_md, claude_old, claude_new)]
    if (project / ".git").exists() or gitignore.exists():
        git_old = gitignore.read_text(encoding="utf-8") if gitignore.exists() else ""
        changes.append((gitignore, git_old, new_gitignore(git_old)))
    changes = [c for c in changes if c[1] != c[2]]

    if not changes:
        print("Already up to date. Nothing to change.")
        print_lsp_hints(project)
        return
    for path, old, new in changes:
        show_diff(path, old, new)
    print("\nAGENTS.md: " + ("imported via @AGENTS.md, not modified" if (project / "AGENTS.md").is_file()
                             else "not present"))
    print_lsp_hints(project)
    if not args.apply:
        print("\nDry run. Re-run with --apply to write these changes.")
        return

    backup_dir = project / ".cardume" / "backups" / datetime.now().strftime("%Y%m%d-%H%M%S")
    for path, old, new in changes:
        if path.exists():
            backup_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, backup_dir / path.name)
        path.write_text(new, encoding="utf-8")

    written = claude_md.read_text(encoding="utf-8")
    expected_outside = outside_block(claude_old) if BLOCK_RE.search(claude_old) else claude_old.rstrip("\n")
    if outside_block(written).rstrip("\n") != expected_outside.rstrip("\n"):
        if (backup_dir / "CLAUDE.md").exists():
            shutil.copy2(backup_dir / "CLAUDE.md", claude_md)
        else:
            claude_md.unlink()
        sys.exit("Safety check failed: content outside the Cardume block changed. CLAUDE.md restored.")

    print(f"\nWritten. Backups: {backup_dir if backup_dir.exists() else 'none needed (new files)'}")


if __name__ == "__main__":
    main()
