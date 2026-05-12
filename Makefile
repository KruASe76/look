SOURCE_CODE_DIR := app
DEPLOY_DIR := deploy

INSTALL_DIRS := $(DEPLOY_DIR)
INSTALL_FILES := \
	$(DEPLOY_DIR)/compose.yml \
	$(DEPLOY_DIR)/compose.dev.yml \
	$(DEPLOY_DIR)/.env.example
REPO_TREE_URL := https://github.com/KruASe76/look/raw/refs/heads/main


all: prod


prod: setup-once pull run
dev: dev-check run-dev

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
