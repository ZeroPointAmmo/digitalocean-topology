import json
from pathlib import Path

import pytest

from app.topology import build_graph

FIXTURE = Path(__file__).parent / "fixtures" / "sample_snapshot.json"


@pytest.fixture(scope="module")
def graph() -> dict:
    payload = json.loads(FIXTURE.read_text())
    return build_graph(payload)


def _ids(items: list[dict]) -> set[str]:
    return {it["data"]["id"] for it in items}


def _edge_kinds(graph: dict) -> set[tuple[str, str, str]]:
    return {
        (e["data"]["source"], e["data"]["kind"], e["data"]["target"])
        for e in graph["edges"]
    }


def test_droplets_become_nodes(graph):
    ids = _ids(graph["nodes"])
    assert "droplet__100" in ids
    assert "droplet__101" in ids


def test_database_attaches_to_vpc(graph):
    edges = _edge_kinds(graph)
    assert ("db__db-uuid-1", "member_of", "vpc__vpc-aaa") in edges


def test_droplet_attaches_to_vpc(graph):
    edges = _edge_kinds(graph)
    assert ("droplet__100", "member_of", "vpc__vpc-aaa") in edges
    assert ("droplet__101", "member_of", "vpc__vpc-aaa") in edges


def test_firewall_protects_droplets(graph):
    edges = _edge_kinds(graph)
    assert ("fw__fw-1", "protects", "droplet__100") in edges
    assert ("fw__fw-1", "protects", "droplet__101") in edges


def test_load_balancer_routes_to_droplets(graph):
    edges = _edge_kinds(graph)
    assert ("lb__lb-1", "routes_to", "droplet__100") in edges
    assert ("lb__lb-1", "routes_to", "droplet__101") in edges
    assert ("lb__lb-1", "member_of", "vpc__vpc-aaa") in edges


def test_reserved_ip_assigned_to_droplet(graph):
    edges = _edge_kinds(graph)
    assert ("rip__203.0.113.20", "assigned_to", "droplet__100") in edges


def test_volume_attached_to_droplet(graph):
    edges = _edge_kinds(graph)
    assert ("volume__vol-1", "attached_to", "droplet__100") in edges


def test_snapshot_of_droplet(graph):
    edges = _edge_kinds(graph)
    assert ("snapshot__snap-1", "snapshot_of", "droplet__100") in edges


def test_dns_a_record_resolves_to_droplet(graph):
    edges = _edge_kinds(graph)
    assert ("record__example.com__1", "resolves_to", "droplet__100") in edges


def test_dns_a_record_resolves_to_load_balancer(graph):
    edges = _edge_kinds(graph)
    assert ("record__example.com__2", "resolves_to", "lb__lb-1") in edges


def test_dns_cname_alias_edge(graph):
    edges = _edge_kinds(graph)
    # CNAME www -> example.com. should alias to the apex A record
    assert ("record__example.com__3", "alias_of", "record__example.com__1") in edges


def test_domain_owns_records(graph):
    edges = _edge_kinds(graph)
    assert ("domain__example.com", "has_record", "record__example.com__1") in edges


def test_node_count_matches_expectation(graph):
    types = {}
    for n in graph["nodes"]:
        t = n["data"]["type"]
        types[t] = types.get(t, 0) + 1
    assert types["droplet"] == 2
    assert types["db"] == 1
    assert types["vpc"] == 1
    assert types["firewall"] == 1
    assert types["lb"] == 1
    assert types["reserved_ip"] == 1
    assert types["volume"] == 1
    assert types["snapshot"] == 1
    assert types["domain"] == 1
    assert types["record"] == 3
