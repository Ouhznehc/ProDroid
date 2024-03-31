plugin=method

simidroid:
	@test -d data/$(plugin) || mkdir -p data/$(plugin)
	@java -jar simidroid.jar ../apps/repack > data/$(plugin)/$(plugin).log
	@python3 analyzer.py data/$(plugin)/$(plugin).log data/$(plugin)/$(plugin).csv
	@rm data/$(plugin)/$(plugin).log
	@python3 draw.py data/$(plugin)/$(plugin).csv ../apps/repack.csv data/$(plugin)/$(plugin).png

clean:
	@rm data/resource/*
	@rm data/component/*

.PHONY: simidroid clean