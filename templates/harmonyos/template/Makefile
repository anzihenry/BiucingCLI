SHELL := /bin/zsh
HVIGOR ?= hvigorw

.PHONY: bootstrap doctor build clean open

bootstrap:
	./scripts/bootstrap

doctor:
	./scripts/doctor

build:
	$(HVIGOR) assembleHap --mode module -p module={{HARMONY_MODULE_NAME}}

clean:
	$(HVIGOR) clean

open:
	open -a "DevEco Studio" .
