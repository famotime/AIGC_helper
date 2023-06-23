"""解析Civitai网站例图生成参数，或者从现有图片文件读取生成参数，并调用SD WebUI的API作画"""
import pyperclip
import pathlib
import pprint
import re
import requests
import io
import base64
from PIL import Image, PngImagePlugin


def parse_parameters(data, add_prompts=None, del_prompts=None, rep_prompts=None, del_parameters=None):
    """解析civitai网站图像或本地图片文件生成参数"""
    # API生成参数key值
    keys = ['enable_hr', 'denoising_strength', 'firstphase_width', 'firstphase_height', 'hr_scale', 'hr_upscaler', 'hr_second_pass_steps', 'hr_resize_x', 'hr_resize_y', 'hr_sampler_name', 'hr_prompt', 'hr_negative_prompt', 'prompt', 'styles', 'seed', 'subseed', 'subseed_strength', 'seed_resize_from_h', 'seed_resize_from_w', 'sampler_name', 'batch_size', 'n_iter', 'steps', 'cfg_scale', 'width', 'height', 'restore_faces', 'tiling', 'do_not_save_samples', 'do_not_save_grid', 'negative_prompt', 'eta', 's_min_uncond', 's_churn', 's_tmax', 's_tmin', 's_noise', 'override_settings', 'override_settings_restore_afterwards', 'script_args', 'sampler_index', 'script_name', 'send_images', 'save_images', 'alwayson_scripts']
    keys += ['model_hash', 'model']    # 其他需要解析的图像信息，非API参数

    # 生成参数与API关键字映射关系
    mappings = {'sampler': 'sampler_index', 'hires_steps': 'hr_second_pass_steps', 'hires_upscale': 'hr_scale', 'hires_upscaler': 'hr_upscaler', 'face_restoration': 'restore_faces'}

    # 从图片文件读取配置信息
    if str(data).endswith(".png"):
        data = get_parameters_from_img(str(data))

    parameters = {}
    text = data.replace('\r', '')
    # 替换提示词
    if rep_prompts:
        for k, v in rep_prompts.items():
            text = text.replace(k, v)

    # 解析文本信息
    if "Negative prompt" in text:
        prompt, negtive_prompt, others_first_key, others = re.search(r'(.*?)Negative prompt: (.*?)(ENSD|Size|Steps)(.*)', text, flags=re.DOTALL).groups()
    else:
        prompt, others_first_key, others = re.search(r'(.*?)(ENSD|Size|Steps)(.*)', text, flags=re.DOTALL).groups()
        negtive_prompt = ''
    others = others_first_key + others
    others = others.split('\n')[0]
    # print(prompt, negtive_prompt, others, sep='\n')

    # 增加或删除提示词
    if add_prompts:
        prompt += add_prompts
    if del_prompts:
        for i in del_prompts:
            prompt = prompt.replace(i, '')

    parameters['prompt'] = prompt
    if negtive_prompt:
        parameters['negative_prompt'] = negtive_prompt
    # print(others)
    for i in others.split(', '):
        k, v = i.split(': ')
        k = k.lower().replace(' ', '_')
        # print(k, v)
        if k == 'size':
            parameters['width'], parameters['height'] = [int(i) for i in v.split('x')]
            continue
        if k in mappings:
            k = mappings[k]
        try:
            v = int(v)
        except ValueError:
            try:
                v = float(v)
            except ValueError:
                pass
        if k in keys:
            parameters[k] = v

    if 'restore_faces' in parameters:
        parameters['restore_faces'] = True

    hr_upscalers = ['Latent', 'Latent (antialiased)', 'Latent(bicubic)', 'Latent(bicubic antialiased)', 'Latent (nearest)', 'Latent(nearest-exact)', 'None', 'Lanczos', 'Nearest', '4x-UltraSharp', 'BSRGAN', 'ESRGAN 4x', 'LDSR', 'R-ESRGAN 4x+', 'R-ESRGAN 4x+Anime6B', 'ScuNET', 'ScuNET PSNR', 'SwinlR_4x']
    if 'hr_upscaler' in parameters:
        parameters['enable_hr'] = True
        if parameters['hr_upscaler'] not in hr_upscalers:
            parameters['hr_upscaler'] = 'R-ESRGAN 4x+'

    # 删除不需要的参数
    if del_parameters:
        for i in del_parameters:
            try:
                del parameters[i]
            except Exception:
                pass

    return parameters


def get_parameters_from_img(img_path):
    """从图片文件读取配置信息"""
    image = Image.open(img_path)
    data = image.info['parameters']
    # print(data)
    return data


def generate_images(parameters, folder):
    """基于配置参数生成图片并保存"""
    response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=parameters).json()

    for num, i in enumerate(response['images']):
        image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))

        png_payload = {
            "image": "data:image/png;base64," + i
        }
        response2 = requests.post(url=f'{url}/sdapi/v1/png-info', json=png_payload)

        # 将参数信息写入png图片文件
        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text("parameters", response2.json().get("info"))

        # 替换文件名非法字符为下划线
        illegal_chars = r'[<>:"/\\|?*]'
        image_name = re.sub(illegal_chars, '_', parameters['prompt'][:100].replace('\n', ''))
        while (folder / f'{image_name}.png').exists():
            image_name += f'_{num}'
        image.save(folder / f'{image_name}.png', pnginfo=pnginfo)
    return response


if __name__ == "__main__":
    url = "http://127.0.0.1:7860"
    output_folder = pathlib.Path(r"D:\sd-webui\outputs\txt2img-images")
    add_prompts = ""    # 增加提示词，如：", ulzzang-6500-v1.1_2, "
    del_prompts = []    # 删除提示词，如：["ulzzang-6500-v1.1_2", "blurry"]
    rep_prompts = {}    # 替换提示词，如：{'koreanDollLikeness_v10': 'koreanDollLikeness_v15'}
    del_parameters = []  # 删除不想跟样图保持一致的参数，包括seed等，例：['width', 'height', 'seed']

    # 从剪贴板读取从Civitai网站复制的生成参数信息或者是本地png文件路径
    data = pyperclip.paste()
    parameters = parse_parameters(data, add_prompts=add_prompts, del_prompts=del_prompts, rep_prompts=rep_prompts, del_parameters=del_parameters)
    pprint.pprint(parameters)

    # 调用SD WebUI的API生成图像
    result = generate_images(parameters, output_folder)
    image = Image.open(io.BytesIO(base64.b64decode(result['images'][-1].split(",", 1)[0])))    # 最后一张图
    # image.show()
