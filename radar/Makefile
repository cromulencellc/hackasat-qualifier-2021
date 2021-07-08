CHAL_NAME ?= radar
CHAL_PORT ?= 12345
CHAL_HOST ?= 172.17.0.1
TICKET ?= ticket{zulu10571quebec:GKP9suZz2eyyEpgOpgn1fvN67EpR2MYxvtrAdVfdUtPjBA1w0QSGxD9cWz4grDWaOg}
FLAG ?= flag{zulu49225delta\:GG1EnNVMK3-hPvlNKAdEJxcujvp9WK4rEchuEdlDp3yv_Wh_uvB5ehGq-fyRowvwkWpdAMTKbidqhK4JhFsaz1k}
SEED ?= 1465500232115169100
TEST_PORT ?= 50021
PROD_PORT ?= 5021
DEMO_TICKET ?= ticket{november171186romeo2:GDNTb-M6gjVS-I9XVyQJYu5SGJJQU12uF6nQeiLsEW77VtMjwerh10VmEd5dBlPxMA}

build: challenge solver

.PHONY:challenge
challenge:
	$(COPY_FILE_CHALLENGE)
	docker build challenge -t $(CHAL_NAME):challenge

.PHONY:solver
solver: 
	$(COPY_FILE_CHALLENGE)
	docker build solver -t $(CHAL_NAME):solver

.PHONY:test
test:
	socat -v tcp-listen:$(CHAL_PORT),reuseaddr exec:"docker run --rm -i -e FLAG=${FLAG} ${CHAL_NAME}\:challenge" > log 2>&1 &
	docker run --rm -it -e CHAL_HOST=${CHAL_HOST} -e CHAL_PORT=${CHAL_PORT} ${CHAL_NAME}:solver

.PHONY:test-aws
test-aws:
	docker run -it --rm -e "CHAL_HOST=$(EC2_QA)" -e "CHAL_PORT=$(TEST_PORT)" -e "TICKET=$(TICKET)" $(CHAL_NAME):solver

.PHONY:prod
prod:
	docker login registry:443
	docker pull registry.mlb.cromulence.com/has2/quals/challenges/$(CHAL_NAME)/$(CHAL_NAME):challenge
	docker image tag registry.mlb.cromulence.com/has2/quals/challenges/$(CHAL_NAME)/$(CHAL_NAME):challenge registry:443/$(CHAL_NAME):challenge
	docker push registry:443/$(CHAL_NAME):challenge

.PHONY:prod_test
prod_test:
	docker run -it -e CHAL_HOST=${PROD_HOST} -e CHAL_PORT=${PROD_PORT} -e "TICKET=$(DEMO_TICKET)" ${CHAL_NAME}:solver