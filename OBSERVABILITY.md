# Observability Stack — Prometheus + Grafana + Loki

**Status:** Ready to implement
**Cost:** $0 (self-hosted on same Docker network)
**Time:** ~30 minutes

---

## 1. Docker Compose Additions

Add to `docker-compose.yml`:

```yaml
# Observability
prometheus:
  image: prom/prometheus:v2.53.0
  container_name: lankaagent-prometheus
  ports:
    - "9090:9090"
  volumes:
    - ./observability/prometheus.yml:/etc/prometheus/prometheus.yml
    - prometheus_data:/prometheus
  command:
    - '--config.file=/etc/prometheus/prometheus.yml'
    - '--storage.tsdb.path=/prometheus'
    - '--web.console.libraries=/usr/share/prometheus/console_libraries'
    - '--web.console.templates=/usr/share/prometheus/consoles'
  networks:
    - lankaagent-internal
  restart: unless-stopped

grafana:
  image: grafana/grafana:11.0.0
  container_name: lankaagent-grafana
  ports:
    - "3000:3000"
  environment:
    - GF_SECURITY_ADMIN_USER=admin
    - GF_SECURITY_ADMIN_PASSWORD=admin  # Change in production
    - GF_USERS_ALLOW_SIGN_UP=false
  volumes:
    - ./observability/grafana/datasources:/etc/grafana/provisioning/datasources
    - ./observability/grafana/dashboards:/etc/grafana/provisioning/dashboards
    - grafana_data:/var/lib/grafana
  networks:
    - lankaagent-internal
  restart: unless-stopped

loki:
  image: grafana/loki:2.9.0
  container_name: lankaagent-loki
  ports:
    - "3100:3100"
  volumes:
    - ./observability/loki-config.yml:/etc/loki/local-config.yaml
    - loki_data:/loki
  command: -config.file=/etc/loki/local-config.yaml
  networks:
    - lankaagent-internal
  restart: unless-stopped

promtail:
  image: grafana/promtail:2.9.0
  container_name: lankaagent-promtail
  volumes:
    - ./observability/promtail-config.yml:/etc/promtail/config.yml
    - /var/log:/var/log:ro
    - /c/Users/nishanthap/lankaagent/logs:/app/logs:ro
  command: -config.file=/etc/promtail/config.yml
  networks:
    - lankaagent-internal
  restart: unless-stopped

volumes:
  prometheus_data:
  grafana_data:
  loki_data:
```

---

## 2. Prometheus Config (`observability/prometheus.yml`)

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'lankaagent-api'
    static_configs:
      - targets: ['api:8000']
    metrics_path: '/metrics'

  - job_name: 'mcp-server'
    static_configs:
      - targets: ['mcp:8000']
    metrics_path: '/metrics'

  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['host.docker.internal:9100']  # If running on host
```

---

## 3. Application Metrics Endpoint

Add to `app/main.py`:

```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response

# Metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency', ['method', 'endpoint'])
ACTIVE_SESSIONS = Gauge('active_sessions', 'Active chat sessions')
MCP_CALLS = Counter('mcp_calls_total', 'MCP tool calls', ['tool', 'status'])
LLM_CALLS = Counter('llm_calls_total', 'LLM provider calls', ['provider', 'model', 'status'])
ACTIVE_TENANTS = Gauge('active_tenants', 'Active tenants')

# Middleware
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    return response

@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
```

---

## 4. Grafana Dashboards (Provisioned)

### 4.1 API Health Dashboard (`observability/grafana/dashboards/api-health.json`)

```json
{
  "title": "LankaAgent API Health",
  "panels": [
    {
      "title": "Request Rate",
      "type": "graph",
      "targets": [{"expr": "rate(http_requests_total[5m])", "legendFormat": "{{method}} {{endpoint}}"}]
    },
    {
      "title": "Error Rate",
      "type": "graph",
      "targets": [{"expr": "rate(http_requests_total{status=~\"5..\"}[5m])"}]
    },
    {
      "title": "P95 Latency",
      "type": "graph",
      "targets": [{"expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"}]
    },
    {
      "title": "Active Sessions",
      "type": "stat",
      "targets": [{"expr": "active_sessions"}]
    },
    {
      "title": "MCP Call Success Rate",
      "type": "graph",
      "targets": [
        {"expr": "rate(mcp_calls_total{status=\"success\"}[5m])", "legendFormat": "Success"},
        {"expr": "rate(mcp_calls_total{status=\"error\"}[5m])", "legendFormat": "Error"}
      ]
    },
    {
      "title": "LLM Provider Distribution",
      "type": "piechart",
      "targets": [{"expr": "sum by (provider) (rate(llm_calls_total[5m]))"}]
    }
  ]
}
```

### 4.2 Business Dashboard (`observability/grafana/dashboards/business.json`)

```json
{
  "title": "LankaAgent Business Metrics",
  "panels": [
    {
      "title": "Leads per Day",
      "type": "graph",
      "targets": [{"expr": "increase(leads_created_total[1d])"}]
    },
    {
      "title": "Quotes Generated",
      "type": "stat",
      "targets": [{"expr": "quotes_generated_total"}]
    ],
    {
      "title": "Conversion Rate",
      "type": "graph",
      "targets": [{"expr": "bookings_total / leads_created_total"}]
    ],
    {
      "title": "Revenue (MRR)",
      "type": "stat",
      "targets": [{"expr": "sum(subscription_amount) / 100"}]
    },
    {
      "title": "Active Tenants",
      "type": "stat",
      "targets": [{"expr": "active_tenants"}]
    },
    {
      "title": "Language Distribution",
      "type": "piechart",
      "targets": [{"expr": "sum by (language) (rate(chat_messages_total[1h]))"}]
    }
  ]
}
```

---

## 5. Loki Config (`observability/loki-config.yml`)

```yaml
auth_enabled: false

server:
  http_listen_port: 3100
  grpc_listen_port: 9096

common:
  path_prefix: /loki
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules
  replication_factor: 1
  ring:
    instance_addr: 127.0.0.1
    kvstore:
      store: inmemory

schema_config:
  configs:
    - from: 2024-01-01
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

limits_config:
  reject_old_samples: true
  reject_old_samples_max_age: 168h
```

---

## 6. Promtail Config (`observability/promtail-config.yml`)

```yaml
server:
  http_listen_port: 9080
  grpc_listen_port: 9081

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: lankaagent-api
    static_configs:
      - targets:
          - localhost
        labels:
          job: lankaagent-api
          __path__: /app/logs/*.log

  - job_name: docker-containers
    static_configs:
      - targets:
          - localhost
        labels:
          job: docker
          __path__: /var/log/containers/*.log
```

---

## 6. Quick Start Commands

```bash
# Create observability directory
mkdir -p observability/grafana/dashboards observability/grafana/datasources

# Add to docker-compose.yml (append to existing file)
# Then:
docker compose up -d prometheus grafana loki promtail

# Verify
curl http://localhost:9090/-/healthy  # Prometheus
curl http://localhost:3000/api/health  # Grafana (admin/admin)
curl http://localhost:3100/ready       # Loki

# Access Grafana: http://localhost:3000 (admin/admin)
# Add Prometheus datasource: http://prometheus:9090
# Import dashboards from observability/grafana/dashboards/
```

---

## 7. Alert Rules (Prometheus)

```yaml
# observability/alerts.yml
groups:
  - name: lankaagent
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate on {{ $labels.endpoint }}"
          
      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "P95 latency > 5s"

      - alert: MCPDown
        expr: rate(mcp_calls_total{status="error"}[5m]) > 0.5
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "MCP server failing"

      - alert: NoActiveSessions
        expr: active_sessions == 0
        for: 10m
        labels:
          severity: info
        annotations:
          summary: "No active chat sessions"
```

---

## 7. Next Steps

1. **Create observability directory structure**
2. **Add to docker-compose.yml**
3. **Add `/metrics` endpoint to FastAPI**
4. **Deploy stack**
5. **Import Grafana dashboards**
6. **Configure alerting (email/Slack webhook)**

---

**Time to implement:** ~30 minutes
**Cost:** $0
**Value:** Production-grade observability for pilot demos and beyond