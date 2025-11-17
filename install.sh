#!/bin/bash

# DarkWiFi Installation Script
# Creates a virtual environment and sets up global access

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║               DarkWiFi Installation Script                    ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}[!] Please do NOT run this script as root${NC}"
    echo -e "${YELLOW}[*] The tool will ask for sudo when needed${NC}"
    exit 1
fi

INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$INSTALL_DIR/venv"
BIN_LINK="/usr/local/bin/darkwifi"

echo -e "${CYAN}[*] Installation directory: $INSTALL_DIR${NC}"
echo

# Check for Python 3
echo -e "${CYAN}[*] Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[!] Python 3 is not installed${NC}"
    echo -e "${YELLOW}[*] Install with: sudo apt-get install python3 python3-venv python3-pip${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}[✓] Found: $PYTHON_VERSION${NC}"

# Install system dependencies
echo
echo -e "${CYAN}[*] Checking system dependencies...${NC}"
MISSING_DEPS=()

check_tool() {
    if ! command -v "$1" &> /dev/null; then
        MISSING_DEPS+=("$1")
        return 1
    fi
    return 0
}

check_tool "airmon-ng" || true
check_tool "airodump-ng" || true
check_tool "aireplay-ng" || true
check_tool "aircrack-ng" || true

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo -e "${YELLOW}[!] Missing system dependencies:${NC}"
    for dep in "${MISSING_DEPS[@]}"; do
        echo "    - $dep"
    done
    echo
    echo -e "${CYAN}[*] Installing dependencies...${NC}"
    sudo apt-get update
    sudo apt-get install -y aircrack-ng
fi

# Optional tools
echo
echo -e "${CYAN}[*] Checking optional tools...${NC}"
check_tool "hcxdumptool" && echo -e "${GREEN}[✓] hcxdumptool found${NC}" || echo -e "${YELLOW}[!] hcxdumptool not found (optional)${NC}"
check_tool "hcxpcapngtool" && echo -e "${GREEN}[✓] hcxpcapngtool found${NC}" || echo -e "${YELLOW}[!] hcxpcapngtool not found (optional)${NC}"
check_tool "hashcat" && echo -e "${GREEN}[✓] hashcat found${NC}" || echo -e "${YELLOW}[!] hashcat not found (optional)${NC}"

# Create virtual environment
echo
echo -e "${CYAN}[*] Creating virtual environment...${NC}"
if [ -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}[*] Virtual environment already exists, removing...${NC}"
    rm -rf "$VENV_DIR"
fi

python3 -m venv "$VENV_DIR"
echo -e "${GREEN}[✓] Virtual environment created${NC}"

# Activate venv and install Python dependencies
echo
echo -e "${CYAN}[*] Installing Python dependencies...${NC}"
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r "$INSTALL_DIR/requirements.txt"
deactivate
echo -e "${GREEN}[✓] Python dependencies installed${NC}"

# Create global launcher script
echo
echo -e "${CYAN}[*] Creating global launcher...${NC}"

LAUNCHER_SCRIPT="$INSTALL_DIR/darkwifi_launcher.sh"
cat > "$LAUNCHER_SCRIPT" << 'EOFLAUNCH'
#!/bin/bash

# DarkWiFi Global Launcher
# Activates venv and runs the tool

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "\033[0;31m[!] DarkWiFi requires root privileges\033[0m"
    echo -e "\033[1;33m[*] Please run with: sudo darkwifi [options]\033[0m"
    exit 1
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Run the tool with all arguments
python3 "$SCRIPT_DIR/darkwifi.py" "$@"

# Deactivate when done
deactivate
EOFLAUNCH

chmod +x "$LAUNCHER_SCRIPT"
chmod +x "$INSTALL_DIR/darkwifi.py"

# Create symbolic link
echo -e "${CYAN}[*] Creating global command 'darkwifi'...${NC}"
if [ -L "$BIN_LINK" ] || [ -f "$BIN_LINK" ]; then
    echo -e "${YELLOW}[*] Removing existing link...${NC}"
    sudo rm -f "$BIN_LINK"
fi

sudo ln -s "$LAUNCHER_SCRIPT" "$BIN_LINK"
echo -e "${GREEN}[✓] Global command created${NC}"

# Create directories
echo
echo -e "${CYAN}[*] Creating working directories...${NC}"
mkdir -p "$INSTALL_DIR/captures"
mkdir -p "$INSTALL_DIR/wordlists"
mkdir -p "$INSTALL_DIR/cracked"
echo -e "${GREEN}[✓] Directories created${NC}"

# Success message
echo
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                               ║${NC}"
echo -e "${GREEN}║              Installation completed successfully!             ║${NC}"
echo -e "${GREEN}║                                                               ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo
echo -e "${CYAN}[*] DarkWiFi is now installed and ready to use!${NC}"
echo
echo -e "${YELLOW}Usage:${NC}"
echo -e "  ${GREEN}sudo darkwifi --interface wlan0 --scan${NC}"
echo -e "  ${GREEN}sudo darkwifi -i wlan0 --auto${NC}"
echo -e "  ${GREEN}sudo darkwifi -i wlan0 --handshake --target \"MyNetwork\" --crack --personal${NC}"
echo
echo -e "${YELLOW}Help:${NC}"
echo -e "  ${GREEN}darkwifi --help${NC}"
echo
echo -e "${CYAN}[*] Installation location: $INSTALL_DIR${NC}"
echo -e "${CYAN}[*] Virtual environment: $VENV_DIR${NC}"
echo -e "${CYAN}[*] Global command: $BIN_LINK${NC}"
echo
