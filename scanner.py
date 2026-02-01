"""Multi-threaded TCP port scanner."""

import socket
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

from netscanner.services import get_service_name


def _scan_port(ip: str, port: int, timeout: float) -> dict[str, int | str] | None:
    """Attempt a TCP connect to a single port.

    Returns a dict with port and service name if open, None otherwise.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        result = sock.connect_ex((ip, port))
        if result == 0:
            return {"port": port, "service": get_service_name(port)}
    except (OSError, socket.timeout):
        pass
    finally:
        sock.close()
    return None


def scan_host(
    ip: str,
    port_range: tuple[int, int] = (1, 49151),
    timeout: float = 0.5,
    max_threads: int = 100,
    on_complete: Callable[[], None] | None = None,
) -> list[dict[str, int | str]]:
    """Scan a host for open TCP ports using multiple threads.

    Args:
        ip: Target IP address.
        port_range: Tuple of (start_port, end_port) inclusive.
        timeout: Connection timeout in seconds (default 0.5).
        max_threads: Thread pool size (default 100).
        on_complete: Optional callback invoked after each port is checked.

    Returns:
        List of dicts with keys 'port' (int) and 'service' (str)
        for each open port found, sorted by port number.
    """
    start_port, end_port = port_range
    ports = range(start_port, end_port + 1)

    open_ports: list[dict[str, int | str]] = []

    with ThreadPoolExecutor(max_workers=min(max_threads, len(ports))) as executor:
        futures = {
            executor.submit(_scan_port, ip, port, timeout): port for port in ports
        }
        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                open_ports.append(result)
            if on_complete is not None:
                on_complete()

    open_ports.sort(key=lambda x: x["port"])
    return open_ports
