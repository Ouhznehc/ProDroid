UPLOAD_PATH := $(shell node -p "require('./config.json').upload_folder")
RES_PATH := $(shell node -p "require('./config.json').resource_path")

collection:
	@for fn in $$(find $(UPLOAD_PATH) -type f); do \
		filename=$$(basename -- "$$fn"); \
		if [[ $$filename =~ ^([^-]+)-.*\.*$$ ]]; then \
			APKNAME="$${BASH_REMATCH[1]}"; \
			mkdir -p "$(RES_PATH)/$$APKNAME"; \
			mv "$$fn" "$(RES_PATH)/$$APKNAME"; \
		else \
			echo "File '$$filename' is not the expected name format, skip..."; \
			rm $$fn; \
		fi; \
	done; \
	echo "Finish file collection!"



.PHONY: collection server