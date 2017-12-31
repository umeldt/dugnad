all: messages

messages:
	cd lang/nb_NO/LC_MESSAGES; msgfmt messages.po

