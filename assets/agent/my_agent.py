import sys
import json
from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context

@AgentServer.custom_action("execute_sequential")
class ExecuteSequential(CustomAction):
    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> CustomAction.RunResult:
        # 1. 获取你在 pipeline 中传入的任务列表
        task_list = json.loads(argv.custom_action_param).get("tasks", [])

        # 2. 按顺序执行它们
        for task_name in task_list:
            ret = context.run_task(task_name)
            if not ret:
                print(f"任务执行失败: {task_name}")
                # 如果想让一个任务失败后停止，可以在这里取消注释下一行
                # return CustomAction.RunResult(success=False)

        # 3. 所有任务执行完毕，通知框架动作成功
        return CustomAction.RunResult(success=True)

if __name__ == "__main__":
    # 接收从UI传来的 socket_id
    # UI 会以 "python my_agent.py <socket_id>" 的形式启动你的脚本
    socket_id = sys.argv[1] if len(sys.argv) > 1 else None

    if socket_id is None:
        print("错误：必须提供一个 socket_id 作为命令行参数")
        sys.exit(1)

    # 用获取到的 socket_id 启动 Agent 服务器
    print(f"正在使用 socket {socket_id} 启动 Agent 服务器...")
    AgentServer.start_up(socket_id)      # <--- 这里传入 socket_id
    AgentServer.join()