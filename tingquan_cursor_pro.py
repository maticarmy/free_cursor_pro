import os
import sys
import json
import time
import uuid
import socket
import hashlib
import subprocess
import warnings
import requests
from colorama import Fore, Style, init
from logger import logging
from logo import print_logo
from cursor_auth_manager import CursorAuthManager
from reset_machine import MachineIDResetter
import patch_cursor_get_machine_id
import go_cursor_help
import exit_cursor

# 禁用urllib3的不安全请求警告
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 初始化colorama
init()

# 定义emoji和颜色常量
EMOJI = {
    "ERROR": "❌", 
    "WARNING": "⚠️", 
    "INFO": "ℹ️",
    "SUCCESS": "✅",
    "API": "🌐",
    "KEY": "🔑",
    "SAVE": "💾",
    "HARDWARE": "🖥️",
    "FREE": "🎁",
    "IP": "🌍"
}

# 颜色格式化函数
def format_success(text):
    return f"{Fore.GREEN}{text}{Style.RESET_ALL}"

def format_error(text):
    return f"{Fore.RED}{text}{Style.RESET_ALL}"

def format_warning(text):
    return f"{Fore.YELLOW}{text}{Style.RESET_ALL}"

def format_info(text):
    return f"{Fore.CYAN}{text}{Style.RESET_ALL}"

def format_highlight(text):
    return f"{Fore.MAGENTA}{text}{Style.RESET_ALL}"

# API相关常量
API_URL = "https://api.cursorpro.com.cn/admin/api.pool/getAccount"
FREE_API_URL = "https://api.cursorpro.com.cn/admin/api.pool/getaccountfree"
HEADERS = {'Content-Type': 'application/x-www-form-urlencoded'}
CONFIG_FILE = "identity_key.json"
FREE_CACHE_FILE = "free_account_cache.json"
CACHE_DURATION = 5 * 60 * 60  # 5小时的秒数

def get_ip_address():
    """获取当前公网IP地址"""
    ip_apis = [
        {'url': 'https://api.ipify.org?format=json', 'type': 'json', 'key': 'ip'},
        {'url': 'https://ifconfig.me/ip', 'type': 'text', 'key': None},
        {'url': 'https://api.ip.sb/ip', 'type': 'text', 'key': None},
        {'url': 'https://api.myip.com', 'type': 'json', 'key': 'ip'},
        {'url': 'https://ipinfo.io/json', 'type': 'json', 'key': 'ip'},
    ]
    
    logging.info(f"{EMOJI['IP']} 正在获取当前公网IP地址...")
    
    # 临时禁用所有警告
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        
        # 尝试禁用代理（如果有）
        original_proxies = os.environ.get('HTTP_PROXY'), os.environ.get('HTTPS_PROXY')
        try:
            os.environ.pop('HTTP_PROXY', None)
            os.environ.pop('HTTPS_PROXY', None)
        except:
            pass
        
        # 尝试每个API
        for api in ip_apis:
            try:
                response = requests.get(api['url'], timeout=3, verify=False)
                if response.status_code == 200:
                    if api['type'] == 'json':
                        data = response.json()
                        ip = data.get(api['key'])
                    else:
                        ip = response.text.strip()
                    
                    if ip and is_valid_ip(ip):
                        logging.info(f"{EMOJI['IP']} 当前公网IP: {ip}")
                        return ip
            except Exception as e:
                logging.debug(f"API {api['url']} 获取失败: {str(e)}")
                continue
        
        # 如果上面的方法都失败，尝试直接连接特定服务检测IP
        logging.warning(f"{EMOJI['WARNING']} 无法通过公网服务获取IP，尝试备用方法")
        
        # 恢复原始代理设置
        try:
            if original_proxies[0]:
                os.environ['HTTP_PROXY'] = original_proxies[0]
            if original_proxies[1]:
                os.environ['HTTPS_PROXY'] = original_proxies[1]
        except:
            pass
    
    # 返回本地IP作为备用
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        logging.info(f"{EMOJI['IP']} 使用本地IP: {local_ip}")
        return local_ip
    except:
        pass
    
    # 最后的备选：尝试从socket获取主机名对应的IP
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        logging.info(f"{EMOJI['IP']} 使用主机名解析IP: {local_ip}")
        return local_ip
    except:
        logging.error(f"{EMOJI['ERROR']} 无法获取任何IP地址")
        return "127.0.0.1"  # 返回本地回环地址而不是"unknown"

def is_valid_ip(ip):
    """检查是否是有效的IPv4地址"""
    try:
        parts = ip.split('.')
        return len(parts) == 4 and all(0 <= int(part) < 256 for part in parts)
    except:
        return False

def get_approximate_location():
    """获取大致位置信息"""
    location_apis = [
        {'url': 'http://ip-api.com/json/{ip}', 'fields': {
            'country': 'country',
            'region': 'regionName',
            'city': 'city',
            'lat': 'lat',
            'lon': 'lon'
        }},
        {'url': 'https://ipinfo.io/{ip}/json', 'fields': {
            'country': 'country',
            'region': 'region',
            'city': 'city',
            'loc': 'loc'  # 将以逗号分隔的"lat,lon"转换为单独字段
        }}
    ]
    
    try:
        # 临时禁用所有警告
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            
            ip = get_ip_address()
            if ip == "127.0.0.1":
                return None
            
            for api in location_apis:
                try:
                    url = api['url'].format(ip=ip)
                    response = requests.get(url, timeout=3, verify=False)
                    if response.status_code == 200:
                        data = response.json()
                        
                        location = {}
                        for target_field, source_field in api['fields'].items():
                            value = data.get(source_field, '')
                            if target_field == 'lat' and source_field == 'loc' and ',' in value:
                                # 处理ipinfo.io的特殊情况，其中loc是"lat,lon"格式
                                lat, lon = value.split(',')
                                location['lat'] = lat
                                location['lon'] = lon
                            else:
                                location[target_field] = value
                        
                        # 如果成功获取到位置信息
                        if any(location.values()):
                            logging.info(f"{EMOJI['IP']} 成功获取位置信息: {location['city'] if 'city' in location else '未知城市'}, {location['country'] if 'country' in location else '未知国家'}")
                            return location
                except Exception as e:
                    logging.debug(f"位置API {api['url']} 获取失败: {str(e)}")
                    continue
    except Exception as e:
        logging.debug(f"获取位置信息失败: {str(e)}")
    
    logging.debug("无法获取位置信息，继续执行其他操作")
    return None

def get_hardware_machine_id():
    """
    获取硬件机器码，根据不同操作系统采用不同方法
    如果无法获取硬件特定信息，则使用其他可靠的唯一标识
    """
    machine_id = None
    platform_name = sys.platform
    
    try:
        if platform_name == "win32":  # Windows
            try:
                # 尝试获取CPU和主板信息
                output = subprocess.check_output("wmic csproduct get uuid", shell=True).decode().strip()
                if "UUID" in output:
                    machine_id = output.split("\n")[1].strip()
                
                # 如果上面的方法失败，尝试使用主板序列号
                if not machine_id or machine_id == "":
                    output = subprocess.check_output("wmic baseboard get serialnumber", shell=True).decode().strip()
                    if "SerialNumber" in output:
                        machine_id = output.split("\n")[1].strip()
            except:
                pass
                
        elif platform_name == "darwin":  # macOS
            try:
                # 尝试获取硬件UUID
                output = subprocess.check_output(["ioreg", "-rd1", "-c", "IOPlatformExpertDevice"]).decode()
                for line in output.split("\n"):
                    if "IOPlatformUUID" in line:
                        machine_id = line.split('"')[3]
                        break
            except:
                pass
                
        elif platform_name.startswith("linux"):  # Linux
            try:
                # 尝试读取machine-id
                if os.path.exists("/etc/machine-id"):
                    with open("/etc/machine-id", "r") as file:
                        machine_id = file.read().strip()
                # 如果上述方法失败，尝试使用DMI信息
                elif os.path.exists("/sys/class/dmi/id/product_uuid"):
                    with open("/sys/class/dmi/id/product_uuid", "r") as file:
                        machine_id = file.read().strip()
            except:
                pass
    except Exception as e:
        logging.warning(f"{EMOJI['WARNING']} 获取硬件机器码时发生错误: {str(e)}")
    
    # 如果无法获取硬件特定信息，使用其他可靠标识
    if not machine_id or machine_id == "":
        fallback_ids = []
        
        # 获取主机名
        try:
            fallback_ids.append(socket.gethostname())
        except:
            pass
            
        # 获取MAC地址
        try:
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                            for elements in range(0, 2*6, 8)][::-1])
            fallback_ids.append(mac)
        except:
            pass
            
        # 获取当前用户名
        try:
            fallback_ids.append(os.getlogin())
        except:
            pass
            
        # 组合信息生成一个唯一标识
        if fallback_ids:
            combined = "-".join(fallback_ids)
            machine_id = hashlib.sha256(combined.encode()).hexdigest()
        else:
            # 最后的后备方案: 生成一个随机UUID
            machine_id = str(uuid.uuid4())
    
    return {"id": machine_id, "platform": platform_name}

def save_identity_key(identity_key):
    """保存身份密钥到本地文件"""
    try:
        config_data = {"identity_key": identity_key, "last_used": int(time.time())}
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4)
        logging.info(f"{EMOJI['SAVE']} 身份密钥已保存到本地")
        return True
    except Exception as e:
        logging.error(f"{EMOJI['ERROR']} 保存身份密钥失败: {str(e)}")
        return False

def load_identity_key():
    """从本地文件加载身份密钥"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config_data = json.load(f)
            return config_data.get("identity_key")
        return None
    except Exception as e:
        logging.error(f"{EMOJI['ERROR']} 加载身份密钥失败: {str(e)}")
        return None

def get_account_from_api(identity_key):
    """从API获取账号信息"""
    try:
        logging.info(f"{EMOJI['API']} 正在从API获取账号信息...")
        data = {'identity_key': identity_key}
        
        try:
            # 使用更长的超时时间和错误处理
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                response = requests.post(API_URL, headers=HEADERS, data=data, timeout=10, verify=False)
            
            if response.status_code != 200:
                logging.error(f"{EMOJI['ERROR']} API服务暂时不可用 ({response.status_code})")
                return None
            
            try:
                result = response.json()
                if result.get("code") != 0:
                    logging.error(f"{EMOJI['ERROR']} {result.get('msg', 'API返回错误')}")
                    return None
                
                account_info = result.get("data")
                if not account_info:
                    logging.error(f"{EMOJI['ERROR']} API返回数据格式错误")
                    return None
                
                logging.info(f"{EMOJI['SUCCESS']} 成功获取账号信息")
                return account_info
                
            except ValueError:
                logging.error(f"{EMOJI['ERROR']} API返回的数据无法解析")
                return None
            
        except requests.exceptions.Timeout:
            logging.error(f"{EMOJI['ERROR']} API请求超时，服务器可能繁忙")
            return None
        except requests.exceptions.ConnectionError:
            logging.error(f"{EMOJI['ERROR']} 无法连接到API服务器，请检查网络连接")
            return None
        except Exception as e:
            logging.error(f"{EMOJI['ERROR']} 请求API时发生错误")
            logging.debug(f"详细错误信息: {str(e)}")
            return None
            
    except Exception as e:
        logging.error(f"{EMOJI['ERROR']} 请求API过程中发生错误")
        logging.debug(f"详细错误信息: {str(e)}")
        return None

def save_free_account_cache(account_info):
    """保存免费账号到本地缓存"""
    try:
        cache_data = {
            "account": account_info,
            "timestamp": int(time.time())
        }
        with open(FREE_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=4)
        logging.info(f"{EMOJI['SAVE']} 免费账号已缓存到本地，有效期5小时")
        return True
    except Exception as e:
        logging.error(f"{EMOJI['ERROR']} 保存免费账号缓存失败: {str(e)}")
        return False

def load_free_account_cache():
    """从本地缓存加载免费账号"""
    try:
        if os.path.exists(FREE_CACHE_FILE):
            with open(FREE_CACHE_FILE, "r", encoding="utf-8") as f:
                cache_data = json.load(f)
            
            # 检查缓存是否过期（5小时）
            timestamp = cache_data.get("timestamp", 0)
            current_time = int(time.time())
            
            if current_time - timestamp <= CACHE_DURATION:
                logging.info(f"{EMOJI['INFO']} 使用本地缓存的免费账号，剩余有效时间: {format_time_remaining(timestamp + CACHE_DURATION - current_time)}")
                return cache_data.get("account")
            else:
                logging.info(f"{EMOJI['INFO']} 本地缓存的免费账号已过期，将重新获取")
                return None
        return None
    except Exception as e:
        logging.error(f"{EMOJI['ERROR']} 加载免费账号缓存失败: {str(e)}")
        return None

def format_time_remaining(seconds):
    """格式化剩余时间"""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours)}小时{int(minutes)}分钟"

def show_promotion():
    """显示推广信息"""
    logging.info("\n" + "=" * 50)
    logging.info(f"{EMOJI['FREE']}  每日免费功能由【听泉】提供支持")
    logging.info(f"{EMOJI['INFO']}  免费账号每天可使用一次，并且可能有使用限制")
    logging.info(f"{EMOJI['INFO']}  【推荐使用】:")
    logging.info(f"   🔥 付费号池API: 稳定高权重不降智 全部独立IP不重复 购买后换上新密钥即可使用")
    logging.info(f"   🔥 听泉一键助手: 提供界面化操作，更加便捷可靠")
    logging.info(f"{EMOJI['INFO']}  详情请访问: https://cursorpro.com.cn")
    logging.info(f"{EMOJI['INFO']}  或联系微信: behikcigar")
    logging.info("=" * 50 + "\n")
    
    # 延迟几秒钟，确保用户看到广告信息
    for i in range(3, 0, -1):
        logging.info(f"广告倒计时: {i}秒...")
        time.sleep(1)

def get_free_account():
    """获取免费账号"""
    try:
        logging.info(f"{EMOJI['FREE']} 正在准备获取每日免费账号...")
        
        # 检查本地缓存
        cached_account = load_free_account_cache()
        if cached_account:
            return cached_account
        
        # 显示推广信息
        show_promotion()
        
        # 获取必要的参数
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            ip_address = get_ip_address()
            machine_info = get_hardware_machine_id()
            machine_id = machine_info["id"]
            saved_key = load_identity_key()
            location = get_approximate_location()
        
        # 构建请求数据
        data = {
            'ip': ip_address,
            'machine_id': machine_id
        }
        
        # 添加可选参数
        if saved_key:
            data['identity_key'] = saved_key
        
        if location:
            data['location'] = json.dumps(location)
        
        # 发送请求
        logging.info(f"{EMOJI['API']} 正在向免费API发送请求...")
        try:
            # 使用更长的超时时间和错误处理
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                response = requests.post(FREE_API_URL, headers=HEADERS, data=data, timeout=10, verify=False)
            
            if response.status_code != 200:
                logging.error(f"{EMOJI['ERROR']} 免费API服务暂时不可用 ({response.status_code})")
                return None
            
            try:
                result = response.json()
                if result.get("code") != 0:
                    logging.error(f"{EMOJI['ERROR']} {result.get('msg', '免费API返回错误')}")
                    return None
                
                account_info = result.get("data")
                if not account_info:
                    logging.error(f"{EMOJI['ERROR']} 免费API返回数据格式错误")
                    return None
                
                logging.info(f"{EMOJI['SUCCESS']} 成功获取免费账号")
                
                # 保存到本地缓存
                save_free_account_cache(account_info)
                
                return account_info
            except ValueError:
                logging.error(f"{EMOJI['ERROR']} 免费API返回的数据无法解析")
                return None
            
        except requests.exceptions.Timeout:
            logging.error(f"{EMOJI['ERROR']} 免费API请求超时，服务器可能繁忙")
            return None
        except requests.exceptions.ConnectionError:
            logging.error(f"{EMOJI['ERROR']} 无法连接到免费API服务器，请检查网络连接")
            return None
        except Exception as e:
            logging.error(f"{EMOJI['ERROR']} 请求免费API时发生错误")
            logging.debug(f"详细错误信息: {str(e)}")
            return None
            
    except Exception as e:
        logging.error(f"{EMOJI['ERROR']} 获取免费账号过程中发生错误")
        logging.debug(f"详细错误信息: {str(e)}")
        return None

def check_cursor_version():
    """检查cursor版本"""
    pkg_path, main_path = patch_cursor_get_machine_id.get_cursor_paths()
    with open(pkg_path, "r", encoding="utf-8") as f:
        version = json.load(f)["version"]
    return patch_cursor_get_machine_id.version_check(version, min_version="0.45.0")

def reset_machine_id(greater_than_0_45):
    """重置机器码"""
    if greater_than_0_45:
        logging.info(f"{EMOJI['INFO']} 检测到Cursor版本 >= 0.45.0，使用go_cursor_help方法")
        go_cursor_help.go_cursor_help()
    else:
        logging.info(f"{EMOJI['INFO']} 检测到Cursor版本 < 0.45.0，使用MachineIDResetter方法")
        MachineIDResetter().reset_machine_ids()

def update_cursor_auth(account_info):
    """更新Cursor认证信息"""
    try:
        auth_manager = CursorAuthManager()
        email = account_info.get("email")
        access_token = account_info.get("access_token")
        refresh_token = account_info.get("refresh_token")
        result = auth_manager.update_auth(email=email, access_token=access_token, refresh_token=refresh_token)
        if result:
            logging.info(f"{EMOJI['SUCCESS']} Cursor认证信息更新成功")
            return True
        else:
            logging.error(f"{EMOJI['ERROR']} Cursor认证信息更新失败")
            return False
    except Exception as e:
        logging.error(f"{EMOJI['ERROR']} 更新认证信息时发生错误: {str(e)}")
        return False

def print_account_info(account_info):
    """打印账号信息"""
    logging.info(f"\n{EMOJI['INFO']} {format_info('Cursor 账号信息:')}")
    logging.info(f"邮箱: {format_highlight(account_info.get('email'))}")
    logging.info(f"密码: {format_highlight(account_info.get('password'))}")
    
    remaining_balance = account_info.get('remaining_balance', '未知')
    logging.info(f"可用额度: {format_success(remaining_balance)}")
    
    
    registration_time = account_info.get('registration_time', '未知')
    logging.info(f"注册时间: {format_info(registration_time)}")

def print_end_message():
    """打印结束信息"""
    logging.info("\n\n")
    logging.info(format_success("=" * 50))
    logging.info(format_success("🎉 所有操作已完成"))
    logging.info(format_info("\n=== 获取更多信息 ==="))
    logging.info(format_highlight("🏆 成品助手: 听泉cursor助手"))
    logging.info(format_highlight("🔥 万级高权重账号池api购买请联系: 微信淘宝购买"))
    logging.info(format_success("=" * 50))
    logging.info(format_info("请前往发卡网网站有淘宝链接和微信联系方式：https://cursorpro.com.cn"))

def main():
    """主函数"""
    print_logo()
    logging.info(f"\n{EMOJI['INFO']}  {format_info('听泉CursorPro换号工具')} {format_highlight('[配合听泉高权重cursor账号池使用]')}")
    
    # 获取并显示硬件机器码
    machine_info = get_hardware_machine_id()
    logging.info(f"{EMOJI['HARDWARE']}  当前系统:  {format_info(machine_info['platform'])}")
    logging.info(f"{EMOJI['HARDWARE']}  机器码:  {format_highlight(machine_info['id'])}")
    
    # 检查Cursor版本
    greater_than_0_45 = check_cursor_version()
    
    # 重复选择模式的标记
    while True:
        # 显示功能选择菜单
        print("\n" + format_info("请选择使用模式:"))
        print(f"{EMOJI['FREE']} 1. {format_highlight('每日免费使用一次')}")
        print(f"{EMOJI['API']} 2. {format_info('使用身份密钥')}")
        
        # 获取用户选择
        choice = 0
        while choice not in [1, 2]:
            try:
                choice_input = input(f"{format_info('请输入选项 (1 或 2):')} ").strip()
                if not choice_input:  # 如果用户直接回车，默认选择免费模式
                    choice = 1
                    break
                choice = int(choice_input)
                if choice not in [1, 2]:
                    print(format_warning("无效选项，请重新输入"))
            except ValueError:
                print(format_error("请输入有效数字"))
        
        account_info = None
        
        # 根据用户选择执行相应操作
        if choice == 1:
            # 使用免费模式
            logging.info(f"{EMOJI['FREE']} {format_highlight('您选择了每日免费使用模式')}")
            account_info = get_free_account()
            if not account_info:
                logging.error(f"{EMOJI['ERROR']} {format_error('获取免费账号失败')}")
                retry_input = input(f"{format_info('是否重新选择模式? (Y/n):')} ").strip().lower()
                if retry_input == 'n':
                    logging.error(f"{EMOJI['ERROR']} {format_error('程序将退出')}")
                    return
                continue  # 返回选择模式
        
        if choice == 2:
            # 使用身份密钥模式
            logging.info(f"{EMOJI['API']} {format_info('您选择了身份密钥模式')}")
            
            # 加载已保存的密钥
            saved_key = load_identity_key()
            if saved_key:
                logging.info(f"{EMOJI['KEY']} {format_info('检测到已保存的身份密钥')}")
                user_input = input(f"{format_info('是否使用已保存的身份密钥? (直接回车使用，输入新密钥覆盖):')} ").strip()
                identity_key = user_input if user_input else saved_key
            else:
                identity_key = input(f"{EMOJI['KEY']} {format_info('请输入您的身份密钥:')} ").strip()
            
            if not identity_key:
                logging.error(f"{EMOJI['ERROR']} {format_error('身份密钥不能为空')}")
                retry_input = input(f"{format_info('是否重新选择模式? (Y/n):')} ").strip().lower()
                if retry_input == 'n':
                    return
                continue  # 返回选择模式
            
            # 保存身份密钥
            if not saved_key or identity_key != saved_key:
                save_identity_key(identity_key)
            
            # 从API获取账号信息
            account_info = get_account_from_api(identity_key)
            if not account_info:
                logging.error(f"{EMOJI['ERROR']} {format_error('无法获取账号信息，请检查身份密钥是否正确')}")
                retry_input = input(f"{format_info('是否重新选择模式? (Y/n):')} ").strip().lower()
                if retry_input == 'n':
                    return
                continue  # 返回选择模式
        
        # 处理获取到的账号信息
        if account_info:
            # 打印账号信息
            print_account_info(account_info)
            # 关闭编辑器
            exit_cursor.ExitCursor()

            # 更新Cursor认证信息
            if update_cursor_auth(account_info):
                # 重置机器码
                logging.info(f"{EMOJI['INFO']} {format_info('开始重置机器码...')}")
                reset_machine_id(greater_than_0_45)
                logging.info(f"{EMOJI['SUCCESS']} {format_success('机器码重置完成')}")
            
            # 打印结束信息
            print_end_message()
            break  # 完成所有操作，退出循环
        else:
            logging.error(f"{EMOJI['ERROR']} {format_error('无法获取账号信息')}")
            retry_input = input(f"{format_info('是否重新选择模式? (Y/n):')} ").strip().lower()
            if retry_input == 'n':
                logging.error(f"{EMOJI['ERROR']} {format_error('程序将退出')}")
                return
            # 如果用户选择重试，循环会继续，重新显示选择菜单

if __name__ == "__main__":
    try:
        # 设置控制台窗口标题（仅在Windows系统下有效）
        if sys.platform == "win32":
            os.system("title 听泉CursorPro换号工具")
            
        main()
    except KeyboardInterrupt:
        logging.info(f"\n{EMOJI['INFO']} {format_warning('程序已被用户中断')}")
    except Exception as e:
        logging.error(f"{EMOJI['ERROR']} {format_error('程序执行出现错误')}")
        logging.debug(f"详细错误信息: {str(e)}")
        import traceback
        logging.debug(traceback.format_exc())
    finally:
        input(f"\n{format_info('程序执行完毕，按回车键退出...')}") 