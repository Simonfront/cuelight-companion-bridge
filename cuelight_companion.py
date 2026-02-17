#!/usr/bin/env python3
"""
DSAN CueLight → Bitfocus Companion Bridge
==========================================
Listens on a DSAN Perfect Cue remote and triggers buttons in Companion.

Run as root (sudo) for access to input devices.
Run as a systemd service to start automatically at boot.

Usage:
    sudo python3 cuelight_companion.py
"""

import sys
import urllib.request
import urllib.error

try:
    import evdev
    from evdev import InputDevice, categorize, ecodes
except ImportError:
    print("evdev library is missing!")
    print("Install it with:")
    print("    sudo pip3 install evdev --break-system-packages")
    sys.exit(1)


# =============================================================================
# CONFIGURATION
# =============================================================================

# Companion HTTP API
COMPANION_HOST = "localhost"
COMPANION_PORT = 8000

# DSAN CueLight USB identification
# Change these if you have a different model
CUELIGHT_VENDOR_ID = 0x0483
CUELIGHT_PRODUCT_ID = 0x2080

# Button mapping: keycode → (page, row, column)
# Format for Companion API: /api/location/{page}/{row}/{column}/press
# Customize this to match your Companion setup
BUTTON_MAPPING = {
    "KEY_LEFT":  (2, 1, 1),  # Back button
    "KEY_RIGHT": (2, 1, 2),  # Forward button
    "KEY_B":     (2, 1, 3),  # B button
}


# =============================================================================
# FUNCTIONS
# =============================================================================

def find_cuelight():
    """Find the DSAN CueLight USB device."""
    for path in evdev.list_devices():
        device = evdev.InputDevice(path)
        try:
            if (device.info.vendor == CUELIGHT_VENDOR_ID and 
                device.info.product == CUELIGHT_PRODUCT_ID):
                return device
        except:
            pass
    return None


def press_companion_button(page, row, column):
    """Send HTTP request to Companion to press a button."""
    url = f"http://{COMPANION_HOST}:{COMPANION_PORT}/api/location/{page}/{row}/{column}/press"
    
    try:
        req = urllib.request.Request(url, method="POST")
        with urllib.request.urlopen(req, timeout=2) as response:
            return response.status == 200
    except urllib.error.URLError as e:
        print(f"  [ERROR] Could not reach Companion: {e.reason}")
        return False
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def main():
    print("\n" + "=" * 60)
    print("   DSAN CUELIGHT -> COMPANION BRIDGE")
    print("=" * 60)
    
    # Find CueLight
    print("\n[*] Looking for DSAN CueLight...")
    device = find_cuelight()
    
    if not device:
        print("[!] DSAN CueLight not found!")
        print("    Make sure the USB receiver is connected.")
        print(f"    (Looking for Vendor: 0x{CUELIGHT_VENDOR_ID:04x}, "
              f"Product: 0x{CUELIGHT_PRODUCT_ID:04x})")
        sys.exit(1)
    
    print(f"[+] Found: {device.name}")
    print(f"    Path: {device.path}")
    
    # Show mapping
    print("\n[*] Button mapping:")
    for key, (page, row, col) in BUTTON_MAPPING.items():
        print(f"    {key:12} -> Companion {page}/{row}/{col}")
    
    print(f"\n[*] Companion: http://{COMPANION_HOST}:{COMPANION_PORT}")
    
    # Test connection to Companion
    print("\n[*] Testing connection to Companion...")
    try:
        url = f"http://{COMPANION_HOST}:{COMPANION_PORT}/api/version"
        with urllib.request.urlopen(url, timeout=2) as response:
            print("[+] Companion is online!")
    except:
        print("[!] Could not reach Companion API - continuing anyway...")
    
    # Start listening
    print("\n" + "-" * 60)
    print("[*] Listening for CueLight input... (Ctrl+C to stop)")
    print("-" * 60 + "\n")
    
    try:
        for event in device.read_loop():
            if event.type == ecodes.EV_KEY:
                key_event = categorize(event)
                
                # Only react to key-down (not release or hold)
                if key_event.keystate != 1:
                    continue
                
                keycode = key_event.keycode
                if isinstance(keycode, list):
                    keycode = keycode[0]
                
                if keycode in BUTTON_MAPPING:
                    page, row, col = BUTTON_MAPPING[keycode]
                    print(f"  [>] {keycode} -> Companion {page}/{row}/{col}", end=" ")
                    
                    if press_companion_button(page, row, col):
                        print("[OK]")
                    else:
                        print("[FAIL]")
                else:
                    print(f"  [>] {keycode} (not mapped)")
                    
    except KeyboardInterrupt:
        print("\n\n[*] Stopped.")
    except Exception as e:
        print(f"\n[!] Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
