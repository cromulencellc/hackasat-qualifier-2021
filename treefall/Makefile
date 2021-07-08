CHAL_NAME ?= treefall
CHAL_PORT ?= 54321
CHAL_HOST ?= 172.17.0.1
SERVICE_PORT ?= 19021
TICKET ?= ticket{zulu10571quebec:GKP9suZz2eyyEpgOpgn1fvN67EpR2MYxvtrAdVfdUtPjBA1w0QSGxD9cWz4grDWaOg}
TEST_PORT ?= 50008
PROD_PORT ?= 5008
DEMO_TICKET ?= ticket{juliet993879india2:GMNr1u5E8pTRClYgyneB6m9GFVfYR-EylkAZrxN7tuvVotijDWUSIcaEMtcKyZunhQ}

build: challenge solver

.PHONY:challenge
challenge:
	docker build challenge -t $(CHAL_NAME):challenge

.PHONY:solver
solver:
	docker build solver -t $(CHAL_NAME):solver

.PHONY:test
test:
	socat -v tcp-listen:19020,reuseaddr exec:"docker run --rm -i -e SERVICE_HOST=${CHAL_HOST} -e SERVICE_PORT=${SERVICE_PORT} -e SEED=1465500232115169100 -e FLAG=flag{TESTflag1234} -p ${SERVICE_PORT}\:${CHAL_PORT}/udp -e CHAL_PORT=${CHAL_PORT} ${CHAL_NAME}\:challenge" > log 2>&1 &
	docker run --rm -i -e CHAL_HOST=${CHAL_HOST} -e CHAL_PORT=${CHAL_PORT} ${CHAL_NAME}:solver 

.PHONY:test-aws
test-aws:
	docker run -it --rm -e "CHAL_HOST=$(EC2_QA)" -e "CHAL_PORT=50008" -e "TICKET=$(TICKET)" $(CHAL_NAME):solver

.PHONY:prod
prod:
	docker login registry:443
	docker pull registry.mlb.cromulence.com/has2/quals/challenges/$(CHAL_NAME)/$(CHAL_NAME):challenge
	docker image tag registry.mlb.cromulence.com/has2/quals/challenges/$(CHAL_NAME)/$(CHAL_NAME):challenge registry:443/$(CHAL_NAME):challenge
	docker push registry:443/$(CHAL_NAME):challenge

.PHONY:prod_test
prod_test:
	docker run -it -e CHAL_HOST=${PROD_HOST} -e CHAL_PORT=${PROD_PORT} -e "TICKET=$(DEMO_TICKET)" ${CHAL_NAME}:solver