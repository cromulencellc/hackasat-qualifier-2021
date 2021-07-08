CHAL_NAME ?= groundead
CHAL_PORT ?= 12345
CHAL_HOST ?= 172.17.0.1
TICKET ?= ticket{zulu10571quebec:GKP9suZz2eyyEpgOpgn1fvN67EpR2MYxvtrAdVfdUtPjBA1w0QSGxD9cWz4grDWaOg}
FLAG = 
SEED = 1465500232115169100
PROD_PORT ?= 5001
DEMO_TICKET ?= ticket{papa962762quebec2:GLro_I0dHUpkzoTRBhL3nUSjTn5yoIwfe8AzhBHs886nHzYwW8W2vvWjPmFc2W4zIg}

# COPY_FILE_CHALLENGE = cp static/packetbug.c challenge/.

COPY_FILE_CHALLENGE = cp challenge/packetbug.cpp static/.

build: challenge solver generator static 

.PHONY:challenge
challenge:
	docker build challenge -t $(CHAL_NAME):challenge

.PHONY:solver
solver: 
	docker build solver -t $(CHAL_NAME):solver

.PHONY: generator
generator:
	docker build challenge --target builder -t $(CHAL_NAME):generator 

.PHONY: static
static: 
	docker run --rm -v $(PWD)/static:/out $(CHAL_NAME):generator

.PHONY:test
test:
	socat -v tcp-listen:$(CHAL_PORT),reuseaddr exec:"docker run --rm -i -e SEED=$(SEED) -e FLAG=flag{TESTflag1234} ${CHAL_NAME}\:challenge" > log 2>&1 &
	docker run --rm -it -e CHAL_HOST=${CHAL_HOST} -e CHAL_PORT=${CHAL_PORT} ${CHAL_NAME}:solver
	#docker run -it --rm -e "HOST=$(CHAL_HOST)" -e "PORT=$(CHAL_PORT)" -e "TICKET=$(TICKET)" $(CHAL_NAME):solver

.PHONY:test-aws
test-aws:
	docker run -it --rm -e "CHAL_HOST=$(EC2_QA)" -e "CHAL_PORT=50001" -e "TICKET=$(TICKET)" $(CHAL_NAME):solver

.PHONY:prod
prod:
	docker login registry:443
	docker pull registry.mlb.cromulence.com/has2/quals/challenges/$(CHAL_NAME)/$(CHAL_NAME):challenge
	docker image tag registry.mlb.cromulence.com/has2/quals/challenges/$(CHAL_NAME)/$(CHAL_NAME):challenge registry:443/$(CHAL_NAME):challenge
	docker push registry:443/$(CHAL_NAME):challenge

.PHONY:prod_test
prod_test:
	docker run -it -e CHAL_HOST=${PROD_HOST} -e CHAL_PORT=${PROD_PORT} -e "TICKET=$(DEMO_TICKET)" ${CHAL_NAME}:solver