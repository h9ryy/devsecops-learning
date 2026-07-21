FROM python:3.11-slim
RUN apt-get update && apt-get install -y git
WORKDIR /app
COPY audit.py net_audit.py ./
ENTRYPOINT [ "python" ]
CMD [ "audit.py" ]