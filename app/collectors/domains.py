import asyncio

from app.do_client import DOClient


async def collect(client: DOClient) -> list[dict]:
    domains = await client.paginate("/v2/domains", "domains")
    if not domains:
        return []

    async def fetch_records(domain_name: str) -> list[dict]:
        records = await client.paginate(
            f"/v2/domains/{domain_name}/records", "domain_records"
        )
        for r in records:
            r["_domain"] = domain_name
        return records

    record_lists = await asyncio.gather(
        *(fetch_records(d["name"]) for d in domains)
    )
    for d, records in zip(domains, record_lists):
        d["_records"] = records
    return domains
