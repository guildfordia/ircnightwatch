# Detect if Docker needs sudo
DOCKER := $(shell docker ps >/dev/null 2>&1 || echo sudo)docker
ENV = .global.env
IS_LINUX := $(shell uname -s | grep -q Linux && echo true || echo false)

# Warn if user is not in the docker group and Docker needs sudo
ifeq ($(DOCKER),sudodocker)
$(warning ⚠️ You are not in the docker group. Running Docker with sudo.)
$(warning 👉 To fix this permanently, run: sudo usermod -aG docker $$USER && newgrp docker)
endif

.PHONY: all build up stop down restart clean clean-global-env clean-all-env setup-global-env logs-% sh-% re network env-setup rmi prune status clean-cache

# Default: build & run all
all: build up

# Ensure irc-net exists before anything that uses it
network:
	@$(DOCKER) network inspect irc-net >/dev/null 2>&1 || \
	($(DOCKER) network create irc-net && echo "Created network: irc-net")

build: setup-global-env network
	$(MAKE) -C irc -f Makefile-irc build
	$(MAKE) -C sentiment -f Makefile-sentiment build
	@if [ "$(IS_LINUX)" = "true" ]; then \
		$(MAKE) -C batman -f Makefile-batman build; \
	else \
		echo "[!] Skipping BATMAN build (not on Linux)"; \
	fi

up: setup-global-env network
	$(MAKE) -C irc -f Makefile-irc up
	$(MAKE) -C sentiment -f Makefile-sentiment up
	@if [ "$(IS_LINUX)" = "true" ]; then \
		$(MAKE) -C batman -f Makefile-batman up; \
	else \
		echo "[!] Skipping BATMAN up (not on Linux)"; \
	fi

# Add `network` dependency here
clean:
	-$(MAKE) -C sentiment -f Makefile-sentiment clean
	-$(MAKE) -C irc -f Makefile-irc clean
	@if [ "$(IS_LINUX)" = "true" ]; then \
		$(MAKE) -C batman -f Makefile-batman clean; \
	else \
		echo "[!] Skipping BATMAN clean (not on Linux)"; \
	fi

clean-global-env:
	rm -rf $(ENV)

clean-all-env: clean-global-env
	-$(MAKE) -C sentiment -f Makefile-sentiment clean-sentiment-env
	-$(MAKE) -C irc -f Makefile-irc clean-irc-env
	@if [ "$(IS_LINUX)" = "true" ]; then \
		$(MAKE) -C batman -f Makefile-batman clean-batman-env; \
	else \
		echo "[!] Skipping BATMAN env clean (not on Linux)"; \
	fi

stop:
	-$(MAKE) -C sentiment -f Makefile-sentiment stop
	-$(MAKE) -C irc -f Makefile-irc stop
	@if [ "$(IS_LINUX)" = "true" ]; then \
		$(MAKE) -C batman -f Makefile-batman stop; \
	else \
		echo "[!] Skipping BATMAN stop (not on Linux)"; \
	fi

down:
	-$(MAKE) -C sentiment -f Makefile-sentiment down
	-$(MAKE) -C irc -f Makefile-irc down
	@if [ "$(IS_LINUX)" = "true" ]; then \
		$(MAKE) -C batman -f Makefile-batman down; \
	else \
		echo "[!] Skipping BATMAN down (not on Linux)"; \
	fi

restart: stop up

# Add `network` dependency here too
re:
	$(MAKE) -C sentiment -f Makefile-sentiment re
	$(MAKE) -C irc -f Makefile-irc re
	@if [ "$(IS_LINUX)" = "true" ]; then \
		$(MAKE) -C batman -f Makefile-batman re; \
	else \
		echo "[!] Skipping BATMAN re (not on Linux)"; \
	fi

logs-%:
	-$(MAKE) -C irc -f Makefile-irc logs-$*
	-$(MAKE) -C sentiment -f Makefile-sentiment logs-$*
	@if [ "$(IS_LINUX)" = "true" ]; then \
		$(MAKE) -C batman -f Makefile-batman logs-$*; \
	else \
		echo "[!] Skipping BATMAN logs-$* (not on Linux)"; \
	fi

sh-%:
	-$(MAKE) -C irc -f Makefile-irc sh-$*
	-$(MAKE) -C sentiment -f Makefile-sentiment sh-$*
	@if [ "$(IS_LINUX)" = "true" ]; then \
		$(MAKE) -C batman -f Makefile-batman sh-$*; \
	else \
		echo "[!] Skipping BATMAN sh-$* (not on Linux)"; \
	fi

rmi:
	-$(MAKE) -C irc -f Makefile-irc rmi
	-$(MAKE) -C sentiment -f Makefile-sentiment rmi
	@if [ "$(IS_LINUX)" = "true" ]; then \
		$(MAKE) -C batman -f Makefile-batman rmi; \
	else \
		echo "[!] Skipping BATMAN rmi (not on Linux)"; \
	fi

prune:
	docker system prune -a

status:
	@if [ "$(IS_LINUX)" = "true" ]; then \
		$(MAKE) -C batman -f Makefile-batman status; \
	else \
		echo "[!] Skipping BATMAN status (not on Linux)"; \
	fi

# Setup global environment
setup-global-env:
	@if [ ! -f .global.env ]; then \
		echo "Creating .global.env from example..."; \
		cp .global.env.example .global.env; \
	else \
		echo ".global.env already exists."; \
	fi


clean-cache:
	$(MAKE) -C sentiment -f Makefile-sentiment clean-cache

# Main environment setup target
env-setup: setup-global-env
	$(MAKE) -C irc -f Makefile-irc setup-irc-env
	$(MAKE) -C sentiment -f Makefile-sentiment setup-sentiment-env
	@if [ "$(IS_LINUX)" = "true" ]; then \
		$(MAKE) -C batman -f Makefile-batman setup-batman-env; \
	else \
		echo "[!] Skipping BATMAN env setup (not on Linux)"; \
	fi