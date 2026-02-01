"""Host discovery via ping sweep."""

import ipaddress
import platform
import subprocess
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed


def _ping_host(ip: str, timeout: int) -> str | None:
    """Ping a single host and return its IP if responsive, None otherwise."""
    system = platform.system().lower()
    if system == "windows":
        cmd = ["ping", "-n", "1", "-w", str(timeout * 1000), ip]
    else:
        cmd = ["ping", "-c", "1", "-W", str(timeout), ip]

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=timeout + 2,
        )
        if result.returncode == 0:
            return ip
    except subprocess.TimeoutExpired:
        pass
    except OSError:
        pass
    return None


def discover_hosts(
    cidr: str,
    timeout: int = 1,
    max_threads: int = 100,
    on_complete: Callable[[], None] | None = None,
) -> list[str]:
    """Discover active hosts on a subnet using a parallel ping sweep.

    Args:
        cidr: Subnet in CIDR notation (e.g. '192.168.1.0/24').
        timeout: Ping timeout in seconds (default 1).
        max_threads: Maximum number of concurrent ping threads (default 100).
        on_complete: Optional callback invoked after each host is checked.

    Returns:
        List of responsive IP addresses as strings.
    """
    network = ipaddress.IPv4Network(cidr, strict=False)
    # hosts() excludes network and broadcast addresses
    host_ips = [str(ip) for ip in network.hosts()]

    if not host_ips:
        return []

    active_hosts: list[str] = []

    with ThreadPoolExecutor(max_workers=min(max_threads, len(host_ips))) as executor:
        futures = {
            executor.submit(_ping_host, ip, timeout): ip for ip in host_ips
        }
        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                active_hosts.append(result)
            if on_complete is not None:
                on_complete()

    return active_hosts
