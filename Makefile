export WORK_DIR = $(shell pwd)
export RANDOM_DIR = $(WORK_DIR)/randomized_test
export RESOURCE_DIR = $(WORK_DIR)/resource_collection
export REPACKAGE_DIR = $(WORK_DIR)/repackage_detection
export BIRTHMARK_DIR = $(WORK_DIR)/birthmark_generation
export DATA_DIR = $(WORK_DIR)/data

randomized_test:
	@echo "randomized testing..."
	@make -C $(RANDOM_DIR) random

resource_collection:
	@echo "resource collection..."
	@make -C $(RESOURCE_DIR) collection

server:
	@make -C $(RESOURCE_DIR) server

birthmark_generation:
	@echo "birthmark generation..."
	@make -C $(BIRTHMARK_DIR) birthmark

archive:
	@echo "archive..."
	@make -C $(DATA_DIR) archive

clean:
	@echo "clean..."
	@make -C $(DATA_DIR) clean

clean-all:
	@echo "clean all..."
	@make -C $(DATA_DIR) clean-all



.PHONY: randomized_test archive server clean clean-all birthmark_generation