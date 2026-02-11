# docker build -f report/remote_runner/Dockerfile -t remote-runner-server .
# mkdir -p remote_runner_data
# docker run --rm -p 8000:8000 -v "$(pwd)/remote_runner_data:/app/data" remote-runner-server
FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir flask==3.0.2

COPY report/remote_runner/server.py /app/server.py

VOLUME ["/app/data"]

ENV DB_PATH=/app/data/db.sqlite3

CMD ["python", "-u", "/app/server.py", "--host", "0.0.0.0", "--port", "8000"]
