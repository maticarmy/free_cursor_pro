# -*- mode: python ; coding: utf-8 -*-
import os
import sys

# 添加管理员权限要求的manifest
admin_manifest = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0"><trustInfo xmlns="urn:schemas-microsoft-com:asm.v3"><security><requestedPrivileges><requestedExecutionLevel level="requireAdministrator" uiAccess="false"/></requestedPrivileges></security></trustInfo></assembly>'

a = Analysis(
    ['tingquan_cursor_pro.py'],  # 更新主脚本名称
    pathex=[],
    binaries=[],
    datas=[
        ('logo.py', '.'),  # 添加logo.py
        ('cursor_auth_manager.py', '.'),
        ('reset_machine.py', '.'),
        ('patch_cursor_get_machine_id.py', '.'),  
        ('go_cursor_help.py', '.'),
        ('exit_cursor.py', '.'),  # 添加退出脚本
        ('logger.py', '.'),  # 添加日志
    ],
    hiddenimports=[
        'cursor_auth_manager',
        'reset_machine',
        'patch_cursor_get_machine_id',
        'go_cursor_help',
        'exit_cursor',
        'logger',
        'logo',
        # 外部库
        'requests',
        'colorama',
        'psutil',
        'urllib3',
        # 标准库
        'json',
        'uuid',
        'socket',
        'hashlib',
        'time',
        'warnings',
        'platform',
        'sqlite3',
        'datetime',
        'shutil',
        'subprocess',
        'os',
        'sys',
        're',
        'tempfile',
        'logging'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'DrissionPage',
        'dotenv'
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

target_arch = os.environ.get('TARGET_ARCH', None)

# 创建临时manifest文件
if sys.platform == 'win32':
    import tempfile
    manifest_path = os.path.join(tempfile.gettempdir(), 'admin_manifest.xml')
    with open(manifest_path, 'w') as f:
        f.write(admin_manifest)
else:
    manifest_path = None

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='听泉CursorPro换号工具',  # 程序名称：听泉CursorPro换号工具
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=True,  # 对非Mac平台无影响
    target_arch=target_arch,  # 仅在需要时通过环境变量指定
    codesign_identity=None,
    entitlements_file=None,
    icon='screen/icon.ico' if os.path.exists('screen/icon.ico') else None,  # 如果有icon文件则使用
    manifest=manifest_path if sys.platform == 'win32' else None,  # 添加管理员权限manifest
    uac_admin=True if sys.platform == 'win32' else False,  # 在Windows上请求管理员权限
)

# 清理临时manifest文件
if sys.platform == 'win32' and os.path.exists(manifest_path):
    os.remove(manifest_path) 