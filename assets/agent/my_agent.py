from maa.agent.agent_server import AgentServer

@AgentServer.custom_action("execute_sequential")
def execute_sequential(context):
    # 1. 从任务配置里，获取要执行的任务清单
    # 我们在Pipeline里写的 {"tasks": ["任务A", "任务B"]} 会通过这行被读取进来
    task_list = context.param.get("tasks", [])
    
    # 2. 按顺序一个一个执行这些任务
    for task_name in task_list:
        # context.run_task 会执行对应的Pipeline节点，并等待它完成
        ret = context.run_task(task_name)
        # 可选的错误处理：如果某个任务失败了，可以在这里加个简单的提示
        if not ret:
            print(f"任务执行失败: {task_name}")
            # 你也可以在这里决定是继续还是中断整个流程
            # return False
    
    # 3. 任务全部完成，返回成功
    return True