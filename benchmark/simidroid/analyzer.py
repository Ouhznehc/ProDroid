import csv
import re
import argparse

def extract_similarity(log_file, output_csv):
    apk_names = {}
    pattern_apk = re.compile(r'^a(\d+)-->([\w\d]+)\.apk')
    pattern_distance = re.compile(r'The distance for app_{(\d+), (\d+)} is (\d+\.\d+)')

    with open(log_file, 'r') as infile:
        for line in infile:
            match_apk = pattern_apk.search(line)
            if match_apk:
                apk_index, apk_name = match_apk.groups()
                apk_names[apk_index] = apk_name

    with open(log_file, 'r') as infile, open(output_csv, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['APK1', 'APK2', 'Distance'])

        for line in infile:
            match_distance = pattern_distance.search(line)
            if match_distance:
                apk1_index, apk2_index, distance = match_distance.groups()
                apk1_name = apk_names.get(apk1_index)
                apk2_name = apk_names.get(apk2_index)

                if apk1_name and apk2_name:
                    writer.writerow([apk1_name, apk2_name, distance])

def main():
    parser = argparse.ArgumentParser(description="Extract APK similarity data.")
    parser.add_argument("log_file", help="Path to the log file")
    parser.add_argument("output_csv", help="Path to the output CSV file")

    args = parser.parse_args()

    extract_similarity(args.log_file, args.output_csv)

if __name__ == "__main__":
    main()
