.PHONY: all build up stop down restart clean logs logs-% sh-% re network

# Default: build & run all
all: build up

# Ensure irc-net exists before anything that uses it
network:
	@docker network inspect irc-net >/dev/null 2>&1 || \
	(docker network create irc-net && echo "Created network: irc-net")

build: network
	$(MAKE) -C IRC build
	$(MAKE) -C Sentiment build

up: network
	$(MAKE) -C IRC up
	$(MAKE) -C Sentiment up

# Add `network` dependency here too
clean: network
	-$(MAKE) -C Sentiment clean
	-$(MAKE) -C IRC clean

stop:
	-$(MAKE) -C Sentiment stop
	-$(MAKE) -C IRC stop

down:
	-$(MAKE) -C Sentiment down
	-$(MAKE) -C IRC down

restart: stop up

# Add `network` dependency here too
re: network clean build up

logs-%:
	-$(MAKE) -C IRC logs-$*
	-$(MAKE) -C Sentiment logs-$*

sh-%:
	-$(MAKE) -C IRC sh-$*
	-$(MAKE) -C Sentiment sh-$*
