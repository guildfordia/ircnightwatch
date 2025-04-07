# Detect if Docker needs sudo
DOCKER := $(shell docker ps >/dev/null 2>&1 || echo sudo)docker

# Warn if user is not in the docker group and Docker needs sudo
ifeq ($(DOCKER),sudodocker)
$(warning ⚠️ You are not in the docker group. Running Docker with sudo.)
$(warning 👉 To fix this permanently, run: sudo usermod -aG docker $$USER && newgrp docker)
endif

.PHONY: all build up stop down restart clean logs logs-% sh-% re network

# Default: build & run all
all: build up

# Ensure irc-net exists before anything that uses it
network:
	@$(DOCKER) network inspect irc-net >/dev/null 2>&1 || \
	($(DOCKER) network create irc-net && echo "Created network: irc-net")

build: network
	$(MAKE) -C IRC build
	$(MAKE) -C Sentiment build
	$(MAKE) -C BATMAN build

up: network
	$(MAKE) -C IRC up
	$(MAKE) -C Sentiment up
	$(MAKE) -C BATMAN all

# Add `network` dependency here too
clean: network
	-$(MAKE) -C Sentiment clean
	-$(MAKE) -C IRC clean
	-$(MAKE) -C BATMAN clean

stop:
	-$(MAKE) -C Sentiment stop
	-$(MAKE) -C IRC stop

down:
	-$(MAKE) -C Sentiment down
	-$(MAKE) -C IRC down

restart: stop up

# Add `network` dependency here too
re:
	$(MAKE) -C Sentiment re
	$(MAKE) -C IRC re
	$(MAKE) -C BATMAN re

logs-%:
	-$(MAKE) -C IRC logs-$*
	-$(MAKE) -C Sentiment logs-$*

sh-%:
	-$(MAKE) -C IRC sh-$*
	-$(MAKE) -C Sentiment sh-$*

status:
	$(MAKE) -C BATMAN status