import json
import os
import subprocess

def hamming_distance(hash1, hash2):
    """
    计算两个16进制哈希值之间的汉明距离。
    :param hash1: 第一个16进制哈希值
    :param hash2: 第二个16进制哈希值
    :return: 汉明距离
    """
    # 将16进制转换为2进制，并去掉前缀'0b'
    bin_hash1 = bin(int(hash1, 16))[2:].zfill(64)
    bin_hash2 = bin(int(hash2, 16))[2:].zfill(64)

    # 计算不同位的数量
    distance = sum(c1 != c2 for c1, c2 in zip(bin_hash1, bin_hash2))
    return distance

def get_dhash(image_path):
    """
    调用dhash.py脚本并获取图片的dhash值。
    :param image_path: 图片的路径
    :return: 计算得到的dhash值
    """
    print(f'Processing {image_path}...')
    result = subprocess.run(['python', 'dhash.py', image_path], capture_output=True, text=True)
    print(result.stdout.strip())
    return result.stdout.strip()

def read_kmeans_centers(kmeans_file_path):
    """
    从kmeans.txt文件中读取聚类中心信息。
    :param kmeans_file_path: kmeans.txt文件的路径
    :return: 聚类中心的列表，每个中心是一个(编号, 哈希值)的元组
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
    :param image_hash: 图片的哈希值
    :param centers: 聚类中心的列表
    :return: 最匹配的中心编号
    """
    if not image_hash:
        return None
    min_distance = float('inf')
    min_center = None
    for center_id, center_hash in centers:
        distance = hamming_distance(image_hash, center_hash)
        if distance < min_distance:
            min_distance = distance
            min_center = center_id
    return min_center

def process_apk_images(apk_name, apk_images_dir, centers, output_dir):
    """
    处理给定APK名称的图片集合, 并将匹配结果输出到指定目录。
    :param apk_name: APK名称
    :param apk_images_dir: APK图片集合的目录
    :param centers: kmeans聚类中心列表
    :param output_dir: 输出目录
    """
    results = []
    for image_name in os.listdir(apk_images_dir):
        image_path = os.path.join(apk_images_dir, image_name)
        image_hash = get_dhash(image_path)
        matched_center = match_center(image_hash, centers)
        if matched_center:
            results.append(matched_center)

    apk_output_path = os.path.join(output_dir, apk_name)
    os.makedirs(apk_output_path, exist_ok=True)
    with open(os.path.join(apk_output_path, 'kmeans.txt'), 'w') as file:
        for center_id in results:
            file.write(f'{center_id}\n')

def main():
    with open('config.json', 'r') as file:
        config = json.load(file)

    apk_dir = config['apk_dir']
    kmeans_file_path = config['kmeans_file_path']
    output_dir = config['kmeans_output_dir']

    centers = read_kmeans_centers(kmeans_file_path)

    for apk_name in os.listdir(apk_dir):
        apk_images_dir = os.path.join(apk_dir, apk_name)
        if os.path.isdir(apk_images_dir):
            process_apk_images(apk_name, apk_images_dir, centers, output_dir)

if __name__ == '__main__':
    main()
