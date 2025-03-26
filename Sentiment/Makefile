.PHONY: all build up stop down restart clean logs logs-% sh-% re test

DC = docker-compose

all: build up

build:
	$(DC) build

up:
	$(DC) up -d

stop:
	$(DC) stop

down:
	$(DC) down

restart: stop up

clean:
	$(DC) down --volumes --remove-orphans

logs:
	$(DC) logs -f

logs-%:
	$(DC) logs -f $*

sh-%:
	$(DC) exec $* /bin/bash

test:
	echo "No tests defined yet"

re: clean all
