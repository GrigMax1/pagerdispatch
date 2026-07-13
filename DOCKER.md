# 🐳 SAPD PagerDispatch Bot - Docker Setup

This guide explains how to run the bot using Docker and Docker Compose.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (version 20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (version 1.29+)
- Discord bot token
- Configured `config.json`

## Quick Start (Recommended)

### 1. Clone Repository
```bash
git clone https://github.com/GrigMax1/pagerdispatch.git
cd pagerdispatch
```

### 2. Create Environment File
```bash
cp .env.example .env
```

Edit `.env` and add your bot token:
```
DISCORD_TOKEN=your_bot_token_here
```

### 3. Configure Bot
Edit `config.json` with your Discord server settings:
- Guild ID
- Channel IDs
- Role IDs

### 4. Start Bot
```bash
docker-compose up -d
```

### 5. View Logs
```bash
docker-compose logs -f sapd-dispatch-bot
```

## Docker Compose Commands

### Start
```bash
docker-compose up -d
```

### Stop
```bash
docker-compose stop
```

### Restart
```bash
docker-compose restart
```

### View Logs
```bash
# Last 50 lines
docker-compose logs sapd-dispatch-bot

# Follow (live)
docker-compose logs -f sapd-dispatch-bot

# With timestamps
docker-compose logs -f -t sapd-dispatch-bot

# Last 100 lines
docker-compose logs --tail=100 sapd-dispatch-bot
```

### Remove (with data cleanup)
```bash
# Stop and remove container
docker-compose down

# Remove everything including volumes
docker-compose down -v
```

### Rebuild Image
```bash
# Rebuild without using cache
docker-compose build --no-cache

# Rebuild and restart
docker-compose up -d --build
```

## Manual Docker Commands

### Build Image
```bash
docker build -t sapd-dispatch-bot .
```

### Run Container
```bash
docker run -d \
  --name sapd-dispatch-bot \
  -e DISCORD_TOKEN=your_token_here \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/config.json:/app/config.json \
  -v $(pwd)/logs:/app/logs \
  --restart unless-stopped \
  sapd-dispatch-bot
```

### View Logs
```bash
# Follow logs
docker logs -f sapd-dispatch-bot

# Get last 100 lines
docker logs --tail 100 sapd-dispatch-bot
```

### Container Status
```bash
# List running containers
docker ps

# List all containers
docker ps -a
```

### Stop Container
```bash
docker stop sapd-dispatch-bot
```

### Start Container
```bash
docker start sapd-dispatch-bot
```

### Restart Container
```bash
docker restart sapd-dispatch-bot
```

### Remove Container
```bash
docker rm sapd-dispatch-bot
```

### Execute Command in Container
```bash
# Run Python command
docker exec -it sapd-dispatch-bot python -c "import sys; print(sys.version)"

# Access shell
docker exec -it sapd-dispatch-bot bash

# Check database
docker exec -it sapd-dispatch-bot ls -la /app/data/
```

### View Container Details
```bash
# Inspect container
docker inspect sapd-dispatch-bot

# View resource usage
docker stats sapd-dispatch-bot
```

## Data Persistence

Three volumes maintain data across container restarts:

| Path | Purpose | Location |
|------|---------|----------|
| `/app/data` | SQLite database | `./data/dispatch.db` |
| `/app/logs` | Bot logs | `./logs/bot.log` |
| `/app/config.json` | Configuration | `./config.json` |

### Backup Data
```bash
# Backup database
cp -r data/ data-backup-$(date +%Y%m%d-%H%M%S)/

# Backup logs
cp -r logs/ logs-backup-$(date +%Y%m%d-%H%M%S)/
```

### Restore Data
```bash
# Stop container
docker-compose stop

# Restore database
rm -rf data/
cp -r data-backup-20240101-120000/ data/

# Restart container
docker-compose start
```

## Environment Variables

### Required
```
DISCORD_TOKEN=your_bot_token
```

### Optional (in docker-compose.yml)
```
TZ=America/Los_Angeles
PYTHONUNBUFFERED=1
```

## Troubleshooting

### Bot not starting
```bash
# Check logs
docker-compose logs sapd-dispatch-bot

# Verify container is running
docker-compose ps

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Database errors
```bash
# Remove corrupted database
rm ./data/dispatch.db

# Restart container (will reinitialize)
docker-compose restart
```

### Permission denied errors
```bash
# Fix permissions
chmod -R 755 ./data
chmod -R 755 ./logs

# On Linux, may need to fix ownership
sudo chown -R $(whoami):$(whoami) ./data ./logs
```

### High memory usage
```bash
# Add resource limits to docker-compose.yml
services:
  sapd-dispatch-bot:
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
```

### Container keeps restarting
```bash
# Check logs for errors
docker-compose logs --tail=50 sapd-dispatch-bot

# Verify .env has correct token
cat .env

# Verify config.json is valid JSON
python -m json.tool config.json
```

## Advanced Setup

### Development Mode (with local code)
```yaml
volumes:
  - .:/app  # Mount entire project
  - /app/__pycache__  # Exclude cache
```

### Production with health checks
```bash
# Check container health
docker inspect --format='{{.State.Health.Status}}' sapd-dispatch-bot
```

### Multiple Bot Instances
```bash
# Create separate compose files
cp docker-compose.yml docker-compose.bot1.yml
cp docker-compose.yml docker-compose.bot2.yml

# Edit each file with different names and configs
docker-compose -f docker-compose.bot1.yml up -d
docker-compose -f docker-compose.bot2.yml up -d
```

### Using .env Override
```bash
# Create override file
cp docker-compose.yml docker-compose.override.yml

# Edit and customize (automatically loaded)
docker-compose up -d
```

## Docker Hub (Future)

When ready to share, push to Docker Hub:
```bash
# Tag image
docker tag sapd-dispatch-bot grigmax1/sapd-dispatch-bot:latest

# Login to Docker Hub
docker login

# Push image
docker push grigmax1/sapd-dispatch-bot:latest

# Then users can:
docker pull grigmax1/sapd-dispatch-bot:latest
```

## Updating Bot

```bash
# Pull latest code from GitHub
git pull origin main

# Rebuild image
docker-compose build --no-cache

# Restart with new build
docker-compose up -d

# Verify it's running
docker-compose logs -f sapd-dispatch-bot
```

## Performance Tips

1. **Use Alpine Linux base** (lightweight):
   ```dockerfile
   FROM python:3.12-alpine
   ```

2. **Multi-stage builds** (reduce image size):
   ```dockerfile
   FROM python:3.12-slim as builder
   # ... build steps ...
   
   FROM python:3.12-slim
   COPY --from=builder /app .
   ```

3. **Layer caching** - order Dockerfile commands from least to most changeable

4. **Volume optimization**:
   ```yaml
   volumes:
     - data:/app/data  # Named volume for better performance
   ```

## Security Best Practices

1. ✅ Never commit `.env` (added to `.gitignore`)
2. ✅ Use secrets for sensitive data in production
3. ✅ Run as non-root user (uses `python:3.12-slim`)
4. ✅ Set read-only filesystem where possible
5. ✅ Keep Docker daemon updated
6. ✅ Use specific image versions (not `latest`)

## Support & Documentation

- [Docker Docs](https://docs.docker.com/)
- [Docker Compose Docs](https://docs.docker.com/compose/)
- [Bot Repository](https://github.com/GrigMax1/pagerdispatch)
- [Main README](./README.md)