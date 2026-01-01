#!/bin/bash
echo "[*] Installing MR_VIRUS_SYSTEM"
sudo apt update
sudo apt install -y python3 python3-pip
pip3 install -r requirements.txt
echo "[✓] Installation complete"
echo "Run: python3 main.py"

