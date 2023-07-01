"""SD生成图像文件处理脚本"""
import pathlib
import parse_and_create
from PIL import Image, PngImagePlugin


def count_files(func):
    def wrapper(folder):
        count = 0
        for image in folder.glob("*.png"):
            count += 1
            print(f"正在处理：{image.name}...")
            func(image)
        print(f"\n总计处理{count}个图片文件。\n")
    return wrapper


@count_files
def organize_image_by_model(image):
    """解析图片文件中包含的生成模型信息，分类归档图片文件"""
    parameters = parse_and_create.parse_parameters(image)
    # print(parameters)
    model = parameters['model'] if 'model' in parameters else parameters['model_hash']
    new_path = image.parent / model / image.name
    new_path.parent.mkdir(parents=True, exist_ok=True)
    image.rename(new_path)


@count_files
def remove_chunk_info(input_file):
    """清除SD WebUI生成图片文件中自动添加的生成参数信息，避免prompt等参数泄漏"""
    image = Image.open(input_file)
    png_info = PngImagePlugin.PngInfo()
    chunk_name = "parameters"
    for key in image.info.keys():
        if key != chunk_name:
            png_info.add_text(key, image.info[key])
    output_file = input_file.with_name(f"{input_file.stem}_no_parameters.png")
    image.save(output_file, pnginfo=png_info)


if __name__ == "__main__":
    folder = pathlib.Path(r"D:\sd-webui\outputs\txt2img-images")

    # 根据图片文件中的生成模型信息，分类归档图片文件
    organize_image_by_model(folder)

    # 清除图片文件中包含的生成参数信息，避免prompt等参数泄漏
    # remove_chunk_info(folder)
