# ProDroid

## Install

you may need to check whether you have already downloaded the following packages:

**Shell**
```
sudo apt install jq
```

**Android Tools**
```
adb aapt
```
**Python Module**
```
pip install flask imagehash datasketch
```

## Usage

1. open a new terminal, use `make server` to start listenning.

2. put apk file into `data/apk/temporary`

3. begin prodroid rontine:
  - `make randomized_test` to run automatic test.
  - `make resource_collection` to classify resources.
  - `make birthmark_generation` to generate birthmark.
  - `make repackage_detection`: to generate repackage detection report to `data/report/report.csv`

4. more support:
  - `make archive` to move all file in `data/*/temporary` into `data/*/permanent`
  - `make clean` to clean all file in `temporary/*, log/*, upload/*` 
  - `make clean-all` to clean all file in `data/*`

