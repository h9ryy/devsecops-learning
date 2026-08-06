import argparse
import os
import sys
import subprocess
import time

parser = argparse.ArgumentParser(description="Configuration backup")
parser.add_argument("-d", "--dir", type=str, required=True, help="Path to configuration")
args = parser.parse_args()

if not os.path.exists(args.dir):
    print("The script could not find the configuration folder.", file=sys.stderr)
    sys.exit(1)

try:
    backup_name = f"backup{int(time.time())}.tar.gz"
    command = ["tar", "-czf", backup_name, args.dir]
    
    sub_run = subprocess.run(command, capture_output=True, text=True, timeout=60)
    if sub_run.returncode == 0:
        print(f"[OK] Backup of '{args.dir}' created successfully as {backup_name}.")
        sys.exit(0)
    else:
        print(f"[ERROR] Tar command failed with exit code {sub_run.returncode}. Details: {sub_run.stderr}",file=sys.stderr,)
        sys.exit(1)
except subprocess.TimeoutExpired:
    print(f"[ERROR] Backup process timed out after 60 seconds.", file=sys.stderr)
    sys.exit(1)