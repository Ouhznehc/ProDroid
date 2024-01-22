archive:
	@cp -r $(DATA_DIR)/resource/temporary/ $(DATA_DIR)/resource/permanent/
	@cp -r $(DATA_DIR)/apk/temporary/ $(DATA_DIR)/apk/permanent/

clean:
	@rm -rf $(DATA_DIR)/upload
	@rm -rf $(DATA_DIR)/resource/temporary
	@rm -rf $(DATA_DIR)/apk/temporary
	@rm -rf $(DATA_DIR)/log

clean-all: clean
	@rm -rf $(DATA_DIR)/resource/permanent
	@rm -rf $(DATA_DIR)/apk/permanent

.PHONY: archive clean clean-all