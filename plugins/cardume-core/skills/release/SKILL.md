---
name: release
description: "Prepares a release: checks the approved gate or explicit OK, detects existing release tooling, picks the semver bump with reasons, writes the Keep a Changelog entry and docs/release/vX.Y.Z.md (notes, rollback, honest announcement), and hands over tag/publish commands for confirmation. Use when a version is ready to ship; invoked by the user (/cardume-core:release) or the release-manager agent."
disable-model-invocation: true
allowed-tools: Read Grep Glob Edit Write Bash(git log *) Bash(git describe *) Bash(git tag --list *) Bash(gh pr list *) Bash(cardume-checklist *)
compatibility: "Claude Code with the Cardume plugins (uses cardume-* commands, subagents or plugin paths); the guidance itself is portable."
---

# Release

A release is a promise to users: this version number means this set of changes, it was checked,
and there is a way back if it goes wrong. Prepare all of it locally; the public steps (tag push,
GitHub release, package publish, announcement) run only after the user confirms them, because they
are visible to others and hard to undo. The pre-approved tools above are read-only on purpose:
pushing, tagging and publishing go through the normal permission prompt.

Detailed templates: `reference/release-file.md` (the `docs/release/vX.Y.Z.md` checklist, the
announcement post, rollback per registry and supply-chain notes).

## 1. Preconditions

Check these before writing anything, and report each with evidence:

- **Approval.** Level-3 work: the gate in `docs/gates/GATE-<id>.md` shows the human's decision as
  approved, and any conditions attached to it are met. Other projects: the user explicitly approved
  what ships. Without either, stop and ask; a recommendation from `qa-gatekeeper` is not a decision.
- **Green checks.** Run `cardume-checklist .` and the project's test suite. A failure blocks the
  release: report it (issue draft) rather than fixing code inside the release.
- **Clean state.** `git status` is clean and the branch is the one that ships (usually `main`),
  up to date with its remote.

## 2. Detect existing release automation

Look before hand-editing anything, because a release tool owns the changelog and version fields
and will fight manual edits:

| Found | Tool | Do instead |
|-------|------|-----------|
| `release-please-config.json`, `.release-please-manifest.json` | release-please | review/merge its release PR |
| `.changeset/` | Changesets | `npx changeset` / `changeset version` flow |
| `.releaserc*`, `release.config.*` | semantic-release | let CI release from the merge |
| `.goreleaser.yml` / `.goreleaser.yaml` | GoReleaser | tag, then let its workflow build |

If one is present, follow that tool's flow and use this skill only for the parts it does not cover
(gate check, release file, rollback plan, announcement).

## 3. Collect what changed

```bash
git describe --tags --abbrev=0 --match 'v[0-9]*' --exclude '*-*'   # last stable tag, e.g. v0.3.0
git log v0.3.0..HEAD --oneline --no-merges
gh pr list --state merged --base main --limit 200 --search "merged:>=<date of last tag>"
```

The `--exclude '*-*'` skips pre-release tags so an `-rc.1` does not become the baseline; drop it
when preparing the next pre-release. `gh pr list` returns only 30 results by default, so keep the
explicit `--limit`.

Start from the existing `## [Unreleased]` section of `CHANGELOG.md`: those entries were written by
the people who made the changes, so move them into the new version and add only what git shows is
missing. Read commit and PR titles, not just prefixes: a `chore:` can still change behavior. Leave
internal-only changes (CI, refactors with no visible effect) out of user-facing notes, but keep
anything a user, operator or integrator would notice.

## 4. Choose the version (semver)

| Change since last tag | Bump | Example |
|-----------------------|------|---------|
| Breaking: removed/renamed API, changed defaults, incompatible data or config | major (`1.4.2 → 2.0.0`) | dropped a CLI flag |
| New backwards-compatible capability, or a deprecation | minor (`1.4.2 → 1.5.0`) | new endpoint, option marked deprecated |
| Fixes only, no new surface | patch (`1.4.2 → 1.4.3`) | crash fix |

- **0.x.** SemVer itself says anything may change in `0.y.z` (spec item 4). The common convention,
  which Cargo and npm's caret ranges rely on, is breaking → minor (`0.3.0 → 0.4.0`) and everything
  else → patch. Follow it and say clearly in the notes what breaks.
- **1.0.0.** Propose it when the software is used in production or users depend on a stable API
  (semver.org FAQ); staying on `0.x` then only hides breaking changes.
- **Pre-releases:** `1.0.0-rc.1`, `0.4.0-beta.2` when the user wants testers before a final.
- State the choice and the reason in one or two sentences, naming the change that decided it.

## 5. Update CHANGELOG.md (Keep a Changelog)

Create the file if it does not exist. Newest version first, an `Unreleased` section on top,
ISO dates, and only the groups that have entries:

```markdown
# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project
uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.4.0] - 2026-10-28

### Added
- Level editor exports scenarios as JSON (#42).

### Changed
- **Breaking:** `score` in save files is now an integer; old saves migrate on load (#45).

### Fixed
- Replays no longer desync after pausing (#47).

[Unreleased]: https://github.com/<owner>/<repo>/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/<owner>/<repo>/compare/v0.3.0...v0.4.0
```

Groups: Added, Changed, Deprecated, Removed, Fixed, Security. Write entries for the reader
("Exports scenarios as JSON"), not the commit log ("refactor exporter"), and link the PR or issue.

## 6. Bump versions

Update every manifest that carries the version (`package.json`, `pyproject.toml`, `Cargo.toml`,
`.claude-plugin/plugin.json`, app constants). Grep for the old version string to catch the ones
that are easy to miss, and rebuild lockfiles if the toolchain requires it.

## 7. Write `docs/release/vX.Y.Z.md`

One file per release, so the decision, the notes and the plan sit next to each other. Use the
template in `reference/release-file.md`. It covers:

- [ ] CHANGELOG.md updated
- [ ] Version bumped in all manifests
- [ ] Release PR merged; tag created on the merged commit and pushed
- [ ] GitHub release notes (from the changelog entry)
- [ ] Package published and smoke-installed from the registry
- [ ] README status / "What's new" updated
- [ ] Migration notes, breaking changes and known issues
- [ ] Rollback plan
- [ ] Announcement post (≤ 300 words: what it is, who it's for, what it is NOT, one specific ask)
- [ ] Channels list with dates and owner
- [ ] Response-time commitment for new issues

Tick only what is actually done; the unticked items are the remaining work.

## 8. Prepare the public steps and hand them over

Put the release files on a branch and open a release PR. Tag only after it is merged, and tag the
merged commit on the default branch, so the tag points at exactly what was reviewed:

```bash
git fetch origin && git rev-parse origin/main               # <sha> of the merged release commit
git tag -a v0.4.0 <sha> -m "v0.4.0: <one-line summary>"
git push origin v0.4.0
gh release create v0.4.0 --verify-tag --title "v0.4.0" --notes-file docs/release/v0.4.0-notes.md
# plus the package publish command, if any (npm publish, uv publish, cargo publish ...)
```

- Extract the release notes (the changelog entry plus migration notes and known issues) into the
  notes file, so the GitHub release matches the changelog word for word.
- **Pre-releases** (`-rc`, `-beta`, `-alpha`): add `--prerelease`. Add `--latest=false` when the
  release should not become "Latest", e.g. a patch to an older major line.
- **Immutable releases** (repo setting): assets and the tag lock on publish, and a deleted
  release's tag name can never be reused. Create a draft, attach assets, then publish:
  `gh release create v0.4.0 --verify-tag --draft ...`, `gh release upload v0.4.0 dist/*`,
  `gh release edit v0.4.0 --draft=false`.
- **Security fixes:** coordinate a GitHub Security Advisory (and CVE, requested through it) before
  release; keep exploit details out of the changelog and notes until the fix has shipped ("Fixed a
  security issue in X, see GHSA-…"), then publish the advisory right after the release.
- Show the commands as one numbered list. Ask for confirmation per step or for the whole listed
  batch, as the user prefers. A gate approval or an earlier "go ahead with the release prep" is not
  a yes to pushing.
- After running, report each command's result (tag SHA, release URL), then smoke-install the
  published version from the registry in a clean directory. Never say a tag or release is
  published unless the command ran and succeeded.
- Posting announcements on external channels stays with the user unless they ask you to do it
  with a tool you have; hand them the final text.

Publishing from CI with OIDC trusted publishing and provenance is the safer default; see
`reference/release-file.md` for the recommendations.

## Honest release communication

- Say the real version and scope. A `0.4.0` is not "1.0-ready"; a beta is called a beta.
- Name what the release does not do yet and known issues, so readers do not find out by failing.
- No invented numbers, quotes or comparisons. If performance improved, give the measurement and
  how it was taken, or leave it out.

## If something is wrong

A failing check, a bug found while writing notes, or a gate condition not met: stop, write an
issue draft (title, reproduction, impact), report it, and leave the fix to normal development.
Shipping around a known problem without telling the user turns one bug into a trust problem.
After publication, follow the rollback plan in the release file (yank/deprecate, mark the
changelog entry `[YANKED]`, ship a fixed patch).
