CC = gcc
CFLAGS = -Wall -Wextra -O2
TARGET = deauth

all: $(TARGET)

$(TARGET): deauth.c
	$(CC) $(CFLAGS) -o $(TARGET) deauth.c

clean:
	rm -f $(TARGET)

install: $(TARGET)
	install -m 755 $(TARGET) /usr/local/bin/

uninstall:
	rm -f /usr/local/bin/$(TARGET)

.PHONY: all clean install uninstall
