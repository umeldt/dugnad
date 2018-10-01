all: db config.yaml messages

db:
	./scripts/prepare-db.sh

config.yaml:
	cp config.def.yaml config.yaml

messages:
	cd lang/nb_NO/LC_MESSAGES; msgfmt messages.po

