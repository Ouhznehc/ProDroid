import argparse
import requests
import os

def download_apk(sha256, download_dir):
    apk_path = os.path.join(download_dir, f'{sha256}.apk')
    # Check if the file already exists to avoid redundant downloads
    if os.path.exists(apk_path):
        print(f'APK for {sha256} already downloaded, skiping...')
        return

    api_key = '71910e1cfbacae7228b9a2b3ca74eb64d75722e667afc534887499855e68103f'
    url = f'https://androzoo.uni.lu/api/download?apikey={api_key}&&sha256={sha256}'
    response = requests.get(url)
    if response.status_code == 200:
        with open(apk_path, 'wb') as file:
            file.write(response.content)
        print(f'Downloaded APK to {apk_path}')
    else:
        print(f'Failed to download APK for SHA256 {sha256}')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Path to the repack.txt file", default="repack.txt")
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

    with open(args.input, 'r') as file:
        # Skip the first line if the enumeration is to start from line 2 for -s 1
        next(file)
        for i, line in enumerate(file, 1):  # Start counting from 1 after skipping header
            if args.start <= i <= args.end:
                sha256_original, sha256_repackage = line.strip().split(',')
                # Check if the files are already downloaded or listed before attempting to download
                if args.type == 'original':
                    download_apk(sha256_original, args.output)
                elif args.type == 'repacked_pairs':
                    download_apk(sha256_original, args.output)
                    download_apk(sha256_repackage, args.output)
                    

if __name__ == "__main__":
    main()
