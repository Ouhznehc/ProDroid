import os
import subprocess
import time
import sys
import re
import json
import shutil

# Set the PYTHONIOENCODING environment variable to utf-8
os.environ['PYTHONIOENCODING'] = 'utf-8'

with open('config.json', 'r') as config_file:
    config = json.load(config_file)

RANDOM_SEED = config['random_seed']
INITIAL_DELAY = config['initial_delay']
EVENTS_COUNT = config['events_count']
LOG_PATH = config['log_path']
APK_KEEP_PATH = config['apk_keep_path']



# Check if the correct number of command line arguments is provided
if len(sys.argv) != 2:
    print("Usage: python monkey.py <APK_FILE_PATH>")
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
    # After detecting Unity3D application
    if "unity3d" in main_activity:
        user_input = input("Unity application detected. Do you want to continue testing? (Y/N): ")
        if user_input.strip().upper() != 'Y':
            log_info("User opted to stop testing the Unity application.")
            exit(0)
        log_info("Proceeding with the Unity application testing...")
    
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
            with open(os.devnull, 'w') as devnull:
                subprocess.run(lock_task_command, shell=True, stdout=devnull, stderr=devnull)
                subprocess.run(monkey_command, shell=True, stdout=devnull, stderr=devnull)
                subprocess.run(unlock_task_command, shell=True, stdout=devnull, stderr=devnull)
                subprocess.run(uninstall_command, shell=True, stdout=devnull, stderr=devnull)

            log_info("Testing completed")
            # After the Monkey testing completes and before uninstalling the application
            keep_app_input = input("Testing completed. Do you want to keep the application? (Y/N): ")
            if keep_app_input.strip().upper() == 'Y':
                try:
                    shutil.move(APK_FILE, APP_KEEP_PATH)
                    log_info(f"Application moved to {APK_KEEP_PATH}")
                except Exception as e:
                    log_error(f"Failed to move APK to {APK_KEEP_PATH}: {e}")
            else:
                try:
                    os.remove(APK_FILE)
                    log_info("Application APK deleted")
                except Exception as e:
                    log_error(f"Failed to delete APK: {e}")  
        else:
            log_error("Task ID not found, unable to lock the application")
    else:
        log_error("Failed to install APK")
else:
    log_error("Unable to find package name or MainActivity")
    

