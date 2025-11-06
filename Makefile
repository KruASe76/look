SOURCE_CODE_DIR := app
DEPLOY_DIR := deploy

CERT_DIR := $(DEPLOY_DIR)/certs
CERT_PATH := $(CERT_DIR)/cert.pem
CERT_KEY_PATH := $(CERT_DIR)/key.pem
CERT_AND_KEY_EXISTENCE_CHECK = $(and $(wildcard $(CERT_PATH)),$(wildcard $(CERT_KEY_PATH)))
CERT_OR_KEY_EXISTENCE_CHECK = $(or $(wildcard $(CERT_PATH)),$(wildcard $(CERT_KEY_PATH)))

INSTALL_DIRS := $(DEPLOY_DIR)
INSTALL_FILES := \
	$(DEPLOY_DIR)/compose.yml \
	$(DEPLOY_DIR)/compose.dev.yml \
	$(DEPLOY_DIR)/traefik.yml \
	$(DEPLOY_DIR)/.env.example
REPO_TREE_URL := https://github.com/KruASe76/look/raw/refs/heads/main


all: prod


prod: setup-once prod-certs pull run
dev: dev-check dev-certs run-dev

restart: stop prod
redev: stop dev


setup: install-all setup-env

setup-once: .setup.stamp

.setup.stamp:
	$(MAKE) setup
	touch $@


run:
	cd $(DEPLOY_DIR) && docker compose up -d

run-dev:
	cd $(DEPLOY_DIR) && docker compose -f compose.yml -f compose.dev.yml up -d

stop:
	cd $(DEPLOY_DIR) && docker compose -f compose.yml -f compose.dev.yml down --rmi local

clean:
	cd $(DEPLOY_DIR) && docker compose -f compose.yml -f compose.dev.yml down --rmi local -v

pull:
	cd $(DEPLOY_DIR) && docker compose pull backend bot

dev-check:
ifeq "$(wildcard $(SOURCE_CODE_DIR))" ""
	$(error Source code directory '$(SOURCE_CODE_DIR)' does not exist. Please clone the full repository)
endif


install-all: $(INSTALL_DIRS) $(INSTALL_FILES)

$(INSTALL_DIRS):
	mkdir -p ./$@

$(INSTALL_FILES): $(INSTALL_DIRS)
	curl -sSL $(REPO_TREE_URL)/$@ -o ./$@


setup-env: $(DEPLOY_DIR)/.env

$(DEPLOY_DIR)/.env:
	cp $(DEPLOY_DIR)/.env.example $(DEPLOY_DIR)/.env
	nano $(DEPLOY_DIR)/.env


$(CERT_DIR):
	mkdir -p $(CERT_DIR)

prod-certs: $(CERT_DIR)
ifeq "$(CERT_AND_KEY_EXISTENCE_CHECK)" ""
	$(error '$(CERT_PATH)' and '$(CERT_KEY_PATH)' should be present)
else
	@echo "Certificates are present"
endif

dev-certs: $(CERT_DIR)
ifeq "$(CERT_OR_KEY_EXISTENCE_CHECK)" ""
	openssl req -x509 -newkey rsa:4096 -sha256 -noenc -out $(CERT_PATH) -keyout $(CERT_KEY_PATH) -days 365 -batch 2> /dev/null
else
	@echo "Not overwriting existing certificates"
endif
