# Slice documentation plan

Which documentation surfaces a shipped slice brings up to date, and the rules for each. This is the
doc `.aiworkflowrc` names as `doc_phase.plan`: the run loop's doc phase is "read this and execute
it", working from the whole slice's merged diff.

Work the diff, not a checklist. Each surface below is owed an update only when the slice's changes
actually reached it.

## The surfaces

### 1. The `docs/` that owns the change

Three scopes:

| Scope | Owns |
|---|---|
| root `docs/` | cross-cutting and repo-wide: the change discipline, this plan, the slice testing strategy, anything that describes backend and frontend together |
| `backend/docs/` | the Flask API — the product brief, and the backend's Architecture-as-Code artifact |
| `frontend/docs/` | the SPA — the product brief, the generated API client (`api-generation.md`), the API usage examples, and the frontend's AaC artifact |

Design belongs to the subproject it describes; design that **spans** both — the wire contract between
them, the SSE stream, the dev stack — belongs to the root. A slice that changed the OpenAPI surface
changed a cross-cutting thing, whichever side's code moved: `frontend/docs/api-generation.md`
describes how the client is regenerated from it, and that description has to still be true.

The `docs/architecture/architecture.yaml` artifacts under each subproject are the federated
Architecture-as-Code model's, not this phase's. They are maintained by the `update-architecture`
agent and validated by the `AaC/DHCPApp` job. If the slice added a daemon, a managed host, an
external identity or a service — the changes that model notices — say so in the close-out so the
agent gets run; do not hand-edit the YAML as part of a doc pass.

### 2. The reader-facing READMEs

`backend/README.md` and `frontend/README.md` are what someone opening a subproject reads first. Both
are currently near-worthless — the backend's is empty and the frontend's is the unmodified Vite
template — which is a real state, not a gap this phase closes. Rewrite one only when **this slice's**
change makes its absence actively wrong (a new entry point, a changed way to run the thing); a
general rewrite is its own slice.

### 3. The `CLAUDE.md` files

Root, `backend/`, and `frontend/`. Each is loaded every turn by every agent the pipeline spawns, so
each is kept to about one screen and holds each fact **once** — the root carries what is true of the
repo, a subproject file carries only what is true of that subproject. A slice rarely touches them.
When a new standing rule genuinely belongs in one, something else moves out to a `docs/` topic doc
rather than the file growing.

Nothing the pipeline reads by machine goes in a `CLAUDE.md`; that is `.aiworkflowrc`'s job.

## What "up to date" means here

**State the design as it is**, as implemented, not as the slice authored it. Where the implementation
diverged from the plan, the doc describes what shipped. No changelog entries, no "as of slice NNN",
no tombstones for superseded conventions — rewrite the doc instead, per
[`change-discipline.md`](change-discipline.md).

**Ground every claim in the shipped source.** A doc sentence that cannot be checked against the merged
tree does not go in. This bites hardest in the frontend docs, which carry stale examples from before
the current layout (`api-generation.md` still names a port and a virtualenv the repo no longer uses);
when a slice makes you touch such a passage, fix what you touched — do not adopt the whole file.

## Gates

Documentation changes do not compile, but they do live beside code:

```bash
kc project build      # unchanged and green — the doc phase must not have moved code
```

Check that relative links resolve. Then commit; and if the slice's own folder in `../DHCPAppSpecs`
needs anything, commit there separately — it is a separate git repo.

## When there is little to do

A slice that changed no design, no convention and no reader-facing surface owes nothing here, and
saying so plainly is the correct outcome. Do not invent doc work to fill the phase; a paragraph
nobody needed is worse than no paragraph.
