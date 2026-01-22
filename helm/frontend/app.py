from flask import Flask, Response
import time
import random

from prometheus_client import (
    Counter,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST
)

app = Flask(__name__)

# ---- Metrics ----

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "path"],
    buckets=(0.1, 0.3, 0.5, 0.75, 1, 1.5, 2, 3, 5)
)

# ---- Routes ----

@app.route("/")
def home():
    start_time = time.time()

    # Simulate work
    time.sleep(random.uniform(0.05, 0.8))

    # Simulate occasional errors
    if random.random() < 0.1:
        status = "500"
        REQUEST_COUNT.labels("GET", "/", status).inc()
        REQUEST_LATENCY.labels("GET", "/").observe(time.time() - start_time)
        return "Internal Server Error\n", 500

    status = "200"
    REQUEST_COUNT.labels("GET", "/", status).inc()
    REQUEST_LATENCY.labels("GET", "/").observe(time.time() - start_time)

    return "Hello from frontend 👋\n"

@app.route("/health")
def health():
    REQUEST_COUNT.labels("GET", "/health", "200").inc()
    return "OK\n"

@app.route("/metrics")
def metrics():
    return Response(
        generate_latest(),
        mimetype=CONTENT_TYPE_LATEST
    )

# ---- Main ----

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
