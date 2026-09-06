# Seed notes — `dhcpapp-ui` producer

First architecture artifact for the DHCP Monitoring UI (the web frontend for
DHCPApp). Hand-authored mode (the YAML is the source of truth). Headless seed —
modeling decisions made without operator triage; open questions logged below.

## Identity (fixed by task brief, not re-derived)

- Producer id: `dhcpapp-ui`
- `introduced` on every element: **2025-08-17** (this repo's first commit,
  `git log --reverse --format=%ad --date=short | head -1`).

## Minted ids (uuid4, mint-once)

| id | label | notes |
|---|---|---|
| `app:dhcpapp-ui,56e0795a-4140-40b6-84b3-7a2efb3bc9f5` | DHCP Monitoring UI | «SoftwareProduct», `sourceRepository: git:pvginkel/DHCPAppUI`, image `registry:5000/dhcpapp-ui`. |
| `svc:dhcpapp-ui-web,b7228a02-7a61-4b43-aea7-6cb2f14b9471` | DHCP App Web UI | The SPA served over HTTP to browsers. |
| `if:dhcpapp-ui-browser,79151ce4-b985-4896-ac92-bffe5f211a24` | DHCP App Web UI (browser) | End-user browser consumer of the web UI. |

## Modeling decisions

### Exposed surface — INCLUDED
The frontend is a static SPA served by NGINX (`nginx.conf` listens on 3300,
SPA fallback `try_files … /index.html`). Modeled as ONE `ApplicationService`
(`svc:dhcpapp-ui-web`) realized by the product, with ONE `ApplicationInterface`
(`if:dhcpapp-ui-browser`) for the single consumer class (the end-user browser).
This gives the deployer (helm-charts) a service UUID to attach the public host
to per the manual's "deployer references the service UUID" convention.

### Capabilities realized — NONE
A presentation-layer SPA realizes no capability from the enum.

### Outbound consumption edges

1. **Frontend → backend API** (required by brief).
   `app:dhcpapp-ui —Association→ svc:dhcpapp-api,a5f9d4f7-2ee8-4c14-bf89-b59054699d5f`.
   The SPA calls `/api/dhcp/leases`, `/api/dhcp/pools`, `/api/auth/...` etc.
   (relative paths; `src/lib/api/*.ts`). Cross-producer ref to `dhcpapp`'s
   ApplicationService, resolved from its local checkout
   (`../DHCPApp/docs/architecture/architecture.yaml`).

2. **Frontend → SSE gateway** (genuine, added).
   `app:dhcpapp-ui —Association→ svc:ssegateway,59a7d043-bb0c-4e44-a8b8-3e943338f807`.
   The SPA opens an `EventSource` to `/api/sse/stream`
   (`src/contexts/sse-context-provider.tsx:196`, `src/workers/sse-worker.ts:150`),
   NGINX-proxied to the gateway (`nginx.conf` `location /api/sse/`). The
   SSEGateway service models browser clients consuming the SSE stream as a
   first-class role, so this is a real dependency distinct from the backend's
   publisher edge. Cross-producer ref to `ssegateway`.

### No `boundBy` on either consumption edge
The production frontend always uses **relative** `/api` paths (per CLAUDE.md);
the concrete backend/gateway hosts are resolved by the container's NGINX
(`proxy_pass http://127.0.0.1:3301` / `:3302` — same-pod sidecars, a deployment
detail). No frontend runtime env var carries a provider address. The
`BACKEND_URL` / `SSE_GATEWAY_URL` env vars in `vite.config.ts` drive only the
**Vite dev proxy** and OpenAPI generation — not the deployed app. Per the
manual, a dependency located by something other than an env var is still a
legitimate edge but carries no `boundBy`. Omitted on both.

### Excluded (inclusion rule / out of scope)
- `/health` endpoint in `nginx.conf` — operational surface, belongs to the
  deployment lens, not the app.
- `BACKEND_URL` / `SSE_GATEWAY_URL` — dev-tooling config, not a runtime
  dependency of the deployed artifact (see above).
- `external-link.tsx` `http(s)://` strings — a scheme guard, not an outbound
  call. No real external SaaS dependency found (`grep -rIi '://' src` clean).
- `version.json` / git-rev — build provenance, not an architecture element.

## Cross-producer references (dangling until siblings publish)
- `svc:dhcpapp-api,a5f9d4f7-2ee8-4c14-bf89-b59054699d5f` — owned by producer
  `dhcpapp` (local checkout; not yet published). Validator does not check
  cross-producer refs; will dangle in `validation-report.json` until DHCPApp's
  first build registers — reported, not failing.
- `svc:ssegateway,59a7d043-bb0c-4e44-a8b8-3e943338f807` — owned by producer
  for the SSE gateway. Same dangling caveat.

## Open questions for the operator
- **Exposed web service modeling**: I modeled the SPA's served web surface as
  an `ApplicationService` + browser `ApplicationInterface` so the deployer has a
  UUID to attach the public host to. If you prefer frontends to carry *no*
  exposed service (treating the public web surface purely as a helm-charts
  ingress concern), drop `svc:dhcpapp-ui-web` + `if:dhcpapp-ui-browser` and
  their two relations.
- **SSE-gateway edge**: confirm the frontend→SSE-gateway `Association` is wanted
  here. It mirrors the backend's gateway edge but from the browser-consumer
  side; both are legitimate per the SSEGateway service's dual-role design.
- **boundBy absence**: confirmed there is no production env var on the frontend
  carrying backend/gateway addresses (relative paths + NGINX). If a future
  deployment injects one, add `boundBy: "env:<VAR>"` to the relevant edge.
