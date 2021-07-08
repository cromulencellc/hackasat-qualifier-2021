CHAL_NAME ?= noise
CHAL_PORT ?= 12345
CHAL_HOST ?= 172.17.0.1

TICKET ?= ticket{zulu10571quebec:GKP9suZz2eyyEpgOpgn1fvN67EpR2MYxvtrAdVfdUtPjBA1w0QSGxD9cWz4grDWaOg}

build: generator solver

.PHONY: generator
generator:
	docker build generator -t ${CHAL_NAME}:generator

.PHONY: solver
solver:
	docker build solver -t ${CHAL_NAME}:solver

.PHONY: test
test:
	rm -rf data/*
	docker run -it --rm -v `pwd`/data:/out -e "FLAG=flag{TESTflag1234}" ${CHAL_NAME}:generator
	docker run -it --rm -v `pwd`/data:/data ${CHAL_NAME}:solver
