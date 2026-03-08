# Enhanced Makefile — Namespace-isolierte Docker Compose Operationen
# Schutz gegen Cross-Project Contamination (Blast Radius Containment)
#
# Verwendung:
#   AGENT_NAMESPACE=myagent make up
#   AGENT_NAMESPACE=myagent make down
#   AGENT_NAMESPACE=myagent make ps
#   AGENT_NAMESPACE=myagent make logs

SHELL := /bin/bash
.ONESHELL:
.SHELLFLAGS := -euo pipefail -c

# Doppelte Namespace-Validierung:
# AGENT_NAMESPACE muss explizit gesetzt sein — kein Fallback auf UNKNOWN
AGENT_NS  := $(or $(AGENT_NAMESPACE),$(error AGENT_NAMESPACE nicht gesetzt))
PROJ_ID   := $(shell basename $$PWD | sed 's/pjc//' | xargs printf '%03d')
COMPOSE_PROJ := $(AGENT_NS)-pjc$(PROJ_ID)

LOG_DIR := /var/log/docker-projects/$(AGENT_NS)

# Audit-Logging: jede Docker-Operation wird mit Timestamp, Namespace und
# Compose-Project-Name protokolliert — sowohl auf stdout als auch in Datei
define log_action
	@mkdir -p $(LOG_DIR)
	@echo "$$(date -Iseconds) [$(AGENT_NS)] [$(COMPOSE_PROJ)] $(1)" | \
		tee -a $(LOG_DIR)/audit.log
endef

.PHONY: up down ps logs validate

## validate — Prüft, ob AGENT_NAMESPACE korrekt gesetzt ist
validate:
	@if [ -z "$(AGENT_NS)" ] || [ "$(AGENT_NS)" = "UNKNOWN" ]; then \
		echo "❌ KRITISCH: AGENT_NAMESPACE nicht gesetzt oder ungültig"; \
		exit 1; \
	fi
	@echo "✅ Namespace validiert: $(COMPOSE_PROJ)"

## up — Startet Container unter isoliertem Compose-Project-Scope
up: validate
	$(call log_action,Container-Start)
	docker compose -p $(COMPOSE_PROJ) up -d --remove-orphans
	$(call log_action,Aktive Container: $$(docker compose -p $(COMPOSE_PROJ) ps -q | wc -l))

## down — Stoppt NUR Container dieses Projekts (Bestätigung erforderlich)
##         Verhindert versehentliches `docker compose down` ohne -p Flag,
##         das alle Projekte aller Agenten beenden würde.
down: validate
	$(call log_action,Container-Stopp-Anfrage)
	@echo "⚠️  Beende nur $(COMPOSE_PROJ) Container — Bestätigung erforderlich"
	@read -p "Fortfahren? [y/N]: " confirm && [ "$$confirm" = "y" ] || exit 1
	docker compose -p $(COMPOSE_PROJ) down --volumes
	$(call log_action,Container gestoppt)

## ps — Zeigt Container-Status des aktuellen Projekts
ps: validate
	docker compose -p $(COMPOSE_PROJ) ps

## logs — Streamt Logs des aktuellen Projekts (JSON-annotiert)
logs: validate
	docker compose -p $(COMPOSE_PROJ) logs -f --tail=100 2>&1 | \
		jq -R -c --arg agent "$(AGENT_NS)" --arg project "$(COMPOSE_PROJ)" \
		'{timestamp: now|todate, agent: $$agent, project: $$project, message: .}'
