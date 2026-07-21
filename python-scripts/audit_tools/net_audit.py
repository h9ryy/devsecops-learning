import socket
import sys
import argparse

parser = argparse.ArgumentParser(description="Open port scanner")
parser.add_argument("-t", "--target", type=str, default="localhost", help="Target host to scan")
parser.add_argument("-p", "--ports", type=str, default="3306,5432,22", help="Ports separated by commas")
args = parser.parse_args()

ports = [int(port.strip()) for port in args.ports.split(",")]
target_host = args.target
def scan_ports(host, ports):
    dangerous_found = False
    for port in ports:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                
                connect = s.connect_ex((host, port))
                if connect == 0:
                    sys.stdout.write(f"ALERT: Port {port} is OPEN on {host}!\n")
                    dangerous_found = True
                else:
                    sys.stdout.write(f"Port {port} is closed.\n")
        except Exception as e:
            sys.stderr.write(f"Error: Connection failed on port {port}. Details: {e}\n")
            continue 
        
    return dangerous_found

has_vulnerabilities = scan_ports(target_host, ports)

if has_vulnerabilities:
    sys.exit(1)
else:
    sys.stdout.write("[SUCCESS] No dangerous open ports discovered.\n")
    sys.exit(0)
