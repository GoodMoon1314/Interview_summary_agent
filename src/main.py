import time

from langgraph.checkpoint.postgres import PostgresSaver
from utils.loggerUtil import logger
from langgraph.types import Command
from agent.graph.graph import builder
from config.config import db_config

config = {
    "configurable":{
        "thread_id":"test_9_19_5"
    }
}

with PostgresSaver.from_conn_string(db_config["DB_URL"]) as checkpointer:
    main_graph = builder.compile(checkpointer=checkpointer)


    #获取面试题
    problem_result = main_graph.invoke(
        {
            "user_input": "rag面试题",
            "is_history": False
        },
        config=config
    )

    #图中断,传出面试题
    problem_list = problem_result["__interrupt__"][0].value
    logger.info(f"[传出面试题]{problem_list}")

    # 定义指令字典-用于传回审核指令
    command = {
        "is_continuous": True, #是否还有任务
        "task_list": [] #任务列表
    }

    # 恢复中断
    main_graph.invoke(Command(resume=command), config=config)

    #遍历面试题,开始面试
    num = len(problem_list)
    for i, e in enumerate(problem_list): #遍历面试题
        # 拿取检查点信息
        snapshot = main_graph.get_state(config)

        # 判断是否要上传任务
        if snapshot.interrupts:  # 中断,上传任务指令

            res = main_graph.invoke(Command(resume=command),config=config)

            logger.info(res)

            command["task_list"] = []

        #询问用户问题,并且拼接到task中
        problem = e["problem"]
        answer = e["answer"]

        user_answer = input(problem+"\n")

        task = {
            "problem": problem,
            "answer": answer,
            "user_answer": user_answer
        }
        command["task_list"].append(task)

        # 判断是否最后一题
        is_last = (i == num - 1)
        command["is_continuous"] = not is_last


    while True:
        snapshot = main_graph.get_state(config)
        if snapshot.interrupts:
            print("提交最后一轮任务，开始生成面试总结...")
            res = main_graph.invoke(Command(resume=command),config=config)
            print(res)
            break
        time.sleep(0.5)


