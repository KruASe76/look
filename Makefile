DEPLOY_DIR := deploy
CERTS_DIR := $(DEPLOY_DIR)/certs
CERT_PATH := $(CERTS_DIR)/cert.pem
CERT_KEY_PATH := $(CERTS_DIR)/key.pem
CERT_AND_KEY_EXISTENCE_CHECK = $(and $(wildcard $(CERT_PATH)),$(wildcard $(CERT_KEY_PATH)))
CERT_OR_KEY_EXISTENCE_CHECK = $(or $(wildcard $(CERT_PATH)),$(wildcard $(CERT_KEY_PATH)))


all: prod


prod: setup-env prod-certs run

dev: setup-env dev-certs run-dev


$(DEPLOY_DIR)/.env:
	cp $(DEPLOY_DIR)/.env.example $(DEPLOY_DIR)/.env
	nano $(DEPLOY_DIR)/.env

setup-env: $(DEPLOY_DIR)/.env


$(CERTS_DIR):
	mkdir -p $(CERTS_DIR)

prod-certs: $(CERTS_DIR)
ifeq "$(CERT_AND_KEY_EXISTENCE_CHECK)" ""
	$(error '$(CERT_PATH)' and '$(CERT_KEY_PATH)' should be present)
else
	@echo "Certificates are present"
endif

dev-certs: $(CERTS_DIR)
ifeq "$(CERT_OR_KEY_EXISTENCE_CHECK)" ""
	openssl req -x509 -newkey rsa:4096 -sha256 -noenc -out $(CERT_PATH) -keyout $(CERT_KEY_PATH) -days 365 -batch 2> /dev/null
else
	@echo "Not overwriting existing certificates"
endif


run:
	cd $(DEPLOY_DIR) && docker compose up -d

run-dev:
	cd $(DEPLOY_DIR) && docker compose -f compose.yml -f compose.dev.yml up -d

stop:
	cd $(DEPLOY_DIR) && docker compose -f compose.yml -f compose.dev.yml down --rmi local

clean:
	cd $(DEPLOY_DIR) && docker compose -f compose.yml -f compose.dev.yml down --rmi local -v

restart: stop run
redev: stop run-dev
