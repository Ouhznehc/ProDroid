import os
import subprocess
import time
import sys
import re
import json
import shutil
from PIL import Image
import imagehash

# Set the PYTHONIOENCODING environment variable to utf-8
os.environ['PYTHONIOENCODING'] = 'utf-8'

with open('config.json', 'r') as config_file:
    config = json.load(config_file)

RANDOM_SEED = config['random_seed']
INITIAL_DELAY = config['initial_delay']
EVENTS_COUNT = config['events_count']
LOG_PATH = config['log_path']
SCREENSHOT_INTERVAL = config['screenshot_interval']
DATA_PATH = config['data_path']


# Check if the correct number of command line arguments is provided
if len(sys.argv) != 2:
    print("Usage: python birthmark.py <APK_FILE_PATH>")
    sys.exit(1)

log_file = open(LOG_PATH, 'a', encoding='utf-8')

def log_info(message):
  log_file.write(f"[INFO] : {message}\n")
  print(f"[INFO] : {message}")

def log_error(message):
  log_file.write(f"[ERROR]: {message}\n")
  print(f"[ERROR]: {message}")

# Get the APK file path from command line arguments
APK_FILE = sys.argv[1]

log_file.write(f'\n')
print("")
log_info(f"Perform random test on `{os.path.basename(APK_FILE)}`")


# Define regular expressions to extract package name and main activity with onLaunch attribute
package_name_pattern = re.compile(r"package: name='([^']+)'")
main_activity_pattern = re.compile(r"launchable-activity: name='([^']+)'")

def take_screenshot_and_save(package_name):
    timestamp = int(time.time())
    screenshot_path = f"{DATA_PATH}/{package_name}/img/screenshot_{timestamp}.png"
    os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
    subprocess.run(f"adb shell screencap -p > {screenshot_path}", shell=True)
    img = Image.open(screenshot_path)
    hash = imagehash.dhash(img, hash_size=16)
    return screenshot_path, str(hash)

def save_hash_data(package_name, screenshot_path, hash_value):
    csv_path = f"{DATA_PATH}/{package_name}/birthmark.csv"
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    screenshot = os.path.splitext(os.path.basename(screenshot_path))[0]
    with open(csv_path, 'a') as f:
        f.write(f"{screenshot},{hash_value}\n")
        
def run_monkey_with_screenshots(package_name, monkey_process):
    next_screenshot_time = time.time() + SCREENSHOT_INTERVAL
    while monkey_process.poll() is None:
        current_time = time.time()
        if current_time >= next_screenshot_time:
            screenshot_path, hash_value = take_screenshot_and_save(package_name)
            save_hash_data(package_name, screenshot_path, hash_value)
            next_screenshot_time = current_time + SCREENSHOT_INTERVAL
        time.sleep(1)  # Sleep briefly to reduce load
    log_info("Monkey test completed successfully")

# Function to run aapt command and extract package name and main activity
def get_aapt_output(command, package_name_pattern, main_activity_pattern):
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
    package_match = package_name_pattern.search(result.stdout)
    main_activity_match = main_activity_pattern.search(result.stdout)
    if package_match and main_activity_match:
        return package_match.group(1), main_activity_match.group(1)
    return None, None

# Get the package name and main activity
package_name, main_activity = get_aapt_output(f'aapt dump badging {APK_FILE}', package_name_pattern, main_activity_pattern)

if package_name and main_activity:
    log_info(f"Package name: {package_name}, Main activity: {main_activity}")
    
    # Install the APK file
    install_command = f'adb install {APK_FILE}'
    install_result = subprocess.run(install_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if install_result.returncode == 0:

        # Start the application
        start_app_command = f'adb shell am start {package_name}/{main_activity}'
        with open(os.devnull, 'w') as devnull:
            subprocess.run(start_app_command, shell=True, stdout=devnull, stderr=devnull)

        # Wait for a short time to ensure the activity starts
        time.sleep(INITIAL_DELAY)

        # Get the task ID of the started application
        task_list_command = 'adb shell am stack list'
        task_list_result = subprocess.run(task_list_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        task_id_pattern = re.compile(r'taskId=(.*?)\s')

        matching_task_id = None
        for line in task_list_result.stdout.split('\n'):
            if f"{package_name}/{main_activity}" in line:
                task_id_match = task_id_pattern.search(line)
                if task_id_match:
                    matching_task_id = task_id_match.group(1).strip(':')
                    break

        if matching_task_id:
            log_info(f"Task ID of the started application: {matching_task_id}")
            
            # Lock the currently running application
            lock_task_command = f'adb shell am task lock {matching_task_id}'
            
            # Unlock the currently running application
            unlock_task_command = 'adb shell am task lock stop'
            
            # Uninstall the application
            uninstall_command = f'adb uninstall {package_name}'

            # Run Monkey to perform random testing
            monkey_command = f'adb shell monkey -p {package_name} --ignore-crashes --ignore-timeouts --ignore-security-exceptions --pct-nav 0 --pct-syskeys 0 --pct-appswitch 0 --pct-anyevent 0 -s {RANDOM_SEED} {EVENTS_COUNT}'
            
            apk_name = os.path.splitext(os.path.basename(APK_FILE))[0]
            
            with open(os.devnull, 'w') as devnull:
                subprocess.run(lock_task_command, shell=True, stdout=devnull, stderr=devnull)
                monkey_process = subprocess.Popen(monkey_command, shell=True, stdout=devnull, stderr=devnull)
                run_monkey_with_screenshots(apk_name, monkey_process)

                subprocess.run(unlock_task_command, shell=True, stdout=devnull, stderr=devnull)
                subprocess.run(uninstall_command, shell=True, stdout=devnull, stderr=devnull)
            # After the Monkey testing completes and before uninstalling the application
        else:
            log_error("Task ID not found, unable to lock the application")
            os.remove(APK_FILE)
    else:
        log_error("Failed to install APK")
        os.remove(APK_FILE)
else:
    log_error("Unable to find package name or MainActivity")
    os.remove(APK_FILE)
    

