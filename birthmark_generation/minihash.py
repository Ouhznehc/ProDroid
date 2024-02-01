from datasketch import MinHash
import os
import json

def process_apk_minihash(apk_name, kmeans_file_path, minihash_output_dir, num_perm):
    """
    处理给定APK的kmeans结果, 并输出Minihash值。
    :param apk_name: APK名称
    :param kmeans_file_path: kmeans结果文件的路径
    :param minihash_output_dir: Minihash输出目录
    :param num_perm: MinHash置换的数量
    """
    minhash = MinHash(num_perm=num_perm)
    with open(kmeans_file_path, 'r') as file:
        for line in file:
            hash_val = line.strip()
            minhash.update(str(hash_val).encode())

    apk_output_path = os.path.join(minihash_output_dir, apk_name)
    os.makedirs(apk_output_path, exist_ok=True)
    with open(os.path.join(apk_output_path, 'minihash.txt'), 'w') as file:
        file.write(str(minhash.hashvalues) + '\n')

def main():
    with open('config.json', 'r') as file:
        config = json.load(file)

    kmeans_output_dir = config['kmeans_output_dir']
    minihash_output_dir = config['minihash_output_dir']
    num_perm = config.get('num_perm', 1000)  # 默认为1000
    # 读取threshold和weights配置
    threshold = config.get('threshold', 0.3)
    weights = tuple(config.get('weights', (0.9, 0.1)))

    for apk_name in os.listdir(kmeans_output_dir):
        apk_kmeans_dir = os.path.join(kmeans_output_dir, apk_name)
        kmeans_file_path = os.path.join(apk_kmeans_dir, 'kmeans.txt')
        if os.path.isfile(kmeans_file_path):
            process_apk_minihash(apk_name, kmeans_file_path, minihash_output_dir, num_perm)

if __name__ == '__main__':
    main()
