CC=g++
CFLAGS=-Wall
LDFLAGS=-lpthread
SRCS=$(wildcard *.cpp)
OBJS=$(SRCS:.cpp=.o)

BIN=challenge

build: $(BIN)

$(BIN): $(OBJS)
	$(CC) $(CFLAGS) $< -o $@ $(LDFLAGS)
