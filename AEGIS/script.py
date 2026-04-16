import json
import socket
import subprocess
from datetime import datetime


HOSTNAME = socket.gethostname()
TARGET_IP = "127.0.0.1"
PORTS_TO_CHECK = [22, 80, 443, 3306]


def check_port(ip: str, port: int, timeout: float = 1.0) -> str:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    result = sock.connect_ex((ip, port))
    sock.close()
    return "open" if result == 0 else "closed"


def get_active_services() -> list[str]:
    cmd = [
        "systemctl",
        "list-units",
        "--type=service",
        "--state=running",
        "--no-pager",
        "--no-legend",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    services = []

    for line in result.stdout.splitlines():
        parts = line.split()
        if parts:
            services.append(parts[0])

    return services


def main() -> None:
    report = {
        "hostname": HOSTNAME,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ports": {},
        "running_services": get_active_services(),
    }

    for port in PORTS_TO_CHECK:
        report["ports"][str(port)] = check_port(TARGET_IP, port)

    print("=== Rapport d'audit local ===")
    print(f"Machine : {report['hostname']}")
    print(f"Date    : {report['date']}")
    print("\nPorts vérifiés :")
    for port, status in report["ports"].items():
        print(f" - Port {port} : {status}")

    print("\nServices actifs :")
    for service in report["running_services"]:
        print(f" - {service}")

    with open("rapport_audit.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4, ensure_ascii=False)

    print("\nFichier exporté : rapport_audit.json")


if __name__ == "__main__":
    main()
