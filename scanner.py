#!/usr/bin/env python3
"""
Port Scanner - A lightweight TCP/UDP port scanning tool.
Usage: python scanner.py <target> [options]
"""

import socket
import argparse
import ipaddress
import concurrent.futures
import sys
from datetime import datetime

# ──────────────────────────────────────────────
# Common ports reference
# ──────────────────────────────────────────────
COMMON_PORTS = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
    53: "DNS", 80: "HTTP", 110: "POP3", 143: "IMAP",
    443: "HTTPS", 445: "SMB", 3306: "MySQL", 3389: "RDP",
    5432: "PostgreSQL", 5900: "VNC", 6379: "Redis",
    8080: "HTTP-Alt", 8443: "HTTPS-Alt", 27017: "MongoDB",
}


def resolve_target(target: str) -> str:
    """Resolve hostname to IP address."""
    try:
        return socket.gethostbyname(target)
    except socket.gaierror:
        print(f"[ERROR] Could not resolve host: {target}")
        sys.exit(1)


def scan_tcp_port(ip: str, port: int, timeout: float) -> dict | None:
    """Attempt a TCP connection to a single port."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            result = s.connect_ex((ip, port))
            if result == 0:
                service = COMMON_PORTS.get(port, "Unknown")
                # Try banner grab
                banner = ""
                try:
                    s.send(b"HEAD / HTTP/1.0\r\n\r\n")
                    banner = s.recv(1024).decode("utf-8", errors="ignore").strip()
                except Exception:
                    pass
                return {"port": port, "state": "open", "service": service, "banner": banner[:60]}
    except (socket.timeout, ConnectionRefusedError, OSError):
        pass
    return None


def scan_udp_port(ip: str, port: int, timeout: float) -> dict | None:
    """Attempt a UDP probe on a single port."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(timeout)
            s.sendto(b"\x00", (ip, port))
            s.recvfrom(1024)
            service = COMMON_PORTS.get(port, "Unknown")
            return {"port": port, "state": "open|filtered", "service": service, "banner": ""}
    except socket.timeout:
        return {"port": port, "state": "open|filtered", "service": COMMON_PORTS.get(port, "Unknown"), "banner": ""}
    except Exception:
        pass
    return None


def scan_ports(ip: str, ports: list[int], protocol: str, timeout: float, threads: int) -> list[dict]:
    """Scan a list of ports using a thread pool."""
    results = []
    scan_fn = scan_tcp_port if protocol == "tcp" else scan_udp_port

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(scan_fn, ip, port, timeout): port for port in ports}
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                results.append(result)

    return sorted(results, key=lambda x: x["port"])


def parse_ports(port_str: str) -> list[int]:
    """Parse port specification like '80,443,1-1024'."""
    ports = set()
    for part in port_str.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-")
            ports.update(range(int(start), int(end) + 1))
        else:
            ports.add(int(part))
    return sorted(ports)


def print_banner():
    print("""
╔═══════════════════════════════════════╗
║         🔍  PORT SCANNER v1.0         ║
║   For authorized use on your own      ║
║   systems or with explicit permission ║
╚═══════════════════════════════════════╝
""")


def print_results(target: str, ip: str, results: list[dict], protocol: str, start_time: datetime):
    elapsed = (datetime.now() - start_time).total_seconds()
    print(f"\n{'─'*55}")
    print(f"  Scan report for {target} ({ip})")
    print(f"  Protocol : {protocol.upper()}")
    print(f"  Started  : {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'─'*55}")
    if results:
        print(f"  {'PORT':<8} {'STATE':<16} {'SERVICE':<14} BANNER")
        print(f"  {'─'*8} {'─'*16} {'─'*14} {'─'*14}")
        for r in results:
            banner_preview = f"  {r['banner'][:40]}" if r["banner"] else ""
            print(f"  {str(r['port'])+'/'+ protocol:<8} {r['state']:<16} {r['service']:<14}{banner_preview}")
    else:
        print("  No open ports found.")
    print(f"{'─'*55}")
    print(f"  {len(results)} open port(s) found in {elapsed:.2f}s\n")


def main():
    print_banner()

    parser = argparse.ArgumentParser(
        description="Simple Python port scanner",
        epilog="Example: python scanner.py 192.168.1.1 -p 1-1024 --threads 200"
    )
    parser.add_argument("target", help="Target IP address or hostname")
    parser.add_argument("-p", "--ports", default="1-1024",
                        help="Ports to scan (default: 1-1024). Examples: 80,443  |  22-443  |  1-65535")
    parser.add_argument("--protocol", choices=["tcp", "udp"], default="tcp",
                        help="Protocol to use (default: tcp)")
    parser.add_argument("--timeout", type=float, default=0.5,
                        help="Connection timeout in seconds (default: 0.5)")
    parser.add_argument("--threads", type=int, default=100,
                        help="Number of concurrent threads (default: 100)")
    parser.add_argument("--common", action="store_true",
                        help="Scan only common ports (overrides -p)")

    args = parser.parse_args()

    # Resolve target
    ip = resolve_target(args.target)

    # Determine port list
    if args.common:
        ports = list(COMMON_PORTS.keys())
        print(f"  [*] Scanning {len(ports)} common ports on {args.target} ({ip})")
    else:
        ports = parse_ports(args.ports)
        print(f"  [*] Scanning {len(ports)} port(s) on {args.target} ({ip})")

    print(f"  [*] Protocol: {args.protocol.upper()} | Threads: {args.threads} | Timeout: {args.timeout}s\n")

    start_time = datetime.now()
    results = scan_ports(ip, ports, args.protocol, args.timeout, args.threads)
    print_results(args.target, ip, results, args.protocol, start_time)


if __name__ == "__main__":
    main()
