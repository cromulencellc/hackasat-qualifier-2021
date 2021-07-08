CC=gcc
INCLUDES=-lssl -lcrypto -lpthread

IDAR=./include
CFLAGS=-I$(IDAR) -Wall -no-pie

_DEPS = interface.h
DEPS = $(patsubst %,$(IDIR)/%,$(_DEPS))

_SRC = interface.c
SRC = $(patsubst %,$(SDIR)/%,$(_SRC)

_OBJ = $(patsubst %.c,%.o,$(_SRC)) 
OBJ = $(patsubst %,$(ODIR)/%,$(_OBJ))

TARGET = challenge

all: $(TARGET)

challenge: src/interface.c
	$(CC) -o $@ $^ $(CFLAGS) $(LIBS) $(INCLUDES)
	# strip $@

clean:
	$(RM) $(TARGET) $(TARGET).o
