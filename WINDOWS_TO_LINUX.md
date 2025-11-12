# Transferring Darknet from Windows to Linux

This guide explains how to transfer your Darknet framework from Windows (where you're building it) to your Linux PC (where it will run).

## 🎯 Quick Overview

Darknet is a Linux-only framework, but you can develop/modify it on Windows and deploy to Linux easily.

---

## Method 1: Git (Recommended) ⭐

This is the cleanest and easiest method.

### On Windows:

```bash
# Commit your changes
git add -A
git commit -m "Your commit message"
git push
```

### On Linux PC:

```bash
# Clone or pull
git clone https://github.com/codypratt88/Darknet.git
cd Darknet

# Or if already cloned:
git pull

# Install
sudo ./install.sh
```

**Pros:**
- Cleanest method
- Version controlled
- Easy updates
- Can deploy to multiple PCs

**Cons:**
- Requires internet on Linux PC

---

## Method 2: Create Package + USB Transfer

### On Windows (in WSL or Git Bash):

```bash
cd /path/to/Darknet

# Create portable package
./create-package.sh

# This creates: darknet-1.0.0.tar.gz
```

### Transfer via USB:

1. **Copy to USB drive:**
   ```bash
   # In Windows/WSL
   cp darknet-1.0.0.tar.gz /mnt/d/  # D: drive (USB)
   # Or just drag-drop in Windows Explorer
   ```

2. **On Linux PC:**
   ```bash
   # Copy from USB
   cp /media/usb/darknet-1.0.0.tar.gz ~/

   # Extract and install
   cd ~
   tar -xzf darknet-1.0.0.tar.gz
   cd darknet-1.0.0
   sudo ./install.sh
   ```

**Pros:**
- No internet required
- Fast transfer
- Portable

**Cons:**
- Requires USB drive
- Manual process

---

## Method 3: Network Transfer (SCP/SFTP)

If both computers are on the same network:

### Using SCP (from Windows WSL or Git Bash):

```bash
# Create package first
./create-package.sh

# Transfer to Linux PC
scp darknet-1.0.0.tar.gz username@linux-pc-ip:/tmp/

# SSH into Linux PC and install
ssh username@linux-pc-ip
cd /tmp
tar -xzf darknet-1.0.0.tar.gz
cd darknet-1.0.0
sudo ./install.sh
```

### Using SFTP/WinSCP (Windows GUI):

1. Download [WinSCP](https://winscp.net/)
2. Connect to your Linux PC
3. Upload `darknet-1.0.0.tar.gz`
4. SSH into Linux and extract/install

**Pros:**
- No USB needed
- Can script it
- Fast on LAN

**Cons:**
- Requires network access
- Need SSH enabled on Linux

---

## Method 4: Zip and Transfer

Simple Windows-friendly method:

### On Windows:

1. Right-click Darknet folder
2. Send to → Compressed (zipped) folder
3. Copy `Darknet.zip` to USB drive

### On Linux:

```bash
# Copy from USB
cp /media/usb/Darknet.zip ~/
cd ~
unzip Darknet.zip
cd Darknet
sudo ./install.sh
```

---

## Method 5: Direct Folder Copy

If you have shared network drive:

### Setup Shared Folder:

1. **On Windows:** Share the Darknet folder
2. **On Linux:** Mount the share
   ```bash
   sudo mount -t cifs //windows-pc/Darknet /mnt/darknet
   cp -r /mnt/darknet ~/Darknet
   cd ~/Darknet
   sudo ./install.sh
   ```

---

## Development Workflow

### Recommended Setup:

**On Windows:**
- Edit code in your favorite Windows editor (VSCode, Notepad++, etc.)
- Commit to git
- Push to GitHub

**On Linux:**
- Pull from GitHub
- Build and test
- Report issues back

### Example Workflow:

```bash
# On Windows (after editing files)
git add -A
git commit -m "Added new feature"
git push

# On Linux
cd ~/Darknet
git pull
make clean && make
sudo make install
darknet <test your changes>
```

---

## Quick Transfer Scripts

### Windows Script (transfer.bat):

```batch
@echo off
echo Creating package...
bash -c "./create-package.sh"

echo Package created: darknet-1.0.0.tar.gz
echo.
echo Copy this file to your Linux PC and run:
echo   tar -xzf darknet-1.0.0.tar.gz
echo   cd darknet-1.0.0
echo   sudo ./install.sh
pause
```

### Linux Install Script (quick-install.sh):

```bash
#!/bin/bash
# Run this on Linux after transferring files

if [ -f "darknet-1.0.0.tar.gz" ]; then
    tar -xzf darknet-1.0.0.tar.gz
    cd darknet-1.0.0
    sudo ./install.sh
else
    echo "Error: darknet-1.0.0.tar.gz not found"
    echo "Please transfer the package file first"
fi
```

---

## Troubleshooting

### Problem: Line Ending Issues

Windows uses CRLF, Linux uses LF. This can cause script errors.

**Solution:**
```bash
# On Linux, after transfer
find . -type f -name "*.sh" -exec dos2unix {} \;

# Or:
sed -i 's/\r$//' install.sh
chmod +x install.sh
```

### Problem: Permission Issues

**Solution:**
```bash
# Make scripts executable
chmod +x install.sh create-package.sh
chmod +x examples/*.sh
```

### Problem: Missing Files After Transfer

**Solution:**
```bash
# Ensure all files transferred
tar -tzf darknet-1.0.0.tar.gz | wc -l  # Check file count

# Re-create package if needed
```

---

## Best Practices

### 1. Always Use Git
- Easiest to maintain
- Version controlled
- Easy updates

### 2. Test Before Transfer
```bash
# On Windows/WSL, test the package
./create-package.sh
tar -tzf darknet-1.0.0.tar.gz  # Verify contents
```

### 3. Document Changes
Keep a CHANGELOG.md of what you modified

### 4. Backup
Keep backups before major changes:
```bash
cp -r Darknet Darknet-backup-$(date +%Y%m%d)
```

---

## Automated Sync Script

### Create sync.sh on Windows (WSL/Git Bash):

```bash
#!/bin/bash

# Configuration
LINUX_USER="your-username"
LINUX_IP="192.168.1.100"
LINUX_PATH="/home/$LINUX_USER/"

echo "Syncing Darknet to Linux PC..."

# Create package
./create-package.sh

# Transfer
scp darknet-1.0.0.tar.gz $LINUX_USER@$LINUX_IP:$LINUX_PATH

# Remote install
ssh $LINUX_USER@$LINUX_IP << 'ENDSSH'
cd ~
tar -xzf darknet-1.0.0.tar.gz
cd darknet-1.0.0
sudo ./install.sh
echo "Darknet installed successfully!"
ENDSSH

echo "Sync complete!"
```

Make executable:
```bash
chmod +x sync.sh
```

Use:
```bash
./sync.sh
```

---

## Transfer Checklist

Before transferring:
- [ ] All changes committed (if using git)
- [ ] Package created successfully
- [ ] Transfer medium ready (USB/network)
- [ ] Linux PC accessible

After transferring:
- [ ] Files extracted correctly
- [ ] Scripts are executable
- [ ] Installation successful
- [ ] `darknet version` works
- [ ] Modules accessible

---

## Summary

**Easiest:** Git clone on Linux
**Fastest:** Network transfer (SCP)
**Most Portable:** USB with package
**For Development:** Git workflow

Choose the method that fits your setup!

---

**Need Help?**
- Check [INSTALL.md](INSTALL.md) for installation details
- See [DEPLOYMENT.md](DEPLOYMENT.md) for deployment options
- Read [README.md](README.md) for usage info
