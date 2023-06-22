"""模型训练辅助脚本，批量增删、替换标签、统计标签频次"""
import pathlib
import re


def get_tag_files(folder):
    """获取中英文tag文件列表"""
    eng_tag_files = [i for i in folder.glob("*.txt") if not i.stem.endswith('zh')]
    zh_tag_files = [i for i in folder.glob("*.txt") if i.stem.endswith('zh')]
    return eng_tag_files, zh_tag_files


def get_tags(tag_file):
    """获取标签文件中的tag列表"""
    with open(tag_file, 'r') as file:
        content = file.read()
        if flag == "eng":
            content = content.replace("，", ',')
            tags = re.split(r"\s*,\s*|\n", content.strip())  # 分割tag
        elif flag == "zh":
            content = content.replace(",", '，').replace("、", "，")
            tags = re.split(r"\s*，\s*|\n", content.strip())  # 分割tag
    return tags


def handle_tags(tag_files, add_tags, del_tags, replace_tags):
    """在训练图片对应的标签文件中批量增加、删除tag"""
    add_count, del_count, replace_count = 0, 0, 0

    for tag_file in tag_files:
        tags = get_tags(tag_file)
        for t in reversed(add_tags):
            if t not in tags:
                tags.insert(0, t)
                add_count += 1

        for t in del_tags:
            while t in tags:
                tags.remove(t)
                del_count += 1

        for k in replace_tags.keys():
            for i in range(len(tags)):
                if tags[i] == k:
                    tags[i] = replace_tags[k]
                    replace_count += 1

        with open(tag_file, 'w') as file:
            if flag == "eng":
                file.write(', '.join(tags))
            elif flag == "zh":
                file.write('，'.join(tags))

    print(f"总计增加了{add_count}个tag，删除了{del_count}个tag，替换了{replace_count}个tag。\n")


def tag_stat(tag_files):
    """统计训练图片相关tag频次"""
    tag_counts = {} # 用于存储tag频次的字典
    for tag_file in tag_files:
        with open(tag_file) as file:
            content = file.read()
            if flag == "eng":
                content = content.replace("，", ',')
                tags = re.split(r"\s*,\s*|\n", content.strip()) # 分割tag
            elif flag == "zh":
                content = content.replace(",", '，')
                tags = re.split(r"\s*，\s*|\n", content.strip()) # 分割tag
            for tag in tags:
                if tag not in tag_counts:
                    tag_counts[tag] = 1
                else:
                    tag_counts[tag] += 1

    # 按照频次降序排列tag
    sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)

    # 输出tag及其频次
    print("\n标签数量统计如下：")
    for tag, count in sorted_tags:
        print(count, tag)


if __name__ == "__main__":
    # folder = pathlib.Path(r"E:\lora-train\lora-scripts\train\blhx\6_blhx")
    folder = pathlib.Path(r"E:\训练素材\test")

    flag = "eng"    # 处理范围：zh中文, eng英文
    add_tags = ["blhx", "xxx"]
    del_tags = ["1girl"]
    replace_tags = {"blhx": "BLHX", "xxx": "XXXX"}

    eng_tag_files, zh_tag_files = get_tag_files(folder)

    if flag == "eng":
        handle_tags(eng_tag_files, add_tags, del_tags, replace_tags)
        tag_stat(eng_tag_files)
    elif flag == "zh":
        handle_tags(zh_tag_files, add_tags, del_tags, replace_tags)
        tag_stat(zh_tag_files)
