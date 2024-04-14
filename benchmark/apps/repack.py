import argparse
import requests
import os
from tqdm import tqdm



def load_downloaded_apks(downloaded_apk_path):
    # Load the SHA256 hashes of already downloaded APKs into a set
    if os.path.exists(downloaded_apk_path):
        with open(downloaded_apk_path, 'r') as file:
            return set(line.strip() for line in file)
    return set()

def update_downloaded_apks(sha256, downloaded_apk_path, downloaded_apks):
    # Add the SHA256 hash to the set and file if it's not already there
    if sha256 not in downloaded_apks:
        with open(downloaded_apk_path, 'a') as file:
            file.write(f'{sha256}\n')
        downloaded_apks.add(sha256)

def download_apk(sha256, download_dir, downloaded_apk_path, downloaded_apks):
    apk_path = os.path.join(download_dir, f'{sha256}.apk')

    if sha256 in downloaded_apks:
        print(f'APK for {sha256} already downloaded, skipping...')
        return
    
    api_key = '71910e1cfbacae7228b9a2b3ca74eb64d75722e667afc534887499855e68103f'
    url = f'https://androzoo.uni.lu/api/download?apikey={api_key}&&sha256={sha256}'
    try:
        print(f'Downloading APK for {sha256}')
        response = requests.get(url, timeout=300, stream=True)
        # Sizes in bytes.
        total_size = int(response.headers.get("content-length", 0))
        block_size = 1024
        with tqdm(total=total_size, unit="B", unit_scale=True) as progress_bar:
            with open(apk_path, "wb") as file:
                for data in response.iter_content(block_size):
                    progress_bar.update(len(data))
                    file.write(data)
        if total_size != 0 and progress_bar.n != total_size:
            raise RuntimeError("Could not download file")
        update_downloaded_apks(sha256, downloaded_apk_path, downloaded_apks)
    except requests.Timeout:
        print(f'Timeout (5 minutes)')
    except requests.RequestException as e:
        print(f'Error occurred: {e}')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Path to the repack.csv file", default="repack.csv")
    parser.add_argument("-o", "--output", help="Output directory for downloaded APKs", default="repack/")
    parser.add_argument("-s", "--start", help="Start line (1-based, starts after the first line)", type=int, required=True)
    parser.add_argument("-e", "--end", help="End line (1-based, starts after the first line)", type=int, required=True)
    parser.add_argument("-t", "--type", help="Type of APK to download ('original' or 'repacked_pairs')", required=True)
    args = parser.parse_args()

    if not os.path.exists(args.output):
        os.makedirs(args.output)
        
    if args.type != 'original' and args.type != 'repacked_pairs':
        print(f"Invalid type: {args.type}, required ('original' or 'repacked_paris')")
        return

    downloaded_apk_path = 'downloaded_apk.log'
    downloaded_apks = load_downloaded_apks(downloaded_apk_path)

    # Existing file reading and processing logic...
    with open(args.input, 'r') as file:
        next(file)
        for i, line in enumerate(file, 1):
            if args.start <= i <= args.end:
                sha256_original, sha256_repackage = line.strip().split(',')
                if args.type == 'original':
                    download_apk(sha256_original, args.output, downloaded_apk_path, downloaded_apks)
                elif args.type == 'repacked_pairs':
                    download_apk(sha256_original, args.output, downloaded_apk_path, downloaded_apks)
                    download_apk(sha256_repackage, args.output, downloaded_apk_path, downloaded_apks)

if __name__ == "__main__":
    main()
