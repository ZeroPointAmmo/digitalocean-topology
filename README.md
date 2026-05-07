# DigitalOcean Topology Visualizer

A local, self-hosted web app that maps your DigitalOcean infrastructure as an interactive topology graph — droplets, managed databases (with read-only replicas), DNS records, networking (VPCs, firewalls, load balancers, reserved IPs), storage (volumes, snapshots), and compute extras (Kubernetes, App Platform, Functions, Container Registry). Click any node to see its connections; add notes; flag resources for deletion; switch between light and dark themes.

Manage **multiple DigitalOcean accounts** in one app — each gets its own token, snapshot history, and notes. Switch from the header chip; only one account is active at a time.

Everything runs in a single Docker container on your machine. The DigitalOcean API token never leaves your laptop.

## Features

- **Interactive force-directed graph** of your DO account, rendered with Cytoscape.js
- **Click any node** to see all its connections grouped by relationship (VPC, firewalls, load balancers, DNS, volumes, snapshots, etc.)
- **Isolation mode** — focus on a single node and only its direct connections
- **Filter by type** via the legend (click any resource type to hide / show)
- **Multiple DigitalOcean accounts** — name each one, switch in a click; per-account snapshot history and notes
- **Per-node notes** — freeform text saved locally per resource (scoped to the active account)
- **Flag for deletion** — mark resources for cleanup; flagged nodes get a red outline
- **Search** by name, IP, tag, role, region
- **Snapshot history** — every refresh is stored in SQLite so you can browse past states
- **Light & dark themes** with system-preference default
- **Read-only by design** — this app never writes anything to your DO account

## Quick start

1. **Clone and start the container:**
   ```bash
   git clone https://github.com/ZeroPointAmmo/digitalocean-topology.git
   cd digitalocean-topology
   docker compose up --build
   ```

2. **Open the app:** <http://localhost:8000>

3. **Add your first DigitalOcean account** when prompted in the Settings → Accounts panel.
   - Give it a name (e.g. "Personal", "Work") and paste the token
   - Generate a token at <https://cloud.digitalocean.com/account/api/tokens>
   - Read scope is sufficient — this app never writes to your account
   - The token is validated against `/v2/account` before saving; the account's UUID and email are captured so you can verify which DO account you're looking at

To add more accounts later, open Settings → Accounts and click **Add account**. Switch between them via the chip in the header.

That's it. The graph populates after a few seconds.

## Stack

- **Backend:** Python 3.12, FastAPI, httpx (async DO API client)
- **Storage:** SQLite (`./data/topology.db`, host-mounted, persists across restarts)
- **Frontend:** static HTML/CSS/JS + locally vendored Cytoscape.js (no build step, no npm)
- **Container:** single image via `docker compose`

## Configuration

Accounts are managed entirely in the UI: open **Settings → Accounts** to add, edit, switch, or delete an account. Each row shows the account name, DO email (captured from `/v2/account` at validation time), token hint, and Spaces status. The chip in the app header is the quick switcher.

### Migration from older versions

If you're upgrading a `data/topology.db` from before multi-account support:

- The legacy `DO_TOKEN` row in the `settings` table or `DO_TOKEN` from `.env` is imported into a seeded "Account 1" (or "from .env") on first start.
- Existing snapshots and notes are reattributed to that account automatically.
- After migration, the env vars `DO_TOKEN`, `SPACES_KEY`, `SPACES_SECRET`, `SPACES_REGION` are no longer consulted — manage everything via the Accounts panel.

### Spaces credentials

Spaces is per-account: open the account's edit form to add `spaces_key`, `spaces_secret`, and `spaces_region`. If you previously had Spaces creds in `.env`, they're copied into the seeded account during migration.

## Resource coverage

| Resource | API endpoint | Notes |
|---|---|---|
| Droplets | `/v2/droplets` | + tags, public/private IPs, VPC membership |
| Managed databases | `/v2/databases` | Includes engine, size, real disk capacity |
| Database replicas | `/v2/databases/{id}/replicas` | Linked to primary via `replica_of` edge |
| DNS | `/v2/domains`, `/v2/domains/{name}/records` | A/AAAA records linked to droplets/LBs by IP |
| VPCs | `/v2/vpcs` | |
| Firewalls | `/v2/firewalls` | Linked to droplets they protect |
| Load balancers | `/v2/load_balancers` | Linked to backend droplets |
| Reserved IPs | `/v2/reserved_ips` | Linked to assigned droplet |
| Volumes | `/v2/volumes` | Linked to attached droplet |
| Snapshots | `/v2/snapshots` | Linked to source droplet/volume |
| Kubernetes | `/v2/kubernetes/clusters` | |
| App Platform | `/v2/apps` | |
| Functions | `/v2/functions/namespaces` | |
| Container Registry | `/v2/registry` | |

**Caveats:**
- **Spaces buckets** require S3-compatible auth (separate Spaces access keys). Configure them per-account in Settings → Accounts → Edit → Spaces credentials.
- **Real-time database disk usage** is not in the standard DO API. The app shows provisioned capacity from `storage_size_mib`.

## Folder structure

```
.
├── app/                  # FastAPI backend
│   ├── collectors/       # one module per resource family
│   ├── do_client.py      # async DO API client
│   ├── topology.py       # graph builder + snapshot orchestrator
│   ├── db.py             # SQLite (snapshots, annotations, settings)
│   ├── routes.py
│   ├── main.py
│   └── config.py
├── static/               # Cytoscape.js frontend (no build)
│   ├── index.html
│   ├── theme.css         # light/dark color tokens
│   ├── styles.css
│   ├── app.js
│   └── vendor/           # local browser assets such as Cytoscape.js
├── data/topology.db      # SQLite — accounts, snapshots, notes (host-mounted, gitignored)
├── tests/                # pytest: routes, topology graph, v1->v2 migration
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## Useful commands

```bash
# Start (rebuild if Dockerfile or requirements changed)
docker compose up --build

# Stop
docker compose down

# Live logs
docker compose logs -f

# Run tests
docker compose run --rm topology pytest tests/

# Inspect snapshot history (per account)
sqlite3 data/topology.db "SELECT s.id, a.name AS account, s.fetched_at, s.status, s.duration_ms FROM snapshots s JOIN accounts a ON a.id=s.account_id ORDER BY s.id DESC LIMIT 10;"
```

## Backup

Everything you care about lives in `data/topology.db`:
- Account list (names, tokens, optional Spaces credentials, captured DO email/UUID)
- Per-account snapshot history
- Per-account notes and flagged resources

Copy that one file to back up the entire app state.

## Security notes

- The app runs **on localhost only** (`127.0.0.1:8000` exposed via Docker, not externally routable unless you change `docker-compose.yml`).
- DO API tokens are stored **plaintext** in `data/topology.db` (one per account). Same security profile as `.env` — it's a local file on your machine. Don't commit `data/topology.db` (it's gitignored by default).
- The app **only reads** from the DigitalOcean API. There are no `POST` / `PUT` / `DELETE` calls to DO.
- "Flag for deletion" is purely a local marker. It never deletes anything from your account.

## License

MIT — see [LICENSE](LICENSE).

## Contributing

Issues and pull requests welcome. The codebase is small and intentionally simple. To add a new resource type:

1. Add a collector in `app/collectors/`
2. Register it in `app/topology.py` (`FAMILIES` list)
3. Add node + edge construction in `topology.py`'s `build_graph`
4. Add display logic in `static/app.js` (`summaryFields`, `relationLabel`)
