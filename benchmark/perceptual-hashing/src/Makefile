# Get a list of APK files in the APK_LIST directory
APK_PATH := $(shell node -p "require('./config.json').apk_path")
APK_LIST := $(wildcard $(APK_PATH)/*.apk)

LOG_FILE := $(shell node -p "require('./config.json').log_path")

birthmark:
# Check sanity for necessary file
	@test -d "$(APK_PATH)" || (echo "Error: $(APK_PATH) directory not found." && exit 1)

	@test -n "$(APK_LIST)" || (echo "Error: No APK files found in $(APK_PATH) directory." && exit 1)

	-@test -f $(LOG_FILE) && rm -f $(LOG_FILE) || true
	
	@for APK_FILE in $(APK_LIST); do \
		python birthmark.py $$APK_FILE; \
		MONKEY_STATUS=$$?; \
		if [ $$MONKEY_STATUS -ne 0 ]; then \
			echo "birthmark.py failed with status $$MONKEY_STATUS, removing $$APK_FILE"; \
			rm $$APK_FILE; \
		fi; \
	done

compare: 
	@python compare.py

percuptual: birthmark compare

clean:
	rm -rf ../data/*


.PHONY: birthmark compare percuptual
