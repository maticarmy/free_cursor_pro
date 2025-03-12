# 听泉CursorPro换号工具

这是一个帮助开发者管理Cursor Pro账号的工具，支持每日免费使用和身份密钥验证模式。

## 功能特点

- 每日免费模式：提供每日免费使用的Cursor账号
- 身份密钥模式：使用专属密钥获取高权重账号
- 自动重置机器码：适配不同版本的Cursor编辑器
- 兼容性强：支持Windows、macOS和Linux系统

## 入口文件和运行方法

### 入口文件
项目的主入口文件是 `tingquan_cursor_pro.py`

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行方法

⚠️ **重要提示：Windows系统需要以管理员身份运行程序！**

#### Windows用户
右键点击程序，选择"以管理员身份运行"，或者：
```bash
# 以管理员身份打开PowerShell或命令提示符，然后运行：
python tingquan_cursor_pro.py
```

#### 其他系统用户
```bash
# Linux/macOS用户使用sudo运行：
sudo python tingquan_cursor_pro.py
```

## 构建方法

项目提供了多个平台的构建脚本：

- Windows: `build_tingquan_win.bat`
- macOS Intel: `build_tingquan_mac_intel.sh`
- macOS ARM: `build_tingquan_mac.sh`
- Linux: `build_tingquan_linux.sh`

也可以使用通用构建脚本：
```bash
python build_tingquan.py
```

或一键构建所有平台版本：
```bash
python build_all.py
```

## 赞助与支持

如果您觉得本工具对您有帮助，欢迎请作者喝杯茶☕

### 请我喝杯茶 | buy me a cup of tea

<div align="center">
  <img src="./screen/donate_qrcode.png"  width="200"/>
</div>

<div align="center">
  <h3></h3>
  <img src="./screen/asdqaaaaaaa.png"  width="200"/>
</div>

## 联系方式

微信：behikcigar

官网：https://cursorpro.com.cn

天猫 

## 许可证声明
本项目采用 [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/) 许可证。
这意味着您可以：
- 分享 — 在任何媒介以任何形式复制、发行本作品
但必须遵守以下条件：
- 非商业性使用 — 您不得将本作品用于商业目的

## 声明
- 本项目仅供学习交流使用，请勿用于商业用途。
- 本项目不承担任何法律责任，使用本项目造成的任何后果，由使用者自行承担。


## 感谢 linuxDo 这个开源社区(一个真正的技术社区)
https://linux.do/

## 特别鸣谢
本项目的开发过程中得到了众多开源项目和社区成员的支持与帮助，在此特别感谢：

### 开源项目
- [go-cursor-help](https://github.com/yuaotian/go-cursor-help) - 一个优秀的 Cursor 机器码重置工具，本项目的机器码重置功能使用该项目实现。该项目目前已获得 9.1k Stars，是最受欢迎的 Cursor 辅助工具之一。



