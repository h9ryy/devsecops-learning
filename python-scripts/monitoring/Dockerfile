FROM python:3.11-slim
RUN apt-get update && apt-get -y install netcat-openbsd
WORKDIR /app
COPY port_monitor.py .
ENTRYPOINT [ "python", "port_monitor.py" ]