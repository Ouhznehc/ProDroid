
# Get a list of APK files in the APK_LIST directory
APK_PATH := $(shell node -p "require('./config.json').apk_path")
APK_LIST := $(wildcard $(APK_PATH)/*.apk)

LOG_FILE := $(shell node -p "require('./config.json').log_path")


VM_NAME := bliss

init:
	@if vboxmanage list runningvms | grep -q "\"$(VM_NAME)\""; then \
		echo "VM is already running. Closing it..."; \
		vboxmanage controlvm "$(VM_NAME)" poweroff; \
		sleep 2; \
	fi


random: init
# Check sanity for necessary file
	@test -d "$(APK_PATH)" || (echo "Error: $(APK_PATH) directory not found." && exit 1)

	@test -n "$(APK_LIST)" || (echo "Error: No APK files found in $(APK_PATH) directory." && exit 1)

	@test -f $(LOG_FILE) && rm -f $(LOG_FILE) || true
	
# Perform monkey testing on each APK file
	@for APK_FILE in $(APK_LIST); do \
		vboxmanage snapshot bliss restore BlissOS && vboxmanage startvm bliss; \
		sleep 5; \
		while true; do \
			adb connect 172.26.105.228:5555; \
			DEVICE_STATE=$$(adb devices | grep '172.26.105.228:5555' | awk '{print $$2}'); \
			if [ "$$DEVICE_STATE" = "device" ]; then \
				echo "ADB is successfully connected to the device."; \
				break; \
			fi; \
		done; \
		python monkey.py $$APK_FILE; \
		MONKEY_STATUS=$$?; \
		adb pull /storage/emulated/0/Documents/ ~/ResouceCollector; \
		if [ $$MONKEY_STATUS -ne 0 ]; then \
			echo "monkey.py failed with status $$MONKEY_STATUS, removing $$APK_FILE"; \
			rm $$APK_FILE; \
		fi; \
		vboxmanage controlvm bliss poweroff; \
		sleep 5; \
	done

activity:
# Check sanity for necessary file
	@test -d "$(APK_PATH)" || (echo "Error: $(APK_PATH) directory not found." && exit 1)

	@test -n "$(APK_LIST)" || (echo "Error: No APK files found in $(APK_PATH) directory." && exit 1)

	@test -f $(LOG_FILE) && rm -f $(LOG_FILE) || true
	
	@for APK_FILE in $(APK_LIST); do \
		python activity.py $$APK_FILE; \
	done


.PHONY:init random activity
