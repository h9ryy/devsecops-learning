import subprocess
import sys
import argparse

parser = argparse.ArgumentParser(description="Open port scanner")
parser.add_argument("-p", "--ports", type=str, default="3306,5432,22", help="Ports separated by commas")
args = parser.parse_args()

ports = [port.strip() for port in args.ports.split(",")]

def run_network_audit(ports):
    try:
        sub_run = subprocess.run(["ss", "-tulpn"], capture_output=True, text=True, timeout=5)
        dangerous_found = False
        
        for line in sub_run.stdout.split("\n"):
            for p in ports:
                if f":{p}" in line and ("0.0.0.0" in line or "[::]" in line):
                    sys.stdout.write(f"🚨 CRITICAL VULNERABILITY: Port {line} is exposed to the outside!\n")
                    dangerous_found = True

    except subprocess.TimeoutExpired:
        sys.stderr.write("[-] Error: Network sockets command timeout.\n")
        sys.exit(1)
        
    return dangerous_found

has_vulnerabilities = run_network_audit(ports)

if has_vulnerabilities:
    sys.exit(1)
else:
    sys.stdout.write("✅ No open ports found\n")
    sys.exit(0)
