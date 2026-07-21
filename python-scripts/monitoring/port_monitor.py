import argparse
import sys
import json
import os
import subprocess

parser = argparse.ArgumentParser(description="Utility for network port availability.")
parser.add_argument("-f", "--file", type=str, required=True, help="Path to the source file with ports")
parser.add_argument("--host", type=str, required=True, help="Target host to check (IP address or domain name, e.g., 127.0.0.1 or example.com)")
args = parser.parse_args()

if not os.path.exists(args.file):
    sys.stderr.write(f"The file {args.file} does not exist!\n")
    sys.exit(1)
    
try:
    with open(args.file, "r", encoding="utf-8") as f:
        ports = [port.strip() for port in f.read().splitlines() if port.strip()]
        
        result = []
        for port in ports:
            sub_run = subprocess.run(["nc", "-zv", "-w", "2", args.host, port], capture_output=True, text=True)
            
            status = "DOWN"
            raw_output = sub_run.stderr + sub_run.stdout
            details = raw_output.strip() if raw_output.strip() else "No output from nc"
            
            if sub_run.returncode == 0:
                status = "UP"
            
            port_data = {
                "port": port,
                "status": status,
                "details": details
            }
            result.append(port_data)
        report = {
            "host": args.host,
            "results": result
        }
        sys.stdout.write(json.dumps(report, indent=4))
        
        all_statuses = [res["status"] for res in result]
        if "DOWN" in all_statuses:
            sys.exit(1)
        else:
            sys.exit(0)
except OSError as e:
    sys.stderr.write(f"Ошибка при работе с файлом: {e.strerror} (код {e.errno})\n")
    sys.exit(1)