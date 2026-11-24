# agent 版本不匹配（连不上 agent）排查与重新打包

## 典型报错

`logs/log-YYYYMMDD.log` 或 `debug/maafw.log` 里会出现：

```
[ERR][AgentClient.cpp][L188] Protocol version mismatch
  client: ["v5.16.1"=v5.16.1] [kProtocolVersion=8]
  server: [resp.version=v5.8.0-beta.1] [resp.protocol=7]
[ERR][AgentClient.cpp][L190] Please update AgentServer
...
[ERR] 启动 Agent 失败：reason=Agent './agent/my_agent.exe' failed to start
[INF] 任务失败：连接
```

界面上表现为：点开始后卡在「连接」，提示 Agent 启动失败或一直连不上。

## 原因

`agent/my_agent.exe` 是用 Python 的 `MaaFw`（MaaFramework 的 Python 绑定）打包的
PyInstaller 单文件程序，它内部自带一份 `MaaAgentServer.dll`，这份 DLL 把
**agent 通信协议号** 写死在二进制里。

MFA 的「更新资源」是整包更新，会把 MaaFramework 一起升级，而协议号随框架版本变过：

| MaaFramework | agent 协议号 kProtocolVersion |
| --- | --- |
| 5.8.0-beta.1 | 7 |
| 5.12.3 | 7 |
| 5.16.1 | 8 |

框架升级后协议号一变，仓库里预编译的旧 `my_agent.exe` 就会被新客户端拒绝：

- 客户端（MFA，新框架）：我这里是协议 8
- 服务端（my_agent.exe，旧 MaaFw）：我这里是协议 7
- 不一致 → 直接断开 → agent 进程退出 → 任务在「连接」阶段失败

与游戏窗口、截图模式、配置无关，纯粹是 agent 打包版本太旧。

## 解决：用相同版本重打包

1. 安装 Python 3.11+（勾选 Add Python to PATH）。
2. 在 MFA 里查看当前 **MaaFramework 版本**（例如 `v5.16.1`）。
3. 修改 `build_agent.bat` 里的 `MAAFW_VER` 为同一版本（当前已设为 `5.16.1`）。
4. 双击 `agent/build_agent.bat`，它会自动建虚拟环境、装 `MaaFw==5.16.1`、打包，
   最后把新的 `my_agent.exe` 覆盖到 `agent/` 目录。
5. 重新打开 MFA 执行一次任务，确认能连上再提交 / 发版。

手动等价命令（在 `agent/` 目录下）：

```bat
py -3 -m venv .buildenv
.\.buildenv\Scripts\python.exe -m pip install "MaaFw==5.16.1" pyinstaller
.\.buildenv\Scripts\python.exe -m PyInstaller --noconfirm --clean my_agent.spec
copy /y dist\my_agent.exe my_agent.exe
```

> `my_agent.spec` 已改为自动定位当前环境里的 `maa/bin`，不再硬编码某台机器的
> `C:\Users\...\site-packages\maa\bin`，任何人克隆仓库后都能直接重建。

## 发版注意

- 打出来的 `my_agent.exe` 约 55 MB（含框架 DLL），低于 GitHub 单文件 100 MB 限制，
  继续按现在的方式提交 `agent/my_agent.exe` 即可（`tools/install.py` 会把整个
  `agent/` 目录打进发布包）。
- `agent/.buildenv/`、`agent/build/`、`agent/dist/` 已在 `.gitignore` 里，不要提交。
- **每次 MFA 整包更新把框架版本推上去后，都可能需要重打一次 exe**（协议号变了就会再断）。
  发版前建议本地先跑一次任务。
- `.github/workflows/install.yml` 里已把 MaaFramework 固定为 `MAAFW_VERSION`（当前 `v5.16.1`），
  不再跟随 `latest`。以后想升级框架，只改这一个变量是**不够**的：必须同时用同版本
  `MaaFw` 重打 `agent/my_agent.exe`，否则新包一发出去 agent 就连不上。
- 如果不想频繁受影响，可以把 MFA 的 `config/config.json` 里
  `EnableAutoUpdateResource` 设为 `false` 暂停自动更新；但更推荐框架更新后按上面步骤重打包。
