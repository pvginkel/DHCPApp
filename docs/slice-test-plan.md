# Slice testing strategy

How a slice is proven once its phases are merged. This is the doc `.aiworkflowrc` names as
`test_phase.strategy`: the run loop's test phase is "read this and execute it", and nothing else
names it. Read it top to bottom and do what it says.

## What this phase proves, and what it does not

**Verification here is local.** DHCPApp has exactly one deployment — production, in the homelab
cluster — and no dev instance to roll. So this phase deploys nothing and verifies against nothing
deployed. It runs the suites tree-wide and boots the dev stack in this environment, from the merged
working tree.

**The push in step 4 deploys to production.** `Jenkinsfile` has no DTAP and no branch gating: the
`DHCP/DHCPApp` job validates, builds both images with `helmCharts.kaniko(...)` — `dhcpapp` and
`dhcpapp-ui` — and ends in `cicd.helmDeploy()`. Every push to `main` has always done that; it is the
repo's standing behaviour, not something this phase chooses. The consequence for ordering is the
whole point of this doc: **everything is verified before the push, because after the push it is
live.**

There is no `devlock`: with no dev instance, nothing contends.

## 0. Preconditions

The driver has ff-merged every code phase into the base branch. Confirm the tree is clean
(`git status --short`) before starting — a dirty tree here means an earlier phase left something
behind, and that is a finding, not something to tidy away.

Every verb below runs from the repo root: `kc project` is cwd-bound.

## 1. The suites, tree-wide

```bash
kc project build      # frontend: pnpm build (which also runs pnpm check)
kc project test       # backend: pytest; frontend: Playwright
```

Both must be green. `kc project build` is also what preflight demands, so a red build here means the
slice never should have reached this phase. The expected shape of a green `kc project test` is 62
passed / 4 skipped (backend 23, frontend 39 + 4), which is exactly what CI reports — a different
count is worth a sentence in the close-out even when it is green.

```bash
kc project lint       # backend: ruff, mypy, vulture; frontend: pnpm check
```

`kc project lint` must be green; no gate in this repo is known red, so a failure is this slice's.

## 2. The live check

Boot the dev stack the way this repo does — `Procfile.dev` under honcho, inside the `modern-app`
sidecar — and exercise the ports `.kubecoder/config.yaml` publishes: frontend 3300, backend 3301,
SSE gateway 3302.

```bash
cexec modern-app sh -c "poetry run honcho -f Procfile.dev start & echo \$! > /tmp/dhcpapp-dev.pid; wait" \
  > /tmp/dhcpapp-dev.log 2>&1 &
```

The pid file is written **from inside the sidecar**, and that is the point: killing the local `cexec`
client does not reach the honcho it started, and leaves all three services orphaned on their ports.
The pod shares one PID namespace, so the pid honcho reports there is signallable from here.

Wait for the stack to come up (poll `http://localhost:3300/` and
`http://localhost:3301/health/readyz` until both answer; ~20s), then probe:

```bash
curl -sS -o /dev/null -w 'frontend      %{http_code}\n' http://localhost:3300/
curl -sS -o /dev/null -w 'backend ready %{http_code}\n' http://localhost:3301/health/readyz
curl -sS -o /dev/null -w 'gateway ready %{http_code}\n' http://localhost:3302/readyz
curl -sS -o /dev/null -w 'leases direct %{http_code}\n' http://localhost:3301/api/dhcp/leases
curl -sS -o /dev/null -w 'leases proxy  %{http_code}\n' http://localhost:3300/api/dhcp/leases
```

All five answer `200`. **The last one is the one that matters** and is not redundant: it goes through
Vite's dev proxy, which is what proves the frontend is wired to *this* backend rather than three
unrelated processes happening to be up. Readiness alone is not enough either — `/health/readyz` only
checks the SSE gateway, and the backend has shipped in a state where readyz was green while every
`/api/dhcp/*` request failed. Hit real data, and compare what it returns against what the slice
changed.

The backend serves the sample dnsmasq tree the repo ships (`backend/data/`), so the leases, pools and
static reservations are fixed and can be asserted against. A slice that changed a rendered surface is
also worth loading in a browser at `https://frontend.$KUBECODER_ENVIRONMENT_ID.home/`.

Then stop it:

```bash
kill "$(cat /tmp/dhcpapp-dev.pid)"
```

honcho SIGTERMs all three children. Confirm all three ports are free afterwards with a socket connect
(`(exec 3<>/dev/tcp/127.0.0.1/3300)`), **not** an HTTP probe — the backend 404s on `/`, so a `curl`
against a live server reads as "free" and the next run dies on `Address already in use`. Leave no
survivors: an orphaned Vite or Flask holds the port for every later phase.

A slice that touched neither `backend/` nor `frontend/` — a docs-only or CI-only slice — can skip this
step and say so.

## 3. Check off `verification.json`

Mark each acceptance criterion with the evidence that settled it: the command run and what it
returned, or the endpoint hit and what it answered. A criterion nothing in steps 1–2 exercised is not
"passed by inspection"; it is either an untested criterion (a finding) or one whose check belongs in
this doc and is missing from it.

## 4. Push, then follow the build

Pushing is this phase's job — the driver ff-merges locally and never pushes a code phase, then checks
before the doc phase that every repo in `state.json`'s `bases` reached `origin`. Push each one,
honouring any repo named in `plan.md`'s `## Push holds`.

Record the current build number **before** pushing, so you can tell your build from the one already
there:

```
mcp__jenkins__getJob  jobFullName='DHCP/DHCPApp'  tree='lastBuild[number,result]'
```

Push, then poll the same call until `lastBuild.number` is higher and its `result` is no longer
`null`, and read the outcome:

```
mcp__jenkins__getBuild  jobFullName='DHCP/DHCPApp'  buildNumber=<n>  tree='number,result,description'
```

The description carries the suite summary the Jenkinsfile builds from `run-suite`'s
`===SUITE_RESULT:===` markers (`exit=0, 62 passed, 0 failed, 4 skipped` on a green build), so one call
gives both the verdict and the counts.

**The Jenkins MCP tools are the only way this works from here.** The unauthenticated JSON API answers
`403` and redirects to a login, so a session without `mcp__jenkins__*` cannot follow the build: report
the build number and say the result was not observed, rather than inventing one. That is a
reportable gap, not a blocker — the slice was already proven in steps 1–2.

This is a **did-I-break-CI check, not a verification gate**. What it catches is the class of failure
only CI can see: both Dockerfiles building end-to-end and the Helm deploy landing. A red build is a
blocking finding even though every local check passed — and because the deploy is downstream of the
image builds, a red build usually means production is still running the previous images rather than
something half-applied.

The second job, `AaC/DHCPApp` (`Jenkinsfile.architecture`), validates the two
`docs/architecture/*.yaml` artifacts. Follow it the same way when the slice touched either.

## Findings

Blocking findings come back as appended phases. Sub-bar findings go in the close-out report for the
operator to triage. A live check that cannot be run at all — the sidecar unavailable, a port already
held — is reported as *not verified*, never as passed. The phase is allowed to end with a criterion
unproven and said so; it is not allowed to end with one assumed.

## The operator gate

The operator's gate is the close-out report, after the run. Production has by then already taken the
change, which is what makes steps 1–2 the real gate and why they precede the push.
