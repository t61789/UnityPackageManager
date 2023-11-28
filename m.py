# from pynput import keyboard


# def on_key_release(key):
# try:
# if key == keyboard.Key.f1:
# print("快捷键 'f1' 被触发！")
# # 在这里可以添加更多的快捷键监听
# except AttributeError:
# pass


# def on_key_press(key):
# pass


# # 创建一个键盘监听器
# with keyboard.Listener(on_release=on_key_release, on_press=on_key_press) as listener:
# listener.join()  # 启动监听

# # 你的程序将在这里继续执行

# while True:
# input()

from openpyxl import Workbook
import re
import os

# m = re.findall(r"(\d\d\d)", "012.234")
# print(m)

wb = Workbook()

sheet = wb.active

t = open("D://target.txt", "r")
lines = t.readlines()

curExcelLine = 2
for line in lines:
    if ".cs" not in line:
        continue

    project = re.findall(r"<.*>", line)
    if len(project) > 0:
        sheet["A" + str(curExcelLine)] = project[0]
        path = re.findall(r"\\.*\.cs", line)[0]
        (dir, fileName) = os.path.split(path)
        sheet["B" + str(curExcelLine)] = dir
        sheet["C" + str(curExcelLine)] = fileName
    else:
        fileName = re.findall(r"\S*\.cs", line)
        sheet["C" + str(curExcelLine)] = fileName[0]

    curExcelLine += 1

t.close()
wb.save("D://e.xlsx")
