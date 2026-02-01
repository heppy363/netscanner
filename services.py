import socket

COMMON_PORTS: dict[int, str] = {
    20: "FTP-Data",
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    67: "DHCP",
    68: "DHCP",
    69: "TFTP",
    80: "HTTP",
    110: "POP3",
    111: "RPCbind",
    119: "NNTP",
    123: "NTP",
    135: "MSRPC",
    137: "NetBIOS-NS",
    138: "NetBIOS-DGM",
    139: "NetBIOS-SSN",
    143: "IMAP",
    161: "SNMP",
    162: "SNMP-Trap",
    389: "LDAP",
    443: "HTTPS",
    445: "Microsoft-DS",
    465: "SMTPS",
    514: "Syslog",
    587: "SMTP-Submission",
    636: "LDAPS",
    993: "IMAPS",
    995: "POP3S",
    1080: "SOCKS",
    1433: "MSSQL",
    1521: "Oracle-DB",
    1723: "PPTP",
    2049: "NFS",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    5672: "AMQP",
    5900: "VNC",
    6379: "Redis",
    8080: "HTTP-Proxy",
    8443: "HTTPS-Alt",
    9090: "WebSM",
    9200: "Elasticsearch",
    27017: "MongoDB",
}


def get_service_name(port: int) -> str:
    """Look up the service name for a given port number.

    Uses socket.getservbyport() as primary lookup, falls back to
    a built-in dictionary for common ports, and returns 'unknown'
    for unrecognized ports.
    """
    try:
        return socket.getservbyport(port, "tcp")
    except OSError:
        return COMMON_PORTS.get(port, "unknown")
