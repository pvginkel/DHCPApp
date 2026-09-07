# DHCPApp

DHCPApp gives a homelab real-time visibility into its dnsmasq DHCP leases. The Flask backend parses
dnsmasq's config tree and lease file off disk and serves leases, pools and pool usage over a REST API
plus a Server-Sent Events stream; the React SPA renders them live. Both ship as containers into the
homelab Kubernetes cluster.

**Public repo — assume world-readable.** No secrets, credentials, internal hostnames/IPs or
non-public names, anywhere. That rule and the rest of the change discipline — clean breaking changes,
no tombstones, no defensive coding, testability is non-negotiable, never hand-edit the generated
OpenAPI client — are stated in full in [`docs/change-discipline.md`](docs/change-discipline.md).

## Repo structure

The three components are what `kc project list` returns; each subproject has its own `CLAUDE.md` and
`docs/`.

- **Root** — the `run-suite` orchestrator (`tools/suite_runner/`, CI's single entry point), the
  shared `Procfile.dev` dev stack and its `scripts/dev.py` launcher, the two Jenkinsfiles, and the
  repo-wide docs in `docs/`. Declares no tests: the suites belong to the components.
- **`backend/`** — the Flask REST + SSE API (Python, Poetry). Reads a sample dnsmasq tree from
  `backend/data/` in development and testing; mounts the real one in production.
- **`frontend/`** — the React 19 + Vite SPA (TypeScript, pnpm) with TanStack Router/Query, an
  OpenAPI-generated client, and a Playwright E2E suite that boots backend and SSE gateway per worker.

Everything builds through `kc project build|test|lint|setup`, run **from the repo root** — those
verbs are cwd-bound. The toolchain lives in the `modern-app` sidecar, so ad-hoc `poetry`/`pnpm`
commands need `cexec modern-app`. `scripts/dev.py` starts all three services together.

The spec repo is `../DHCPAppSpecs` (private): slices, plans and each run's state. It is a **separate
git repo** — commit there separately.

## Working rules

**Commit early and often, each meaningful unit, without being asked** — in this repo and the specs
repo alike; never batch unrelated changes.

**Work directly on `main`; no topic branches, and push as you go.** Single-person homelab, no other
committers to coordinate with. Don't make "ahead of origin" remarks — just push. Note that **a push
to `main` deploys to production**: the `DHCP/DHCPApp` job builds both images and runs
`cicd.helmDeploy()`, with no DTAP and no branch gating.

## The dev pipeline

Code changes go through the `dev` plugin's slice workflow — `/dev:triage` → `/dev:plan-slice` →
`/dev:run-slice` — which the operator drives; **never start a run yourself.** The project's half of
the contract is `.aiworkflowrc` and `.kubecoder/project.yaml`; nothing the pipeline reads by machine
belongs in this file.

Issue tracking follows the host convention; this project's owner tag is **`DHCPApp`**.

## Federated architecture model

This repo is one producer (`dhcpapp`) in a federated Architecture-as-Code model, with two
hand-authored artifacts: `backend/docs/architecture/architecture.yaml` and
`frontend/docs/architecture/architecture.yaml`. The `AaC/DHCPApp` job (`Jenkinsfile.architecture`)
validates both.

When a change here could affect an ArchiMate model of what this repo owns, nudge the operator to
spawn the `update-architecture` agent; nudge harder for a new managed host, a new daemon, a removed
service or a renamed external identity. The agent is incremental, so it need not run on every change,
and when working unattended you may invoke it yourself. The tooling lives on the operator's
filesystem, not in this repo: the `/seed-architecture` skill and the `update-architecture` agent, with
`~/.claude/architecture/producer-manual.md` as the authoritative vocabulary reference.

## Key documentation

- [`docs/change-discipline.md`](docs/change-discipline.md) — the rules every code change obeys.
- [`docs/slice-test-plan.md`](docs/slice-test-plan.md) — how a slice is verified before it is pushed.
- [`docs/slice-doc-plan.md`](docs/slice-doc-plan.md) — which doc surfaces a shipped slice updates.
- `backend/CLAUDE.md`, `frontend/CLAUDE.md` — per-subproject conventions and commands.
- `frontend/docs/api-generation.md` — how the generated OpenAPI client is produced.
- `backend/docs/product_brief.md`, `frontend/docs/product_brief.md` — the functional context.
