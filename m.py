from pynput import keyboard


def on_key_release(key):
    try:
        if key == keyboard.Key.f1:
            print("快捷键 'f1' 被触发！")
        # 在这里可以添加更多的快捷键监听
    except AttributeError:
        pass


def on_key_press(key):
    pass


# 创建一个键盘监听器
with keyboard.Listener(on_release=on_key_release, on_press=on_key_press) as listener:
    listener.join()  # 启动监听

# 你的程序将在这里继续执行

while True:
    input()
