# Gemini Legion V2 Deployment Guide

## Overview

This guide shows you how to deploy the clean V2 architecture alongside or instead of the old broken V1. Because you deserve a system that doesn't duplicate messages like a drunk person seeing double.

## Prerequisites

- Python 3.10+ (because we're not fucking cavemen)
- Redis (for distributed state)
- MongoDB or PostgreSQL (for persistence)
- Node.js 18+ (for the frontend)
- A Gemini API key (obviously)
- A burning hatred for duplicate messages

## Development Deployment (Local)

### 1. Backend Setup

```bash
# Clone if you haven't already
git clone [your-repo-url] gemini-legion
cd gemini-legion

# Create virtual environment (always use venv, you animal)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add:
# GOOGLE_API_KEY=your-actual-api-key
# REDIS_URL=redis://localhost:6379
# MONGODB_URL=mongodb://localhost:27017/gemini_legion
# PORT=8001  # V2 on different port for testing
```

### 2. Running V2 Alongside V1

This is the smart way - run both and compare:

```bash
# Terminal 1: Run V1 (the broken shit)
cd gemini_legion_backend
python -m main  # Runs on port 8000

# Terminal 2: Run V2 (the clean architecture)
cd gemini_legion_backend
python -m main_v2  # Runs on port 8001
```

### 3. Frontend Configuration

```bash
cd gemini_legion_frontend

# Install dependencies
npm install

# Configure for V2
cp .env .env.v1.backup  # Backup V1 config
echo "VITE_API_URL=http://localhost:8001/api/v2" > .env
echo "VITE_WS_URL=ws://localhost:8001" >> .env

# Run frontend
npm run dev
```

### 4. Verify It's Working

```bash
# Test V2 health
curl http://localhost:8001/api/v2/status

# Should return:
{
  "status": "operational",
  "version": "2.0.0",
  "architecture": {
    "event_driven": true,
    "message_paths": 1,
    "communication": "ADK Event Bus",
    "agents": "Native ADK patterns"
  }
}
```

## Production Deployment

### Option 1: Blue-Green Deployment (Recommended)

Perfect for zero-downtime migration:

```bash
# 1. Deploy V2 to new instances/containers
docker build -t gemini-legion:v2 -f Dockerfile.v2 .
docker run -d --name gemini-legion-v2 \
  -p 8001:8001 \
  -e GOOGLE_API_KEY=$GOOGLE_API_KEY \
  -e REDIS_URL=$REDIS_URL \
  -e MONGODB_URL=$MONGODB_URL \
  gemini-legion:v2

# 2. Run migration script
python migrate_to_v2.py

# 3. Test V2 thoroughly
python -m pytest tests/v2/

# 4. Switch load balancer to V2
# Update your nginx/caddy/whatever config

# 5. Keep V1 running for rollback capability
```

### Option 2: Rolling Deployment

For Kubernetes or similar orchestrated environments:

```yaml
# k8s/gemini-legion-v2-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gemini-legion-v2
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: gemini-legion
      version: v2
  template:
    metadata:
      labels:
        app: gemini-legion
        version: v2
    spec:
      containers:
      - name: backend
        image: gemini-legion:v2
        ports:
        - containerPort: 8001
        env:
        - name: GOOGLE_API_KEY
          valueFrom:
            secretKeyRef:
              name: gemini-secrets
              key: api-key
        - name: REDIS_URL
          value: redis://redis-service:6379
        - name: MONGODB_URL
          value: mongodb://mongo-service:27017/gemini_legion
        livenessProbe:
          httpGet:
            path: /api/v2/health
            port: 8001
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/v2/status
            port: 8001
          initialDelaySeconds: 5
          periodSeconds: 5
```

Apply with:
```bash
kubectl apply -f k8s/gemini-legion-v2-deployment.yaml
```

### Option 3: Docker Compose (Simple but Effective)

```yaml
# docker-compose.v2.yml
version: '3.8'

services:
  backend-v2:
    build:
      context: .
      dockerfile: Dockerfile.v2
    ports:
      - "8001:8001"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - REDIS_URL=redis://redis:6379
      - MONGODB_URL=mongodb://mongo:27017/gemini_legion
      - EVENT_BUS_MODE=distributed
    depends_on:
      - redis
      - mongo
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/api/v2/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ./gemini_legion_frontend
      args:
        - API_URL=http://backend-v2:8001/api/v2
    ports:
      - "3000:3000"
    depends_on:
      - backend-v2

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  mongo:
    image: mongo:6
    volumes:
      - mongo_data:/data/db
    environment:
      - MONGO_INITDB_DATABASE=gemini_legion

volumes:
  redis_data:
  mongo_data:
```

Run with:
```bash
docker-compose -f docker-compose.v2.yml up -d
```

## Migration Process

### 1. Data Migration

Run the migration script to move data from V1 to V2:

```bash
python migrate_to_v2.py

# Options:
# --skip-messages     Don't migrate messages (prevents potential duplicates)
# --minions-only      Only migrate minions
# --channels-only     Only migrate channels
# --dry-run          Show what would be migrated without doing it
```

### 2. Gradual Traffic Shift

If using a load balancer:

```nginx
# nginx.conf - Start with 10% to V2
upstream gemini_backend {
    server localhost:8000 weight=9;  # V1 - 90%
    server localhost:8001 weight=1;  # V2 - 10%
}

# Gradually increase V2 weight as confidence grows
# Final state: 100% to V2
upstream gemini_backend {
    server localhost:8001;  # V2 - 100%
}
```

### 3. Feature Flags (Optional)

In frontend .env:
```
VITE_USE_V2_API=true
VITE_V2_ROLLOUT_PERCENTAGE=10  # Start with 10% of users
```

## Monitoring

### 1. Health Checks

```bash
# V2 includes comprehensive health endpoints
curl http://localhost:8001/api/v2/health
curl http://localhost:8001/api/v2/status
curl http://localhost:8001/api/v2/metrics
```

### 2. Log Aggregation

V2 uses structured logging:

```python
# All V2 components log with structure
logger.info("Event emitted", extra={
    "event_type": "channel.message",
    "channel_id": channel_id,
    "sender_id": sender_id,
    "trace_id": trace_id
})
```

Use ELK, Datadog, or similar to aggregate and monitor.

### 3. Metrics

V2 exposes Prometheus metrics:

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'gemini-legion-v2'
    static_configs:
      - targets: ['localhost:8001']
    metrics_path: '/api/v2/metrics'
```

Key metrics to watch:
- `event_bus_messages_total` - Total events processed
- `event_bus_delivery_duration_seconds` - Event delivery latency
- `minion_response_time_seconds` - Minion response latency
- `websocket_connections_active` - Active WebSocket connections

## Rollback Plan

If shit goes sideways (it shouldn't, but Murphy's Law):

### Quick Rollback (< 1 minute)

```bash
# 1. Switch load balancer back to V1
# Update nginx/caddy config to point to port 8000

# 2. Stop V2
docker stop gemini-legion-v2

# 3. Notify team
echo "Rolled back to V1 due to [ISSUE]. Investigating." | slack-notify
```

### Data Rollback

If data corruption occurred:

```bash
# 1. Stop V2
systemctl stop gemini-legion-v2

# 2. Restore from pre-migration backup
mongorestore --uri=$MONGODB_URL --dir=./backups/pre-v2-migration

# 3. Clear Redis
redis-cli FLUSHDB

# 4. Restart V1
systemctl start gemini-legion-v1
```

## Environment Variables

Complete list for V2:

```bash
# Required
GOOGLE_API_KEY=your-api-key

# Optional with defaults
PORT=8001
HOST=0.0.0.0

# Redis (default: in-memory)
REDIS_URL=redis://localhost:6379
REDIS_KEY_PREFIX=gemini_legion_v2

# Database (default: in-memory)
DATABASE_TYPE=mongodb  # or postgresql
MONGODB_URL=mongodb://localhost:27017/gemini_legion
POSTGRES_URL=postgresql://user:pass@localhost/gemini_legion

# Event Bus
EVENT_BUS_MODE=distributed  # or local
EVENT_BUS_HISTORY_LIMIT=10000

# Rate Limiting
DEFAULT_RATE_LIMIT=10  # events per second
MINION_RATE_LIMIT=5

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json  # or text

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090
```

## Troubleshooting

### Common Issues

**1. "Rate limit exceeded" errors**
```bash
# Increase rate limits in V2
export DEFAULT_RATE_LIMIT=20
export MINION_RATE_LIMIT=10
```

**2. WebSocket connection drops**
```bash
# Check nginx/proxy timeouts
# Increase proxy_read_timeout in nginx
proxy_read_timeout 3600s;
proxy_send_timeout 3600s;
```

**3. Memory growth in event bus**
```bash
# Reduce history limit
export EVENT_BUS_HISTORY_LIMIT=1000

# Enable periodic cleanup
export EVENT_BUS_CLEANUP_INTERVAL=300  # 5 minutes
```

**4. Minions not responding**
```bash
# Check if minions are subscribed to events
curl http://localhost:8001/api/v2/debug/subscriptions

# Verify Gemini API key
curl http://localhost:8001/api/v2/debug/minion-status
```

## Performance Tuning

### 1. Event Bus Optimization

```python
# In production, use Redis for distributed events
EVENT_BUS_MODE=distributed
REDIS_POOL_SIZE=50
REDIS_MAX_CONNECTIONS=100
```

### 2. Database Indexes

```javascript
// MongoDB indexes for V2
db.messages.createIndex({ "channel_id": 1, "timestamp": -1 })
db.messages.createIndex({ "message_id": 1 }, { unique: true })
db.events.createIndex({ "type": 1, "timestamp": -1 })
db.events.createIndex({ "source": 1, "timestamp": -1 })
```

### 3. Minion Pooling

```yaml
# Limit concurrent minions for resource management
MAX_ACTIVE_MINIONS: 50
MINION_IDLE_TIMEOUT: 300  # 5 minutes
MINION_POOL_SIZE: 10  # Pre-warmed minions
```

## Success Criteria

You'll know V2 is working when:

1. **No duplicate messages** - Check `test_no_duplicates.py` passes
2. **Real ADK responses** - No "ADK integration needs work" placeholders
3. **Single event path** - Event bus metrics show 1:1 emission to delivery
4. **Happy minions** - Minion status endpoint shows all "active"
5. **Clean logs** - No "Multiple paths detected" warnings

## Final Notes

The V2 architecture is what V1 should have been from the start. It's clean, it's ADK-native, and it doesn't duplicate messages like a broken record player.

If you have issues, check:
1. The logs (they're structured now, you're welcome)
2. The metrics (Prometheus endpoint has everything)
3. The tests (run `pytest tests/v2/` for quick validation)

And remember: In V2, the event bus is god. Everything flows through it. No shortcuts, no custom paths, just clean event-driven beauty.

---

*"By any means necessary, but preferably by clean architecture"* - The V2 Way
