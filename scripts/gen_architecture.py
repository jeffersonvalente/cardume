#!/usr/bin/env python3
"""
Generate docs/assets/architecture-{light,dark}.svg, the "How it works" diagram in the README.

Both files come from the same layout; only the palette changes. Edit the layout or the labels here and
re-run `python scripts/gen_architecture.py`.
"""

import sys
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "docs" / "assets"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate  # noqa: E402  (shared agent/skill discovery)
W, H = 1040, 512
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"

PALETTES = {
    "light": dict(bg="#ffffff", box="#f6f8fa", line="#d0d7de", text="#1f2328", muted="#59636e",
                  chip="#ffffff", arrow="#8c959f",
                  s1="#8250df", s2="#0969da", s3="#1a7f37", s4="#bf3989",
                  hook_fill="#fff8c5", hook_line="#d4a72c", hook_name="#7d4e00",
                  done_fill="#dafbe1", done_line="#1a7f37", doc_fill="#ddf4ff", doc_line="#54aeff"),
    "dark": dict(bg="#0d1117", box="#151b23", line="#3d444d", text="#f0f6fc", muted="#9198a1",
                 chip="#0d1117", arrow="#656c76",
                 s1="#ab7df8", s2="#4493f8", s3="#3fb950", s4="#db61a2",
                 hook_fill="#2a2111", hook_line="#9e6a03", hook_name="#e3b341",
                 done_fill="#12261e", done_line="#3fb950", doc_fill="#0c2d6b", doc_line="#1f6feb"),
}

LEVELS = [("0", "direct fix"), ("1", "mini-spec"), ("2", "spec → tasks"), ("3", "PRD → ADRs")]
PLUGINS = [
    ("core", "plan · debug · release"), ("frontend", "design · web · mobile"),
    ("backend", "APIs · databases"), ("data", "BigQuery · pipelines"),
    ("platform", "IaC · K8s · FinOps"), ("qa", "tests · security"),
    ("games", "engines · game feel"),
]
HOOKS = [
    ("guard_bash", "asks before risky commands"), ("syntax_check", "syntax errors after each edit"),
    ("stop_verify", "lint + scan must pass to end"), ("restrict_verifier_writes", "the verifier can't edit code"),
]
DOCS = ["spec.md", "tasks.md", "ADRs", "gate report"]


def text(x, y, s, size=13, color="text", weight=400, anchor="start", family=SANS):
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" '
            f'fill="{{{color}}}" text-anchor="{anchor}">{escape(s)}</text>')


def rect(x, y, w, h, fill="box", stroke="line", r=10, dash=None, sw=1):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{{{fill}}}" '
            f'stroke="{{{stroke}}}" stroke-width="{sw}"{d}/>')


def arrow(x1, y1, x2, y2):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{{arrow}}" stroke-width="1.5" marker-end="url(#head)"/>'


def stage(x, w, n, title, color):
    """Stage box with a numbered badge and a title; returns the parts."""
    y, h = 96, 300
    return [rect(x, y, w, h),
            f'<circle cx="{x + 22}" cy="{y + 26}" r="11" fill="{{{color}}}"/>',
            text(x + 22, y + 30.5, n, 12, "bg", 700, "middle"),
            text(x + 40, y + 31, title, 15, "text", 600)]


def layout():
    p = [f'<rect width="{W}" height="{H}" fill="{{bg}}"/>',
         '<defs><marker id="head" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
         'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{arrow}"/></marker></defs>']

    # documents written along the way
    p.append(rect(140, 12, 884, 40, "box", "line", 8))
    p.append(text(156, 37, "Written as it goes", 13, "muted", 600))
    x = 300
    for d in DOCS:
        w = 18 + 8.2 * len(d)
        p.append(rect(x, 20, w, 24, "doc_fill", "doc_line", 6))
        p.append(text(x + w / 2, 36.5, d, 12.5, "text", 500, "middle", MONO))
        x += w + 12

    # feedback loop: verifier sends gaps back to the builders
    p.append('<path d="M872,96 V74 H632 V92" fill="none" stroke="{s4}" stroke-width="1.5" '
             'stroke-dasharray="5 4" marker-end="url(#head)"/>')
    p.append(text(752, 68, "gap found → back to work", 12, "s4", 600, "middle"))

    # request
    p.append(rect(16, 206, 104, 80, "box", "line", 10))
    p.append(text(68, 238, "Your", 15, "text", 600, "middle"))
    p.append(text(68, 257, "request", 15, "text", 600, "middle"))
    p.append(text(68, 275, "plain words", 11.5, "muted", 400, "middle"))
    p.append(arrow(120, 246, 138, 246))

    # 1 classify
    p += stage(140, 176, "1", "Classify", "s1")
    p.append(text(156, 152, "work level", 12, "muted"))
    for i, (lvl, what) in enumerate(LEVELS):
        y = 172 + i * 50
        p.append(rect(154, y, 148, 38, "chip", "line", 8))
        p.append(f'<circle cx="{172}" cy="{y + 19}" r="10" fill="none" stroke="{{s1}}" stroke-width="1.5"/>')
        p.append(text(172, y + 23.5, lvl, 12, "s1", 700, "middle"))
        p.append(text(190, y + 23.5, what, 12.5, "text"))
    p.append(arrow(316, 246, 334, 246))

    # 2 route
    p += stage(336, 116, "2", "Route", "s2")
    for i, line in enumerate(["picks the", "specialist", "for the task"]):
        p.append(text(352, 160 + i * 19, line, 13, "text"))
    p.append(rect(348, 228, 92, 26, "chip", "line", 6))
    p.append(text(394, 245.5, "routing table", 11.5, "s2", 600, "middle"))
    for i, line in enumerate(["you never", "name an agent"]):
        p.append(text(352, 290 + i * 18, line, 12, "muted"))
    p.append(arrow(452, 246, 470, 246))

    # 3 specialists
    p += stage(472, 320, "3", "Specialists build", "s3")
    n_skills = sum(1 for s in validate.skills() if not s.manual_only)
    p.append(text(488, 152, f"{len(validate.agents())} agents · {n_skills} skills in seven plugins", 12, "muted"))
    for i, (name, what) in enumerate(PLUGINS):
        col, row = i % 2, i // 2
        x, y = 486 + col * 150, 166 + row * 54
        p.append(rect(x, y, 144, 46, "chip", "line", 8))
        p.append(text(x + 12, y + 19, name, 13, "s3", 700, family=MONO))
        p.append(text(x + 12, y + 36, what, 11.5, "muted"))
    x, y = 486 + 150, 166 + 3 * 54
    p.append(rect(x, y, 144, 46, "chip", "line", 8, dash="4 3"))
    p.append(text(x + 72, y + 28, "+ /commands", 12.5, "muted", 500, "middle", MONO))
    p.append(arrow(792, 246, 810, 246))

    # 4 verify
    p += stage(812, 120, "4", "Verify", "s4")
    for i, line in enumerate(["separate", "context"]):
        p.append(text(828, 160 + i * 19, line, 13, "text"))
    for i, name in enumerate(["verify", "qa-gatekeeper"]):
        p.append(rect(822, 204 + i * 32, 100, 26, "chip", "line", 6))
        p.append(text(872, 221.5 + i * 32, name, 11, "s4", 600, "middle", MONO))
    for i, line in enumerate(["accepts only", "evidence:", "commands and", "their output,", "tests, files"]):
        p.append(text(828, 286 + i * 18, line, 12, "muted"))
    p.append(arrow(932, 246, 950, 246))

    # done
    p.append(rect(952, 216, 72, 60, "done_fill", "done_line", 10))
    p.append(text(988, 243, "Done", 15, "text", 700, "middle"))
    p.append(text(988, 262, "with proof", 11.5, "muted", 400, "middle"))

    # hooks
    p.append(text(140, 426, "Hooks — run outside the model, on edits, shell commands and turn end", 13, "muted", 600))
    for i, (name, what) in enumerate(HOOKS):
        x = 140 + i * 224
        p.append(rect(x, 436, 212, 58, "hook_fill", "hook_line", 8))
        p.append(text(x + 12, 459, name, 12.5, "hook_name", 700, family=MONO))
        p.append(text(x + 12, 479, what, 12, "text"))
    return p


def render(palette: dict) -> str:
    body = "\n  ".join(part.format(**palette) for part in layout())
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'role="img" aria-label="How Cardume works">\n  {body}\n</svg>\n')


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, palette in PALETTES.items():
        (OUT / f"architecture-{name}.svg").write_text(render(palette), encoding="utf-8")
        print(f"wrote docs/assets/architecture-{name}.svg")


if __name__ == "__main__":
    main()
