import argparse
import subprocess
import io
import re
import sys

parser = argparse.ArgumentParser(
    description="A script for searching patterns in a local repository."
)
parser.add_argument("--repo", type=str, help="Path to local repository")
parser.add_argument(
    "-s",
    "--search",
    type=str,
    required=True,
    help="String or regular expression to search for",
)
args = parser.parse_args()

try:
    sub_run = subprocess.run(
        ["git", "log", "-p"], cwd=args.repo, capture_output=True, text=True, timeout=3
    )
    if sub_run.returncode != 0:
        sys.stderr.write(sub_run.stderr)
        sys.exit(1)

    found_secrets = False
    pattern = re.compile(args.search, re.IGNORECASE)
    if sub_run.returncode == 0:
        sub_text = io.StringIO(sub_run.stdout)
        for line in sub_text:
            if line.startswith("+") or line.startswith("-"):
                match = pattern.search(line)
                if match:
                    sys.stdout.write(f"[!]A vulnerability has been discovered: {line}")
                    found_secrets = True
    if not found_secrets:
        sys.stdout.write("No vulnerabilities found")
        sys.exit(0)
    else:
        sys.exit(1)

except subprocess.TimeoutExpired:
    sys.stderr.write("[-]Error: file response timeout")
    sys.exit(1)
