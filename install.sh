#!/bin/bash
#
# Darknet Framework - Installation Script
# Automated installation for Debian/Ubuntu, Red Hat/CentOS/Fedora, and Arch Linux
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
cat << "EOF"
██████╗  █████╗ ██████╗ ██╗  ██╗███╗   ██╗███████╗████████╗
██╔══██╗██╔══██╗██╔══██╗██║ ██╔╝████╗  ██║██╔════╝╚══██╔══╝
██║  ██║███████║██████╔╝█████╔╝ ██╔██╗ ██║█████╗     ██║
██║  ██║██╔══██║██╔══██╗██╔═██╗ ██║╚██╗██║██╔══╝     ██║
██████╔╝██║  ██║██║  ██║██║  ██╗██║ ╚████║███████╗   ██║
╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝

Darknet Framework - Installation Script
EOF
echo -e "${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}[!] This script must be run as root${NC}"
    echo -e "${YELLOW}[*] Please run: sudo $0${NC}"
    exit 1
fi

echo -e "${GREEN}[*] Starting Darknet installation...${NC}\n"

# Detect OS
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        VER=$VERSION_ID
    elif [ -f /etc/redhat-release ]; then
        OS="rhel"
    else
        OS=$(uname -s)
    fi
    echo -e "${BLUE}[*] Detected OS: $OS${NC}"
}

# Install dependencies based on OS
install_dependencies() {
    echo -e "${GREEN}[*] Installing dependencies...${NC}"

    case "$OS" in
        ubuntu|debian)
            apt-get update
            apt-get install -y build-essential gcc make libpcap-dev git
            ;;
        fedora)
            dnf install -y gcc make libpcap-devel git
            ;;
        centos|rhel)
            yum install -y gcc make libpcap-devel git
            ;;
        arch|manjaro)
            pacman -S --noconfirm gcc make libpcap git
            ;;
        *)
            echo -e "${YELLOW}[!] Unsupported OS. Please install manually:${NC}"
            echo "    - gcc compiler"
            echo "    - make"
            echo "    - libpcap-dev/libpcap-devel"
            echo "    - git"
            exit 1
            ;;
    esac

    echo -e "${GREEN}[✓] Dependencies installed${NC}"
}

# Build the framework
build_framework() {
    echo -e "${GREEN}[*] Building Darknet framework...${NC}"

    # Clean previous builds
    make clean 2>/dev/null || true

    # Build
    if make; then
        echo -e "${GREEN}[✓] Build successful${NC}"
    else
        echo -e "${RED}[!] Build failed${NC}"
        exit 1
    fi
}

# Install to system
install_to_system() {
    echo -e "${GREEN}[*] Installing to /usr/local/bin...${NC}"

    # Install binary
    install -m 755 bin/darknet /usr/local/bin/darknet

    # Create man page directory if it doesn't exist
    mkdir -p /usr/local/share/man/man1

    # Create documentation directory
    mkdir -p /usr/local/share/doc/darknet
    cp README.md LICENSE ETHICAL_GUIDELINES.md /usr/local/share/doc/darknet/

    echo -e "${GREEN}[✓] Darknet installed successfully${NC}"
}

# Create uninstall script
create_uninstall() {
    echo -e "${GREEN}[*] Creating uninstall script...${NC}"

    cat > /usr/local/bin/darknet-uninstall << 'UNINSTALL_EOF'
#!/bin/bash
# Darknet Framework Uninstall Script

if [ "$EUID" -ne 0 ]; then
    echo "[!] This script must be run as root"
    echo "[*] Please run: sudo darknet-uninstall"
    exit 1
fi

echo "[*] Uninstalling Darknet framework..."
rm -f /usr/local/bin/darknet
rm -rf /usr/local/share/doc/darknet
rm -f /usr/local/bin/darknet-uninstall
echo "[✓] Darknet uninstalled successfully"
UNINSTALL_EOF

    chmod +x /usr/local/bin/darknet-uninstall
    echo -e "${GREEN}[✓] Uninstall script created at /usr/local/bin/darknet-uninstall${NC}"
}

# Verify installation
verify_installation() {
    echo -e "${GREEN}[*] Verifying installation...${NC}"

    if command -v darknet &> /dev/null; then
        echo -e "${GREEN}[✓] Darknet is installed and accessible${NC}"
        echo -e "${BLUE}[*] Version: $(darknet version 2>&1 | grep "Darknet version" || echo "Unable to get version")${NC}"
    else
        echo -e "${RED}[!] Installation verification failed${NC}"
        exit 1
    fi
}

# Display post-install message
post_install_message() {
    echo -e "\n${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║         Darknet Framework Installed Successfully       ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}\n"

    echo -e "${YELLOW}⚠️  IMPORTANT LEGAL NOTICE:${NC}"
    echo -e "   This tool is for ${RED}AUTHORIZED TESTING ONLY${NC}"
    echo -e "   Unauthorized use is ${RED}ILLEGAL${NC} and may result in prosecution\n"

    echo -e "${BLUE}Quick Start:${NC}"
    echo -e "  • Run: ${GREEN}darknet help${NC}        - Show help"
    echo -e "  • Run: ${GREEN}darknet modules${NC}     - List all modules"
    echo -e "  • Run: ${GREEN}sudo darknet <module>${NC} - Use a module (requires root)\n"

    echo -e "${BLUE}Documentation:${NC}"
    echo -e "  • /usr/local/share/doc/darknet/README.md"
    echo -e "  • /usr/local/share/doc/darknet/ETHICAL_GUIDELINES.md\n"

    echo -e "${BLUE}Uninstall:${NC}"
    echo -e "  • Run: ${GREEN}sudo darknet-uninstall${NC}\n"

    echo -e "${YELLOW}Please read the ethical guidelines before using this tool!${NC}\n"
}

# Main installation flow
main() {
    detect_os
    install_dependencies
    build_framework
    install_to_system
    create_uninstall
    verify_installation
    post_install_message
}

# Run installation
main
