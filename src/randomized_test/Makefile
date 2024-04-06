
# Get a list of APK files in the APK_LIST directory
APK_PATH := $(shell jq -r '.apk_path' config.json)
APK_LIST := $(wildcard $(APK_PATH)/*.apk)

LOG_FILE := $(shell jq -r '.log_path' config.json)

random:
# Check sanity for necessary files

	@test -d "$(APK_PATH)" || (echo "Error: $(APK_PATH) directory not found." && exit 1)

	@test -n "$(APK_LIST)" || (echo "Error: No APK files found in $(APK_PATH) directory." && exit 1)

	@test -f $(LOG_FILE) && rm -f $(LOG_FILE) || true

# Perform monkey testing on each APK file
	@for APK_FILE in $(APK_LIST); do python3 monkey.py $$APK_FILE; done

.PHONY: random
