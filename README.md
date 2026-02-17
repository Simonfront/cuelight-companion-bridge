# DSAN CueLight → Bitfocus Companion Bridge

A lightweight Python service that connects a DSAN Perfect Cue presenter remote to Bitfocus Companion. Press buttons on your remote to trigger actions in Companion.

## Features

- Auto-detects DSAN CueLight USB receiver
- Maps remote buttons to Companion button presses
- Runs as a systemd service (starts at boot)
- Minimal dependencies (just `evdev`)

## Requirements

- Linux (tested on Raspberry Pi OS)
- Python 3
- Bitfocus Companion running on the same machine (or accessible via network)
- DSAN Perfect Cue remote with USB receiver

## Quick Start

### 1. Install dependencies

```bash
sudo pip3 install evdev --break-system-packages
```

### 2. Install the script

```bash
sudo mkdir -p /opt/cuelight-companion
sudo cp cuelight_companion.py /opt/cuelight-companion/
sudo chmod +x /opt/cuelight-companion/cuelight_companion.py
```

### 3. Test manually

```bash
sudo python3 /opt/cuelight-companion/cuelight_companion.py
```

Press buttons on your remote to verify it works.

### 4. Install as a service

```bash
sudo cp cuelight-companion.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable cuelight-companion
sudo systemctl start cuelight-companion
```

### 5. Check status

```bash
sudo systemctl status cuelight-companion
```

View logs:

```bash
sudo journalctl -u cuelight-companion -f
```

## Configuration

Edit `cuelight_companion.py` to customize:

### Companion connection

```python
COMPANION_HOST = "localhost"
COMPANION_PORT = 8000
```

### Button mapping

```python
BUTTON_MAPPING = {
    "KEY_LEFT":  (2, 1, 1),  # Back button -> Page 2, Row 1, Column 1
    "KEY_RIGHT": (2, 1, 2),  # Forward button -> Page 2, Row 1, Column 2
    "KEY_B":     (2, 1, 3),  # B button -> Page 2, Row 1, Column 3
}
```

### USB device identification

If you have a different DSAN model, you may need to change these values:

```python
CUELIGHT_VENDOR_ID = 0x0483
CUELIGHT_PRODUCT_ID = 0x2080
```

To find your device's vendor and product ID, run:

```bash
lsusb
```

## Detecting your remote's keycodes

If your remote sends different keycodes, use `evtest` to discover them:

```bash
sudo apt install evtest
sudo evtest
```

Select your device and press buttons to see the keycodes.

## Troubleshooting

### Service fails to start

Check the logs:

```bash
sudo journalctl -u cuelight-companion -n 50
```

### Device not found

- Ensure the USB receiver is plugged in
- Check that the vendor/product ID matches your device
- Verify you're running as root

### Companion not responding

- Verify Companion is running
- Check the host and port configuration
- Test the API manually:

```bash
curl -X POST http://localhost:8000/api/location/2/1/1/press
```

## Uninstall

```bash
sudo systemctl stop cuelight-companion
sudo systemctl disable cuelight-companion
sudo rm /etc/systemd/system/cuelight-companion.service
sudo rm -rf /opt/cuelight-companion
sudo systemctl daemon-reload
```

## License

MIT License - Use freely in your own projects.
