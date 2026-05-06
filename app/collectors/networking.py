import asyncio

from app.do_client import DOClient


async def collect_vpcs(client: DOClient) -> list[dict]:
    return await client.paginate("/v2/vpcs", "vpcs")


async def collect_firewalls(client: DOClient) -> list[dict]:
    return await client.paginate("/v2/firewalls", "firewalls")


async def collect_load_balancers(client: DOClient) -> list[dict]:
    return await client.paginate("/v2/load_balancers", "load_balancers")


async def collect_reserved_ips(client: DOClient) -> list[dict]:
    return await client.paginate("/v2/reserved_ips", "reserved_ips")


async def collect(client: DOClient) -> dict[str, list[dict]]:
    vpcs, firewalls, lbs, reserved_ips = await asyncio.gather(
        collect_vpcs(client),
        collect_firewalls(client),
        collect_load_balancers(client),
        collect_reserved_ips(client),
    )
    return {
        "vpcs": vpcs,
        "firewalls": firewalls,
        "load_balancers": lbs,
        "reserved_ips": reserved_ips,
    }
