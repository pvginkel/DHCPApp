# Seed notes — `dhcpapp` producer

First architecture artifact for the DHCP Monitoring App backend. Hand-authored
mode (YAML is the source of truth). Headless seeding — modeling decisions made
without operator input; open questions listed at the end.

- **Producer id:** `dhcpapp`
- **`introduced` date:** `2025-08-16` (repo's first commit, `git log --reverse`),
  same on every element.
- **Mode:** hand-authored, uuid4 minted once per element.

## Minted ids

| id | kind | uuid | notes |
|---|---|---|---|
| `app:dhcpapp` | ApplicationComponent «SoftwareProduct» | `4396ad25-8251-4429-a154-3f8c11a8b6fc` | provided by task brief; `sourceRepository: git:pvginkel/DHCPApp`, `stats.image: registry:5000/dhcpapp` |
| `svc:dhcpapp-api` | ApplicationService | `a5f9d4f7-2ee8-4c14-bf89-b59054699d5f` | the exposed HTTP/SSE API |
| `if:dhcpapp-spa` | ApplicationInterface | `bf6ad452-927a-41d5-a1fc-e28c22101554` | single consumer class: the SPA frontend |
| `svc:ieee-oui` | ApplicationService (external) | `b7f68b34-230a-4dd8-ae1b-2d6f8b096d71` | external IEEE OUI registry; `stats.homepage` set, no «SoftwareProduct» |

## Cross-producer references

- `svc:ssegateway,59a7d043-bb0c-4e44-a8b8-3e943338f807` — in-house SSE gateway,
  UUID hand-provided by the task brief (not yet in the published dataset). The
  `app —Association→ svc:ssegateway` edge will **dangle** until the gateway's
  producer publishes; the validator reports this, it is not a failure.

## Exposed surface

- One `ApplicationService` (`svc:dhcpapp-api`) realized by the product
  (`app —Realization→ svc`). One `ApplicationInterface` (`if:dhcpapp-spa`) for
  the single distinct consumer class — the DHCP app SPA frontend (a separate
  producer; not modeled here) — assigned to the service.
- Routes surveyed: `/api/dhcp/{leases,pools,pools/usage}`, `/api/tasks/*`,
  `/api/auth/*`, OpenAPI at `/api/docs`. All grouped under the one SPA-facing
  service+interface (group by consumer, not per route).

## Included / excluded outbound dependencies

| Dependency | Env / source | Decision | Rationale |
|---|---|---|---|
| SSE gateway | `SSE_GATEWAY_URL` → POST `/internal/send` | **IN** — `Association → svc:ssegateway`, `boundBy: env:SSE_GATEWAY_URL` | In-house provider service; reference its specific `svc:` UUID. The `/api/sse/callback` webhook the app exposes is an implementation detail of consuming the gateway → modeled as ONE edge, not a second interface (per brief). |
| OIDC / IdP | `OIDC_ISSUER_URL` (active only when `OIDC_ENABLED=true`) | **IN** — `Association → cap:iam`, `boundBy: env:OIDC_ISSUER_URL` | Substitutable in-house infra → curated capability `cap:iam`; env carries issuer URL. Modeled even though optional — the dependency edge is real when enabled. |
| IEEE OUI / MAC vendor DB | `OUI_URL` constant inside the `mac_vendor_lookup` library (scheme rewritten http→https); fetched at startup when `UPDATE_MAC_VENDOR_DATABASE=true` | **IN** — external `svc:ieee-oui`, `Association`, `stats.homepage: https://standards-oui.ieee.org/`, no `boundBy` (URL not env-bound) | Borderline. Real recurring outbound HTTPS call to a stable named endpoint, so modeled as an external `svc:`. But it is a reference-data download (static OUI file), not an API integration, and the URL lives in a third-party library rather than this repo's config. Easy to prune if the operator prefers to treat it as a library/data detail. |
| Frontend version check | `FRONTEND_VERSION_URL` (default `http://localhost:3300/version.json`) | **OUT** | Trivial backend→frontend version-check ping — explicitly excluded by the modeling conventions. |
| `BASEURL` | self-reference for OIDC redirect_uri / cookie scheme | **OUT** | No outbound call; self-identity only. |

## Other exclusions

- Operational surfaces **OUT** (belong to the helm-charts/deployment lens, not
  the app): `/metrics` (Prometheus), `/health/{healthz,readyz,drain}`.
- `/internal/notify-lease-change` (POST from the in-pod dnsmasq companion
  container) — **OUT** as deployment-internal plumbing. It is arguably a second
  consumer class (the lease-watcher sidecar), but it is same-pod operational
  glue rather than a published API contract; defaulted out per the inclusion
  rule. See open questions.
- `/api/testing/*` endpoints — **OUT**; only mounted under `FLASK_ENV=testing`,
  not a production surface.
- Capabilities **realized**: none. This app *monitors* DHCP (reads dnsmasq lease
  data); it does not allocate IPs, so it does not realize `cap:dhcp` (that is
  dnsmasq's). It realizes no capability.

## `environment` / `cluster`

Left UNSET on all elements — these are logical, type-level surfaces spanning
every deployed env; per-env placement is the helm-charts producer's job.

## Validation

`./scripts/arch-validate.py docs/architecture/*.yaml` → exit 0 (clean). The
cross-producer `svc:ssegateway` ref is acceptable/dangling until that producer
publishes.

## Open questions for a human

- **IEEE OUI registry (`svc:ieee-oui`):** keep it as a modeled external service,
  or treat the OUI download as a library/data-fetch detail and drop it? Modeled
  IN as the best-effort call; low confidence.
- **`/internal/notify-lease-change`:** should the dnsmasq lease-watcher companion
  be modeled as a distinct consumer (a second `ApplicationInterface` on
  `svc:dhcpapp-api`), or does it stay deployment-internal plumbing (current
  choice)?
- **OIDC edge:** OIDC is optional (`OIDC_ENABLED`, off by default for the
  single-user homelab profile). Kept the `cap:iam` edge as the dependency is
  real when enabled — confirm this is the desired modeling for an optional
  integration.
