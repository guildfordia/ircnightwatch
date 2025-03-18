.PHONY: all build up re stop restart down clean ps logs rebuild check-env

# Project Name
PROJECT_NAME = ircnightwatch

# Docker Compose
DOCKER_COMPOSE = docker-compose

# Default target
all: check-env build up

re: down build up

# Check if .env file exists, if not, copy .env.example to .env
check-env:
	@if [ ! -f .env ]; then \
		echo "No .env file found. Copying .env.example to .env..."; \
		cp .env.example .env; \
	fi

# Build the Docker images
build:
	$(DOCKER_COMPOSE) build

# Start the containers in detached mode
up:
	$(DOCKER_COMPOSE) up -d

# Stop the containers without removing them
stop:
	$(DOCKER_COMPOSE) stop

# Restart the containers
restart: stop up

# Remove the containers and networks (but keep volumes)
down:
	$(DOCKER_COMPOSE) down

# Clean up everything including volumes
clean:
	$(DOCKER_COMPOSE) down --volumes --remove-orphans

# View running containers
ps:
	$(DOCKER_COMPOSE) ps

# Show logs in real-time
logs:
	$(DOCKER_COMPOSE) logs -f

# Rebuild and restart everything
rebuild: clean build up
