# Darknet - Network Pentesting Framework
# Makefile

CC = gcc
CFLAGS = -Wall -Wextra -O2 -Iinclude -pthread -Wno-unused-parameter
LDFLAGS = -pthread -lm
# Uncomment to enable libpcap (requires libpcap-dev installed)
# LDFLAGS += -lpcap
DEBUG_FLAGS = -g -DDEBUG -O0
RELEASE_FLAGS = -O3 -DNDEBUG

# Directories
SRC_DIR = src
INC_DIR = include
OBJ_DIR = obj
BIN_DIR = bin

# Target executable
TARGET = $(BIN_DIR)/darknet

# Source files
SOURCES = $(wildcard $(SRC_DIR)/*.c) \
          $(wildcard $(SRC_DIR)/wifi/*.c) \
          $(wildcard $(SRC_DIR)/scan/*.c) \
          $(wildcard $(SRC_DIR)/arp/*.c) \
          $(wildcard $(SRC_DIR)/stress/*.c) \
          $(wildcard $(SRC_DIR)/packet/*.c)

# Object files
OBJECTS = $(SOURCES:$(SRC_DIR)/%.c=$(OBJ_DIR)/%.o)

# Default target
all: directories $(TARGET)

# Create directories
directories:
	@mkdir -p $(OBJ_DIR)/wifi
	@mkdir -p $(OBJ_DIR)/scan
	@mkdir -p $(OBJ_DIR)/arp
	@mkdir -p $(OBJ_DIR)/stress
	@mkdir -p $(OBJ_DIR)/packet
	@mkdir -p $(BIN_DIR)

# Link executable
$(TARGET): $(OBJECTS)
	@echo "Linking $@..."
	$(CC) $(OBJECTS) -o $@ $(LDFLAGS)
	@echo "Build complete: $@"

# Compile source files
$(OBJ_DIR)/%.o: $(SRC_DIR)/%.c
	@echo "Compiling $<..."
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) -c $< -o $@

# Debug build
debug: CFLAGS += $(DEBUG_FLAGS)
debug: clean all

# Release build
release: CFLAGS += $(RELEASE_FLAGS)
release: clean all

# Install (requires root)
install: release
	@echo "Installing Darknet..."
	install -m 755 $(TARGET) /usr/local/bin/darknet
	@echo "Installation complete. Run 'darknet' to start."

# Uninstall
uninstall:
	@echo "Uninstalling Darknet..."
	rm -f /usr/local/bin/darknet
	@echo "Uninstall complete."

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf $(OBJ_DIR) $(BIN_DIR)
	@echo "Clean complete."

# Clean everything including captures
distclean: clean
	rm -f *.pcap *.cap *.log

# Run with root privileges
run: all
	@if [ "$(shell id -u)" != "0" ]; then \
		echo "Darknet requires root privileges. Run with sudo."; \
		exit 1; \
	fi
	@$(TARGET)

# Help target
help:
	@echo "Darknet Network Pentesting Framework - Build System"
	@echo ""
	@echo "Targets:"
	@echo "  all       - Build the project (default)"
	@echo "  debug     - Build with debug symbols"
	@echo "  release   - Build optimized release version"
	@echo "  install   - Install to /usr/local/bin (requires root)"
	@echo "  uninstall - Remove from /usr/local/bin"
	@echo "  clean     - Remove build artifacts"
	@echo "  distclean - Remove all generated files"
	@echo "  run       - Build and run (requires root)"
	@echo "  help      - Show this help message"
	@echo ""
	@echo "Dependencies: gcc, libpcap-dev, pthread"

.PHONY: all directories debug release install uninstall clean distclean run help
