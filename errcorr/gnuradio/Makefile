VERSION=3.7
build: gnuradio

.PHONY:gnuradio
gnuradio:
	docker build . -t gnuradio:${VERSION}

.PHONY:run
run:
	xhost +local:root
	docker run \
	--privileged \
	--net=host \
	--env="DISPLAY" \
	--volume="${HOME}/.Xauthority:/root/.Xauthority:rw" \
	--device /dev/snd \
	-v ${PWD}/flowgraphs:/flowgraphs \
	--group-add=audio \
	-it gnuradio:${VERSION} bash
	xhost -local:root
