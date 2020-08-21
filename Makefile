SHELL := /bin/bash

# Variables definitions
# -----------------------------------------------------------------------------
ifeq ($(DISCOGS_USER_TOKEN),)
DISCOGS_USER_TOKEN := "Environment variable not exported!"
endif

neo4j:
	docker run \
		--name jazz \
		-p 7474:7474 \
		-p 7687:7687 \
		--env NEO4J_AUTH=none \
    neo4j:latest

discogs:
	DISCOGS_USER_TOKEN=$(DISCOGS_USER_TOKEN) \
	python data/store_masters_ids.py

dependencies: discogs neo4j

run:
	python jazz_graph.py
