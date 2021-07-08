CHAL_NAME ?= errcorr
CHAL_PORT ?= 31401
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
	sudo rm -rf data/*

	# docker run -it --rm -v `pwd`/data:/out -e "FLAG=flag{TESTflag1234}" ${CHAL_NAME}:generator 

	docker run -it --rm -v `pwd`/data:/out -e "FLAG=flag{zulu49225delta:GEuHu-lkVHZUryVLA926sLeEqnjP4C6ELc4fglSzpy92FOaFnGwcwWRB-Y_zDPijwJJzub-e5qr79IsIfgv3BiU}" ${CHAL_NAME}:generator

	docker run -it --rm -v `pwd`/data:/out ${CHAL_NAME}:solver

