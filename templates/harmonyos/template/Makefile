SHELL := /bin/zsh
HVIGOR ?= hvigorw

.PHONY: bootstrap doctor lint build package signing-info clean open

bootstrap:
	./scripts/bootstrap

doctor:
	./scripts/doctor

lint:
	./scripts/lint

build:
	$(HVIGOR) assembleHap --mode module -p module={{HARMONY_MODULE_NAME}}

package: build

signing-info:
	@printf '%s\n' "Configure signing in DevEco Studio or copy docs/release-signing.local.properties.example to local.properties."

clean:
	$(HVIGOR) clean

open:
	open -a "DevEco Studio" .
