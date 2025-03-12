#!/usr/bin/env python3
import os
import platform
import subprocess
import time
from colorama import Fore, Style, init

# 初始化colorama
init()

LOGO = """
  ████████╗██╗███╗   ██╗ ██████╗  ██████╗ ██╗   ██╗ █████╗ ███╗   ██╗
  ╚══██╔══╝██║████╗  ██║██╔═══██╗██╔═══██╗██║   ██║██╔══██╗████╗  ██║
     ██║   ██║██╔██╗ ██║██║   ██║██║   ██║██║   ██║███████║██╔██╗ ██║
     ██║   ██║██║╚██╗██║██║▄▄ ██║██║▄▄ ██║██║   ██║██╔══██║██║╚██╗██║
     ██║   ██║██║ ╚████║╚██████╔╝╚██████╔╝╚██████╔╝██║  ██║██║ ╚████║
     ╚═╝   ╚═╝╚═╝  ╚═══╝ ╚══▀▀═╝  ╚══▀▀═╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝
  换号工具
"""

def clear_screen():
    os.system('cls' if platform.system() == 'Windows' else 'clear')

def print_header():
    print(f"{Fore.CYAN}{LOGO}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{'听泉CursorPro换号工具多平台构建工具'.center(56)}{Style.RESET_ALL}\n")

def print_status(message, color=Fore.CYAN):
    print(f"{color}[*] {message}{Style.RESET_ALL}")

def print_success(message):
    print(f"{Fore.GREEN}[✓] {message}{Style.RESET_ALL}")

def print_error(message):
    print(f"{Fore.RED}[✗] {message}{Style.RESET_ALL}")

def run_windows_build():
    print_status("开始构建 Windows 版本...", Fore.YELLOW)
    try:
        subprocess.run(["build_tingquan_win.bat"], check=True, shell=True)
        print_success("Windows 版本构建完成")
        return True
    except subprocess.CalledProcessError:
        print_error("Windows 版本构建失败")
        return False

def run_mac_build():
    print_status("开始构建 macOS (Apple Silicon) 版本...", Fore.YELLOW)
    try:
        # 确保脚本有执行权限
        os.chmod("build_tingquan_mac.sh", 0o755)
        subprocess.run(["./build_tingquan_mac.sh"], check=True, shell=True)
        print_success("macOS (Apple Silicon) 版本构建完成")
        return True
    except subprocess.CalledProcessError:
        print_error("macOS (Apple Silicon) 版本构建失败")
        return False

def run_mac_intel_build():
    print_status("开始构建 macOS (Intel) 版本...", Fore.YELLOW)
    try:
        # 确保脚本有执行权限
        os.chmod("build_tingquan_mac_intel.sh", 0o755)
        subprocess.run(["./build_tingquan_mac_intel.sh"], check=True, shell=True)
        print_success("macOS (Intel) 版本构建完成")
        return True
    except subprocess.CalledProcessError:
        print_error("macOS (Intel) 版本构建失败")
        return False

def run_linux_build():
    print_status("开始构建 Linux 版本...", Fore.YELLOW)
    try:
        # 确保脚本有执行权限
        os.chmod("build_tingquan_linux.sh", 0o755)
        subprocess.run(["./build_tingquan_linux.sh"], check=True, shell=True)
        print_success("Linux 版本构建完成")
        return True
    except subprocess.CalledProcessError:
        print_error("Linux 版本构建失败")
        return False

def main():
    clear_screen()
    print_header()
    
    # 获取当前系统
    system = platform.system()
    
    print_status("欢迎使用听泉CursorPro换号工具多平台构建工具", Fore.GREEN)
    print_status(f"当前系统: {system}")
    
    print("\n选择要构建的版本:")
    print(f"{Fore.CYAN}1. Windows 版本{Style.RESET_ALL}")
    print(f"{Fore.CYAN}2. macOS (Apple Silicon) 版本{Style.RESET_ALL}")
    print(f"{Fore.CYAN}3. macOS (Intel) 版本{Style.RESET_ALL}")
    print(f"{Fore.CYAN}4. Linux 版本{Style.RESET_ALL}")
    print(f"{Fore.CYAN}5. 构建所有版本{Style.RESET_ALL}")
    
    choice = input("\n请输入选项 (1-5): ").strip()
    
    results = []
    
    if choice == '1':
        results.append(("Windows", run_windows_build()))
    elif choice == '2':
        results.append(("macOS (Apple Silicon)", run_mac_build()))
    elif choice == '3':
        results.append(("macOS (Intel)", run_mac_intel_build()))
    elif choice == '4':
        results.append(("Linux", run_linux_build()))
    elif choice == '5':
        if system == 'Windows':
            results.append(("Windows", run_windows_build()))
            # 在Windows上无法直接运行macOS和Linux构建脚本，提示用户
            print_status("注意: Windows系统不能直接构建macOS和Linux版本，请在相应系统上运行构建脚本", Fore.YELLOW)
        elif system == 'Darwin':  # macOS
            results.append(("macOS (Apple Silicon)", run_mac_build()))
            results.append(("macOS (Intel)", run_mac_intel_build()))
            # 在macOS上无法直接运行Windows构建脚本，提示用户
            print_status("注意: macOS系统不能直接构建Windows和Linux版本，请在相应系统上运行构建脚本", Fore.YELLOW)
        elif system == 'Linux':
            results.append(("Linux", run_linux_build()))
            # 在Linux上无法直接运行Windows和macOS构建脚本，提示用户
            print_status("注意: Linux系统不能直接构建Windows和macOS版本，请在相应系统上运行构建脚本", Fore.YELLOW)
        else:
            print_status("无法识别的操作系统", Fore.RED)
    else:
        print_error("无效选项!")
        return
    
    # 显示构建结果汇总
    if results:
        print("\n构建结果汇总:")
        for platform_name, success in results:
            if success:
                print_success(f"{platform_name}: 构建成功")
            else:
                print_error(f"{platform_name}: 构建失败")
    
    print_status("构建过程完成", Fore.GREEN)
    input("\n按回车键退出...")

if __name__ == "__main__":
    main() 