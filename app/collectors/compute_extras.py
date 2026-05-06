import asyncio

from app.do_client import DOAPIError, DOClient


async def collect_kubernetes(client: DOClient) -> list[dict]:
    return await client.paginate("/v2/kubernetes/clusters", "kubernetes_clusters")


async def collect_apps(client: DOClient) -> list[dict]:
    return await client.paginate("/v2/apps", "apps")


async def collect_functions(client: DOClient) -> list[dict]:
    data = await client.get("/v2/functions/namespaces")
    return data.get("namespaces", []) or []


async def collect_registry(client: DOClient) -> dict | None:
    try:
        data = await client.get("/v2/registry")
    except DOAPIError as e:
        # 404 when no registry exists for the account
        if e.status_code == 404:
            return None
        raise
    return data.get("registry")


async def collect(client: DOClient) -> dict:
    k8s, apps, functions, registry = await asyncio.gather(
        collect_kubernetes(client),
        collect_apps(client),
        collect_functions(client),
        collect_registry(client),
    )
    return {
        "kubernetes_clusters": k8s,
        "apps": apps,
        "functions_namespaces": functions,
        "registry": registry,
    }
