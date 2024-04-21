import os
import json
import itertools
import csv

# 读取配置文件
with open('config.json', 'r') as config_file:
    config = json.load(config_file)
data_path = config['data_path']

def read_hashes(file_path):
    """从 CSV 文件读取 dhash 值，返回一个集合"""
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        hashes = {row[1] for row in reader if row}
    return hashes

def jaccard_similarity(set1, set2):
    """计算两个集合的杰卡德相似度"""
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    return len(intersection) / len(union) if union else 0

def compare_birthmarks(data_path):
    """比较所有 APK 的 birthmarks 并保存结果到 CSV 文件中"""
    # 寻找所有的 birthmark.csv 文件
    birthmarks = {}
    for root, dirs, files in os.walk(data_path):
        for file in files:
            if file == 'birthmark.csv':
                package_name = os.path.basename(root)
                file_path = os.path.join(root, file)
                birthmarks[package_name] = read_hashes(file_path)

    # 计算杰卡德相似度并收集结果
    results = []
    for (pkg1, hashes1), (pkg2, hashes2) in itertools.combinations(birthmarks.items(), 2):
        similarity = jaccard_similarity(hashes1, hashes2)
        results.append((pkg1, pkg2, similarity))

    # 写入结果到 CSV 文件
    report_path = os.path.join(data_path, 'report.csv')
    with open(report_path, 'w', newline='') as report_file:
        writer = csv.writer(report_file)
        writer.writerow(['Package 1', 'Package 2', 'Jaccard Similarity'])
        for result in results:
            writer.writerow(result)

# 运行比较函数
compare_birthmarks(data_path)
