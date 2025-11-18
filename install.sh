#!/bin/bash

###############################################################################
# Darknet Device Scanner - Installation Script
# For Linux/Kali/Raspberry Pi
###############################################################################

set -e  # Exit on error

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║         Darknet Counter-Intelligence Device Scanner         ║"
echo "║                    Installation Script                       ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "⚠️  Warning: This script is designed for Linux systems"
    echo "Detected OS: $OSTYPE"
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install system packages
install_system_packages() {
    echo "[*] Installing system dependencies..."

    if command_exists apt-get; then
        # Debian/Ubuntu/Kali/Raspberry Pi OS
        sudo apt-get update

        echo "    Installing wireless tools..."
        sudo apt-get install -y wireless-tools iw aircrack-ng

        echo "    Installing Bluetooth tools..."
        sudo apt-get install -y bluez bluetooth

        echo "    Installing Python development tools..."
        sudo apt-get install -y python3 python3-pip python3-venv python3-dev

        echo "    Installing build essentials..."
        sudo apt-get install -y build-essential libpcap-dev libffi-dev libssl-dev

        echo "✓ System packages installed"
    elif command_exists yum; then
        # RedHat/CentOS/Fedora
        echo "    Installing for RedHat-based system..."
        sudo yum install -y wireless-tools iw aircrack-ng bluez python3 python3-devel gcc libpcap-devel
        echo "✓ System packages installed"
    elif command_exists pacman; then
        # Arch Linux
        echo "    Installing for Arch Linux..."
        sudo pacman -S --noconfirm wireless_tools iw aircrack-ng bluez bluez-utils python python-pip base-devel libpcap
        echo "✓ System packages installed"
    else
        echo "⚠️  Could not detect package manager. Please install manually:"
        echo "    - wireless-tools, iw, aircrack-ng"
        echo "    - bluez, bluetooth"
        echo "    - python3, python3-pip, python3-venv"
        echo "    - build-essential, libpcap-dev"
        read -p "Continue anyway? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Function to create virtual environment
create_venv() {
    echo ""
    echo "[*] Creating Python virtual environment..."

    if [ -d "venv" ]; then
        echo "    Virtual environment already exists"
        read -p "    Recreate it? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf venv
            python3 -m venv venv
            echo "✓ Virtual environment recreated"
        fi
    else
        python3 -m venv venv
        echo "✓ Virtual environment created"
    fi
}

# Function to install Python packages
install_python_packages() {
    echo ""
    echo "[*] Installing Python packages..."

    source venv/bin/activate

    echo "    Upgrading pip..."
    pip install --upgrade pip

    echo "    Installing required packages..."
    pip install -r requirements.txt

    echo "✓ Python packages installed"
    deactivate
}

# Function to set up directories
setup_directories() {
    echo ""
    echo "[*] Setting up directories..."

    mkdir -p data logs
    chmod 755 data logs

    echo "✓ Directories created"
}

# Function to make scripts executable
make_executable() {
    echo ""
    echo "[*] Making scripts executable..."

    chmod +x darknet.py
    chmod +x install.sh

    echo "✓ Scripts are now executable"
}

# Function to check Bluetooth service
check_bluetooth() {
    echo ""
    echo "[*] Checking Bluetooth service..."

    if systemctl is-active --quiet bluetooth; then
        echo "✓ Bluetooth service is running"
    else
        echo "    Bluetooth service not running. Starting..."
        sudo systemctl start bluetooth
        sudo systemctl enable bluetooth
        echo "✓ Bluetooth service started"
    fi
}

# Function to create launcher script
create_launcher() {
    echo ""
    echo "[*] Creating launcher script..."

    cat > run.sh << 'EOF'
#!/bin/bash
# Darknet launcher script

cd "$(dirname "$0")"
source venv/bin/activate
sudo -E python3 darknet.py "$@"
EOF

    chmod +x run.sh
    echo "✓ Launcher script created: ./run.sh"
}

# Main installation
main() {
    echo "This script will install:"
    echo "  • System packages (wireless-tools, aircrack-ng, bluez, etc.)"
    echo "  • Python virtual environment"
    echo "  • Required Python packages"
    echo ""
    echo "Note: Root/sudo privileges required for system packages"
    echo ""
    read -p "Continue with installation? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled"
        exit 0
    fi

    echo ""
    echo "Starting installation..."
    echo ""

    # Run installation steps
    install_system_packages
    create_venv
    install_python_packages
    setup_directories
    make_executable
    check_bluetooth
    create_launcher

    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                                                              ║"
    echo "║                  Installation Complete! ✓                   ║"
    echo "║                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Quick Start:"
    echo ""
    echo "  1. Run with launcher (recommended):"
    echo "     ./run.sh"
    echo ""
    echo "  2. Or activate venv and run directly:"
    echo "     source venv/bin/activate"
    echo "     sudo python3 darknet.py"
    echo ""
    echo "  3. Run without privilege check (not recommended):"
    echo "     ./run.sh --no-privilege-check"
    echo ""
    echo "For full functionality, always run with sudo/root privileges!"
    echo ""
    echo "Type 'help' in the interactive prompt for available commands"
    echo ""
}

# Run main installation
main
