"""提取指定目录下python脚本描述内容，生成脚本概览(markdown文件)"""
import pathlib
import re


path = pathlib.Path.cwd()
folder = path.parts[-1]
python_scripts = [file for file in path.glob("*.py")]

content = f'# {folder}\n'
for pyfile in python_scripts:
    with open(pyfile, encoding='utf-8') as f:
        try:
            description = re.match(r"('''|\"\"\")(.*?)('''|\"\"\")", f.read(), flags=re.DOTALL).group(2).strip().replace('\n', '; ')
            content += '- **{}:** {}'.format(pyfile.name, description + '\n')
        except Exception:
            print(f"{pyfile.name}解析失败，跳过……")

output = path / (folder + '_脚本描述.md')
with open(output, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'已生成脚本概览"{output}"。')
