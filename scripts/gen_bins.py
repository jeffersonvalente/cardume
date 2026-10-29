#!/usr/bin/env python3
"""
gen_bins.py

Regenerates the `cardume-*` launchers in each plugin's bin/ directory.
Claude Code adds every enabled plugin's bin/ to the Bash PATH, so agents and the
check runners call `cardume-<script-name>` instead of plugin-specific file paths.

  plugins/<p>/skills/<skill>/scripts/foo_bar.py  ->  plugins/<p>/bin/cardume-foo-bar
  plugins/cardume-core/scripts/foo_bar.py          ->  plugins/cardume-core/bin/cardume-foo-bar
  plugins/cardume-frontend/skills/design-flow/scripts/*     ->  plugins/cardume-frontend/bin/cardume-design-flow <script>

Run after adding/removing a Python script. CI fails if bin/ is out of date.
"""

import os
import stat
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
PLUGINS_DIR = ROOT / "plugins"

PY_LAUNCHER = '''#!/usr/bin/env bash
here="$(cd "$(dirname "$(readlink -f "${{BASH_SOURCE[0]}}")")" && pwd)"
exec python3 "$here/{rel}" "$@"
'''

DESIGN_FLOW_LAUNCHER = '''#!/usr/bin/env bash
# Usage: cardume-design-flow <script.mjs> [args]  — runs a bundled design-flow script with node
here="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")" && pwd)"
script="$1"; shift || true
[ -z "$script" ] && { ls "$here/../skills/design-flow/scripts"; exit 1; }
exec node "$here/../skills/design-flow/scripts/$script" "$@"
'''


def command_name(script: Path) -> str:
    return "cardume-" + script.stem.replace("_", "-")


def write_exec(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def main() -> None:
    made = {}
    for plugin in sorted(p for p in PLUGINS_DIR.iterdir() if p.is_dir()):
        bin_dir = plugin / "bin"
        if bin_dir.exists():
            for old in bin_dir.glob("cardume-*"):
                old.unlink()
        scripts = sorted(plugin.glob("skills/*/scripts/*.py")) + sorted(plugin.glob("scripts/*.py"))
        for script in scripts:
            cmd = command_name(script)
            if cmd in made:
                sys.exit(f"bin collision: {cmd} from {made[cmd]} and {script}")
            made[cmd] = script
            write_exec(bin_dir / cmd, PY_LAUNCHER.format(rel=os.path.relpath(script, bin_dir)))
        if (plugin / "skills/design-flow/scripts").is_dir():
            write_exec(bin_dir / "cardume-design-flow", DESIGN_FLOW_LAUNCHER)
    print(f"{len(made)} python launchers generated")


if __name__ == "__main__":
    main()
