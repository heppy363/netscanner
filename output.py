"""Formatted rich table output for scan results."""

import json
import socket
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.table import Table


# Services categorized by risk level for color coding
_GREEN_SERVICES = {"http", "https", "ssh", "HTTP", "HTTPS", "SSH"}
_RED_SERVICES = {"telnet", "ftp", "ftp-data", "Telnet", "FTP", "FTP-Data"}


def _service_color(service: str) -> str:
    """Return a rich color string based on service risk level."""
    lower = service.lower()
    if lower in {"http", "https", "ssh"}:
        return "green"
    if lower in {"telnet", "ftp", "ftp-data"}:
        return "red"
    return "yellow"


def _resolve_hostname(ip: str) -> str:
    """Resolve IP to hostname via reverse DNS."""
    try:
        return socket.getfqdn(ip)
    except (OSError, socket.herror):
        return ip


def print_results(
    scan_data: dict[str, dict[str, Any]],
    console: Console | None = None,
) -> None:
    """Print scan results as formatted rich tables.

    Args:
        scan_data: Dict mapping host IP to a dict with keys
            'cidr' (str) and 'open_ports' (list of dicts with 'port' and 'service').
        console: Optional Rich Console instance. Creates one if not provided.
    """
    if console is None:
        console = Console()

    if not scan_data:
        console.print("[yellow]No results collected.[/yellow]")
        return

    # Group hosts by subnet (CIDR)
    subnets: dict[str, list[str]] = {}
    for host_ip, data in sorted(scan_data.items()):
        cidr: str = data["cidr"]
        subnets.setdefault(cidr, []).append(host_ip)

    total_hosts = 0
    total_open = 0

    for cidr, hosts in subnets.items():
        console.print(f"\n[bold magenta]Subnet: {cidr}[/bold magenta]")
        console.print("─" * 50)

        # Summary table for this subnet
        summary_table = Table(title="Host Summary")
        summary_table.add_column("IP Address", style="cyan")
        summary_table.add_column("Hostname", style="blue")
        summary_table.add_column("Open Ports", style="green", justify="right")

        for host_ip in hosts:
            open_ports: list[dict[str, int | str]] = scan_data[host_ip]["open_ports"]
            hostname = _resolve_hostname(host_ip)
            summary_table.add_row(host_ip, hostname, str(len(open_ports)))

        console.print(summary_table)

        # Detailed table per host
        for host_ip in hosts:
            open_ports = scan_data[host_ip]["open_ports"]
            total_hosts += 1
            total_open += len(open_ports)

            if not open_ports:
                console.print(f"\n  [dim]{host_ip} — no open ports found[/dim]")
                continue

            hostname = _resolve_hostname(host_ip)
            detail_table = Table(title=f"{host_ip} ({hostname})")
            detail_table.add_column("Port", style="cyan", justify="right")
            detail_table.add_column("Protocol", style="blue")
            detail_table.add_column("Service", no_wrap=True)
            detail_table.add_column("State", style="green")

            for entry in open_ports:
                service_name = str(entry["service"])
                color = _service_color(service_name)
                detail_table.add_row(
                    str(entry["port"]),
                    "TCP",
                    f"[{color}]{service_name}[/{color}]",
                    "open",
                )

            console.print(detail_table)

    # Final summary line
    console.print(
        f"\n[bold]Total: {total_hosts} host(s) scanned, "
        f"{total_open} open port(s) found.[/bold]"
    )


def export_json(
    scan_data: dict[str, dict[str, Any]],
    filepath: str,
    *,
    duration: float = 0.0,
    port_range: str = "1-49151",
) -> None:
    """Export scan results to a JSON file.

    Args:
        scan_data: Dict mapping host IP to a dict with keys
            'cidr' (str) and 'open_ports' (list of dicts with 'port' and 'service').
        filepath: Path to the output JSON file.
        duration: Scan duration in seconds.
        port_range: Port range that was scanned.
    """
    # Group hosts by subnet
    subnets_set: set[str] = set()
    hosts_output: list[dict[str, Any]] = []

    for host_ip, data in sorted(scan_data.items()):
        subnets_set.add(data["cidr"])
        hostname = _resolve_hostname(host_ip)
        hosts_output.append({
            "ip": host_ip,
            "hostname": hostname,
            "open_ports": [
                {"port": entry["port"], "service": entry["service"]}
                for entry in data["open_ports"]
            ],
        })

    output = {
        "scan_metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "duration_seconds": round(duration, 2),
            "port_range": port_range,
        },
        "subnets_scanned": sorted(subnets_set),
        "hosts": hosts_output,
    }

    Path(filepath).write_text(json.dumps(output, indent=2), encoding="utf-8")
