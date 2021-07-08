CHAL_NAME ?= kings
CHAL_PORT ?= 19020
CHAL_HOST ?= 172.17.0.1
SERVICE_PORT ?= 19021
PROD_HOST ?= wealthy-rock.satellitesabove.me
PROD_PORT ?= 5010
DEMO_TICKET ?= ticket{delta515313juliet2:GHO2tLbmYvYQgLKOcBWhQ6PK89C3Ug6eqMF3WHwuUjbaINxgYe45dnwplS05FLCCQA}

TICKET ?= ticket{zulu10571quebec:GKP9suZz2eyyEpgOpgn1fvN67EpR2MYxvtrAdVfdUtPjBA1w0QSGxD9cWz4grDWaOg}A
FLAG ?= flag{zulu49225delta\:GG1EnNVMK3-hPvlNKAdEJxcujvp9WK4rEchuEdlDp3yv_Wh_uvB5ehGq-fyRowvwkWpdAMTKbidqhK4JhFsaz1k}

.PHONY: challenge solver generator test
all : challenge solver generator static

challenge:
	docker build -f challenge/Dockerfile challenge -t ${CHAL_NAME}:challenge
solver:
	docker build -f solver/Dockerfile solver -t ${CHAL_NAME}:solver
generator: 
	docker build -f challenge/Dockerfile_generator challenge -t ${CHAL_NAME}:generator
static:
	mkdir -p static
	docker run --rm -v ${PWD}/static:/out ${CHAL_NAME}:generator

test: 
	socat -v tcp-listen:19020,reuseaddr exec:"docker run --rm -i -e SERVICE_HOST=${CHAL_HOST} -e SERVICE_PORT=${SERVICE_PORT} -e FLAG=$(FLAG) -p ${SERVICE_PORT}\:54321 ${CHAL_NAME}\:challenge" > log 2>&1 &
	docker run --rm -i -e CHAL_HOST=${CHAL_HOST} -e CHAL_PORT=${CHAL_PORT} ${CHAL_NAME}:solver

.PHONY:test-aws
test-aws:
	docker run -it --rm -e "CHAL_HOST=$(EC2_QA)" -e "CHAL_PORT=50010" -e "TICKET=$(TICKET)" $(CHAL_NAME):solver

.PHONY:prod
prod:
	docker login registry
	docker pull registry.mlb.cromulence.com/has2/quals/challenges/$(CHAL_NAME)/$(CHAL_NAME):challenge
	docker image tag registry.mlb.cromulence.com/has2/quals/challenges/$(CHAL_NAME)/$(CHAL_NAME):challenge registry:443/$(CHAL_NAME):challenge
	docker push registry/$(CHAL_NAME):challenge

.PHONY:prod_test
prod_test:
	docker run -it -e CHAL_HOST=${PROD_HOST} -e CHAL_PORT=${PROD_PORT} -e "TICKET=$(DEMO_TICKET)" ${CHAL_NAME}:solver