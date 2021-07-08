CHAL_NAME ?= amongus
CHAL_PORT ?= 31337
CHAL_HOST ?= 172.17.0.1
SERVICE_PORT ?= 19021

TICKET ?= ticket{zulu10571quebec:GKP9suZz2eyyEpgOpgn1fvN67EpR2MYxvtrAdVfdUtPjBA1w0QSGxD9cWz4grDWaOg}
FLAG = 
SEED = 1465500232115169100
PROD_PORT ?= 5024
DEMO_TICKET ?= {demo3tckt:GAJTM2fMBu-LAb9pN8zOAEV9mVoLj0jVhyGkq-3mfSh02D-f7jChGMvVEYqP2djOYw}
PROD_TICKET ?= ticket{uniform982383papa2:GFmznh0cCDo66VyrKnH6wHu9wTyAB1C3-tuiVNzcJ06zKHSYm0vqW3WvMyPbeJNACA}



.PHONY:challenge solver generator test
all: challenge solver generator static

challenge:
	docker build -f challenge/Dockerfile challenge -t ${CHAL_NAME}:challenge
solver:
	docker build -f solver/Dockerfile solver -t ${CHAL_NAME}:solver

.PHONY: generator
generator:
	docker build challenge --target builder -t $(CHAL_NAME):generator 

.PHONY: static
static: 
	docker run --rm -v $(PWD)/static:/out $(CHAL_NAME):generator

test:
	socat -v tcp-listen:$(CHAL_PORT),reuseaddr exec:"docker run --rm -i -e SEED=1465500232115169100 -e FLAG=flag{zulu49225delta:GEuHu-lkVHZUryVLA926sLeEqnjP4C6ELc4fglSzpy92FOaFnGwcwWRB-Y_zDPijwJJzub-e5qr79IsIfgv3BiU} ${CHAL_NAME}\:challenge" > log 2>&1 &
	docker run --rm -i -e CHAL_HOST=${CHAL_HOST} -e CHAL_PORT=${CHAL_PORT} ${CHAL_NAME}\:solver
run:
	socat -v tcp-listen:$(CHAL_PORT),reuseaddr exec:"docker run --rm -i -e SEED=1465500232115169100 -e FLAG=flag{zulu49225delta:GEuHu-lkVHZUryVLA926sLeEqnjP4C6ELc4fglSzpy92FOaFnGwcwWRB-Y_zDPijwJJzub-e5qr79IsIfgv3BiU} ${CHAL_NAME}\:challenge" > log 2>&1 &
solve:
	docker run --rm -i -e CHAL_HOST=${CHAL_HOST} -e CHAL_PORT=${CHAL_PORT} ${CHAL_NAME}\:solver

debug:
	docker run -it -p ${CHAL_PORT}:${CHAL_PORT} -v `pwd`/challenge:/src/challenge ${CHAL_NAME}:challenge /bin/bash

.PHONY:test-aws
test-aws:
	docker run -it --rm -e "CHAL_HOST=$(EC2_QA)" -e "CHAL_PORT=50022" -e "TICKET=$(TICKET)" $(CHAL_NAME):solver

.PHONY:prod
prod:
	#docker login registry:443
	#docker pull registry.mlb.cromulence.com/has2/quals/challenges/$(CHAL_NAME)/$(CHAL_NAME):challenge
	docker image tag $(CHAL_NAME):challenge registry:443/amogus:challenge
	docker push registry:443/amogus:challenge

.PHONY:prod_test
prod_test:
	docker run -it -e CHAL_HOST=${PROD_HOST} -e CHAL_PORT=${PROD_PORT} -e "TICKET=$(PROD_TICKET)" ${CHAL_NAME}:solver