
CC=gcc


IDIR =./include
CFLAGS=-I$(IDIR) -no-pie -fno-stack-protector

ODIR=obj
SDIR=src
LDIR =../lib

_DEPS = common.h msg.h link.h mem.h tlm.h
DEPS = $(patsubst %,$(IDIR)/%,$(_DEPS))

_SRC = msg.c link.c main.c mem.c tlm.c
SRC = $(patsubst %,$(SDIR)/%,$(_SRC)

_OBJ = $(patsubst %.c,%.o,$(_SRC)) 
OBJ = $(patsubst %,$(ODIR)/%,$(_OBJ))


$(ODIR)/%.o: $(SDIR)/%.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

all: build challenge exploit.bin runner

runner: src/runner.c
	$(CC) -o $@ $^ $(CFLAGS)

challenge: $(OBJ)
	$(CC) -o $@ $^ $(CFLAGS) $(LIBS)
	strip $@ 

payload1.bin: src/payload1.c
	$(CC) -c src/payload1.c -fno-stack-protector -pie -o obj/payload1.o
	objcopy -O binary --only-section=.text obj/payload1.o $@

payload2.bin: src/payload2.c
	$(CC) -c src/payload2.c -fno-stack-protector -pie -o obj/payload2.o
	objcopy -O binary --only-section=.text obj/payload2.o $@

exploit.bin: payload1.bin payload2.bin src/payload.py
	python3 src/payload.py

build:
	mkdir -p obj

.PHONY: clean

clean:
	rm -f $(ODIR)/*.o *~ core $(INCDIR)/*~ 
	rm -f *.bin *.bin challenge
