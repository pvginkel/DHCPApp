# Change discipline

The rules every code change in this repo obeys, backend and frontend alike. This is the doc
`.aiworkflowrc` names as `design_philosophy`: it is handed to every `code-writer`, `code-reviewer`,
`plan-writer` and `plan-reviewer` the pipeline dispatches, and it is what a reviewer cites when
sending work back.

## Clean breaking changes

Single-user homelab app, no external consumers. The REST API and the SSE stream have exactly one
client — this repo's own SPA, which uses the backend's types directly rather than translating them
(the BFF pattern). So when an endpoint or a payload changes, **change it and fix the caller**: no
`/v2` path, no shim, no adapter, no optional field kept alive so an old shape still parses. The
generated client is regenerated in the same slice; that is the whole cost.

Two boundaries this rule stops at, both of them inbound:

- **The dnsmasq files.** `DNSMASQ_CONFIG_FILE_PATH` and the lease file are written by dnsmasq, not by
  us. Their formats and dnsmasq's own `conf-dir` filtering rules are a contract we implement, never
  one we redefine — a "simplification" there is a bug against the real world.
- **The architecture artifacts.** `backend/docs/architecture/*.yaml` and
  `frontend/docs/architecture/*.yaml` are validated against the federated model's published schema by
  the `AaC/DHCPApp` job. That schema is versioned in the Architecture repo; changes there come from
  there.

## No tombstones

Delete replaced code completely. No "moved to X" comments, no stub functions that forward, no
deprecated aliases, no commented-out blocks, no dead re-exports, no unused helper kept because it
might come back. Vulture runs over `backend/app/` and knip over the frontend precisely to catch this,
and both are part of `kc project lint`.

The same applies to prose: when a convention is superseded, **rewrite the doc** rather than appending
a note that the old rule no longer holds. Git history is the record of what things used to be; the
working tree is only ever a statement of what is true now.

## No defensive coding, no "just in case" infrastructure

No `try`/`except` that swallows an error, no drop-the-bad-record-and-keep-going path, no null-guard
for a condition the type system or the schema already prevents, no silent fallback. No retry, cache
or scheduled refresh added without a real observed failure to point at.

**Parsing input is the exception, and it is the point.** The backend's job is reading files something
else wrote — dnsmasq's config tree and its lease file. Validating those, and failing loudly and
specifically when they are malformed, is the feature, not defensiveness. The distinction is where the
input comes from: check what crosses into the system, trust what the system already established. A
lease the parser accepted does not get re-checked in the API layer.

Prefer obvious-now failure over silent-wrong-later. This app's entire value is telling the operator
the truth about their network; a view that quietly drops a lease is worse than one that errors.

Per side: the backend uses Python type annotations on every function and method, OOP with the Flask
application-factory + dependency-injection pattern, and the `logging` module rather than `print`. The
frontend is functional throughout — no classes — under TypeScript strict mode, with Zod at the edges
where runtime shape actually needs checking.

## Testability is critical

Every change ships with a test. A feature without one is incomplete, and "I verified it by hand" is
not a substitute — the point of the test is that it runs again next time.

| Component | Suite | Runs as |
|---|---|---|
| `backend` | pytest, under `backend/tests/` | `kc project test --project backend` |
| `frontend` | Playwright E2E, under `frontend/tests/` | `kc project test --project frontend` |
| `root` | none — orchestration and CI only | declares no tests, green by definition |

The Playwright suite boots its own backend, frontend and SSE gateway per worker on free ports, so an
end-to-end test is as cheap to write as a unit test here; reach for one when the behaviour spans the
two sides. A change that genuinely cannot be covered by either suite is a change whose testability
problem is the first thing to solve — say so and fix the seam, rather than shipping it uncovered.

## Never hand-edit generated artifacts

`frontend/src/lib/api/generated/` — types, the openapi-fetch client, the TanStack Query hooks and the
saved spec — is generated from the backend's OpenAPI document by `pnpm generate:api`, which `pnpm
build` runs. It is git-ignored, which makes it look like scratch; it is not editable either way.
Change the backend's schema and regenerate. `frontend/docs/api-generation.md` describes the path.

The same holds for TanStack Router's generated route tree: change the files under `src/routes/`, not
the tree.

## This is a public repo

`github.com/pvginkel/DHCPApp` is world-readable. No secrets, credentials, internal hostnames or IP
addresses, and no non-public names — in code, in tests, in fixtures, in commit messages, or in the
architecture artifacts. The sample dnsmasq tree under `backend/data/` uses RFC1918 example data and
stays that way.

The specs repo at `../DHCPAppSpecs` is **private**, which is where anything operational belongs. It
is not a licence to be careless there, but it is the right side of the line for a slice that has to
name real infrastructure.
