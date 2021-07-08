CHAL_NAME ?= fprime-exploitation
CHAL_PORT ?= 12345
CHAL_PORT2 ?= 12346
CHAL_HOST ?= 172.17.0.1
FLAG ?= flag{test123test123987654321qwertyuiopasdfghjkl1234567890}
CHAL_TIMEOUT ?= 900
TEST_TIMEOUT ?= 120
TEST_PORT ?= 50015
PROD_PORT ?= 5015
DEMO_TICKET ?= ticket{juliet343927mike2:GEBzWTfWh4Tio_CWH13k90Se9s_L--y6jgKGJPNpNQH8k1ie6sg8CbJKgAIkhtf-Kg}

build: challenge solver
TICKET ?= ticket{zulu10571quebec:GKP9suZz2eyyEpgOpgn1fvN67EpR2MYxvtrAdVfdUtPjBA1w0QSGxD9cWz4grDWaOg}

.PHONY:challenge
challenge:
	docker build challenge -t $(CHAL_NAME):challenge
	docker tag $(CHAL_NAME):challenge registry.mlb.cromulence.com/has2/quals/challenges/$(CHAL_NAME)/$(CHAL_NAME):challenge

.PHONY:solver
solver: 
	docker build solver -t $(CHAL_NAME):solver
	docker tag $(CHAL_NAME):solver registry.mlb.cromulence.com/has2/quals/challenges/$(CHAL_NAME)/$(CHAL_NAME):solver

.PHONY:test
test:
	socat -v tcp-listen:$(CHAL_PORT),reuseaddr exec:"docker run -i --rm -p $(CHAL_PORT)\:5000 -p $(CHAL_PORT2)\:5001 -e SERVICE_HOST=$(CHAL_HOST) -e SERVICE_PORT=$(CHAL_PORT) -e FLAG=$(FLAG) -e TIMEOUT=$(TEST_TIMEOUT) registry.mlb.cromulence.com/has2/quals/challenges/$(CHAL_NAME)/$(CHAL_NAME)\:challenge" > log2>&1 &
	docker run -it --rm -e CHAL_HOST=$(CHAL_HOST) -e CHAL_PORT=$(CHAL_PORT) registry.mlb.cromulence.com/has2/quals/challenges/$(CHAL_NAME)/$(CHAL_NAME):solver

.PHONY:test-aws
test-aws:
	docker run -it --rm -e "CHAL_HOST=$(EC2_QA)" -e "CHAL_PORT=50015" -e "TICKET=$(TICKET)" $(CHAL_NAME):solver

.PHONY:prod
prod:
	docker login registry:443
	docker pull registry.mlb.cromulence.com/has2/quals/challenges/$(CHAL_NAME)/$(CHAL_NAME):challenge
	docker image tag registry.mlb.cromulence.com/has2/quals/challenges/$(CHAL_NAME)/$(CHAL_NAME):challenge registry:443/$(CHAL_NAME):challenge
	docker push registry:443/$(CHAL_NAME):challenge

.PHONY:prod_test
prod_test:
	docker run -it -e CHAL_HOST=${PROD_HOST} -e CHAL_PORT=${PROD_PORT} -e "TICKET=$(DEMO_TICKET)" ${CHAL_NAME}:solver
