#!/bin/bash

# 确保提供了路径作为参数
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <path_to_apks>"
    exit 1
fi

APK_PATH=$1

# 检查ADB是否可用
if ! command -v adb &> /dev/null
then
    echo "adb could not be found, please install it and try again."
    exit
fi

# 获取设备ID
DEVICE_ID=$(adb devices | grep -v List | awk '{print $1}')
if [ -z "$DEVICE_ID" ]; then
    echo "No device found. Please connect a device and try again."
    exit 1
fi

# 遍历路径下的所有apk文件
for apk in "$APK_PATH"/*.apk; do
    # 检查文件是否存在
    if [ ! -f "$apk" ]; then
        echo "No APK files found in $APK_PATH."
        continue
    fi

    echo "Installing $apk on device $DEVICE_ID..."
    # 安装APK
    adb -s "$DEVICE_ID" install "$apk"

    # 检查安装是否成功
    if [ $? -eq 0 ]; then
        echo "Installation successful. Uninstalling the app..."
        # 通过获取包名来卸载应用
        PKG_NAME=$(aapt dump badging "$apk" | awk '/package/{gsub("name=|'"'"'","",$2); print $2}')
        adb -s "$DEVICE_ID" uninstall "$PKG_NAME"
    else
        echo "Installation failed. Deleting $apk..."
        rm "$apk"
    fi
done
