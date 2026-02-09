#!/usr/bin/env python3
"""
Minimal label-based task scheduler for Docker Compose
"""
import time
import subprocess
from datetime import datetime
from croniter import croniter
import yaml

def get_scheduled_services():
    try:
        with open('/app/docker-compose.yml', 'r') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"Error reading docker-compose.yml: {e}")
        return []

    services = []
    for name, svc in config.get('services', {}).items():
        labels = svc.get('labels', {})

        # Convert list format to dict
        if isinstance(labels, list):
            labels = {l.split(':', 1)[0].strip(): l.split(':', 1)[1].strip()
                     for l in labels if ':' in l}

        schedule = labels.get('cron.schedule')
        if schedule:
            services.append({'name': name, 'schedule': schedule, 'last_run': 0})

    return services

def should_run(service, now):
    try:
        cron = croniter(service['schedule'], service['last_run'])
        return now >= cron.get_next()
    except:
        return False

def run_service(name):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{ts}] Triggering: {name}")
    print("=" * 50)

    result = subprocess.run(
        ['docker', 'compose', 'run', '--rm', name],
        capture_output=True, text=True, cwd='/app'
    )

    print(f"✓ Completed" if result.returncode == 0 else f"✗ Failed ({result.returncode})")
    if result.stdout:
        print(result.stdout.strip())
    print("=" * 50)

print("=" * 50)
print("Docker Task Scheduler - Label-based")
print("=" * 50)

services = get_scheduled_services()
print(f"\nScheduled services: {len(services)}")
for s in services:
    print(f"  • {s['name']}: {s['schedule']}")
print("=" * 50)

if not services:
    print("No 'cron.schedule' labels found. Exiting.")
else:
    while True:
        now = time.time()
        for svc in services:
            if should_run(svc, now):
                run_service(svc['name'])
                svc['last_run'] = now
        time.sleep(10)
