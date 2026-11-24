@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

REM ============================================================
REM  一键重建 agent/my_agent.exe
REM  前提：已安装 Python 3.11+（安装时勾选 Add Python to PATH）
REM  关键：MAAFW_VER 必须与 MFA 里显示的 MaaFramework 版本一致
REM        （MFA -> 设置 -> 版本信息 里可以看到）
REM        不一致会报 Protocol version mismatch，agent 连不上
REM ============================================================

set "MAAFW_VER=5.16.1"

echo ==========================================
echo   重建 my_agent.exe  (MaaFw %MAAFW_VER%^)
echo ==========================================

where py >nul 2>nul
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.11 并加入 PATH
    pause
    exit /b 1
)

if not exist ".buildenv\Scripts\python.exe" (
    echo [1/3] 创建虚拟环境 .buildenv ...
    py -3 -m venv .buildenv
    if errorlevel 1 ( pause & exit /b 1 )
) else (
    echo [1/3] 复用已有虚拟环境 .buildenv
)

echo [2/3] 安装依赖 MaaFw==%MAAFW_VER% 和 pyinstaller ...
".buildenv\Scripts\python.exe" -m pip install --disable-pip-version-check -q ^
    -i https://pypi.tuna.tsinghua.edu.cn/simple ^
    --trusted-host pypi.tuna.tsinghua.edu.cn ^
    "MaaFw==%MAAFW_VER%" pyinstaller
if errorlevel 1 ( echo [错误] 依赖安装失败 & pause & exit /b 1 )

echo [3/3] 打包中，请稍候（约 1-2 分钟）...
".buildenv\Scripts\python.exe" -m PyInstaller --noconfirm --clean my_agent.spec
if errorlevel 1 ( echo [错误] 打包失败 & pause & exit /b 1 )

copy /y "dist\my_agent.exe" "my_agent.exe" >nul
if errorlevel 1 ( echo [错误] 复制 exe 失败 & pause & exit /b 1 )

echo.
echo [完成] 已生成: %~dp0my_agent.exe
echo        提交前记得跑一次任务，确认 agent 能连上。
echo.
pause
