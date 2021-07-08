CHAL_NAME ?= marsorbust
CHAL_PORT ?= 19020
CHAL_HOST ?= 172.17.0.1
SERVICE_PORT ?= 19021
SERVICE_HOST ?= 172.17.0.1

TICKET ?= ticket{zulu10571quebec:GKP9suZz2eyyEpgOpgn1fvN67EpR2MYxvtrAdVfdUtPjBA1w0QSGxD9cWz4grDWaOg}A
FLAG ?= flag{zulu49225delta\:GG1EnNVMK3-hPvlNKAdEJxcujvp9WK4rEchuEdlDp3yv_Wh_uvB5ehGq-fyRowvwkWpdAMTKbidqhK4JhFsaz1k}

.PHONY: challenge solver test
all : challenge solver 

challenge:
	docker build -f challenge/Dockerfile challenge -t ${CHAL_NAME}:challenge
solver:
	docker build -f solver/Dockerfile solver -t ${CHAL_NAME}:solver

test: 
	socat tcp-listen:19020,reuseaddr exec:"docker run --rm -i -e SERVICE_HOST=${SERVICE_HOST} -e SERVICE_PORT=${SERVICE_PORT} -e FLAG=${FLAG} -p 19021\:3000 ${CHAL_NAME}\:challenge" & 
	docker run --rm -it -e HOST=${CHAL_HOST} -e PORT=${CHAL_PORT} ${CHAL_NAME}:solver
.PHONY: test_aws
test_aws:
	docker run -it --rm -e "HOST=${EC2_QA}" -e "PORT=50012" -e "TICKET=ticket{zulu10571quebec:GKP9suZz2eyyEpgOpgn1fvN67EpR2MYxvtrAdVfdUtPjBA1w0QSGxD9cWz4grDWaOg}" ${CHAL_NAME}:solver
