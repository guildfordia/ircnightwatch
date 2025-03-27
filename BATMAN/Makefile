IMAGE_NAME=batman-node
CONTAINER_NAME=batman-node
MESH_ID=batmesh
FREQ=2412

.PHONY: all install build run clean load-module setup-host

all: install load-module build setup-host

install:
	@echo "[+] Detecting OS and installing packages..."
	@if [ "$$(uname)" = "Darwin" ]; then \
		echo "Detected macOS. Please install dependencies manually with Homebrew."; \
		echo "brew install docker batctl iproute2 iw wireless-tools net-tools"; \
		exit 0; \
	elif [ "$$(uname)" = "Linux" ]; then \
		if [ -f /etc/arch-release ]; then \
			echo "Detected Arch Linux"; \
			sudo pacman -Syu --noconfirm; \
			sudo pacman -S --noconfirm docker batctl iproute2 iw wireless_tools net-tools; \
		elif [ -f /etc/debian_version ]; then \
			echo "Detected Debian-based Linux"; \
			sudo apt-get update; \
			sudo apt-get install -y docker.io batctl iproute2 iw wireless-tools net-tools; \
		else \
			echo "Unsupported Linux distribution. Please install dependencies manually."; \
			exit 1; \
		fi \
	else \
		echo "Unsupported operating system."; \
		exit 1; \
	fi

load-module:
	@echo "[+] Loading batman-adv kernel module..."
	sudo modprobe batman-adv || echo "batman-adv already loaded"
	@grep -qxF 'batman-adv' /etc/modules || echo 'batman-adv' | sudo tee -a /etc/modules

build:
	@echo "[+] Building Docker image..."
	docker build -t $(IMAGE_NAME) .

setup-host:
	@echo "[+] Detecting interface and generating IP from MAC..."
	@iface=$$(iw dev | awk '$$1=="Interface"{print $$2}' | head -n1); \
		mac=$$(cat /sys/class/net/$$iface/address); \
		o1=$$(echo $$mac | cut -d: -f5); \
		o2=$$(echo $$mac | cut -d: -f6); \
		ip_suffix=$$(printf "%d" 0x$$o1); \
		mesh_ip="192.168.199.$$ip_suffix"; \
		echo "[+] Interface: $$iface"; \
		echo "[+] MAC: $$mac"; \
		echo "[+] Auto-assigned IP: $$mesh_ip"; \
		export MESH_IP=$$mesh_ip && export IFACE=$$iface && make run MESH_IP=$$mesh_ip IFACE=$$iface

run:
	@echo "[+] Running BATMAN Docker container..."
	@if [ -z "$(MESH_IP)" ]; then echo "[-] MESH_IP not set"; exit 1; fi; \
	if [ -z "$(IFACE)" ]; then echo "[-] IFACE not set"; exit 1; fi; \
	docker run -it --rm --privileged --net=host \
		-e MESH_IP=$(MESH_IP) \
		-e IFACE=$(IFACE) \
		-e MESH_ID=$(MESH_ID) \
		-e FREQ=$(FREQ) \
		--name $(CONTAINER_NAME) $(IMAGE_NAME)

clean:
	@echo "[+] Removing Docker image..."
	docker rmi $(IMAGE_NAME) || true
