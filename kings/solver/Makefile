
CC=gcc


IDIR =./include
CFLAGS=-I$(IDIR) -g -no-pie -fno-stack-protector

ODIR=obj
SDIR=src

all: build payload.bin py

py: solver.py
	python3 solver.py exploit.bin

payload.bin: src/payload.c
	$(CC) -c src/payload.c -fno-stack-protector -pie -o obj/payload.o
	objcopy -O binary --only-section=.text obj/payload.o $@

build:
	mkdir -p obj

.PHONY: clean

clean:
	rm -f $(ODIR)/*.o *~ core $(INCDIR)/*~ 
	rm -f *.bin
