FROM python:3.11-alpine
RUN apk add --no-cache tar
WORKDIR /app
COPY srv_backup.py .
ENTRYPOINT [ "python", "srv_backup.py" ]
