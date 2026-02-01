"""NetScanner CLI entry point."""

import ipaddress
import signal
import time
from types import FrameType
from typing import Any, Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TaskID
from rich.table import Table

from netscanner.discovery import discover_hosts
from netscanner.network import get_interfaces
from netscanner.output import export_json, print_results
from netscanner.scanner import scan_host

app = typer.Typer(help="NetScanner - Network Port Scanner CLI")
console = Console()


def _parse_port_range(ports: str) -> tuple[int, int]:
    """Parse a port range string like '1-1024' into a (start, end) tuple."""
    parts = ports.split("-")
    if len(parts) != 2:
        raise typer.BadParameter(f"Invalid port range '{ports}'. Use format 'start-end'.")
    try:
        start, end = int(parts[0]), int(parts[1])
    except ValueError:
        raise typer.BadParameter(f"Invalid port range '{ports}'. Ports must be integers.")
    if not (1 <= start <= end <= 65535):
        raise typer.BadParameter(f"Invalid port range '{ports}'. Must satisfy 1 <= start <= end <= 65535.")
    return start, end


@app.command()
def scan(
    ports: str = typer.Option("1-49151", help="Port range to scan (e.g. '1-1024')"),
    threads: int = typer.Option(100, help="Number of threads for scanning"),
    timeout: float = typer.Option(0.5, help="Connection timeout in seconds"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Export results to JSON file"),
) -> None:
    """Scan network interfaces for open ports."""
    port_range = _parse_port_range(ports)
    start_time = time.monotonic()

    # Collect partial results for Ctrl+C handling
    results: dict[str, dict[str, Any]] = {}
    interrupted = False

    def handle_interrupt(signum: int, frame: FrameType | None) -> None:
        nonlocal interrupted
        interrupted = True
        console.print("\n[yellow]Interrupted! Printing partial results...[/yellow]")

    signal.signal(signal.SIGINT, handle_interrupt)

    # Step 1: Detect interfaces
    console.print("[bold cyan]Detecting network interfaces...[/bold cyan]")
    interfaces = get_interfaces()

    if not interfaces:
        console.print("[yellow]No network interfaces found.[/yellow]")
        return

    for iface in interfaces:
        console.print(f"  Found: {iface['name']} - {iface['ip']} ({iface['cidr']})")

    # Step 2: Discover hosts per subnet
    console.print("\n[bold cyan]Discovering active hosts...[/bold cyan]")
    all_hosts: dict[str, list[str]] = {}

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        console=console,
    ) as progress:
        for iface in interfaces:
            if interrupted:
                break
            cidr = iface["cidr"]
            network = ipaddress.IPv4Network(cidr, strict=False)
            total_hosts = network.num_addresses - 2
            if total_hosts <= 0:
                continue

            task_id: TaskID = progress.add_task(
                f"Pinging {cidr}", total=total_hosts
            )

            def _make_discovery_cb(tid: TaskID) -> Any:
                def cb() -> None:
                    progress.advance(tid)
                return cb

            hosts = discover_hosts(
                cidr,
                timeout=1,
                max_threads=threads,
                on_complete=_make_discovery_cb(task_id),
            )
            if hosts:
                all_hosts[cidr] = hosts

    if not all_hosts:
        console.print("[yellow]No active hosts found on any subnet.[/yellow]")
        return

    total_found = sum(len(h) for h in all_hosts.values())
    console.print(f"\n[green]Found {total_found} active host(s).[/green]")

    # Step 3: Scan ports on each discovered host
    console.print("\n[bold cyan]Scanning ports...[/bold cyan]")
    port_start, port_end = port_range
    total_ports = port_end - port_start + 1

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        console=console,
    ) as progress:
        for cidr, hosts in all_hosts.items():
            if interrupted:
                break
            for host_ip in hosts:
                if interrupted:
                    break

                task_id = progress.add_task(
                    f"Scanning {host_ip}", total=total_ports
                )

                def _make_scan_cb(tid: TaskID) -> Any:
                    def cb() -> None:
                        progress.advance(tid)
                    return cb

                open_ports = scan_host(
                    host_ip,
                    port_range=port_range,
                    timeout=timeout,
                    max_threads=threads,
                    on_complete=_make_scan_cb(task_id),
                )

                results[host_ip] = {
                    "cidr": cidr,
                    "open_ports": open_ports,
                }

    # Print results
    console.print("\n[bold cyan]Scan Results[/bold cyan]")
    console.print("=" * 50)

    print_results(results, console=console)

    if output is not None:
        duration = time.monotonic() - start_time
        export_json(results, output, duration=duration, port_range=ports)
        console.print(f"\n[green]Results exported to {output}[/green]")


@app.command()
def info() -> None:
    """Display detected network interfaces and subnets."""
    interfaces = get_interfaces()

    if not interfaces:
        console.print("[yellow]No network interfaces found.[/yellow]")
        return

    table = Table(title="Network Interfaces")
    table.add_column("Interface", style="cyan")
    table.add_column("IP Address", style="green")
    table.add_column("Netmask", style="yellow")
    table.add_column("Subnet (CIDR)", style="magenta")

    for iface in interfaces:
        table.add_row(iface["name"], iface["ip"], iface["netmask"], iface["cidr"])

    console.print(table)


if __name__ == "__main__":
    app()
