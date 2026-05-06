"""Snapshot orchestration + graph builder.

`fetch_snapshot` runs every collector in parallel against the DO API and
returns a structured payload. A failure in any single family is captured
locally so partial snapshots are still useful.

`build_graph` is a pure function: snapshot payload -> {nodes, edges} for
Cytoscape.js.
"""

from __future__ import annotations

import asyncio
import time
import traceback
from typing import Any

from app.collectors import (
    compute_extras,
    databases,
    domains,
    droplets,
    networking,
    storage,
)
from app.do_client import DOClient

FAMILIES: list[tuple[str, Any]] = [
    ("droplets", droplets.collect),
    ("databases", databases.collect),
    ("domains", domains.collect),
    ("networking", networking.collect),
    ("storage", storage.collect),
    ("compute_extras", compute_extras.collect),
]


async def fetch_snapshot(token: str) -> dict[str, Any]:
    started = time.monotonic()
    payload: dict[str, Any] = {}
    errors: dict[str, str] = {}

    async with DOClient(token) as client:
        async def run(name: str, fn) -> tuple[str, Any, str | None]:
            try:
                return name, await fn(client), None
            except Exception as e:
                return name, None, _format_error(e)

        results = await asyncio.gather(*(run(n, fn) for n, fn in FAMILIES))

    for name, value, err in results:
        if err is None:
            payload[name] = value
        else:
            payload[name] = None
            errors[name] = err

    duration_ms = int((time.monotonic() - started) * 1000)
    if not errors:
        status = "success"
    elif len(errors) == len(FAMILIES):
        status = "error"
    else:
        status = "partial"
    return {
        "payload": payload,
        "errors": errors,
        "status": status,
        "duration_ms": duration_ms,
    }


def _format_error(exc: Exception) -> str:
    return f"{type(exc).__name__}: {exc}".strip() or repr(exc)


# ---------- Graph builder ----------

def build_graph(payload: dict[str, Any]) -> dict[str, list[dict]]:
    nodes: list[dict] = []
    edges: list[dict] = []
    seen_node_ids: set[str] = set()

    def add_node(node: dict) -> None:
        nid = node["data"]["id"]
        if nid in seen_node_ids:
            return
        seen_node_ids.add(nid)
        nodes.append(node)

    def add_edge(source: str, target: str, kind: str) -> None:
        if source not in seen_node_ids or target not in seen_node_ids:
            return
        edges.append({
            "data": {
                "id": f"{source}__{kind}__{target}",
                "source": source,
                "target": target,
                "label": kind,
                "kind": kind,
            }
        })

    droplets_list = payload.get("droplets") or []
    databases_list = payload.get("databases") or []
    domains_list = payload.get("domains") or []
    networking_data = payload.get("networking") or {}
    storage_data = payload.get("storage") or {}
    compute_data = payload.get("compute_extras") or {}

    vpcs = networking_data.get("vpcs") or []
    firewalls = networking_data.get("firewalls") or []
    lbs = networking_data.get("load_balancers") or []
    reserved_ips = networking_data.get("reserved_ips") or []

    volumes = storage_data.get("volumes") or []
    snapshots = storage_data.get("snapshots") or []

    k8s_clusters = compute_data.get("kubernetes_clusters") or []
    apps = compute_data.get("apps") or []
    functions = compute_data.get("functions_namespaces") or []
    registry = compute_data.get("registry")

    # ---------- Nodes ----------
    for vpc in vpcs:
        add_node({
            "data": {
                "id": _vpc_id(vpc["id"]),
                "type": "vpc",
                "label": vpc.get("name", vpc["id"]),
                "region": (vpc.get("region") or "").lower(),
                "ip_range": vpc.get("ip_range"),
                "raw": vpc,
            }
        })

    droplet_ip_index: dict[str, str] = {}  # ip -> droplet node id
    for d in droplets_list:
        node_id = _droplet_id(d["id"])
        public_ip = _first_ip(d, "public")
        private_ip = _first_ip(d, "private")
        if public_ip:
            droplet_ip_index[public_ip] = node_id
        if private_ip:
            droplet_ip_index[private_ip] = node_id
        size = d.get("size") or {}
        add_node({
            "data": {
                "id": node_id,
                "type": "droplet",
                "label": d.get("name", str(d["id"])),
                "region": ((d.get("region") or {}).get("slug") or "").lower(),
                "status": d.get("status"),
                "size": size.get("slug") if isinstance(size, dict) else None,
                "memory": size.get("memory") if isinstance(size, dict) else None,
                "vcpus": size.get("vcpus") if isinstance(size, dict) else None,
                "disk": size.get("disk") if isinstance(size, dict) else None,
                "public_ip": public_ip,
                "private_ip": private_ip,
                "vpc_uuid": d.get("vpc_uuid"),
                "tags": d.get("tags") or [],
                "raw": d,
            }
        })

    for db in databases_list:
        node_id = _db_id(db["id"])
        size_slug = db.get("size") or db.get("size_slug")
        connection = db.get("connection") or {}
        add_node({
            "data": {
                "id": node_id,
                "type": "db",
                "label": db.get("name", db["id"]),
                "engine": db.get("engine"),
                "version": db.get("version"),
                "size": size_slug,
                "num_nodes": db.get("num_nodes"),
                "region": (db.get("region") or "").lower(),
                "status": db.get("status"),
                "private_network_uuid": db.get("private_network_uuid"),
                "disk_size_gb": _mib_to_gb(db.get("storage_size_mib"))
                                or db.get("_disk_capacity_gb"),
                "tags": db.get("tags") or [],
                "role": "primary",
                "host": connection.get("host"),
                "raw": db,
            }
        })

        for replica in db.get("_replicas") or []:
            rep_id = _db_id(replica["id"])
            rep_conn = replica.get("connection") or {}
            add_node({
                "data": {
                    "id": rep_id,
                    "type": "db",
                    "label": replica.get("name", replica["id"]),
                    "engine": replica.get("engine"),
                    "version": replica.get("version"),
                    "size": replica.get("size"),
                    "num_nodes": replica.get("num_nodes"),
                    "region": (replica.get("region") or "").lower(),
                    "status": replica.get("status"),
                    "private_network_uuid": replica.get("private_network_uuid"),
                    "disk_size_gb": _mib_to_gb(replica.get("storage_size_mib")),
                    "tags": replica.get("tags") or [],
                    "role": "replica",
                    "host": rep_conn.get("host"),
                    "parent_cluster_id": db["id"],
                    "raw": replica,
                }
            })

    lb_ip_index: dict[str, str] = {}
    for lb in lbs:
        node_id = _lb_id(lb["id"])
        ip = lb.get("ip")
        if ip:
            lb_ip_index[ip] = node_id
        add_node({
            "data": {
                "id": node_id,
                "type": "lb",
                "label": lb.get("name", lb["id"]),
                "ip": ip,
                "region": ((lb.get("region") or {}).get("slug") or "").lower()
                          if isinstance(lb.get("region"), dict)
                          else (lb.get("region") or "").lower(),
                "vpc_uuid": lb.get("vpc_uuid"),
                "tags": lb.get("tags") or [],
                "raw": lb,
            }
        })

    for fw in firewalls:
        add_node({
            "data": {
                "id": _fw_id(fw["id"]),
                "type": "firewall",
                "label": fw.get("name", fw["id"]),
                "tags": fw.get("tags") or [],
                "raw": fw,
            }
        })

    for r in reserved_ips:
        ip = r.get("ip")
        if not ip:
            continue
        droplet_ip_index[ip] = droplet_ip_index.get(ip) or (
            _droplet_id(r["droplet"]["id"]) if r.get("droplet") else None
        )
        add_node({
            "data": {
                "id": _rip_id(ip),
                "type": "reserved_ip",
                "label": ip,
                "ip": ip,
                "region": ((r.get("region") or {}).get("slug") or "").lower()
                          if isinstance(r.get("region"), dict)
                          else (r.get("region") or "").lower(),
                "raw": r,
            }
        })

    for v in volumes:
        add_node({
            "data": {
                "id": _volume_id(v["id"]),
                "type": "volume",
                "label": v.get("name", v["id"]),
                "size_gigabytes": v.get("size_gigabytes"),
                "region": ((v.get("region") or {}).get("slug") or "").lower()
                          if isinstance(v.get("region"), dict)
                          else (v.get("region") or "").lower(),
                "tags": v.get("tags") or [],
                "raw": v,
            }
        })

    for s in snapshots:
        add_node({
            "data": {
                "id": _snapshot_id(s["id"]),
                "type": "snapshot",
                "label": s.get("name", s["id"]),
                "size_gigabytes": s.get("size_gigabytes"),
                "resource_type": s.get("resource_type"),
                "resource_id": str(s.get("resource_id")) if s.get("resource_id") is not None else None,
                "tags": s.get("tags") or [],
                "raw": s,
            }
        })

    for c in k8s_clusters:
        add_node({
            "data": {
                "id": _k8s_id(c["id"]),
                "type": "k8s",
                "label": c.get("name", c["id"]),
                "region": (c.get("region") or "").lower(),
                "vpc_uuid": c.get("vpc_uuid"),
                "node_pool_count": len(c.get("node_pools") or []),
                "tags": c.get("tags") or [],
                "raw": c,
            }
        })

    for a in apps:
        spec = a.get("spec") or {}
        add_node({
            "data": {
                "id": _app_id(a["id"]),
                "type": "app",
                "label": spec.get("name", a["id"]),
                "default_ingress": a.get("default_ingress"),
                "live_url": a.get("live_url"),
                "region": (spec.get("region") or "").lower(),
                "raw": a,
            }
        })

    for f in functions:
        add_node({
            "data": {
                "id": _func_id(f["namespace"]),
                "type": "function_ns",
                "label": f.get("label", f["namespace"]),
                "region": (f.get("region") or "").lower(),
                "raw": f,
            }
        })

    if registry:
        add_node({
            "data": {
                "id": "registry__" + (registry.get("name") or "registry"),
                "type": "registry",
                "label": registry.get("name", "registry"),
                "subscription_tier_slug": (registry.get("subscription_tier_slug")
                                            or registry.get("tier_slug")),
                "raw": registry,
            }
        })

    record_by_fqdn: dict[str, str] = {}
    for d in domains_list:
        domain_id = _domain_id(d["name"])
        add_node({
            "data": {
                "id": domain_id,
                "type": "domain",
                "label": d["name"],
                "raw": {k: v for k, v in d.items() if k != "_records"},
            }
        })
        for r in d.get("_records") or []:
            rec_id = _record_id(d["name"], r["id"])
            full_name = (
                f"{r['name']}.{d['name']}" if r.get("name") and r["name"] != "@"
                else d["name"]
            )
            add_node({
                "data": {
                    "id": rec_id,
                    "type": "record",
                    "label": f"{r.get('type','?')} {full_name}",
                    "name": r.get("name"),
                    "rtype": r.get("type"),
                    "data_value": r.get("data"),
                    "ttl": r.get("ttl"),
                    "domain": d["name"],
                    "fqdn": full_name,
                    "raw": r,
                }
            })
            add_edge(domain_id, rec_id, "has_record")
            if r.get("type") in ("A", "AAAA"):
                # First A/AAAA record wins for a given FQDN (apex if multiple)
                record_by_fqdn.setdefault(_normalize_host(full_name), rec_id)

    # ---------- Edges ----------
    for d in droplets_list:
        if d.get("vpc_uuid"):
            add_edge(_droplet_id(d["id"]), _vpc_id(d["vpc_uuid"]), "member_of")

    for db in databases_list:
        if db.get("private_network_uuid"):
            add_edge(_db_id(db["id"]), _vpc_id(db["private_network_uuid"]), "member_of")
        for replica in db.get("_replicas") or []:
            rep_id = _db_id(replica["id"])
            add_edge(rep_id, _db_id(db["id"]), "replica_of")
            if replica.get("private_network_uuid"):
                add_edge(rep_id, _vpc_id(replica["private_network_uuid"]), "member_of")

    for lb in lbs:
        if lb.get("vpc_uuid"):
            add_edge(_lb_id(lb["id"]), _vpc_id(lb["vpc_uuid"]), "member_of")
        for did in lb.get("droplet_ids") or []:
            add_edge(_lb_id(lb["id"]), _droplet_id(did), "routes_to")

    for c in k8s_clusters:
        if c.get("vpc_uuid"):
            add_edge(_k8s_id(c["id"]), _vpc_id(c["vpc_uuid"]), "member_of")

    for fw in firewalls:
        for did in fw.get("droplet_ids") or []:
            add_edge(_fw_id(fw["id"]), _droplet_id(did), "protects")

    for r in reserved_ips:
        if r.get("droplet") and r.get("ip"):
            add_edge(_rip_id(r["ip"]), _droplet_id(r["droplet"]["id"]), "assigned_to")

    for v in volumes:
        for did in v.get("droplet_ids") or []:
            add_edge(_volume_id(v["id"]), _droplet_id(did), "attached_to")

    for s in snapshots:
        rt = s.get("resource_type")
        rid = s.get("resource_id")
        if not rid:
            continue
        if rt == "droplet":
            add_edge(_snapshot_id(s["id"]), _droplet_id(rid), "snapshot_of")
        elif rt == "volume":
            add_edge(_snapshot_id(s["id"]), _volume_id(rid), "snapshot_of")

    # DNS resolution edges
    for d in domains_list:
        for r in d.get("_records") or []:
            if r.get("type") not in ("A", "AAAA", "CNAME"):
                continue
            target_data = r.get("data")
            if not target_data:
                continue
            rec_id = _record_id(d["name"], r["id"])
            if r["type"] in ("A", "AAAA"):
                if target_data in droplet_ip_index:
                    add_edge(rec_id, droplet_ip_index[target_data], "resolves_to")
                elif target_data in lb_ip_index:
                    add_edge(rec_id, lb_ip_index[target_data], "resolves_to")
            elif r["type"] == "CNAME":
                normalized = _normalize_host(target_data)
                target_rec = record_by_fqdn.get(normalized)
                if target_rec and target_rec != rec_id:
                    add_edge(rec_id, target_rec, "alias_of")

    for a in apps:
        ingress = a.get("default_ingress") or a.get("live_url")
        if not ingress:
            continue
        normalized = _normalize_host(ingress)
        target_rec = record_by_fqdn.get(normalized)
        if target_rec:
            add_edge(_app_id(a["id"]), target_rec, "exposed_via")

    return {"nodes": nodes, "edges": edges}


# ---------- helpers ----------

def _droplet_id(i: Any) -> str: return f"droplet__{i}"
def _db_id(i: Any) -> str: return f"db__{i}"
def _vpc_id(i: Any) -> str: return f"vpc__{i}"
def _fw_id(i: Any) -> str: return f"fw__{i}"
def _lb_id(i: Any) -> str: return f"lb__{i}"
def _rip_id(ip: str) -> str: return f"rip__{ip}"
def _volume_id(i: Any) -> str: return f"volume__{i}"
def _snapshot_id(i: Any) -> str: return f"snapshot__{i}"
def _k8s_id(i: Any) -> str: return f"k8s__{i}"
def _app_id(i: Any) -> str: return f"app__{i}"
def _func_id(i: Any) -> str: return f"funcns__{i}"
def _domain_id(name: str) -> str: return f"domain__{name}"
def _record_id(domain: str, rid: Any) -> str: return f"record__{domain}__{rid}"


def _normalize_host(host: str) -> str:
    h = (host or "").strip().lower()
    if h.endswith("."):
        h = h[:-1]
    if h.startswith("https://"):
        h = h[len("https://"):]
    if h.startswith("http://"):
        h = h[len("http://"):]
    h = h.split("/")[0]
    return h


def _first_ip(droplet: dict, kind: str) -> str | None:
    networks = (droplet.get("networks") or {}).get("v4") or []
    for net in networks:
        if net.get("type") == kind and net.get("ip_address"):
            return net["ip_address"]
    return None


def _mib_to_gb(mib: int | None) -> int | None:
    if not mib:
        return None
    return round(mib / 1024)
