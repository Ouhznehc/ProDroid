export WORK_DIR = $(shell pwd)
export RANDOM_DIR = $(WORK_DIR)/randomized_test
export RESOURCE_DIR = $(WORK_DIR)/resource_detection
export REPACKAGE_DIR = $(WORK_DIR)/repackage_detection
export BIRTHMARK_DIR = $(WORK_DIR)/birthmark_generation
export DATA_DIR = $(WORK_DIR)/data

randomized_test:
	@echo "randomized testing..."
	@make -C $(RANDOM_DIR) random

archive:
	@echo "archive..."
	@make -C $(DATA_DIR) archive



.PHONY: randomized_test archive