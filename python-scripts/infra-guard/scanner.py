import argparse
import os
import sys
import yaml
import socket
import paramiko
from concurrent.futures import ThreadPoolExecutor

parser = argparse.ArgumentParser(description="Автоматизированный сканер периметра и аудитор безопасности инфраструктуры")
parser.add_argument("--config", type=str, help="Путь к файлу конфигурации (config.json)")
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
    
    ssh_user = os.getenv("SSH_USERNAME", "infra_guard_svc")
    ssh_password = os.getenv("SSH_PRIVATE_KEY", "secret_pass")
    try:
        client.connect(hostname=host, username=ssh_user, port=port, password=ssh_password, timeout=5)
        stdin, stdout, stderr = client.exec_command("stat -c '%a' /etc/myapp/config.yaml 2>/dev/null || echo 'NOT_FOUND'; ss -ltupn")
        
        output = stdout.read().decode("utf-8")
        errors = stderr.read().decode("utf-8")
        return {"host": host, "output": output, "errors": errors}
    except paramiko.AuthenticationException:
        sys.stderr.write(f"Авторизация не удалась! Проверьте имя пользователя или пароль.")
    except Exception as e:
        sys.stderr.write(f"[-] Ошибка подключения к {host}: {e}\n")
    finally:
        client.close()
    return None

for host, port in result:
    if port == 22:
        report = connect_ssh(host, port)
        if report:
            lines = report["output"].splitlines()
            permissions = lines[0] if lines else "unknown"
            
            print(f" Результаты аудита для {host}:")
            if permissions == "NOT_FOUND":
                print("[-] Предупреждение: Конфигурационный файл /etc/myapp/config.yaml не найден.")
            elif permissions != "640":
                print(f"Небезопасные права на конфиг: {permissions} (Ожидалось 640!)")
            else:
                print("Права на конфигурационный файл в порядке (640).")
                    
            if ":8080" in report["output"] or "8080" in report["output"]:
                print("На сервере обнаружен запущенный процесс на порту 8080!")
            else:
                print("Опасных открытых портов внутри системы не обнаружено.")