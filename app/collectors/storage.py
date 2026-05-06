import asyncio

from app.do_client import DOClient


async def collect_volumes(client: DOClient) -> list[dict]:
    return await client.paginate("/v2/volumes", "volumes")


async def collect_snapshots(client: DOClient) -> list[dict]:
    return await client.paginate("/v2/snapshots", "snapshots")


async def collect(client: DOClient) -> dict[str, list[dict]]:
    volumes, snapshots = await asyncio.gather(
        collect_volumes(client),
        collect_snapshots(client),
    )
    return {"volumes": volumes, "snapshots": snapshots}
