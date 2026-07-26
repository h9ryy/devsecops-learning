FROM python:3.11-slim
RUN groupadd -r scanner && useradd -r -g scanner scanner
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY scanner.py .
RUN chown -R scanner:scanner /app
USER scanner
ENTRYPOINT ["python", "scanner.py"]
