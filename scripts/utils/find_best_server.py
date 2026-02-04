import asyncio
import logging
import time
from typing import Any, Dict, List

import aiohttp
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


async def measure_latency(session: aiohttp.ClientSession, url: str) -> float:
    """
    Measures the latency of a given URL by making a GET request.

    Args:
        session (aiohttp.ClientSession): The aiohttp client session.
        url (str): The URL to measure latency for.

    Returns:
        float: The latency in seconds, or float('inf') if the request fails.
    """
    try:
        start_time = time.monotonic()
        async with session.get(url, timeout=5) as response:
            await response.text()
            end_time = time.monotonic()
            latency = end_time - start_time
            logging.info(
                f"Successfully connected to {url} with latency: {latency:.4f}s"
            )
            return latency
    except Exception as e:
        logging.warning(f"Failed to connect to {url}: {e}")
        return float("inf")


async def find_best_server(servers: List[str]) -> str:
    """
    Finds the best server from a list by measuring latency.

    Args:
        servers (List[str]): A list of server URLs.

    Returns:
        str: The URL of the server with the lowest latency, or an empty string if none are reachable.
    """
    async with aiohttp.ClientSession() as session:
        tasks = [measure_latency(session, server) for server in servers]
        latencies = await asyncio.gather(*tasks)

    server_latencies = {servers[i]: latencies[i] for i in range(len(servers))}

    # Filter out unreachable servers
    reachable_servers = {s: l for s, l in server_latencies.items() if l != float("inf")}

    if not reachable_servers:
        logging.error("No reachable servers found.")
        return ""

    # Find the server with the minimum latency
    best_server = min(reachable_servers, key=reachable_servers.get)
    min_latency = reachable_servers[best_server]
    logging.info(
        f"The best server is {best_server} with a latency of {min_latency:.4f}s"
    )

    return best_server


async def main():
    """
    Main function to run the server latency test.
    """
    # Expanded list of potential server URLs
    server_urls = [
        "http://www.fxcorporate.com/Hosts.jsp",
        "https://www.fxcorporate.com/Hosts.jsp",
        "http://www.fxcm.com/Hosts.jsp",
        "https://www.fxcm.com/Hosts.jsp",
        "http://www.fxcm.co.uk/Hosts.jsp",
        "https://www.fxcm.co.uk/Hosts.jsp",
        "http://www.fxcm.com.au/Hosts.jsp",
        "https://www.fxcm.com.au/Hosts.jsp",
        "http://www.fxcm.fr/Hosts.jsp",
        "https://www.fxcm.fr/Hosts.jsp",
        "http://www.fxcm.de/Hosts.jsp",
        "https://www.fxcm.de/Hosts.jsp",
        "http://www.fxcm.it/Hosts.jsp",
        "https://www.fxcm.it/Hosts.jsp",
        "http://www.fxcm.gr/Hosts.jsp",
        "https://www.fxcm.gr/Hosts.jsp",
        "http://www.fxcm.jp/Hosts.jsp",
        "https://www.fxcm.jp/Hosts.jsp",
    ]

    best_server = await find_best_server(server_urls)

    if best_server:
        print(f"\nBest server for ForexConnect API: {best_server}")
    else:
        print("\nCould not determine the best server for ForexConnect API.")


if __name__ == "__main__":
    asyncio.run(main())
