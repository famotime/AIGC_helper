"""将目录内特定分辨率的png文件裁剪成4等份"""
from PIL import Image
from pathlib import Path


def crop_image_into_four(image_path):
    # 打开图像
    img = Image.open(image_path)
    width, height = img.size

    # 计算每个裁剪部分的尺寸
    crop_width = width // 2
    crop_height = height // 2

    # 获取文件路径信息
    image_path = Path(image_path)
    image_stem = image_path.stem
    image_suffix = image_path.suffix
    image_dir = image_path.parent

    # 裁剪图像并保存
    for i in range(2):
        for j in range(2):
            if (image_dir / f'{image_stem}_{i}_{j}{image_suffix}').exists():
                # print(f"File {image_stem}_{i}_{j}{image_suffix} already exists. Skipping...")
                continue
            left = i * crop_width
            upper = j * crop_height
            right = left + crop_width
            lower = upper + crop_height
            cropped_img = img.crop((left, upper, right, lower))
            cropped_img.save(image_dir / f'{image_stem}_{i}_{j}{image_suffix}')
            print(f"Saved cropped image {image_stem}_{i}_{j}{image_suffix}")


def check_image_resolution(image_path, resolution=(2912, 1632)):
    with Image.open(image_path) as img:
        return img.size == resolution


def process_image(path):
    if path.is_file():
        crop_image_into_four(path)
    elif path.is_dir():
        png_files = list(path.glob("*.png"))
        if not png_files:
            print("No PNG files found in the directory.")
            return

        for png_file in png_files:
            if check_image_resolution(png_file):
                crop_image_into_four(png_file)
    else:
        print(f"The path {path} does not exist.")


if __name__ == '__main__':
    img_path = Path(r"G:\Download\Edge\midjourney")
    process_image(img_path)
