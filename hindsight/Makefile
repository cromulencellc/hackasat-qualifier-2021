CHAL_NAME ?= hindsight
CHAL_PORT ?= 31318
CHAL_HOST ?= 172.17.0.1

TICKET ?= ticket{zulu10571quebec:GKP9suZz2eyyEpgOpgn1fvN67EpR2MYxvtrAdVfdUtPjBA1w0QSGxD9cWz4grDWaOg}
build: challenge solver generator

PROD_PORT ?= 5002
DEMO_TICKET ?= ticket{xray668545kilo2:GFKdoCH8hty0zu__JWeIDQNsVyvKinB_INcUGgarMqZpExDPPAZCugnE9ERbANN5tw}


.PHONY:challenge
challenge:
	docker build challenge -t ${CHAL_NAME}:challenge

.PHONY:solver
solver:
	docker build solver -t ${CHAL_NAME}:solver

.PHONY:generator
generator:
	docker build generator -t ${CHAL_NAME}:generator

.PHONY:solve
solve:
	docker run -it --rm -e "HOST=${CHAL_HOST}" -e "PORT=${CHAL_PORT}"  -e DIR=/test -v $(PWD)/test:/test ${CHAL_NAME}:solver

.PHONY:static
static:
	docker run --rm -v $(PWD)/static:/out ${CHAL_NAME}:generator

.PHONY:test
test:
	socat -v tcp-listen:19111,reuseaddr exec:"docker run --rm -i -e SEED=6601828937469666254 -e FLAG=flag{0cUlArMot1oNM4ng} hindsight\:challenge" > log 2>&1 &
	docker run --rm -e HOST=${CHAL_HOST} -e PORT=19111 -e DIR=/test -v $(PWD)/static:/test  ${CHAL_NAME}:solver


.PHONY:test-final
test-final:
	docker run --rm -e HOST=spacebook.satellitesabove.me -e PORT=5015 -e DIR=/mnt -v $(PWD)/final:/mnt -e TICKET=ticket{bravo41877echo:GITCUJzbd2EcRb0FDJOAi-AMOqfr2QQAvgjyTykD0YdU2LDRCTbfej84TDAVJ4wi-Q} ${CHAL_NAME}:solver

.PHONY:test-aws
test-aws:
	docker run --rm -e HOST=${EC2_QA} -e PORT=50002 -e DIR=/mnt -v $(PWD)/test:/mnt -e TICKET=$(TICKET) ${CHAL_NAME}:solver

.PHONY:prod
prod:
	docker login registry
	docker pull registry.mlb.cromulence.com/has2/quals/challenges/$(CHAL_NAME)/$(CHAL_NAME):challenge
	docker image tag registry.mlb.cromulence.com/has2/quals/challenges/$(CHAL_NAME)/$(CHAL_NAME):challenge registry/$(CHAL_NAME):challenge
	docker push registry/$(CHAL_NAME):challenge

	
.PHONY:prod_test
prod_test:
	docker run -it -e HOST=${PROD_HOST} -e DIR=/mnt -v $(PWD)/static:/mnt -e PORT=${PROD_PORT} -e "TICKET=$(DEMO_TICKET)" ${CHAL_NAME}:solver
