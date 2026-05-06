from app.do_client import DOClient


async def collect(client: DOClient) -> list[dict]:
    return await client.paginate("/v2/droplets", "droplets")
