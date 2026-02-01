"""Network interface and subnet detection."""

import ipaddress
import socket
from typing import TypedDict

import psutil


class InterfaceInfo(TypedDict):
    name: str
    ip: str
    netmask: str
    cidr: str


def get_interfaces() -> list[InterfaceInfo]:
    """Detect all active network interfaces with their subnets.

    Uses psutil to enumerate network interfaces, extracts IPv4 addresses
    and subnet masks, calculates CIDR notation, and filters out loopback
    and link-local addresses.

    Returns:
        List of dicts with keys: name, ip, netmask, cidr
    """
    interfaces: list[InterfaceInfo] = []
    addrs = psutil.net_if_addrs()

    for iface_name, addr_list in addrs.items():
        for addr in addr_list:
            if addr.family != socket.AF_INET:
                continue

            ip_str = addr.address
            netmask_str = addr.netmask

            if ip_str is None or netmask_str is None:
                continue

            ip_obj = ipaddress.ip_address(ip_str)

            # Exclude loopback
            if ip_obj.is_loopback:
                continue

            # Exclude link-local (169.254.x.x)
            if ip_obj.is_link_local:
                continue

            # Calculate CIDR notation for the subnet
            network = ipaddress.IPv4Network(
                f"{ip_str}/{netmask_str}", strict=False
            )

            interfaces.append(
                InterfaceInfo(
                    name=iface_name,
                    ip=ip_str,
                    netmask=netmask_str,
                    cidr=str(network),
                )
            )

    return interfaces
