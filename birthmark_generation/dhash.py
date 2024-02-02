from PIL import Image, ImageOps
import os
import imagehash
import json

def process_image(img_path):
    img = Image.open(img_path)
    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
        if img.mode == 'P':
            img = img.convert('RGBA')
        if img.mode == 'LA':
            img = img.convert('RGBA')
        
        grayscale = img.convert('L')
        avg_gray = int(sum(grayscale.getdata()) / len(grayscale.getdata()))

        data = img.load()
        for i in range(img.size[0]):
            for j in range(img.size[1]):
                if data[i, j][3] < 32:
                    data[i, j] = (255 - avg_gray, 255 - avg_gray, 255 - avg_gray, 255)
                else:
                    data[i, j] = (data[i, j][0], data[i, j][1], data[i, j][2], 255)

        img = img.convert('RGB')
    else:
        img = img.convert('RGB')

    return imagehash.dhash(img)

def process_directory(res_dir, output_dir):
    for apk_name in os.listdir(res_dir):
        apk_path = os.path.join(res_dir, apk_name)
        if os.path.isdir(apk_path):
            dhash_list = []
            for img_name in os.listdir(apk_path):
                img_path = os.path.join(apk_path, img_name)
                dhash_value = process_image(img_path)
                dhash_list.append(f'{img_name}: {dhash_value}\n')
            
            output_apk_dir = os.path.join(output_dir, apk_name)
            os.makedirs(output_apk_dir, exist_ok=True)
            with open(os.path.join(output_apk_dir, 'dhash.txt'), 'w') as f:
                f.writelines(dhash_list)

def load_config(config_path='config.json'):
    with open(config_path, 'r') as file:
        config = json.load(file)
    return config

if __name__ == '__main__':
    config = load_config()
    res_dir = config['res_dir']
    output_dir = config['output_dir']
    process_directory(res_dir, output_dir)
