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
            if not line.strip() or line.startswith("Netid"):
                continue
            
            columns = line.split()
            if len(columns) < 5:
                continue
            
            local_address = columns[4]
            for p in ports:
                if local_address.endswith(f":{p}"):
                    is_external = (
                        local_address.startswith("0.0.0.0:") or
                        local_address.startswith("[::]:") or 
                        local_address.startswith("*:")
                    )
                    if is_external:
                        sys.stdout.write(f"CRITICAL VULNERABILITY: Port {p} is exposed to the outside!\n")
                        sys.stdout.write(f"Details: {line.strip()}\n")
                        dangerous_found = True

    except subprocess.TimeoutExpired:
        sys.stderr.write("[-] Error: Network sockets command timeout.\n")
        sys.exit(1)
        
    return dangerous_found

has_vulnerabilities = run_network_audit(ports)

if has_vulnerabilities:
    sys.exit(1)
else:
    sys.stdout.write("No open ports found\n")
    sys.exit(0)
