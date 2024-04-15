import os
import json
import subprocess
import shutil
import re

def load_config():
    with open('config.json', 'r') as file:
        return json.load(file)

def check_device():
    result = subprocess.run(['adb', 'devices'], stdout=subprocess.PIPE, text=True)
    lines = result.stdout.splitlines()
    # 开始检查从第二行开始的设备列表（第一行是标题）
    for line in lines[1:]:
        if "device" in line.split() and "device" == line.split()[-1]:
            return True
    return False


def install_apk(apk_path):
    result = subprocess.run(['adb', 'install', apk_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.returncode == 0

def uninstall_apk(package_name):
    subprocess.run(['adb', 'uninstall', package_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def get_aapt_output(apk_path):
    result = subprocess.run(['aapt', 'dump', 'badging', apk_path], stdout=subprocess.PIPE, text=True)
    return result.stdout

def extract_package_main_activity(aapt_output):
    package_match = re.search(r"package: name='([^']+)'", aapt_output)
    main_activity_match = re.search(r"launchable-activity: name='([^']+)'", aapt_output)
    if package_match and main_activity_match:
        return package_match.group(1), main_activity_match.group(1)
    return None, None


def main():
    apk_cnt = 0
    unity3d_cnt = 0
    failed_cnt = 0
    
    config = load_config()
    apk_path = config['apk_path']
    unity3d_path = config['unity3d_path']

    if not check_device():
        print("No devices found. Please connect a device and try again.")
        return

    for apk in os.listdir(apk_path):
        if not apk.endswith('.apk'):
            continue
        apk_full_path = os.path.join(apk_path, apk)
        apk_cnt += 1

        if install_apk(apk_full_path):
            aapt_output = get_aapt_output(apk_full_path)
            package_name, main_activity = extract_package_main_activity(aapt_output)
            if package_name and main_activity:
                print(f"Package: {package_name} MainActivity: {main_activity}")
                if 'unity3d' in main_activity.lower():
                    unity3d_cnt += 1
                    shutil.move(apk_full_path, os.path.join(unity3d_path, apk))
                uninstall_apk(package_name)
            else:
                failed_cnt += 1
                uninstall_apk(package_name)  # Ensure any partial install is cleaned up
                os.remove(apk_full_path)
        else:
            failed_cnt += 1
            os.remove(apk_full_path)
    
        
    print(f"Detecting {apk_cnt} apks.\nFailed to install {failed_cnt} apks.\nDetecting {unity3d_cnt} Unity3D apks.")

if __name__ == '__main__':
    main()

