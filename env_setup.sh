#!/bin/bash

set -e  # Exit on error

red_bold() {
  echo -e "\033[1;31m$1\033[0m"
}

green_bold() {
  echo -e "\033[1;32m$1\033[0m"
}

check_config_txt() {
  if grep -q '^enable_uart=1' /boot/config.txt; then
    green_bold "[OK] enable_uart=1 found in /boot/firmware/config.txt"
  else
    red_bold "[WARN] Missing or incorrect: enable_uart=1 in /boot/firmware/config.txt"
  fi

  if grep -q '^dtoverlay=dwc2' /boot/config.txt; then
    green_bold "[OK] dtoverlay=dwc2 found in /boot/config.txt"
  else
    red_bold "[WARN] Missing: dtoverlay=dwc2 in /boot/config.txt"
  fi
}

check_cmdline_txt() {
  CMDLINE=$(cat /boot/cmdline.txt)
  if echo "$CMDLINE" | grep -q "modules-load=dwc2,g_serial"; then
    green_bold "[OK] modules-load=dwc2,g_serial found in /boot/cmdline.txt"
  else
    red_bold "[WARN] Missing: modules-load=dwc2,g_serial in /boot/cmdline.txt"
  fi
}

echo "=== CONFIG CHECK: Serial Communication ============"
check_config_txt
check_cmdline_txt
echo "=== CONFIG =================="

sudo nmcli connection add type wifi \
con-name "starlink" \
ifname wlan0 \
ssid "PXLLAB" \
wifi-sec.key-mgmt wpa-psk \
wifi-sec.psk 'Slu123!8910' \
connection.autoconnect yes
sudo nmcli connection modify starlink connection.autoconnect-priority 100

echo "Enabling serial communication, tying console to ttyGS0"
sudo systemctl enable serial-getty@ttyGS0.service || echo "Warning, serial port not up"
sudo systemctl start serial-getty@ttyGS0.service || echo "Warning, serial port not up"
sudo systemctl is-active serial-getty@ttyGS0.service

echo "Installing system dependencies..."
sudo apt update
sudo apt install -y python3-picamera2 --no-install-recommends

echo "Creating Python virtual environment with system packages..."
python3 -m venv picamvenv --system-site-packages

echo "Activating virtual environment..."
source picamvenv/bin/activate

echo "Installing Python packages..."
pip install --upgrade pip

pip install pyserial
pip install crcmod

# Optional: mock-serial (comment out for deployment)
pip install mock-serial

# Re-run apt install in case needed again (redundant)
sudo apt install -y python3-picamera2 --no-install-recommends


# Activate venvs and run python tasks if desired
# source picamenv/bin/activate

echo "Setup complete. Environment 'picamvenv' is ready. The system will reboot now..."
