IMAGE_NAME=batman-node
CONTAINER_NAME=batman-node

.PHONY: all re check-env install build run stop rm clean load-module setup-host status

all: check-env install load-module build host-mesh-setup run

check-env:
	@echo "[+] Checking .batman.env..."
	@if [ ! -f .batman.env ]; then \
	  echo "[!] .batman.env not found. Creating it from .batman.env.example..."; \
	  cp .batman.env.example .batman.env; \
	else \
	  echo "[✓] .batman.env exists."; \
	fi


install:
	@echo "[+] Running install script..."
	@chmod +x scripts/*.sh
	@./scripts/install.sh

load-module:
	@chmod +x scripts/*.sh
	@./scripts/load-module.sh

build:
	@echo "[+] Building Docker image..."
	docker build -t $(IMAGE_NAME) .

host-mesh-setup:
	@echo "[+] Setting up BATMAN on host..."
	@chmod +x scripts/host-mesh-setup.sh
	@sudo scripts/host-mesh-setup.sh

run:
	@chmod +x scripts/run.sh
	@sudo scripts/run.sh

#setup-host:
#	@chmod +x scripts/*.sh
#	@./scripts/setup-host.sh

stop:
	@echo "[+] Stopping BATMAN container..."
	docker stop $(CONTAINER_NAME) || true

rm: stop
	@echo "[+] Removing BATMAN container..."
	docker rm $(CONTAINER_NAME) || true

clean: rm
	@echo "[+] Removing BATMAN image..."
	docker rmi $(IMAGE_NAME) || true

re: clean all

status:
	@echo "[+] Checking BATMAN mesh status..."
	@if ! command -v batctl >/dev/null; then echo "[-] batctl not installed"; exit 1; fi
	@if ! ip link show bat0 >/dev/null 2>&1; then echo "[-] bat0 not found"; exit 1; fi
	@echo "[+] bat0 IPs:"
	@ip -4 addr show dev bat0 | grep inet | awk '{print $$2}'
	@echo ""
	@echo "[+] Neighbors (batctl n):"
	@sudo batctl n
	@echo ""
	@echo "[+] Originators (batctl o):"
	@sudo batctl o
	@echo ""
	@echo "[+] Scanning mesh subnet for reachable peers..."
	@fping -a -q -r1 -g 192.168.199.10 192.168.199.254 2>/dev/null || echo "[-] No mesh nodes reachable"