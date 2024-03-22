"""ComfyUI生成图像文件处理脚本"""
from pathlib import Path
import parse_and_create
from PIL import Image, PngImagePlugin
import datetime
import json


def count_files(func):
    def wrapper(folder):
        count = 0
        for image in folder.glob("*.png"):
            count += 1
            print(f"正在处理：{image.name}...")
            func(image)
        print(f"\n总计处理{count}个图片文件。\n")
    return wrapper


def rename_file_to_modified_date(file_path):
    """在文件名开头增加其修改日期"""
    file_path = Path(file_path)

    # 获取文件的修改时间
    modified_time = file_path.stat().st_mtime
    modified_date = datetime.datetime.fromtimestamp(modified_time).strftime("%Y%m%d")

    file_name = file_path.stem.split('_')[:2]  # 获取文件名的前两个部分
    # file_name.append(modified_date)
    file_name.insert(0, modified_date)
    new_file_name = '_'.join(file_name)
    new_file_path = file_path.with_stem(new_file_name)

    try:
        file_path.rename(new_file_path)
    except Exception:
        pass


def organize_image_by_model(image):
    """解析图片文件中包含的生成模型信息，分类归档图片文件及对应的prompt文本文件"""
    parameters = parse_and_create.get_parameters_from_img(image)
    parameters = json.loads(parameters)
    # print(parameters)

    # 查找第一个键为"ckpt_name"的值
    for value in parameters.values():
        if "ckpt_name" in value.get("inputs", {}):
            model = value["inputs"]["ckpt_name"]
            model_name = Path(model).stem
            break

    new_path = image.parent / model_name / image.name
    new_path.parent.mkdir(parents=True, exist_ok=True)
    image.rename(new_path)

    try:
        # prompt文本文件相比image文件的数字减1
        num = int(image.stem.split('_')[-1]) - 1
        prompt_file_name = '_'.join(image.stem.split('_')[:-1] + [str(num).zfill(5)]) + '.txt'
        prompt_file = image.with_name(prompt_file_name)
        new_prompt_path = prompt_file.parent / model_name / prompt_file.name
        prompt_file.rename(new_prompt_path)
    except Exception:
        pass


if __name__ == "__main__":
    folder = Path(r"D:\ComfyUI-aki-v1.1\output")

    img_files = list(folder.glob('*.png'))
    txt_files = list(folder.glob('*.txt'))

    # 重命名文件名，在文件名开头增加其修改日期
    print("正在重命名文件...")
    for file_path in (img_files + txt_files):
        if file_path.stem.startswith('ComfyUI_'):
            rename_file_to_modified_date(file_path)

    # 根据图片文件中的生成模型信息，分类归档图片文件
    print("正在分类归档文件...")
    for file_path in img_files:
        print(f"正在处理：{file_path.name}...")
        organize_image_by_model(file_path)
