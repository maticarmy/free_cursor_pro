#!/bin/bash
export PYTHONWARNINGS=ignore::SyntaxWarning:DrissionPage

echo "正在构建听泉CursorPro换号工具 Linux版本..."

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "创建虚拟环境失败!"
        exit 1
    fi
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "安装依赖项..."
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

# 运行构建脚本
echo "开始构建过程..."
echo "正在构建Linux版本..."

# Linux通常不需要特别设置架构，PyInstaller会使用当前系统架构
# 如需指定架构可取消注释下面的行
# export TARGET_ARCH=x86_64  # 或 aarch64 用于ARM Linux

# 直接使用PyInstaller来构建
pyinstaller TingQuanChanger.spec --distpath dist/linux --workpath build/linux --noconfirm

# 如果构建成功，打开输出目录
if [ $? -eq 0 ]; then
    echo "构建完成！正在打开输出目录..."
    
    # 尝试使用适用于不同Linux桌面环境的方法打开文件夹
    if command -v xdg-open > /dev/null; then
        xdg-open "dist/linux"  # 通用Linux方法
    elif command -v gnome-open > /dev/null; then
        gnome-open "dist/linux"  # GNOME
    elif command -v kde-open > /dev/null; then
        kde-open "dist/linux"  # KDE
    else
        echo "无法自动打开输出目录，请手动浏览到 dist/linux"
    fi
else
    echo "构建过程中出现错误。"
fi

# 为输出的可执行文件添加执行权限
if [ -f "dist/linux/听泉CursorPro换号工具" ]; then
    chmod +x "dist/linux/听泉CursorPro换号工具"
    echo "已为可执行文件添加执行权限"
fi

# 完成
echo "构建完成!"

# 停用虚拟环境
deactivate 