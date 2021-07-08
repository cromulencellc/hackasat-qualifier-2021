CHAL_NAME ?= mongoose_mayhem
CHAL_PORT ?= 19020
CHAL_HOST ?= 172.17.0.1
SERVICE_PORT ?= 19021
SERVICE_HOST ?= 172.17.0.1
AWS_PORT ?= 50012
 
FLAG ?= flag{zulu49225delta\:GG1EnNVMK3-hPvlNKAdEJxcujvp9WK4rEchuEdlDp3yv_Wh_uvB5ehGq-fyRowvwkWpdAMTKbidqhK4JhFsaz1k}
TICKET ?= ticket{zulu10571quebec:GKP9suZz2eyyEpgOpgn1fvN67EpR2MYxvtrAdVfdUtPjBA1w0QSGxD9cWz4grDWaOg}

.PHONY: challenge solver test
all : challenge solver 

challenge:
	docker build -f challenge/Dockerfile challenge -t ${CHAL_NAME}:challenge
solver:
	docker build -f solver/Dockerfile solver -t ${CHAL_NAME}:solver

test_aws: 
	docker run --network=host --rm -it -e CHAL_HOST=${AWS_HOST} -e CHAL_PORT=${AWS_PORT}  -e TICKET=${TICKET} ${CHAL_NAME}:solver

test: 
	socat tcp-listen:19020,reuseaddr exec:"docker run --rm -i -e SERVICE_HOST=${SERVICE_HOST} -e SERVICE_PORT=${SERVICE_PORT} -e FLAG=${FLAG} -p 19021\:3000 ${CHAL_NAME}\:challenge" & 
	docker run --rm -it -e CHAL_HOST=${CHAL_HOST} -e CHAL_PORT=${CHAL_PORT} ${CHAL_NAME}:solver

prod:
	#docker login registry:443
	#docker pull registry.mlb.cromulence.com/has2/quals/challenges/$(CHAL_NAME)/$(CHAL_NAME):challenge
	#docker image tag registry.mlb.cromulence.com/has2/quals/challenges/$(CHAL_NAME)/$(CHAL_NAME):challenge registry:443/$(CHAL_NAME):challenge
	#docker push registry:443/$(CHAL_NAME):challenge
	docker image tag mongoose_mayhem:challenge registry:443/mongoose:challenge
	docker push registry:443/mongoose:challenge