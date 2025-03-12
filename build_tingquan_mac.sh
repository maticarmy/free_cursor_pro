#!/bin/bash
export PYTHONWARNINGS=ignore::SyntaxWarning:DrissionPage

echo "正在构建听泉CursorPro换号工具 macOS ARM版本..."

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
echo "正在构建macOS ARM版本..."

# 设置架构为arm64
export TARGET_ARCH=arm64

# 直接使用PyInstaller来构建
pyinstaller TingQuanChanger.spec --distpath dist/mac_arm --workpath build/mac_arm --noconfirm

# 如果构建成功，打开输出目录
if [ $? -eq 0 ]; then
    echo "构建完成！正在打开输出目录..."
    open "dist/mac_arm"
else
    echo "构建过程中出现错误。"
fi

# 清理环境变量
unset TARGET_ARCH

# 完成
echo "构建完成!"

# 停用虚拟环境
deactivate 