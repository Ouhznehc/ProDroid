import re
import subprocess
import sys
import json
from datetime import datetime
import time
import os

def read_config(config_file):
    try:
        with open(config_file, 'r', encoding='utf-8') as file:
            config = json.load(file)
            return config['log_path'], config['initial_delay']
    except FileNotFoundError:
        print("[ERROR]: Config file not found.")
        sys.exit(1)
    except KeyError:
        print("[ERROR]: Missing required keys in config file.")
        sys.exit(1)

def open_log_file(log_path):
    return open(log_path, 'a', encoding='utf-8')

def log_info(log_file, message):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_file.write(f"{current_time}: [INFO] {message}\n")
    print(f"{current_time}: [INFO] {message}")

def log_error(log_file, message):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_file.write(f"{current_time}: [ERROR] {message}\n")
    print(f"{current_time}: [ERROR] {message}")

def extract_activities(aapt_output):
    activity_pattern = re.compile(r'E: activity.*?A: android:name.*?"(.*?)"', re.DOTALL)
    activities = activity_pattern.findall(aapt_output)
    return activities

def extract_package(command, package_name_pattern, main_activity_pattern):
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
    package_match = package_name_pattern.search(result.stdout)
    main_activity_match = main_activity_pattern.search(result.stdout)
    if package_match and main_activity_match:
        return package_match.group(1), main_activity_match.group(1)
    return None, None

def check_adb_devices():
    result = subprocess.run("adb devices", shell=True, stdout=subprocess.PIPE, text=True)
    if "device\n" not in result.stdout:
        return False
    return True

def main(apk_path, config_path='config.json'):
    log_path, delay = read_config(config_path)
    log_file = open_log_file(log_path)
    
    log_file.write(f'\n')
    print("")
    log_info(log_file, f"===================== `{os.path.basename(apk_path)}` =====================")
    
    if os.path.exists(apk_path) == False:
        log_error(log_file, f"APK file not found: {apk_path}")
        sys.exit(1)
    
    # Get package name and main activity
    command = f"aapt dump badging {apk_path}"
    package_name_pattern = re.compile(r"package: name='([^']+)'")
    main_activity_pattern = re.compile(r"launchable-activity: name='([^']+)'")
    
    package_name, main_activity = extract_package(command, package_name_pattern, main_activity_pattern)
    
    # Get all activities
    aapt_output = subprocess.run(f"aapt dump xmltree {apk_path} AndroidManifest.xml", shell=True, stdout=subprocess.PIPE, text=True).stdout
    activities = extract_activities(aapt_output)
    activities = [main_activity] + activities
    
    if package_name is None or main_activity is None:
        log_error(log_file, "Failed to extract package name or main activity")
        sys.exit(1)

    if check_adb_devices() == False:
        log_error(log_file, "No device connected")
        sys.exit(1)

    # Install APK
    result = subprocess.run(f"adb install {apk_path}", shell=True)
    if result.returncode != 0:
        log_error(log_file, f"Failed to install APK: {os.path.basename(apk_path)}")
        sys.exit(1)
    log_info(log_file, f"Installed {os.path.basename(apk_path)}")
    
    # Launch each activity
    for activity in activities:
        log_info(log_file, f"Launching activity {activity}")
        result = subprocess.run(f"adb shell am start -n {package_name}/{activity}", shell=True)
        log_info(log_file, f"Launch package: {package_name} activity: {activity}")
        time.sleep(delay)

    # Uninstall APK
    subprocess.run(f"adb uninstall {package_name}", shell=True)
    log_info(log_file, f"Uninstalled {os.path.basename(apk_path)}")

    log_file.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python activity.py <apk_path>")
        sys.exit(1)
    main(sys.argv[1])
