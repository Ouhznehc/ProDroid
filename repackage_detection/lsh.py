import os
import json
import csv
from datasketch import MinHash, MinHashLSH

def calculate_jaccard_similarity(file_path1, file_path2):
    def extract_numbers(file_path):
        with open(file_path, 'r') as file:
            return set(line.split(': ')[1].strip() for line in file if ': ' in line)

    set1 = extract_numbers(file_path1)
    set2 = extract_numbers(file_path2)
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    jaccard_similarity = len(intersection) / len(union)
    return jaccard_similarity

def write_report_to_csv(similar_apks, apk_paths, report_path):
    with open(report_path, 'w', newline='') as csvfile:
        fieldnames = ['APK 1', 'APK 2', 'Jaccard Similarity']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for apk1, apk2 in similar_apks:
            jaccard_similarity = calculate_jaccard_similarity(apk_paths[apk1], apk_paths[apk2])
            writer.writerow({'APK 1': apk1, 'APK 2': apk2, 'Jaccard Similarity': jaccard_similarity})

def main():
    with open('config.json', 'r') as file:
        config = json.load(file)

    output_dir = config['output_dir']
    threshold = config.get('threshold', 0.3)
    num_perm = config.get('num_perm', 1000)
    weights = tuple(config.get('weights', (0.9, 0.1)))
    report_path = config.get('report_path', '../data/report/report.csv')  # 默认值为report.csv

    lsh = MinHashLSH(threshold=threshold, num_perm=num_perm, weights=weights)
    minhash_objects = {}

    apk_paths = {}
    for apk_name in os.listdir(output_dir):
        minihash_path = os.path.join(output_dir, apk_name, 'minihash.txt')
        if os.path.exists(minihash_path):
            with open(minihash_path, 'r') as mh_file:
                minihash_values = mh_file.read().strip().strip('[]').replace('\n', ' ').split()
                minihash_values = list(map(int, minihash_values))
                minhash = MinHash(num_perm=num_perm)
                for value in minihash_values:
                    minhash.update((value).to_bytes(4, byteorder='big'))
                lsh.insert(apk_name, minhash)
                minhash_objects[apk_name] = minhash
                apk_paths[apk_name] = os.path.join(output_dir, apk_name, 'kmeans.txt')

    similar_apks = []
    for apk_name, minhash in minhash_objects.items():
        result = lsh.query(minhash)
        for other_apk in result:
            if apk_name != other_apk and (other_apk, apk_name) not in similar_apks:
                similar_apks.append((apk_name, other_apk))

    # 将报告写入CSV文件
    write_report_to_csv(similar_apks, apk_paths, report_path)

if __name__ == '__main__':
    main()
