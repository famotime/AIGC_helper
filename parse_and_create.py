"""解析Civitai网站例图生成参数，或者从现有图片文件读取生成参数，并调用SD WebUI的API作画"""
import pyperclip
import pathlib
import pprint
import re
import requests
import io
import base64
from PIL import Image, PngImagePlugin
from PIL.ExifTags import TAGS


def parse_generation_data(data, type='civitai', add_prompts=None, del_prompts=None, replacements=None, del_parameters=None):
    """解析civitai网站图片配置数据"""
    # 配置项key
    keys = ['enable_hr', 'denoising_strength', 'firstphase_width', 'firstphase_height', 'hr_scale', 'hr_upscaler', 'hr_second_pass_steps', 'hr_resize_x', 'hr_resize_y', 'prompt', 'styles', 'seed', 'subseed', 'subseed_strength', 'seed_resize_from_h', 'seed_resize_from_w', 'sampler_name', 'batch_size', 'n_iter', 'steps', 'cfg_scale', 'width', 'height', 'restore_faces', 'tiling', 'negative_prompt', 'eta', 's_churn', 's_tmax', 's_tmin', 's_noise', 'override_settings', 'override_settings_restore_afterwards', 'script_args', 'sampler_index', 'script_name']

    mappings = {'sampler': 'sampler_index', 'hires_steps': 'hr_second_pass_steps', 'hires_upscale': 'hr_scale', 'hires_upscaler': 'hr_upscaler', 'face_restoration': 'restore_faces'}

    parameters = {}
    text = data.replace('\r', '')
    # 替换提示词
    if replacements:
        for k, v in replacements.items():
            text = text.replace(k, v)
    # prompt, negtive_prompt, others = re.search(r'(.*)Negative prompt: (.*)(Size:.*)', text, flags=re.DOTALL).groups()
    prompt, negtive_prompt, others = text.split('\n')
    negtive_prompt = negtive_prompt.replace('Negative prompt: ', '')

    # 增加或删除提示词
    if add_prompts:
        prompt += add_prompts
    if del_prompts:
        for i in del_prompts:
            prompt = prompt.replace(i, '')
    parameters['prompt'] = prompt
    parameters['negtive_prompt'] = negtive_prompt
    others = others.split('\n')[0]

    for i in others.split(', '):
        k, v = i.split(': ')
        k = k.lower().replace(' ', '_')

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
    parameters = parse_generation_data(data)
    return parameters


def generate_images(parameters, folder):
    """基于配置参数生成图片并保存"""
    response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=parameters)
    r = response.json()

    for num, i in enumerate(r['images']):
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
        image_name = re.sub(illegal_chars, '_', parameters['prompt'][:145].replace('\n', ''))
        image.save(folder / f'{image_name}_{num}.png', pnginfo=pnginfo)
    return r


if __name__ == "__main__":
    url = "http://127.0.0.1:7860"
    output_folder = pathlib.Path(r"E:\novelai-webui\outputs\txt2img-images")
    add_prompts = ""    # ", ulzzang-6500-v1.1_2, "
    del_prompts = []
    replacements = {'koreanDollLikeness_v10': 'koreanDollLikeness_v15'}    # 替换prompt关键词
    del_parameters = []  # 删除不想保持一致的参数，包括seed等，例：['width', 'height', 'seed']

    # 从剪贴板读取从Civitai网站复制的配置信息
    data = pyperclip.paste()
    parameters = parse_generation_data(data, add_prompts=add_prompts, del_prompts=del_prompts, replacements=replacements, del_parameters=del_parameters)
    pprint.pprint(parameters)

    # 从现有图片文件读取配置信息
    # img_path = pathlib.Path(r'E:\novelai-webui\outputs\txt2img-images\01955-4137383039-1girl, beautiful eyes!! anime art style by kuvshinov ilya ( and wayne barlowe ) ), trending on pixiv fanbox! cgsociety digital p.png')
    # parameters = get_parameters_from_img(img_path)
    # pprint.pprint(parameters)

    result = generate_images(parameters, output_folder)
    image = Image.open(io.BytesIO(base64.b64decode(result['images'][-1].split(",", 1)[0])))    # 最后一张图
    image.show()
