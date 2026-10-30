#!/usr/bin/env python3
"""
Cardume suite validator.

Runs every registered check against the repository and exits non-zero when any of them reports a
problem. CI runs it on every pull request; the changelog check compares against BASE_REF (default origin/main).

    python scripts/validate.py            # run all checks
    python scripts/validate.py --hash X   # print the hash used to block the name X (see `identity`)
    git log --format=%B | python scripts/validate.py --check-text   # same rule for commit messages

Each check is a function decorated with @check; its docstring is the one-line description printed
in the report. Checks call `problem(...)` for every violation they find.
"""

import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parent.parent
PLUGINS = ROOT / "plugins"
THIS_FILE = Path(__file__).resolve()
TEXT_SUFFIXES = {".md", ".py", ".mjs", ".js", ".json", ".tf", ".txt", ".sh", ".yml", ".yaml", ".hcl"}


# ---------------------------------------------------------------------------
# Small model of the repository
# ---------------------------------------------------------------------------

FRONT_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
KEY_RE = re.compile(r"^([A-Za-z_][\w-]*):", re.MULTILINE)
DESCRIPTION_RE = re.compile(r"^description:\s*(.*?)(?=^\S|\Z)", re.MULTILINE | re.DOTALL)


@dataclass
class Doc:
    """An agent file or a SKILL.md, with its frontmatter parsed just enough for the checks."""

    path: Path
    plugin: str
    text: str = field(repr=False)

    @property
    def rel(self) -> str:
        return str(self.path.relative_to(ROOT))

    @property
    def front(self) -> str:
        match = FRONT_RE.match(self.text)
        return match.group(1) if match else ""

    def value(self, key: str) -> str | None:
        match = re.search(rf"^{re.escape(key)}:\s*(.*)$", self.front, re.MULTILINE)
        return match.group(1).strip().strip("\"'") if match else None

    @property
    def description(self) -> str:
        match = DESCRIPTION_RE.search(self.front + "\n")
        return " ".join(match.group(1).split()) if match else ""

    @property
    def manual_only(self) -> bool:
        return self.value("disable-model-invocation") == "true"

    def list_value(self, key: str) -> list[str]:
        raw = self.value(key) or ""
        return [item.strip() for item in raw.split(",") if item.strip()]


def plugin_of(path: Path) -> str:
    return path.relative_to(PLUGINS).parts[0]


def agents() -> list[Doc]:
    return [Doc(p, plugin_of(p), p.read_text(encoding="utf-8")) for p in sorted(PLUGINS.glob("*/agents/*.md"))]


def skills() -> list[Doc]:
    return [Doc(p, plugin_of(p), p.read_text(encoding="utf-8")) for p in sorted(PLUGINS.glob("*/skills/*/SKILL.md"))]


def text_files():
    for path in sorted(ROOT.rglob("*")):
        if ".git" in path.parts or not path.is_file() or path.resolve() == THIS_FILE:
            continue
        if path.suffix in TEXT_SUFFIXES or path.parent.name == "bin":
            yield path


def lines_of(path: Path):
    return enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1)


# ---------------------------------------------------------------------------
# Check registry
# ---------------------------------------------------------------------------

CHECKS: list[Callable[[], None]] = []
PROBLEMS: list[str] = []
_current: list[int] = [0]


def check(fn: Callable[[], None]) -> Callable[[], None]:
    CHECKS.append(fn)
    return fn


def problem(message: str) -> None:
    _current[0] += 1
    PROBLEMS.append(message)
    print(f"    ✗ {message}")


# ---------------------------------------------------------------------------
# Structure
# ---------------------------------------------------------------------------

@check
def skill_folders_have_skill_md() -> None:
    """every skill folder has a SKILL.md"""
    for folder in sorted(d for d in PLUGINS.glob("*/skills/*") if d.is_dir()):
        if not (folder / "SKILL.md").exists():
            problem(f"{folder.relative_to(ROOT)}: folder has no SKILL.md")


@check
def frontmatter_present() -> None:
    """agents and skills start with frontmatter that has name and description"""
    for doc in agents() + skills():
        if not doc.front:
            problem(f"{doc.rel}: no frontmatter block at the top")
            continue
        for key in ("name", "description"):
            if doc.value(key) is None:
                problem(f"{doc.rel}: frontmatter has no '{key}'")


SKILL_KEYS = {
    "name", "description", "when_to_use", "argument-hint", "arguments", "disable-model-invocation",
    "user-invocable", "allowed-tools", "disallowed-tools", "model", "effort", "context", "agent",
    "paths", "background", "hooks", "shell", "metadata", "license", "compatibility",
}
AGENT_KEYS = {
    "name", "description", "tools", "disallowedTools", "model", "permissionMode", "maxTurns",
    "autoCompactWindow", "skills", "mcpServers", "hooks", "memory", "background", "omitClaudeMd",
    "effort", "isolation", "color", "initialPrompt", "experimental",
}


@check
def known_frontmatter_keys() -> None:
    """frontmatter uses only keys Claude Code understands (unknown keys are silently ignored)"""
    for docs, allowed in ((skills(), SKILL_KEYS), (agents(), AGENT_KEYS)):
        for doc in docs:
            unknown = sorted(set(KEY_RE.findall(doc.front)) - allowed)
            if unknown:
                problem(f"{doc.rel}: unknown frontmatter key(s) {unknown}")


@check
def names_are_unique() -> None:
    """each skill and agent name exists in exactly one plugin"""
    for kind, docs, key in (("skill", skills(), lambda d: d.path.parent.name),
                            ("agent", agents(), lambda d: d.path.stem)):
        owners: dict[str, list[str]] = {}
        for doc in docs:
            owners.setdefault(key(doc), []).append(doc.plugin)
        for name, plugins in sorted(owners.items()):
            if len(plugins) > 1:
                problem(f"{kind} '{name}' exists in several plugins: {', '.join(plugins)}")


SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


@check
def agent_skills_spec() -> None:
    """skills follow the Agent Skills spec (agentskills.io) so other tools can install them"""
    for doc in skills():
        name = doc.value("name") or ""
        if name != doc.path.parent.name or not SKILL_NAME_RE.match(name) or len(name) > 64:
            problem(f"{doc.rel}: name must be lowercase-hyphenated, ≤64 chars and equal to the folder name")
        if len(doc.description.strip("\"'")) > 1024:
            problem(f"{doc.rel}: description is longer than 1024 characters")
        if "," in (doc.value("allowed-tools") or ""):
            problem(f"{doc.rel}: allowed-tools must be space-separated")


@check
def skill_size() -> None:
    """SKILL.md stays at or under 500 lines (detail belongs in reference files)"""
    for doc in skills():
        count = len(doc.text.splitlines())
        if count > 500:
            problem(f"{doc.rel}: {count} lines")


# ---------------------------------------------------------------------------
# Triggering and context
# ---------------------------------------------------------------------------

TRIGGER_RE = re.compile(r"\buse (it |this |them )?(when|for|to|before|after|proactively)\b", re.IGNORECASE)
# Claude Code gives the skill listing 30,000 characters on a 1M context window and 6,000 on 200k, built-in
# skills take about 7,000 of that, and agent descriptions are listed separately. Every skill line carries
# its `plugin:name` prefix, so the ceiling counts the line, not just the description.
SKILL_LISTING_BUDGET = 20_000
QUOTES = "\"'"
AGENT_DESCRIPTION_BUDGET = 12_000


@check
def descriptions_say_when() -> None:
    """model-invocable skills and agents say when to use them"""
    for doc in agents() + skills():
        if not doc.manual_only and not TRIGGER_RE.search(doc.front):
            problem(f"{doc.rel}: description has no 'Use when …' trigger")


@check
def description_budget() -> None:
    """the skill listing and the agent descriptions leave room for other plugins"""
    listing = sum(len(f"- {doc.plugin}:{doc.path.parent.name}: {doc.description.strip(QUOTES)}\n")
                  for doc in skills() if not doc.manual_only)
    agent_text = sum(len(doc.description) for doc in agents())
    print(f"    · skill listing {listing} of {SKILL_LISTING_BUDGET}, agents {agent_text} of {AGENT_DESCRIPTION_BUDGET} characters")
    if listing > SKILL_LISTING_BUDGET:
        problem(f"skill listing uses {listing} characters (budget {SKILL_LISTING_BUDGET}); tighten the longest ones")
    if agent_text > AGENT_DESCRIPTION_BUDGET:
        problem(f"agent descriptions use {agent_text} characters (budget {AGENT_DESCRIPTION_BUDGET}); tighten the longest ones")


@check
def preloads_are_invocable() -> None:
    """agents preload only existing, model-invocable skills (manual-only skills cannot be preloaded)"""
    by_ref = {f"{doc.plugin}:{doc.path.parent.name}": doc for doc in skills()}
    for agent in agents():
        for ref in agent.list_value("skills"):
            target = by_ref.get(ref)
            if target is None:
                problem(f"{agent.rel}: preloaded skill '{ref}' does not exist (use cardume-<plugin>:<skill>)")
            elif target.manual_only:
                problem(f"{agent.rel}: preloads '{ref}', which is user-invoked only")


@check
def routing_covers_agents() -> None:
    """every agent is listed in the intelligent-routing table"""
    tables = [p.read_text(encoding="utf-8") for p in PLUGINS.glob("*/skills/intelligent-routing/SKILL.md")]
    if not tables:
        problem("intelligent-routing/SKILL.md not found")
        return
    table = "\n".join(tables)
    for agent in agents():
        name = agent.value("name") or agent.path.stem
        if name not in table:
            problem(f"{agent.rel}: agent '{name}' is missing from the intelligent-routing table")


@check
def agents_route_questions() -> None:
    """every agent says how to ask questions when it runs as a subagent"""
    for agent in agents():
        if "When running as a subagent" not in agent.text:
            problem(f"{agent.rel}: missing the subagent rule (questions go under **Open questions**)")


@check
def agents_return_deliverables() -> None:
    """every agent returns an analysis, plan, review or document in full"""
    for agent in agents():
        if "Return it in full" not in agent.text.partition("## Reporting back")[2]:
            problem(f"{agent.rel}: missing the deliverable rule in Reporting back")


# ---------------------------------------------------------------------------
# References and docs
# ---------------------------------------------------------------------------

REF_RE = re.compile(r"(?<![\w/-])/?(cardume-[a-z]+):([a-z0-9][a-z0-9-]*[a-z0-9])\b")
PSEUDO_REF_RE = re.compile(r"@\[(skills|agents|workflows)/")
COUNTS_SENTENCES = {
    "README.md": ("N specialist agents, N skills and N manual commands",
                  re.compile(r"(\d+) specialist agents, (\d+) skills and (\d+) manual commands")),
    "README.pt-BR.md": ("N agentes especialistas, N skills e N comandos manuais",
                        re.compile(r"(\d+) agentes especialistas, (\d+) skills e (\d+) comandos manuais")),
}


@check
def references_resolve() -> None:
    """every cardume-<plugin>:<name> reference points to a real skill or agent"""
    known = {(d.plugin, d.path.parent.name) for d in skills()} | {(d.plugin, d.path.stem) for d in agents()}
    plugins = {p.name for p in PLUGINS.iterdir() if p.is_dir()}
    for path in text_files():
        if path.suffix != ".md" and path.parent.name != "bin":
            continue
        for number, line in lines_of(path):
            for plugin, name in REF_RE.findall(line):
                if plugin in plugins and (plugin, name) not in known:
                    problem(f"{path.relative_to(ROOT)}:{number}: '{plugin}:{name}' does not exist")


@check
def no_pseudo_references() -> None:
    """no @[skills/…]-style references (nothing resolves them)"""
    for path in sorted(PLUGINS.rglob("*.md")):
        for number, line in lines_of(path):
            if PSEUDO_REF_RE.search(line):
                problem(f"{path.relative_to(ROOT)}:{number}: name the skill or agent plainly instead of @[…]")


@check
def readme_counts() -> None:
    """the counts sentence in README.md and README.pt-BR.md matches the files"""
    all_skills = skills()
    manual = sum(1 for doc in all_skills if doc.manual_only)
    actual = (len(agents()), len(all_skills) - manual, manual)
    print(f"    · files: {actual[0]} agents, {actual[1]} skills, {actual[2]} manual commands")
    for name, (sentence, pattern) in COUNTS_SENTENCES.items():
        path = ROOT / name
        match = pattern.search(path.read_text(encoding="utf-8")) if path.is_file() else None
        if not match:
            problem(f"{name}: sentence '{sentence}' not found")
            continue
        stated = tuple(int(n) for n in match.groups())
        if stated != actual:
            problem(f"{name} says {stated}, files have {actual}")


@check
def changelog_updated() -> None:
    """docs/CHANGELOG.md changes whenever plugins/ changes (diff against BASE_REF, default origin/main)"""
    base = os.environ.get("BASE_REF", "origin/main")
    try:
        out = subprocess.run(["git", "diff", "--name-only", f"{base}...HEAD"], cwd=ROOT,
                             capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        if os.environ.get("GITHUB_EVENT_NAME") == "pull_request":
            problem(f"cannot diff against {base}; check out with fetch-depth: 0")
        else:
            print(f"    · skipped: no git history for {base}")
        return
    changed = out.split()
    if any(f.startswith("plugins/") for f in changed) and "docs/CHANGELOG.md" not in changed:
        problem("plugins/ changed but docs/CHANGELOG.md did not — add a changelog entry")


# ---------------------------------------------------------------------------
# Evals
# ---------------------------------------------------------------------------

def yaml_list(text: str, key: str) -> list[str] | None:
    """A top-level YAML list, written inline (`key: [a, b]`) or as a block (`key:` then `- a`)."""
    match = re.search(rf"^{key}:[ \t]*(.*?)[ \t]*(?:#.*)?$", text, re.MULTILINE)
    if not match:
        return None
    inline = match.group(1)
    if inline.startswith("["):
        return [item.strip().strip("\"'") for item in inline.strip("[]").split(",") if item.strip()]
    block = re.match(r"((?:[ \t]*-[^\n]*\n?)+)", text[match.end() + 1:])
    return [re.sub(r"\s+#.*$", "", line.split("-", 1)[1]).strip().strip("\"'")
            for line in (block.group(1).splitlines() if block else [])]


def yaml_value(text: str, key: str) -> list[str]:
    """Every scalar value of `key` at any indentation, without quotes or trailing comments."""
    return [m.strip().strip("\"'") for m in re.findall(rf"^[ \t]*{key}:[ \t]*([^#\n]+)", text, re.MULTILINE)]


def eval_cases():
    """Case folders: any folder under plugins/*/evals/ with a prompt.md or a case.yaml (results excluded)."""
    found = {p.parent for name in ("prompt.md", "case.yaml") for p in PLUGINS.glob(f"*/evals/**/{name}")}
    return sorted(d for d in found if "results" not in d.relative_to(PLUGINS).parts)


@check
def eval_cases_load_their_plugins() -> None:
    """eval cases list their plugin and its dependencies, use `flags: i` instead of (?i), and name existing scaffolds"""
    for case in eval_cases():
        plugin, rel = plugin_of(case), case.relative_to(ROOT)
        manifest = json.loads((PLUGINS / plugin / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        deps = [d if isinstance(d, str) else d["name"] for d in manifest.get("dependencies") or []]
        # `claude plugin eval` loads only the listed plugins, and a plugin whose dependency is missing does
        # not load at all; the run must also start from plugins/ so the dependency is inside its root.
        up = "/".join([".."] * len(case.relative_to(PLUGINS / plugin).parts))
        expected = [up] + [f"{up}/../{d}" for d in deps]
        prompt, case_yaml = case / "prompt.md", case / "case.yaml"
        yaml_text = case_yaml.read_text(encoding="utf-8") if case_yaml.exists() else ""
        listed = None
        if prompt.exists():
            front = FRONT_RE.match(prompt.read_text(encoding="utf-8"))
            if not front:
                problem(f"{rel}/prompt.md: no frontmatter")
                continue
            listed = yaml_list(front.group(1), "plugins")
        if listed is None:
            listed = yaml_list(yaml_text, "plugins")
        missing = [e for e in expected if e not in (listed or [])]
        if missing:
            problem(f"{rel}: plugins must include {expected} (missing {missing})")
        for script in yaml_value(yaml_text, "scaffold_script"):
            if not (case / script).is_file():
                problem(f"{case_yaml.relative_to(ROOT)}: scaffold_script {script} not found")
        for file in [case_yaml, *sorted(case.glob("graders/*.md"))]:
            if file.exists() and "(?i)" in file.read_text(encoding="utf-8"):
                problem(f"{file.relative_to(ROOT)}: inline (?i) is not JavaScript regex; use `flags: i`")


# ---------------------------------------------------------------------------
# Hooks
# ---------------------------------------------------------------------------

PLUGIN_ROOT_RE = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([\w./-]+)")


@check
def hooks_point_to_scripts() -> None:
    """hooks.json parses and every script it runs exists"""
    for hooks_file in sorted(PLUGINS.glob("*/hooks/hooks.json")):
        try:
            config = json.loads(hooks_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            problem(f"{hooks_file.relative_to(ROOT)}: invalid JSON ({error})")
            continue
        handlers = [h for groups in config.get("hooks", {}).values() for g in groups for h in g.get("hooks", [])]
        for handler in handlers:
            command = " ".join([handler.get("command", ""), *handler.get("args", [])])
            for target in PLUGIN_ROOT_RE.findall(command):
                if not (hooks_file.parent.parent / target).exists():
                    problem(f"{hooks_file.relative_to(ROOT)}: runs missing file {target}")


GUARD = PLUGINS / "cardume-core" / "hooks" / "guard_bash.py"
GUARD_ASKS = [
    # kubectl
    "kubectl apply -f deploy.yaml", "kubectl -n prod apply -k overlays/prod", "kubectl create namespace x",
    "kubectl --context prod delete pod x", "kubectl --context=prod -n web delete pod x", "kubectl delete pod x -n prod",
    "kubectl --insecure-skip-tls-verify delete pod x", "kubectl patch deploy x -p '{}'", "kubectl replace -f x.yaml",
    "kubectl scale deploy/x --replicas=0", "kubectl drain node-1", "kubectl cordon node-1", "kubectl uncordon node-1",
    "kubectl edit deploy x", "kubectl set image deploy/x a=b:2", "kubectl label pod x a=b", "kubectl annotate pod x a=b",
    "kubectl taint nodes n a=b:NoSchedule", "kubectl autoscale deploy x --max=5", "kubectl expose deploy x --port=80",
    "kubectl run x --image=y", "kubectl debug pod/x --image=y", "kubectl rollout undo deploy/x",
    "kubectl -n prod rollout restart deploy/x", "kubectl rollout -n prod pause deploy/x", "kubectl rollout resume deploy/x",
    "kubectl certificate approve csr-1", "microk8s kubectl delete pod x", "minikube kubectl -- delete pod x",
    "cat x.yaml | kubectl apply -f -", "kubectl delete pod x --dry-run=none",
    # A dry run of one command does not excuse the next one, or a real run after a quoted mention.
    "kubectl create secret generic x --dry-run=client -o yaml | kubectl apply -f -",
    "kubectl apply -f x.yaml --dry-run=server && kubectl apply -f x.yaml",
    "kubectl annotate pod x note='try --dry-run first'",
    "kubectl apply -f <(kubectl create configmap x --from-file=a --dry-run=client -o yaml)",
    "kubectl apply -f - <<< $(kubectl create ns x --dry-run=client -o yaml)",
    "kubectl delete pod x # --dry-run=client", "kubectl delete pod x -- --dry-run",
    "ssh bastion 'kubectl apply -f x' && echo 'now --dry-run done'", "kubectl annotate pod x note=\"a\\\" --dry-run b\"",
    "kubectl apply -f x --dry-run=client --dry-run=none", "kubectl delete pod x --snapshot",
    # Lines the flag parser can't read still ask.
    'kubectl --context "my ctx" delete pod x', "kubectl $FLAGS delete pod x", 'kubectl "delete" pod x',
    'kubectl --context="$(kubectl config current-context)" delete pod x', "kubectl -n $(get ns) delete pod x",
    '"kubectl" delete pod x', "${KUBECTL} delete pod x", "kubectl-1.28 delete pod x", "kubectl.exe delete pod x",
    "kubectl -n prod \\\n  delete pod x", "helm \\\n  upgrade x ./c", 'helm --kube-context "my ctx" upgrade x ./c',
    # A namespace named like a read is still a namespace.
    "kubectl -n logs delete pod x", "kubectl --namespace events apply -f x", "kubectl -n config scale deploy/x --replicas=0",
    "helm -n history rollback web 3", "kubectl auth reconcile -f rbac.yaml",
    # helm
    "helm install web ./chart", "helm upgrade --install web ./chart -n prod", "helm upgrade web ./chart --dry-run=none",
    "helm uninstall web -n prod", "helm delete web", "helm rollback web 3 -n prod", "helm -n prod rollback web 3",
    "helm --kube-context prod upgrade web ./chart",
    # `-n` is not a dry run outside git push and cargo publish.
    "gh release create v1.0 -n notes", "twine upload -n dist/*", "poetry publish -n", "echo -n x && npm publish",
    "npm publish --dry-run && npm publish",
    # Unrelated rules keep asking.
    "terraform apply", "git push --force origin main", "git push origin v1.0.0", "docker push x/y:1", "DROP TABLE x",
]
GUARD_PASSES = [
    # kubectl: reads, and verbs that only appear in a name or an argument
    "kubectl get pods -n prod", "kubectl --context prod get pod delete-me", "kubectl describe pod scale-api",
    "kubectl logs deploy/drain-worker -f", "kubectl auth can-i delete pods", "kubectl api-resources --verbs=delete",
    "kubectl explain deployment.spec.replicas", "kubectl diff -f x.yaml", "kubectl top pods", "kubectl get events",
    "kubectl rollout status deploy/x", "kubectl rollout history deploy/restart", "kubectl config set-context --current",
    "kubectl config use-context prod", "kubectl apply view-last-applied deploy x", "kubectl -n logs get pods",
    "kubectl wait --for=delete pod/x", "kubectl exec x -- ls", "kubectl port-forward svc/x 8080:80",
    "kubectl --context prod -n web rollout status deploy/x",
    # kubectl: dry runs
    "kubectl apply -f x.yaml --dry-run=client", "kubectl apply -f x.yaml --dry-run=server", "kubectl delete pod x --dry-run=client",
    "kubectl -n prod scale deploy/x --replicas=2 --dry-run=client -o yaml", "kubectl create ns x --dry-run=client -o yaml",
    # helm: reads and dry runs
    "helm list -n prod", "helm status web", "helm history web", "helm get values web", "helm template web ./chart",
    "helm diff upgrade web ./chart", "helm repo update", "helm plugin install https://example.com/x",
    "helm upgrade web ./chart --dry-run", "helm upgrade --install web ./chart --dry-run=server -n prod",
    "helm uninstall web --dry-run", "helm rollback web 3 --dry-run",
    # Other dry runs keep passing.
    "git push -n origin v1.0.0", "cargo publish -n", "npm publish --dry-run", "goreleaser release --snapshot",
    "npm publish \\\n  --dry-run", "git push \\\n  -n origin v1.0.0", "kubectl apply \\\n  -f x --dry-run=client",
]


def guard_asks(command: str) -> bool:
    payload = json.dumps({"tool_input": {"command": command}})
    env = {**os.environ, "CARDUME_GUARD_BASH": "1"}
    result = subprocess.run([sys.executable, str(GUARD)], input=payload, capture_output=True, text=True, env=env)
    return '"permissionDecision": "ask"' in result.stdout


@check
def guard_cases() -> None:
    """guard_bash asks for each risky command and stays quiet on reads and dry runs"""
    for command in GUARD_ASKS:
        if not guard_asks(command):
            problem(f"guard_bash should ask: {command}")
    for command in GUARD_PASSES:
        if guard_asks(command):
            problem(f"guard_bash should stay quiet: {command}")


# ---------------------------------------------------------------------------
# Identity, privacy and portability of the text
# ---------------------------------------------------------------------------

# Names of clients, companies and people that must never ship, stored as truncated SHA-256 of the
# lowercase word so the names themselves are not in the repository. Every word and every pair of
# adjacent words (joined) is tested. Add a name with: python scripts/validate.py --hash <name>
BLOCKED_NAME_HASHES = {
    "ca56cc9fc4e48fae", "ffae63288067a44b", "1bab26e09513e594", "35c1e5df3be4fb97",
    "595a482cfcfc91ca", "658a5b7607f0803e", "8c7735d4a92c37e0", "9710effdc354f0c3",
    "9851d7cade9e4e88", "a8eb95955ee50ffd", "adfdbed1117c4b46", "bbe4b970f3801a5e",
    "e454cf0185a1c9c2", "f1fc9be177f6f1cb", "f4584665c2af1611", "f8b9758a23608862",
}
WORD_RE = re.compile(r"[a-z0-9]+")
# Update hosts of the upstream design flow (Impeccable) and of its earlier port; the first is split so
# a repo-wide grep for the old short name stays clean.
PHONE_HOME_HOSTS = ("x" "d.style", "impeccable.style/api")


def name_hash(name: str) -> str:
    return hashlib.sha256(name.lower().encode()).hexdigest()[:16]


def mentions_blocked_name(line: str) -> bool:
    words = WORD_RE.findall(line.lower())
    return any(name_hash(w) in BLOCKED_NAME_HASHES for w in words + [a + b for a, b in zip(words, words[1:])])


@check
def identity() -> None:
    """no client, company or people names"""
    for path in text_files():
        for number, line in lines_of(path):
            if mentions_blocked_name(line):
                problem(f"{path.relative_to(ROOT)}:{number}: blocked name — use a neutral one (e.g. acme)")


@check
def no_legacy_or_phone_home() -> None:
    """no legacy {{agentRootFolder}} placeholders and no update/phone-home hosts"""
    for path in text_files():
        if path.name == "NOTICE.md":
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        if "{{agentRootFolder}}" in content:
            problem(f"{path.relative_to(ROOT)}: legacy placeholder; use cardume-* commands or ${{CLAUDE_PLUGIN_ROOT}}")
        for host in PHONE_HOME_HOSTS:
            if host in content:
                problem(f"{path.relative_to(ROOT)}: references update host '{host}'")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def main() -> int:
    if len(sys.argv) == 3 and sys.argv[1] == "--hash":
        print(name_hash(sys.argv[2]))
        return 0
    if len(sys.argv) == 2 and sys.argv[1] == "--check-text":
        # Used by CI on commit messages: same blocked-name rule as the files.
        bad = [line for line in sys.stdin.read().splitlines() if mentions_blocked_name(line)]
        for line in bad:
            print(f"✗ blocked name in text: {line.strip()[:120]}")
        return 1 if bad else 0

    print("Cardume — validation\n")
    for number, fn in enumerate(CHECKS, 1):
        _current[0] = 0
        print(f"[{number:2}] {fn.__doc__}")
        fn()
        if _current[0] == 0:
            print("    ✓ ok")

    print()
    if PROBLEMS:
        print(f"✗ {len(PROBLEMS)} problem(s) found.")
        return 1
    print(f"✓ All {len(CHECKS)} checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
