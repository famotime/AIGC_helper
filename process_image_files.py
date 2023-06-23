"""SD生成图像文件处理脚本"""
import pathlib
import parse_and_create
from PIL import Image, PngImagePlugin


def organize_images_by_model(folder):
    """解析图片文件中包含的生成模型信息，分类归档图片文件"""
    for image in folder.glob("*.png"):
        print(f"Processing {image.name}...")
        parameters = parse_and_create.parse_parameters(image)
        # print(parameters)

        model = parameters['model'] if 'model' in parameters else parameters['model_hash']
        new_path = folder / model / image.name
        new_path.parent.mkdir(parents=True, exist_ok=True)
        image.rename(new_path)


def remove_chunk_info(input_file, output_file, chunk_name="parameters"):
    """清除SD WebUI生成图片文件中自动添加的生成参数信息，避免prompt等参数泄漏"""
    image = Image.open(input_file)
    png_info = PngImagePlugin.PngInfo()
    for key in image.info.keys():
        if key != chunk_name:
            png_info.add_text(key, image.info[key])
    image.save(output_file, pnginfo=png_info)


if __name__ == "__main__":
    folder = pathlib.Path(r"D:\sd-webui\outputs\txt2img-images\test")

    # 根据图片文件中的生成模型信息，分类归档图片文件
    # organize_images_by_model(folder)

    # 图片文件中包含的生成参数信息，避免prompt等参数泄漏
    for image in folder.glob("*.png"):
        output_file = image.with_name(f"{image.stem}_no_parameters.png")
        remove_chunk_info(image, output_file)
