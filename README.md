# docker-task-scheduler

**Label-Based Task Scheduler for Docker Compose**

Declarative, scalable task scheduling using Docker labels. Inspired by Docker Swarm patterns.

## Overview

Schedule tasks by adding labels to services in `docker-compose.yml`. No manual cron configuration needed.

**Pattern**: Services declare their schedule → Scheduler reads labels → Tasks execute automatically

## Quick Start

```bash
# 1. Define schedule in docker-compose.yml using labels
services:
  my-task:
    build: .
    profiles: [manual]
    labels:
      cron.schedule: "*/5 * * * *"  # Every 5 minutes

# 2. Start scheduler
docker compose up -d scheduler

# 3. Monitor
docker compose logs -f scheduler
```

## Configuration

### Add Scheduled Tasks

Edit `docker-compose.yml` and add the `cron.schedule` label:

```yaml
services:
  backup-task:
    build: ./backup
    profiles: [manual]
    labels:
      cron.schedule: "0 2 * * *"  # Daily at 2 AM

  cleanup-task:
    build: ./cleanup
    profiles: [manual]
    labels:
      cron.schedule: "0 */6 * * *"  # Every 6 hours
```

Visit [crontab.guru](https://crontab.guru) for schedule syntax help.

### Cron Syntax

```
* * * * *
│ │ │ │ │
│ │ │ │ └─ Day of week (0-7)
│ │ │ └─── Month (1-12)  
│ │ └───── Day (1-31)
│ └─────── Hour (0-23)
└───────── Minute (0-59)
```

### Common Schedules

| Label | Schedule |
|-------|----------|
| `cron.schedule: "* * * * *"` | Every minute |
| `cron.schedule: "*/5 * * * *"` | Every 5 minutes |
| `cron.schedule: "0 * * * *"` | Every hour |
| `cron.schedule: "0 9 * * *"` | Daily at 9 AM |
| `cron.schedule: "0 9 * * 1-5"` | Weekdays at 9 AM |
| `cron.schedule: "@hourly"` | Every hour |
| `cron.schedule: "@daily"` | Every day at midnight |

## Usage

```bash
# Start scheduler
docker compose up -d scheduler

# View logs
docker compose logs -f scheduler

# Test task manually
docker compose run --rm hello-world

# Restart to pick up config changes
docker compose restart scheduler

# Stop
docker compose down
```

## Project Structure

```
.
├── app.py                # Task implementation
├── Dockerfile            # Task container
├── scheduler.py          # Label-based scheduler
├── Dockerfile.scheduler  # Scheduler container
└── docker-compose.yml    # Services + labels
```

## Architecture

```
┌────────────────────────────┐
│  Scheduler Container       │
│                            │
│  1. Read docker-compose    │
│  2. Parse service labels   │
│  3. Check cron schedules   │
│  4. Trigger services       │
└──────────┬─────────────────┘
           │ Via Docker Socket
           ▼
   ┌────────────────┐
   │ Task Container │ ← Spawned on schedule
   │ Runs & Exits   │
   └────────────────┘
```

**Benefits:**
- **Declarative**: Schedule defined in docker-compose.yml
- **Scalable**: Add tasks by adding services
- **No cron config**: Labels define everything
- **Self-documenting**: Schedule visible in compose file

## Multiple Tasks Example

```yaml
services:
  # Database backup - Daily at 2 AM
  db-backup:
    image: postgres:alpine
    profiles: [manual]
    labels:
      cron.schedule: "0 2 * * *"
    command: pg_dump ...

  # Log cleanup - Every 6 hours
  log-cleanup:
    image: alpine
    profiles: [manual]
    labels:
      cron.schedule: "0 */6 * * *"
    command: find /logs -mtime +7 -delete

  # Health check - Every 5 minutes
  health-check:
    image: curlimages/curl
    profiles: [manual]
    labels:
      cron.schedule: "*/5 * * * *"
    command: curl https://api.example.com/health

  scheduler:
    build:
      dockerfile: Dockerfile.scheduler
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - .:/app
```

## Production Tips

1. **Set timezone**: `TZ=America/New_York` in compose environment
2. **Resource limits**: Add to service definitions
3. **Monitoring**: Parse scheduler logs
4. **Alerting**: Watch for failure messages
5. **Persistent logs**: Mount log volumes

## Troubleshooting

```bash
# Check scheduler is reading labels
docker compose logs scheduler | head -20

# Verify cron schedule syntax
# Visit https://crontab.guru

# Test service manually
docker compose run --rm hello-world

# Check Docker socket access
docker exec scheduler docker ps
```

## Example Output

```
==================================================
Docker Task Scheduler - Label-based
==================================================

Found 3 scheduled service(s):
  • hello-world: * * * * *
  • db-backup: 0 2 * * *
  • log-cleanup: 0 */6 * * *
==================================================
[2026-02-06 08:00:00] Triggering service: hello-world
==================================================
Hello World from Docker!
Container ID: abc123
Current Time: 2026-02-06 08:00:00
==================================================
[2026-02-06 08:00:00] ✓ hello-world completed successfully
==================================================
```

## Advantages Over Traditional Cron

| Traditional Cron | Label-Based |
|------------------|-------------|
| Edit crontab manually | Edit docker-compose.yml |
| Separate cron syntax file | Inline with service definition |
| Hard to version control | Git-friendly YAML |
| Manual cron reload needed | Auto-detected on restart |
| Schedule separate from task | Schedule next to task |

## Files

- **scheduler.py**: 60 lines - Reads labels, schedules tasks
- **Dockerfile.scheduler**: 10 lines - Minimal Python + Docker CLI
- **docker-compose.yml**: Services with `cron.schedule` labels
- **No cron configuration files needed**

**Total: One Python script, ~100 lines total**
