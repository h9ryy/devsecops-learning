import argparse
import os
import sys
import json
import io
import yaml
import socket
import paramiko
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

parser = argparse.ArgumentParser(description="Автоматизированный сканер периметра и аудитор безопасности инфраструктуры")
parser.add_argument("--config", type=str, help="Путь к файлу конфигурации (config.json)")
parser.add_argument("--output-dir", type=str, help="Путь к директории для сохранения отчетов")
args = parser.parse_args()

if not args.config:
    sys.stderr.write("Ошибка: Не указан путь к файлу конфигурации.\n")
    sys.exit(1)

if not os.path.exists(args.config):
    sys.stderr.write(f"Ошибка: Файл '{args.config}' не найден!\n")
    sys.exit(1)
    
try:
    with open(args.config, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)
        
        targets = config_data.get("targets", [])
        ports = config_data.get("ports", [])
        print(f"[+] Найдено целей: {len(targets)}, и {len(ports)} портов")
        
except OSError as e:
    sys.stderr.write(f"Ошибка ввода-вывода при работе с файлом: {e}\n")
    sys.exit(1)
    
def check_port(target, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            
            connect = s.connect_ex((target, port))
            if connect == 0:
                print(f"[!] ОБНАРУЖЕН: {target}:{port} ОТКРЫТ")
                return (target, port)
    except Exception as e:
        sys.stderr.write(f"Произошла ошибка детали: {e}\n")
        return None

result = []
with ThreadPoolExecutor(max_workers=15) as executor:
    futures = []
    for target in targets:
        for port in ports:
            futures.append(executor.submit(check_port, target, port))        
    
    for future in futures:
        res = future.result()
        if res:
            result.append(res)

def connect_ssh(host, port):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    ssh_user = os.getenv("SSH_USERNAME", "ubuntu")
    ssh_key_env = os.getenv("SSH_PRIVATE_KEY")
    try:
        private_key = paramiko.Ed25519Key.from_private_key(io.StringIO(ssh_key_env.replace("\\n", "\n")))

        client.connect(hostname=host, username=ssh_user, port=port, pkey=private_key, timeout=5)
        stdin, stdout, stderr = client.exec_command("stat -c '%a' /etc/myapp/config.yaml 2>/dev/null || echo 'NOT_FOUND'; ss -ltupn")
        
        output = stdout.read().decode("utf-8")
        errors = stderr.read().decode("utf-8")
        return {"host": host, "output": output, "errors": errors}
    except paramiko.AuthenticationException as auth_ex:
        sys.stderr.write(f"[-] Ошибка авторизации на {host}: {auth_ex}. Проверь формат ключа!\n")
    except Exception as e:
        sys.stderr.write(f"[-] Ошибка подключения к {host}: {e}\n")
    finally:
        client.close()
    return None

final_report = {
    "scan_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "hosts_audited": {}
}

for host, port in result:
    if port == 22:
        report = connect_ssh(host, port)
        if report:
            lines = report["output"].splitlines()
            permissions = lines[0] if lines else "unknown"
            
            print(f" Результаты аудита для {host}:")
            
            host_data = {
                "ssh_port_open": True,
                "config_permissions": permissions,
                "config_status": "OK",
                "dangerous_port_8080": False
            }
            
            if permissions == "NOT_FOUND":
                host_data["config_status"] = "NOT_FOUND"
            elif permissions != "640":
                host_data["config_status"] = f"INSECURE: {permissions} (Ожидалось 640!)"
            else:
                host_data["config_status"] = "OK: Права 640"
                
            if ":8080" in report["output"] or "8080" in report["output"]:
                host_data["dangerous_port_8080"] = True
            else:
                host_data["dangerous_port_8080"] = False
                
            final_report["hosts_audited"][host] = host_data

if args.output_dir:
    os.makedirs(args.output_dir, exist_ok=True)
    
    current_date = datetime.now().strftime("%Y-%m-%d")
    filename = f"report_{current_date}.json"
    
    full_path = os.path.join(args.output_dir, filename)
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(final_report, f, indent=4, ensure_ascii=False)
    print(f"[+] Отчет сохранен: {full_path}")
else:
    print(json.dumps(final_report, indent=4, ensure_ascii=False))