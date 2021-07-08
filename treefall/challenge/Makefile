
CC=g++

$(ODIR)/%.o: $(SDIR)/%.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

all: challenge

challenge: src/parser.c
	$(CC) src/parser.c -o $@

.PHONY: clean

clean:
	rm -f challenge
