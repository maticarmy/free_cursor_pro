import warnings
import os
import platform
import subprocess
import time
import threading

# Ignore specific SyntaxWarning
warnings.filterwarnings("ignore", category=SyntaxWarning, module="DrissionPage")

TINGQUAN_LOGO = """
  ████████╗██╗███╗   ██╗ ██████╗  ██████╗ ██╗   ██╗ █████╗ ███╗   ██╗
  ╚══██╔══╝██║████╗  ██║██╔═══██╗██╔═══██╗██║   ██║██╔══██╗████╗  ██║
     ██║   ██║██╔██╗ ██║██║   ██║██║   ██║██║   ██║███████║██╔██╗ ██║
     ██║   ██║██║╚██╗██║██║▄▄ ██║██║▄▄ ██║██║   ██║██╔══██║██║╚██╗██║
     ██║   ██║██║ ╚████║╚██████╔╝╚██████╔╝╚██████╔╝██║  ██║██║ ╚████║
     ╚═╝   ╚═╝╚═╝  ╚═══╝ ╚══▀▀═╝  ╚══▀▀═╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝
  换号器
"""


class LoadingAnimation:
    def __init__(self):
        self.is_running = False
        self.animation_thread = None

    def start(self, message="Building"):
        self.is_running = True
        self.animation_thread = threading.Thread(target=self._animate, args=(message,))
        self.animation_thread.start()

    def stop(self):
        self.is_running = False
        if self.animation_thread:
            self.animation_thread.join()
        print("\r" + " " * 70 + "\r", end="", flush=True)  # Clear the line

    def _animate(self, message):
        animation = "|/-\\"
        idx = 0
        while self.is_running:
            print(f"\r{message} {animation[idx % len(animation)]}", end="", flush=True)
            idx += 1
            time.sleep(0.1)


def print_logo():
    print("\033[96m" + TINGQUAN_LOGO + "\033[0m")
    print("\033[93m" + "正在构建「听泉换号器」...".center(56) + "\033[0m\n")


def progress_bar(progress, total, prefix="", length=50):
    filled = int(length * progress // total)
    bar = "█" * filled + "░" * (length - filled)
    percent = f"{100 * progress / total:.1f}"
    print(f"\r{prefix} |{bar}| {percent}% 完成", end="", flush=True)
    if progress == total:
        print()


def simulate_progress(message, duration=1.0, steps=20):
    print(f"\033[94m{message}\033[0m")
    for i in range(steps + 1):
        time.sleep(duration / steps)
        progress_bar(i, steps, prefix="进度:", length=40)


def filter_output(output):
    """ImportantMessage"""
    if not output:
        return ""
    important_lines = []
    for line in output.split("\n"):
        # Only keep lines containing specific keywords
        if any(
            keyword in line.lower()
            for keyword in ["error:", "failed:", "completed", "directory:"]
        ):
            important_lines.append(line)
    return "\n".join(important_lines)


def build():
    # Clear screen
    os.system("cls" if platform.system().lower() == "windows" else "clear")

    # Print logo
    print_logo()

    system = platform.system().lower()
    spec_file = os.path.join("TingQuanChanger.spec")  # 使用新的spec文件

    output_dir = f"dist/{system if system != 'darwin' else 'mac'}"

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    simulate_progress("创建输出目录...", 0.5)

    # Run PyInstaller with loading animation
    pyinstaller_command = [
        "pyinstaller",
        spec_file,
        "--distpath",
        output_dir,
        "--workpath",
        f"build/{system}",
        "--noconfirm",
    ]

    loading = LoadingAnimation()
    try:
        simulate_progress("正在运行PyInstaller...", 2.0)
        loading.start("正在构建中")
        result = subprocess.run(
            pyinstaller_command, check=True, capture_output=True, text=True
        )
        loading.stop()

        if result.stderr:
            filtered_errors = [
                line
                for line in result.stderr.split("\n")
                if any(
                    keyword in line.lower()
                    for keyword in ["error:", "failed:", "completed", "directory:"]
                )
            ]
            if filtered_errors:
                print("\033[93m构建警告/错误:\033[0m")
                print("\n".join(filtered_errors))

    except subprocess.CalledProcessError as e:
        loading.stop()
        print(f"\033[91m构建失败，错误代码 {e.returncode}\033[0m")
        if e.stderr:
            print("\033[91m错误详情:\033[0m")
            print(e.stderr)
        return
    except FileNotFoundError:
        loading.stop()
        print(
            "\033[91m错误: 请确保PyInstaller已安装 (pip install pyinstaller)\033[0m"
        )
        return
    except KeyboardInterrupt:
        loading.stop()
        print("\n\033[91m构建被用户取消\033[0m")
        return
    finally:
        loading.stop()

    print(
        f"\n\033[92m构建成功完成! 输出目录: {output_dir}\033[0m"
    )
    
    # 打开输出目录
    try:
        if system == "windows":
            os.startfile(os.path.abspath(output_dir))
        elif system == "darwin":  # macOS
            subprocess.run(["open", os.path.abspath(output_dir)])
        else:  # Linux
            subprocess.run(["xdg-open", os.path.abspath(output_dir)])
        print("\033[92m已为您打开输出目录\033[0m")
    except:
        print(f"\033[93m请手动打开输出目录: {os.path.abspath(output_dir)}\033[0m")


if __name__ == "__main__":
    build() 