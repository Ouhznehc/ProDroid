export WORK_DIR = $(shell pwd)
export RANDOM_DIR = $(WORK_DIR)/randomized_test
export RESOURCE_DIR = $(WORK_DIR)/resource_collection
export REPACKAGE_DIR = $(WORK_DIR)/repackage_detection
export BIRTHMARK_DIR = $(WORK_DIR)/birthmark_generation
export DATA_DIR = $(WORK_DIR)/data

install:
	@echo "need module: pillow, imagehash, datasketch"
	@pip install pillow imagehash datasketch
	@echo "need package jq"
	@sudo apt install jq

randomized_test:
	@echo "randomized testing..."
	@make -C $(RANDOM_DIR) activity

resource_collection:
	@echo "resource collection..."
	@make -C $(RESOURCE_DIR) collection

birthmark_generation:
	@echo "birthmark generation..."
	@make -C $(BIRTHMARK_DIR) birthmark

repackage_detection:
	@echo "repackage detection..."
	@make -C $(REPACKAGE_DIR) detection

archive:
	@echo "archive..."
	@make -C $(DATA_DIR) archive

clean:
	@echo "clean..."
	@make -C $(DATA_DIR) clean

clean-all:
	@echo "clean all..."
	@make -C $(DATA_DIR) clean-all



.PHONY: randomized_test resource_collection birthmark_generation repackage_detection archive clean clean-all 