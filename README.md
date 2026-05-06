# DigitalOcean Topology Visualizer

A local, self-hosted web app that maps your DigitalOcean infrastructure as an interactive topology graph — droplets, managed databases (with read-only replicas), DNS records, networking (VPCs, firewalls, load balancers, reserved IPs), storage (volumes, snapshots), and compute extras (Kubernetes, App Platform, Functions, Container Registry). Click any node to see its connections; add notes; flag resources for deletion; switch between light and dark themes.

Everything runs in a single Docker container on your machine. The DigitalOcean API token never leaves your laptop.

## Features

- **Interactive force-directed graph** of your DO account, rendered with Cytoscape.js
- **Click any node** to see all its connections grouped by relationship (VPC, firewalls, load balancers, DNS, volumes, snapshots, etc.)
- **Isolation mode** — focus on a single node and only its direct connections
- **Filter by type** via the legend (click any resource type to hide / show)
- **Per-node notes** — freeform text saved locally per resource
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

3. **Paste your DigitalOcean API token** when prompted in the Settings panel.
   - Generate a token at <https://cloud.digitalocean.com/account/api/tokens>
   - Read scope is sufficient — this app never writes to your account
   - The token is validated against `/v2/account` before saving

That's it. The graph populates after a few seconds.

## Stack

- **Backend:** Python 3.12, FastAPI, httpx (async DO API client)
- **Storage:** SQLite (`./data/topology.db`, host-mounted, persists across restarts)
- **Frontend:** static HTML/CSS/JS + Cytoscape.js (no build step, no npm)
- **Container:** single image via `docker compose`

## Configuration

The DigitalOcean API token can be configured two ways. **Either works**; the in-app setting takes precedence over the environment variable.

### Option A — Settings panel (recommended)

Click **Settings** in the header, paste the token, click **Save & test**. Stored in `data/topology.db`.

### Option B — Environment variable

Edit `.env` in the project root:

```
DO_TOKEN=dop_v1_your_token_here
```

Restart the container: `docker compose restart`.

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
- **Spaces buckets** require S3-compatible auth (separate Spaces access keys). If `SPACES_KEY` / `SPACES_SECRET` are set in `.env` they'll be picked up; otherwise Spaces is skipped.
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
│   └── app.js
├── data/topology.db      # SQLite (host-mounted, gitignored)
├── tests/
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

# Inspect snapshot history
sqlite3 data/topology.db "SELECT id, fetched_at, status, duration_ms FROM snapshots ORDER BY id DESC LIMIT 10;"
```

## Backup

Everything you care about lives in `data/topology.db`:
- Snapshot history
- Per-node notes
- Flagged resources
- Saved DO API token

Copy that one file to back up the entire app state.

## Security notes

- The app runs **on localhost only** (`0.0.0.0:8000` exposed via Docker, not externally routable unless you change `docker-compose.yml`).
- The DO API token is stored **plaintext** in `data/topology.db`. Same security profile as `.env` — it's a local file on your machine. Don't commit `data/topology.db` (it's gitignored by default).
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
