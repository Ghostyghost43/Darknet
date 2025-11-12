#!/bin/bash
#
# Darknet Framework - Package Creation Script
# Creates a portable installation package
#

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}[*] Darknet Framework - Package Creator${NC}\n"

# Get version from source
VERSION="1.0.0"
PACKAGE_NAME="darknet-${VERSION}"
PACKAGE_DIR="/tmp/${PACKAGE_NAME}"

echo -e "${GREEN}[*] Creating package: ${PACKAGE_NAME}${NC}"

# Clean previous package
rm -rf "${PACKAGE_DIR}"
mkdir -p "${PACKAGE_DIR}"

# Copy necessary files
echo -e "${BLUE}[*] Copying files...${NC}"

cp -r include "${PACKAGE_DIR}/"
cp -r src "${PACKAGE_DIR}/"
cp Makefile "${PACKAGE_DIR}/"
cp README.md "${PACKAGE_DIR}/"
cp LICENSE "${PACKAGE_DIR}/"
cp ETHICAL_GUIDELINES.md "${PACKAGE_DIR}/"
cp INSTALL.md "${PACKAGE_DIR}/"
cp install.sh "${PACKAGE_DIR}/"
cp -r examples "${PACKAGE_DIR}/" 2>/dev/null || true

# Create README for package
cat > "${PACKAGE_DIR}/PACKAGE_README.txt" << 'EOF'
Darknet Framework Installation Package
=======================================

This package contains everything needed to install Darknet.

Quick Install:
--------------
1. Extract this package
2. cd into the directory
3. Run: sudo ./install.sh

Manual Install:
--------------
1. make
2. sudo make install

For detailed instructions, see INSTALL.md

IMPORTANT: This tool is for authorized testing only!
Read ETHICAL_GUIDELINES.md before use.

Version: 1.0.0
License: GPL v3.0
EOF

# Create tarball
echo -e "${BLUE}[*] Creating tarball...${NC}"
cd /tmp
tar -czf "${PACKAGE_NAME}.tar.gz" "${PACKAGE_NAME}"

# Create portable version with pre-built binary (if exists)
if [ -f "${PACKAGE_DIR}/../Darknet/bin/darknet" ]; then
    echo -e "${BLUE}[*] Creating portable version with binary...${NC}"
    cp -r "${PACKAGE_DIR}" "${PACKAGE_DIR}-portable"
    mkdir -p "${PACKAGE_DIR}-portable/bin"
    cp "${PACKAGE_DIR}/../Darknet/bin/darknet" "${PACKAGE_DIR}-portable/bin/"
    cd /tmp
    tar -czf "${PACKAGE_NAME}-portable.tar.gz" "${PACKAGE_DIR}-portable"
    rm -rf "${PACKAGE_DIR}-portable"
fi

# Move back to original directory and move package
cd - > /dev/null
if [ -f "/tmp/${PACKAGE_NAME}.tar.gz" ]; then
    mv "/tmp/${PACKAGE_NAME}.tar.gz" .
fi
if [ -f "/tmp/${PACKAGE_NAME}-portable.tar.gz" ]; then
    mv "/tmp/${PACKAGE_NAME}-portable.tar.gz" .
fi

# Cleanup
rm -rf "${PACKAGE_DIR}"

echo -e "\n${GREEN}[✓] Package created successfully!${NC}\n"
echo -e "${BLUE}Files created:${NC}"
echo -e "  • ${PACKAGE_NAME}.tar.gz (source package)"
[ -f "${PACKAGE_NAME}-portable.tar.gz" ] && echo -e "  • ${PACKAGE_NAME}-portable.tar.gz (with pre-built binary)"

echo -e "\n${YELLOW}Transfer to another PC:${NC}"
echo -e "  ${GREEN}scp ${PACKAGE_NAME}.tar.gz user@other-pc:/tmp/${NC}"
echo -e "\n${YELLOW}Then on the other PC:${NC}"
echo -e "  ${GREEN}cd /tmp${NC}"
echo -e "  ${GREEN}tar -xzf ${PACKAGE_NAME}.tar.gz${NC}"
echo -e "  ${GREEN}cd ${PACKAGE_NAME}${NC}"
echo -e "  ${GREEN}sudo ./install.sh${NC}\n"
