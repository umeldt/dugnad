SHELL := /bin/bash

all: db config.yaml messages

db:
	./scripts/prepare-db.sh

config.yaml:
	cp config.def.yaml config.yaml

messages:
	for d in lang/*/LC_MESSAGES; do pushd $$d; msgfmt messages.po; popd; done

