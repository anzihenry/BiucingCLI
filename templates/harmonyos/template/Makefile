SHELL := /bin/zsh

.PHONY: bootstrap doctor build test clean open

bootstrap:
	./scripts/bootstrap

doctor:
	./scripts/doctor

build:
	hvigor assembleHap --mode module -p module={{HARMONY_MODULE_NAME}}

test:
	hvigor test

clean:
	hvigor clean

open:
	open -a "DevEco Studio" .
