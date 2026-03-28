# 🔍 Port Scanner

A lightweight, multithreaded TCP/UDP port scanner written in Python — no external dependencies required.

> ⚠️ **Legal Notice:** Only scan systems you own or have explicit written permission to test. Unauthorized port scanning may be illegal in your jurisdiction.

---

## Features

- ✅ TCP & UDP scanning
- ✅ Multithreaded for fast scans
- ✅ Banner grabbing (HTTP)
- ✅ Common ports reference built-in
- ✅ Custom port ranges (e.g. `1-1024`, `80,443,8080`)
- ✅ Zero external dependencies (stdlib only)

---

## Requirements

- Python 3.10+

---

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/port-scanner.git
cd port-scanner
```

No `pip install` needed — pure standard library.

---

## Usage

```bash
python scanner.py <target> [options]
```

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `-p`, `--ports` | Port range or list (e.g. `1-1024`, `80,443`) | `1-1024` |
| `--protocol` | `tcp` or `udp` | `tcp` |
| `--timeout` | Seconds per connection attempt | `0.5` |
| `--threads` | Concurrent threads | `100` |
| `--common` | Scan only well-known ports | off |

---

## Examples

```bash
# Scan ports 1-1024 on a host (TCP)
python scanner.py 192.168.1.1

# Scan specific ports
python scanner.py example.com -p 22,80,443,8080,8443

# Scan all ports (slow — use high thread count)
python scanner.py 192.168.1.1 -p 1-65535 --threads 500

# Scan only common well-known ports
python scanner.py 192.168.1.1 --common

# UDP scan
python scanner.py 192.168.1.1 -p 53,123,161 --protocol udp

# Faster scan with aggressive timeout
python scanner.py 192.168.1.1 -p 1-1024 --threads 300 --timeout 0.3
```

---

## Sample Output

```
╔═══════════════════════════════════════╗
║         🔍  PORT SCANNER v1.0         ║
║   For authorized use on your own      ║
║   systems or with explicit permission ║
╚═══════════════════════════════════════╝

  [*] Scanning 1024 port(s) on 192.168.1.1 (192.168.1.1)
  [*] Protocol: TCP | Threads: 100 | Timeout: 0.5s

───────────────────────────────────────────────────────
  Scan report for 192.168.1.1 (192.168.1.1)
  Protocol : TCP
  Started  : 2026-03-28 12:00:00
───────────────────────────────────────────────────────
  PORT     STATE            SERVICE        BANNER
  ──────── ──────────────── ────────────── ──────────────
  22/tcp   open             SSH
  80/tcp   open             HTTP           HTTP/1.1 200 OK
  443/tcp  open             HTTPS
───────────────────────────────────────────────────────
  3 open port(s) found in 4.21s
```

---

## Project Structure

```
port-scanner/
├── scanner.py       # Main script
├── README.md        # This file
└── .gitignore
```

---

## Contributing

Pull requests are welcome! To contribute:

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m 'Add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

---

## License

MIT License — see [LICENSE](LICENSE) for details.
