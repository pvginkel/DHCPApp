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
  shared `Procfile.dev` dev stack and its `scripts/dev.py` launcher, the `Jenkinsfile` and the
  `Jenkinsfile.architecture` that publishes the architecture model, and the repo-wide docs in
  `docs/`. Declares no tests: the suites belong to the components.
- **`backend/`** — the Flask REST + SSE API (Python, uv). Reads a sample dnsmasq tree from
  `backend/data/` in development and testing; mounts the real one in production.
- **`frontend/`** — the React 19 + Vite SPA (TypeScript, pnpm) with TanStack Router/Query, an
  OpenAPI-generated client, and a Playwright E2E suite that boots backend and SSE gateway per worker.

Everything builds through `kc project build|test|lint|setup`, run **from the repo root** — those
verbs are cwd-bound. The toolchain lives in the `modern-app` sidecar, so ad-hoc `uv`/`pnpm` commands
need `cexec modern-app`. `scripts/dev.py` starts all three services together and
`scripts/dev.py stop` stops them from another shell. The root and `backend/` are two uv projects,
each with its own committed `uv.lock`, because CI and the image sync `--locked`. After a backend API
change, `scripts/regenerate-openapi.py --frontend` refreshes the frontend's OpenAPI cache and
client; a backend test fails while the committed cache is stale.
`cexec modern-app python3 scripts/check_updates.py` reports the dependencies with a newer release,
major, minor and patch, in every component it finds.

The spec repo is `../DHCPAppSpecs` (private): slices, plans and each run's state. It is a **separate
git repo** — commit there separately.

The dnsmasq repo is `../Dnsmasq`: the dnsmasq image, its config generator and management API, and
their tests. Its `dnsmasq/files/dhcp-script.sh` POSTs every lease change to this app's
`/internal/notify-lease-change`, so that contract's two ends change together. Its `kc project test`,
run from `../Dnsmasq`, includes the integration tier, which exercises the dnsmasq image by running
its stacks as Jobs in `development` against images built here. Its `Dnsmasq/Dnsmasq` Jenkins job
builds the three images and pins their tags into the deploy repo, so a push to its `main` deploys
too. A **separate git repo** — commit there separately.

The deploy repo is `../DnsmasqDeploy`: the Helm chart carrying this app's manifests alongside
dnsmasq's own, and the `config/prd/values.yaml` the build pins both image tags into for Argo CD to
sync. Also a **separate git repo** — commit there separately. Its verbs run through the `iac` and
`aac-tools` sidecars.

## Working rules

**Commit early and often, each meaningful unit, without being asked** — in this repo and the specs
repo alike; never batch unrelated changes.

**Work directly on `main`; no topic branches, and push as you go.** Single-person homelab, no other
committers to coordinate with. Don't make "ahead of origin" remarks — just push. Note that **a push
to `main` deploys to production**, with no DTAP and no branch gating: the `Dnsmasq/DHCPApp` job runs
`run-suite` in a validation Job, builds both images with kaniko, then pins the two tags into the
deploy repo's `config/prd/values.yaml` (`cicd.writeVersionPins`) for Argo CD to sync. Git is the
deployed state, so a rollback is a revert in `../DnsmasqDeploy`.

## The dev pipeline

Code changes go through the `dev` plugin's slice workflow — `/dev:triage` → `/dev:plan-slice` →
`/dev:run-slice` — which the operator drives; **never start a run yourself.** The project's half of
the contract is `.aiworkflowrc` and `.kubecoder/project.yaml`; nothing the pipeline reads by machine
belongs in this file.

## Architecture model

DHCPApp is a producer in the estate's federated architecture model. Its two models are
hand-authored, the backend's in `backend/docs/architecture/*.yaml` and the frontend's in
`frontend/docs/architecture/*.yaml`. `Jenkinsfile.architecture`, the job `AaC/DHCPApp`, validates
each against the architecture service on every push and archives them for AaC/Architecture to
collect.

The model is kept current centrally, not from here: the central architecture update in
`pvginkel/Architecture` (`tooling/fleet.py update`) reads the commits since the model last changed
and commits what they change in it. Nothing needs to run here after a change.

`Jenkinsfile.architecture` is the app's own, and `copier update` leaves it alone.

## Key documentation

- [`docs/change-discipline.md`](docs/change-discipline.md) — the rules every code change obeys.
- [`docs/slice-test-plan.md`](docs/slice-test-plan.md) — how a slice is verified before it is pushed.
- [`docs/slice-doc-plan.md`](docs/slice-doc-plan.md) — which doc surfaces a shipped slice updates.
- `backend/CLAUDE.md`, `frontend/CLAUDE.md` — per-subproject conventions and commands.
- `frontend/docs/api-generation.md` — how the generated OpenAPI client is produced.
- `backend/docs/product_brief.md`, `frontend/docs/product_brief.md` — the functional context.
