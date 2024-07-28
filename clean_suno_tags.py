"""删除Suno歌词中的元标签行"""
import pyperclip


txt = pyperclip.paste()
lines = txt.split('\n')
new_lines = [line for line in lines if not line.startswith('[')]
new_txt = '\n'.join(new_lines)
pyperclip.copy(new_txt)
