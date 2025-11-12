# Quick Deployment Guide

This guide explains how to quickly get Darknet running on another PC.

## 🚀 Fastest Method: Git Clone

**On your other PC:**

```bash
git clone https://github.com/codypratt88/Darknet.git
cd Darknet
sudo ./install.sh
```

Done! The install script handles everything automatically.

---

## 📦 Method 2: Transfer Package

### On PC #1 (where you have Darknet):

```bash
cd /path/to/Darknet

# Create portable package
./create-package.sh

# This creates: darknet-1.0.0.tar.gz
```

### Transfer Options:

**Option A - USB Drive:**
```bash
cp darknet-1.0.0.tar.gz /media/usb/
```

**Option B - Network (SCP):**
```bash
scp darknet-1.0.0.tar.gz user@other-pc:/tmp/
```

**Option C - Local Network HTTP:**
```bash
# On PC #1:
python3 -m http.server 8000

# On PC #2:
wget http://PC1-IP:8000/darknet-1.0.0.tar.gz
```

### On PC #2 (your other PC):

```bash
# Extract
tar -xzf darknet-1.0.0.tar.gz
cd darknet-1.0.0

# Install
sudo ./install.sh
```

---

## 💾 Method 3: Binary-Only (Same Architecture)

If both PCs have the same CPU architecture:

### On PC #1:

```bash
cd Darknet
scp bin/darknet user@other-pc:/tmp/
```

### On PC #2:

```bash
sudo mv /tmp/darknet /usr/local/bin/
sudo chmod 755 /usr/local/bin/darknet
darknet version
```

---

## 🔧 System Requirements

Both PCs need:
- Linux (any distribution)
- GCC, Make, libpcap-dev
- Root access
- ~50-100 MB free space

---

## ✅ Verification

After installation on the new PC:

```bash
# Check it's installed
which darknet

# Test it works
darknet version
darknet modules

# Run with sudo for actual operations
sudo darknet help
```

---

## 🔥 Super Quick One-Liner

If your other PC has internet and git:

```bash
git clone https://github.com/codypratt88/Darknet.git && cd Darknet && sudo ./install.sh
```

---

## 📋 Troubleshooting

**Problem:** "Command not found"
**Fix:** Make sure /usr/local/bin is in your PATH or run with full path

**Problem:** "Permission denied"
**Fix:** Use `sudo ./install.sh` and `sudo darknet`

**Problem:** Build fails
**Fix:** Install dependencies:
```bash
# Ubuntu/Debian
sudo apt-get install build-essential libpcap-dev

# Fedora
sudo dnf install gcc make libpcap-devel
```

---

## 🔄 Updating on Other PC

To update Darknet on your other PC:

```bash
cd /path/to/Darknet
git pull
make clean && make
sudo make install
```

Or reinstall:

```bash
sudo ./install.sh
```

---

## 🗑️ Uninstalling

On any PC where it's installed:

```bash
sudo darknet-uninstall
```

Or manually:

```bash
sudo rm /usr/local/bin/darknet
sudo rm /usr/local/bin/darknet-uninstall
```

---

## 📚 More Details

- Full installation guide: [INSTALL.md](INSTALL.md)
- Usage examples: [examples/README.md](examples/README.md)
- Main documentation: [README.md](README.md)
- Ethical guidelines: [ETHICAL_GUIDELINES.md](ETHICAL_GUIDELINES.md)

---

**That's it! Should take less than 5 minutes to deploy to another PC.**
