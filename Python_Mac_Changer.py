"""Im working to update this as much as possible and keep it up to date with any windows updates if there is any errors please text me on discord T0hn_"""

import subprocess
import random
import re
import ctypes
import sys
import time

def is_admin():
    """Check if the script is run as administrator"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run(cmd):
    
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    return result.stdout.strip()

def detect_adapter():
   
    output = run('netsh interface show interface')
    for line in output.splitlines():
        if "Connected" in line and "Dedicated" in line:
            parts = line.split()
            # Adapter name is everything after the status and type
            name = " ".join(parts[3:])
            return name
    return None

def get_adapter_guid(adapter_name):
   
    output = run(f'netsh interface show interface name="{adapter_name}"')
    match = re.search(r'GUID\s*:\s*([a-fA-F0-9\-]+)', output)
    return match.group(1) if match else None

def generate_mac():
    
    mac = [0x02] + [random.randint(0x00, 0xFF) for _ in range(5)]
    return ''.join(f"{b:02X}" for b in mac)

def find_registry_key(adapter_guid):
 
    output = run(
        r'reg query "HKLM\SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}" /s /v NetCfgInstanceId'
    )
    for line in output.splitlines():
        if adapter_guid in line:
            parts = line.strip().split()
            for part in parts:
                if part.startswith("HKEY"):
                    return part
    return None

def apply_mac(reg_key, mac):
  
    subprocess.run(f'reg add "{reg_key}" /v NetworkAddress /t REG_SZ /d {mac} /f', shell=True)

def restart_adapter(adapter_name):

    subprocess.run(f'netsh interface set interface "{adapter_name}" disable', shell=True)
    time.sleep(2)
    subprocess.run(f'netsh interface set interface "{adapter_name}" enable', shell=True)

def main():
    print("="*50)
    print("         Auto MAC Randomizer - Made by Tohn")
    print("="*50)
    print()

    if not is_admin():
        print("ACCESS DENIED")
        print("Please run this script as Administrator.")
        input("Press Enter to exit...")
        sys.exit()

    print("[ .. ] Detecting active network adapter...")
    adapter = detect_adapter()
    if not adapter:
        print("[ !! ] No active adapter detected.")
        input()
        sys.exit()
    print(f"[ OK ] Adapter detected: {adapter}\n")

    print("[ .. ] Retrieving adapter identifier...")
    guid = get_adapter_guid(adapter)
    if not guid:
        print("[ !! ] Failed to retrieve adapter identifier.")
        input()
        sys.exit()
    print(f"[ OK ] Identifier found: {guid}\n")

    print("[ .. ] Generating randomized MAC address...")
    mac = generate_mac()
    print(f"[ OK ] MAC generated: {mac}\n")

    print("[ .. ] Locating system registry entry...")
    reg_key = find_registry_key(guid)
    if not reg_key:
        print("[ !! ] Registry entry not found.")
        input()
        sys.exit()
    print(f"[ OK ] Registry entry located: {reg_key}\n")

    print("[ .. ] Applying MAC address...")
    apply_mac(reg_key, mac)
    print("[ OK ] MAC successfully applied\n")

    print("[ .. ] Restarting network adapter...")
    restart_adapter(adapter)
    print("[ OK ] Adapter restarted\n")

    print("="*50)
    print("                  COMPLETE")
    print(f"   New MAC Address: {mac}")
    print("="*50)
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
