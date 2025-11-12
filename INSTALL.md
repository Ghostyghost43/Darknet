# Darknet Framework - Installation Guide

This guide covers multiple ways to install and deploy Darknet on your systems.

## Table of Contents
1. [Quick Installation](#quick-installation)
2. [Manual Installation](#manual-installation)
3. [Installing on Another PC](#installing-on-another-pc)
4. [System Requirements](#system-requirements)
5. [Troubleshooting](#troubleshooting)
6. [Uninstallation](#uninstallation)

---

## Quick Installation

### Automated Installation (Recommended)

The easiest way to install Darknet:

```bash
# Clone the repository
git clone https://github.com/codypratt88/Darknet.git
cd Darknet

# Run the installation script
sudo ./install.sh
```

This script will:
- Detect your operating system
- Install all required dependencies
- Build the framework
- Install to `/usr/local/bin`
- Create an uninstall script

### Supported Operating Systems

- ✅ Ubuntu / Debian
- ✅ Fedora
- ✅ CentOS / RHEL
- ✅ Arch Linux / Manjaro
- ✅ Other Linux distributions (manual installation)

---

## Manual Installation

If you prefer to install manually or the automated script doesn't work:

### 1. Install Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install build-essential gcc make libpcap-dev git
```

**Fedora:**
```bash
sudo dnf install gcc make libpcap-devel git
```

**CentOS/RHEL:**
```bash
sudo yum install gcc make libpcap-devel git
```

**Arch Linux:**
```bash
sudo pacman -S gcc make libpcap git
```

### 2. Clone and Build

```bash
# Clone the repository
git clone https://github.com/codypratt88/Darknet.git
cd Darknet

# Build the framework
make

# Optional: Build with debug symbols
make debug

# Optional: Build optimized release
make release
```

### 3. Install System-Wide (Optional)

```bash
sudo make install
```

This installs to `/usr/local/bin/darknet`.

### 4. Run Without Installing

You can also run directly from the build directory:

```bash
sudo ./bin/darknet help
```

---

## Installing on Another PC

There are several methods to deploy Darknet to another computer:

### Method 1: Git Clone (Recommended)

On your other PC:

```bash
git clone https://github.com/codypratt88/Darknet.git
cd Darknet
sudo ./install.sh
```

This is the cleanest method and ensures you get the latest version.

### Method 2: Transfer Build Directory

If the other PC has the same architecture and similar OS:

```bash
# On the first PC, create a tarball
cd /path/to/Darknet
tar -czf darknet-portable.tar.gz bin/ include/ src/ Makefile README.md LICENSE ETHICAL_GUIDELINES.md install.sh

# Transfer to other PC (choose one):
# Via SCP:
scp darknet-portable.tar.gz user@other-pc:/tmp/

# Via USB drive:
cp darknet-portable.tar.gz /media/usb/

# On the other PC:
cd /tmp
tar -xzf darknet-portable.tar.gz
cd Darknet
sudo ./install.sh
```

### Method 3: Binary-Only Transfer

If both PCs have identical architecture:

```bash
# On first PC (after building):
cd Darknet
sudo cp bin/darknet /usr/local/bin/

# Copy to other PC:
scp bin/darknet user@other-pc:/tmp/

# On other PC:
sudo cp /tmp/darknet /usr/local/bin/
sudo chmod 755 /usr/local/bin/darknet
```

**Note:** This method doesn't include documentation or full source code.

### Method 4: Create Installation Package

Create a self-contained installer:

```bash
# On first PC:
cd Darknet
./create-package.sh  # Creates darknet-installer.tar.gz

# Transfer to other PC and run:
tar -xzf darknet-installer.tar.gz
cd darknet-installer
sudo ./install.sh
```

### Method 5: Network Installation

Set up a simple HTTP server on first PC:

```bash
# On first PC:
cd /path/to/Darknet
python3 -m http.server 8000

# On second PC:
cd /tmp
wget http://first-pc-ip:8000/darknet-portable.tar.gz
tar -xzf darknet-portable.tar.gz
cd Darknet
sudo ./install.sh
```

---

## System Requirements

### Minimum Requirements
- Linux kernel 2.6.32 or higher
- 50 MB free disk space
- GCC 4.8 or higher
- Root access (for installation and execution)

### Recommended Requirements
- Linux kernel 3.x or higher
- 100 MB free disk space
- GCC 7.0 or higher
- Wireless network adapter (for WiFi modules)
- Multiple network interfaces (for MITM attacks)

### Runtime Requirements
- Root/sudo privileges (required for raw sockets)
- Active network interface
- For WiFi attacks: Monitor mode capable wireless adapter

---

## Verification

After installation, verify it works:

```bash
# Check version
darknet version

# List modules
darknet modules

# Show help
darknet help

# Test a basic command (requires root)
sudo darknet scan --help
```

---

## Configuration

### Optional: Enable libpcap Support

To enable full packet capture support:

1. Edit `Makefile`:
   ```makefile
   # Uncomment this line:
   LDFLAGS += -lpcap
   ```

2. Rebuild:
   ```bash
   make clean
   make
   sudo make install
   ```

### Optional: Add to PATH

If installed locally (not system-wide):

```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH=$PATH:/path/to/Darknet/bin

# Reload shell
source ~/.bashrc
```

---

## Troubleshooting

### "Permission denied" Errors

**Problem:** Cannot run Darknet or install.
**Solution:** Use sudo:
```bash
sudo ./install.sh
sudo darknet <command>
```

### Build Fails with "No such file or directory"

**Problem:** Missing dependencies.
**Solution:** Install build tools:
```bash
# Ubuntu/Debian
sudo apt-get install build-essential

# Fedora/CentOS
sudo dnf groupinstall "Development Tools"
```

### "libpcap not found" Error

**Problem:** Missing libpcap library.
**Solution:** Install libpcap:
```bash
# Ubuntu/Debian
sudo apt-get install libpcap-dev

# Fedora
sudo dnf install libpcap-devel

# Or disable libpcap in Makefile (already disabled by default)
```

### Command Not Found After Installation

**Problem:** Binary not in PATH.
**Solution:**
```bash
# Verify installation
which darknet

# If not found, add to PATH
export PATH=$PATH:/usr/local/bin

# Or run with full path
/usr/local/bin/darknet
```

### Different Architecture Between PCs

**Problem:** Binary compiled on one PC doesn't work on another.
**Solution:** Compile on target PC:
```bash
# Transfer source code, not binary
# Then build on target PC
make clean
make
sudo make install
```

---

## Uninstallation

### If Installed via install.sh

```bash
sudo darknet-uninstall
```

### If Installed via make install

```bash
cd /path/to/Darknet
sudo make uninstall
```

### Manual Uninstallation

```bash
sudo rm -f /usr/local/bin/darknet
sudo rm -f /usr/local/bin/darknet-uninstall
sudo rm -rf /usr/local/share/doc/darknet
```

### Complete Removal (Including Source)

```bash
# Remove installation
sudo darknet-uninstall

# Remove source directory
rm -rf /path/to/Darknet
```

---

## Advanced Installation Options

### Build Options

```bash
# Debug build with symbols
make debug

# Optimized release build
make release

# Build without warnings
make CFLAGS="-w"

# Custom installation directory
make install PREFIX=/opt/darknet
```

### Development Installation

For development or testing:

```bash
# Build but don't install
make

# Run from build directory
sudo ./bin/darknet

# Clean and rebuild
make clean && make

# Install only for current user
mkdir -p ~/bin
cp bin/darknet ~/bin/
export PATH=$PATH:~/bin
```

---

## Network Installation Between PCs

### Using SSH

```bash
# Direct SSH transfer and install
ssh user@remote-pc "git clone https://github.com/codypratt88/Darknet.git && cd Darknet && sudo ./install.sh"
```

### Using rsync

```bash
# Sync entire directory
rsync -avz --progress /path/to/Darknet/ user@remote-pc:/tmp/Darknet/

# On remote PC
ssh user@remote-pc
cd /tmp/Darknet
sudo ./install.sh
```

---

## Docker Installation (Future)

Docker support is planned for future releases.

---

## Support

If you encounter issues:

1. Check this installation guide
2. Review the main [README.md](README.md)
3. Check the troubleshooting section
4. Open an issue on GitHub

---

## Security Notes

- Always verify the source before installing
- The framework requires root privileges - understand what you're running
- Read [ETHICAL_GUIDELINES.md](ETHICAL_GUIDELINES.md) before use
- Only install on systems you own or have permission to modify

---

**Installation complete? Start with:** `darknet help`
