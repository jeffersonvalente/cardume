# `docs/release/vX.Y.Z.md` template

Copy, fill in, and keep it in the repository. Leave a box unticked until it is done.

```markdown
# Release vX.Y.Z

Date: <YYYY-MM-DD> · Owner: <name> · Approval: docs/gates/GATE-<id>.md (approved <date>) | user OK in session <date>
Previous: vA.B.C · Bump: <major|minor|patch> because <the change that decided it>

## Checklist
- [ ] CHANGELOG.md updated (## [X.Y.Z] - <date>, compare links)
- [ ] Version bumped in manifests: <list files>
- [ ] `cardume-checklist .` and test suite green: <command → result>
- [ ] Release PR merged; tag `vX.Y.Z` created on the merged commit `<sha>` and pushed (after confirmation)
- [ ] GitHub release created from `docs/release/vX.Y.Z-notes.md` (after confirmation)
- [ ] Package published: <registry or "n/a"> (after confirmation)
- [ ] Smoke install from the registry in a clean directory: <command → result>
- [ ] README status / "What's new" updated
- [ ] Announcement posted on the channels below

## Release notes
<The changelog entry for this version, plus one paragraph of context if useful.>

## Breaking changes and migration
- <What breaks> → <exact steps to migrate, with before/after snippets>
- "None" if there are none — say so explicitly.

## Known issues
- <Issue> → <workaround, tracking issue>. "None known" if there are none.

## Rollback plan
- Trigger: <what observation means roll back, e.g. error rate, failing smoke test, data issue>
- Steps: <registry action from the table below / revert deploy / restore config>, then a fixed
  patch release; mark the changelog heading `## [X.Y.Z] - <date> [YANKED]`.
- Data: <migrations that are irreversible, and the backup to restore from>

## Announcement (≤ 300 words)
<See the structure below.>

## Channels
| Channel | Date | Owner | Status |
|---------|------|-------|--------|
| GitHub release | <date> | <name> | pending |
| <blog / forum / social / newsletter> | <date> | <name> | pending |

## Issue response commitment
New issues get a first response within <e.g. 2 business days> for <e.g. 2 weeks> after release;
triage owner: <name>.
```

## Announcement structure

Keep it under 300 words. Four parts, in this order:

1. **What it is** — one or two sentences with the real version: "Tidepool v0.4.0 adds JSON
   scenario export and fixes replay desyncs."
2. **Who it's for** — the specific reader who benefits ("people building custom levels").
3. **What it is NOT** — honest limits: "Still beta: save format may change before 1.0; no
   multiplayer; Windows builds are untested."
4. **One specific ask** — a single action: "Try exporting one of your levels and open an issue if
   the file fails to load." One ask gets answered; a list of five gets skipped.

Avoid superlatives, invented numbers and comparisons you have not measured. Link the release notes
and the migration section rather than repeating them.

## Rollback per registry

Published versions are effectively permanent: a version number cannot be reused on npm, PyPI or
crates.io, so "rollback" means steering users away from the bad version and shipping a fix.

| Registry | Action | Notes |
|----------|--------|-------|
| npm | `npm deprecate pkg@X.Y.Z "<reason, use X.Y.Z+1>"`; move the tag back with `npm dist-tag add pkg@A.B.C latest` | `npm unpublish` only within 72 h (or later if no dependents, < 300 weekly downloads and one maintainer); the version number stays burned |
| PyPI | Yank the release in the project's release settings, with a reason | Installers skip it unless pinned with `==`; nothing is deleted |
| crates.io | `cargo yank --version X.Y.Z` (undo with `--undo`) | Existing lockfiles keep working; new resolutions skip it |
| Containers | Re-point the moving tags (`latest`, `1`, `1.4`) to the previous image digest | Never overwrite the immutable `X.Y.Z` tag itself |
| GitHub release | Edit notes to flag the problem; mark the previous release Latest | With immutable releases the tag cannot be reused even after deletion |

In `CHANGELOG.md`, keep the entry and append `[YANKED]` to its heading (Keep a Changelog 1.1.0).

## Supply chain (recommended, not required)

- Publish from CI rather than a laptop, using OIDC trusted publishing instead of long-lived tokens:
  npm (GitHub Actions, GitLab CI; npm CLI 11.5.1+) and PyPI both support it.
- Attach provenance: npm generates it automatically for trusted publishing from public repos; for
  release binaries use `actions/attest-build-provenance` in the workflow and tell users how to check
  it with `gh attestation verify <file> --repo <owner>/<repo>`.
- Ship an SBOM (SPDX or CycloneDX) alongside binaries and container images.
