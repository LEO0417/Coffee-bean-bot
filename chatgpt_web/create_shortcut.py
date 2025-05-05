#!/usr/bin/env python3
import os
import stat
from pathlib import Path

def create_desktop_shortcut():
    # 获取当前脚本的绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 获取启动脚本的路径
    start_script = os.path.join(current_dir, 'start_coffee_ai.command')
    
    # 确保启动脚本有执行权限
    os.chmod(start_script, os.stat(start_script).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    
    # 获取用户桌面路径
    desktop_path = os.path.join(str(Path.home()), 'Desktop')
    
    # 创建桌面快捷方式
    shortcut_path = os.path.join(desktop_path, '好日子咖啡豆 AI 助手.command')
    
    # 创建软链接
    if os.path.exists(shortcut_path):
        os.remove(shortcut_path)
    os.symlink(start_script, shortcut_path)
    
    # 给快捷方式添加执行权限
    os.chmod(shortcut_path, os.stat(shortcut_path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    
    print(f"桌面快捷方式已创建：{shortcut_path}")
    print("双击图标即可启动服务！")

if __name__ == '__main__':
    create_desktop_shortcut() 