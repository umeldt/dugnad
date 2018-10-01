all: db config.yaml messages

db:
	./scripts/prepare-db.sh

config.yaml:
	cp config.def.yaml config.yaml

messages:
	for d in lang/*/LC_MESSAGES; do cd $$d; msgfmt messages.po; done

