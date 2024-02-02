import json
import os

def hamming_distance(hash1, hash2):
    """
    计算两个16进制哈希值之间的汉明距离。
    """
    bin_hash1 = bin(int(hash1, 16))[2:].zfill(64)
    bin_hash2 = bin(int(hash2, 16))[2:].zfill(64)
    distance = sum(c1 != c2 for c1, c2 in zip(bin_hash1, bin_hash2))
    return distance

def read_dhash_from_file(dhash_file_path):
    """
    从dhash.txt文件中读取dhash值。
    """
    dhash_values = []
    with open(dhash_file_path, 'r') as file:
        for line in file:
            res_name, hash_value = line.strip().split(': ')
            dhash_values.append((res_name, hash_value))
    return dhash_values

def read_kmeans_centers(kmeans_file_path):
    """
    从kmeans.txt文件中读取聚类中心信息。
    """
    centers = []
    with open(kmeans_file_path, 'r') as file:
        next(file)  # 跳过第一行
        for line in file:
            parts = line.strip().split()
            centers.append((parts[0], parts[1]))
    return centers

def match_center(image_hash, centers):
    """
    找到与给定哈希值最匹配的中心编号。
    """
    min_distance = float('inf')
    min_center = None
    for center_id, center_hash in centers:
        distance = hamming_distance(image_hash, center_hash)
        if distance < min_distance:
            min_distance = distance
            min_center = center_id
    return min_center

def process_apk_dhashes(apk_name, dhash_file_path, centers, output_dir):
    """
    处理给定APK的dhash.txt文件, 并将匹配结果输出到指定目录。
    """
    dhash_values = read_dhash_from_file(dhash_file_path)
    results = []
    for (res_name, image_hash) in dhash_values:
        matched_center = match_center(image_hash, centers)
        if matched_center:
            results.append((res_name, matched_center))

    apk_output_path = os.path.join(output_dir, apk_name)
    os.makedirs(apk_output_path, exist_ok=True)
    with open(os.path.join(apk_output_path, 'kmeans.txt'), 'w') as file:
        for (res_name, center_id) in results:
            file.write(f'{res_name}: {center_id}\n')

def main():
    with open('config.json', 'r') as file:
        config = json.load(file)

    dhash_dir = config['output_dir']
    kmeans_file_path = config['kmeans_path']
    output_dir = config['output_dir']

    centers = read_kmeans_centers(kmeans_file_path)

    for apk_name in os.listdir(dhash_dir):
        dhash_file_path = os.path.join(dhash_dir, apk_name, 'dhash.txt')
        if os.path.isfile(dhash_file_path):
            process_apk_dhashes(apk_name, dhash_file_path, centers, output_dir)

if __name__ == '__main__':
    main()
