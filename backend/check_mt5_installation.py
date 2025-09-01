#!/usr/bin/env python3
"""
Check MT5 Terminal Installation and Status
"""

import os
import subprocess
import sys

def check_mt5_installation():
    """Check if MT5 is installed and where"""
    print("=== Checking MT5 Installation ===")
    
    # Common MT5 installation paths
    common_paths = [
        "C:\\Program Files\\MetaTrader 5\\terminal64.exe",
        "C:\\Program Files (x86)\\MetaTrader 5\\terminal64.exe",
        "C:\\Users\\{}\\AppData\\Roaming\\MetaQuotes\\Terminal\\*.exe".format(os.getenv('USERNAME', '')),
    ]
    
    print("Checking common MT5 installation paths...")
    for path in common_paths:
        if '*' in path:
            # Handle wildcard paths
            import glob
            matches = glob.glob(path)
            if matches:
                print(f"✅ Found MT5 at: {matches[0]}")
                return matches[0]
        else:
            if os.path.exists(path):
                print(f"✅ Found MT5 at: {path}")
                return path
            else:
                print(f"❌ Not found: {path}")
    
    # Try to find MT5 in the registry (Windows)
    try:
        import winreg
        print("\nChecking Windows registry for MT5...")
        
        # Check HKEY_LOCAL_MACHINE
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall")
            for i in range(winreg.QueryInfoKey(key)[0]):
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    subkey = winreg.OpenKey(key, subkey_name)
                    try:
                        display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                        if "MetaTrader 5" in display_name:
                            install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                            terminal_path = os.path.join(install_location, "terminal64.exe")
                            if os.path.exists(terminal_path):
                                print(f"✅ Found MT5 via registry: {terminal_path}")
                                return terminal_path
                    except FileNotFoundError:
                        pass
                    winreg.CloseKey(subkey)
                except OSError:
                    pass
            winreg.CloseKey(key)
        except Exception as e:
            print(f"Registry search error: {e}")
            
    except ImportError:
        print("Registry module not available")
    
    print("❌ MT5 terminal not found in common locations")
    return None

def check_mt5_processes():
    """Check if MT5 is currently running"""
    print("\n=== Checking Running MT5 Processes ===")
    
    try:
        # Use tasklist to check for running MT5 processes
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq terminal64.exe'], 
                              capture_output=True, text=True)
        
        if 'terminal64.exe' in result.stdout:
            print("✅ MT5 terminal is currently running")
            print(result.stdout)
            return True
        else:
            print("❌ MT5 terminal is not running")
            
            # Also check for metatrader.exe
            result2 = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq metatrader.exe'], 
                                   capture_output=True, text=True)
            if 'metatrader.exe' in result2.stdout:
                print("✅ Found metatrader.exe running")
                print(result2.stdout)
                return True
            
            return False
            
    except Exception as e:
        print(f"Error checking processes: {e}")
        return False

def main():
    print("MT5 Installation and Process Check")
    print("=" * 40)
    
    # Check installation
    mt5_path = check_mt5_installation()
    
    # Check if running
    is_running = check_mt5_processes()
    
    print("\n=== Summary ===")
    if mt5_path:
        print(f"MT5 Installation: ✅ Found at {mt5_path}")
    else:
        print("MT5 Installation: ❌ Not found")
        print("\n💡 Please install MetaTrader 5 from:")
        print("   https://download.mql5.com/cdn/web/exness.technologies.ltd/mt5/exnessmt5setup.exe")
        return
    
    if is_running:
        print("MT5 Process: ✅ Running")
    else:
        print("MT5 Process: ❌ Not running")
        print(f"\n💡 Please start MT5 manually by running: {mt5_path}")
        print("   Then log in with your credentials manually first")
        return
    
    print("\n✅ MT5 appears to be properly installed and running!")
    print("\n🔄 Next steps:")
    print("1. Make sure you can log in manually to MT5 with your Exness credentials")
    print("2. Enable algorithmic trading in MT5 settings")
    print("3. Then try the Python connection again")

if __name__ == "__main__":
    main()
