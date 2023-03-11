"""模型训练辅助脚本，批量增删标签、统计标签频次"""
import pathlib


def add_del_tags(folder, add_tags, del_tags):
    """在训练图片对应的标签文件中批量增加、删除tag"""
    txt_files = list(folder.glob("*.txt"))
    add_count, del_count = 0, 0
    for txt_file in txt_files:
        original_tags = []
        with open(txt_file, 'r') as file:
            for line in file:
                tags = line.strip().split(", ") # 以逗号分隔tag
                for tag in tags:
                    tag = tag.strip() # 去除tag前后的空格
                    original_tags.append(tag)

        for t in reversed(add_tags):
            if t not in original_tags:
                original_tags.insert(0, t)
                add_count += 1
        for t in del_tags:
            while t in original_tags:
                original_tags.remove(t)
                del_count += 1

        with open(txt_file, 'w') as file:
            file.write(', '.join(original_tags))

    print(f"总计增加了{add_count}个tag，删除了{del_count}个tag。\n")


def tag_stat(folder):
    """统计训练图片相关tag频次"""
    tag_counts = {} # 用于存储tag频次的字典

    txt_files = list(folder.glob("*.txt"))
    for txt_file in txt_files:
        with open(txt_file) as file:
            for line in file:
                tags = line.strip().split(", ") # 以逗号分隔tag
                for tag in tags:
                    tag = tag.strip() # 去除tag前后的空格
                    if tag not in tag_counts:
                        tag_counts[tag] = 1
                    else:
                        tag_counts[tag] += 1

    # 按照频次降序排列tag
    sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)

    # 输出tag及其频次
    for tag, count in sorted_tags:
        print(tag, count)


if __name__ == "__main__":
    # folder = pathlib.Path(r"E:\lora-train\lora-scripts\train\blhx\6_blhx")
    folder = pathlib.Path(r"E:\lora-train\lora-scripts\train\xianxia\6_xianxia")

    # add_tags = ["blhx", "1girl"]
    add_tags = ["xianxia_zqx", "1girl"]
    del_tags = ["transparent_background"]

    add_del_tags(folder, add_tags, del_tags)
    tag_stat(folder)
