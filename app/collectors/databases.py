import asyncio

from app.do_client import DOAPIError, DOClient

# Fallback only — DO now returns `storage_size_mib` on the listing endpoint,
# so we prefer that. We keep this map as a backstop for older API responses.
SIZE_SLUG_DISK_GB = {
    "db-s-1vcpu-1gb": 10,
    "db-s-1vcpu-2gb": 25,
    "db-s-2vcpu-4gb": 38,
    "db-s-4vcpu-8gb": 115,
    "db-s-6vcpu-16gb": 270,
    "db-s-8vcpu-32gb": 580,
    "db-s-16vcpu-64gb": 1120,
    "so1_5-2vcpu-16gb": 270,
    "so1_5-4vcpu-32gb": 580,
    "so1_5-8vcpu-64gb": 1120,
    "so1_5-16vcpu-128gb": 2090,
    "so1_5-24vcpu-192gb": 3010,
    "so1_5-32vcpu-256gb": 3840,
    "gd-2vcpu-8gb": 25,
    "gd-4vcpu-16gb": 60,
    "gd-8vcpu-32gb": 145,
    "gd-16vcpu-64gb": 325,
    "gd-32vcpu-128gb": 695,
}


async def collect(client: DOClient) -> list[dict]:
    items = await client.paginate("/v2/databases", "databases")
    for db in items:
        slug = db.get("size") or db.get("size_slug")
        if slug:
            db["_disk_capacity_gb"] = SIZE_SLUG_DISK_GB.get(slug)

    if not items:
        return items

    async def fetch_replicas(cluster: dict) -> list[dict]:
        try:
            data = await client.get(f"/v2/databases/{cluster['id']}/replicas")
        except DOAPIError:
            return []
        return data.get("replicas", []) or []

    replica_lists = await asyncio.gather(*(fetch_replicas(c) for c in items))
    for cluster, replicas in zip(items, replica_lists):
        for r in replicas:
            # Replicas inherit engine/version from the parent (not returned by the
            # replicas endpoint).
            r.setdefault("engine", cluster.get("engine"))
            r.setdefault("version", cluster.get("version"))
            r["_parent_cluster_id"] = cluster["id"]
            r["_parent_cluster_name"] = cluster.get("name")
        cluster["_replicas"] = replicas
    return items
