# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller 打包配置（可移植版）

说明：
- 旧版把 maa/bin 的路径硬编码成了某台机器的
  C:\\Users\\...\\Python311\\Lib\\site-packages\\maa\\bin，
  别人拿到仓库后无法直接重建。这里改为自动定位当前 Python 环境里的 maa/bin。
- 打包前必须先安装与「MFA 使用的 MaaFramework 版本」完全一致的 Python 绑定，
  否则运行时会出现：
      Protocol version mismatch client: [v5.16.1] [kProtocolVersion=8]
      server: [resp.version=v5.8.0-beta.1] [resp.protocol=7]
      -> Please update AgentServer
  表现为 agent 连不上、任务在「连接」阶段失败。

常用命令（版本号按 MFA 设置页显示的 MaaFramework 版本填写）：
    pip install "MaaFw==5.16.1"
    pyinstaller --noconfirm --clean my_agent.spec

也可以直接双击同目录下的 build_agent.bat 一键完成。
"""

import os
import site


def _find_maa_bin() -> str:
    """定位已安装的 maa 包内的 bin 目录（内含 MaaAgentServer.dll 等）。"""
    candidates = []
    try:
        candidates.extend(site.getsitepackages())
    except Exception:
        pass
    try:
        candidates.append(site.getusersitepackages())
    except Exception:
        pass
    for base in candidates:
        path = os.path.join(base, "maa", "bin")
        if os.path.isdir(path):
            return path
    raise SystemExit(
        "未找到 maa/bin 目录，请先执行: pip install \"MaaFw==<与 MaaFramework 相同的版本>\""
    )


a = Analysis(
    ['my_agent.py'],
    pathex=[],
    binaries=[],
    datas=[(_find_maa_bin(), 'maa/bin')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='my_agent',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
