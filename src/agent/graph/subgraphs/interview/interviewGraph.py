from langgraph.graph import StateGraph, START, END
from agent.graph.subgraphs.interview.interviewNodes import *
from agent.graph.state import OverAllState


builder = StateGraph(state_schema=OverAllState)

builder.add_node("review_node", review_node)

builder.add_edge(START, "review_node")
builder.add_edge("review_node", END)

interviewGraph = builder.compile()















"""if __name__ == '__main__':
    list1 = [{'problem': '你在项目中做过 RAG，请描述从用户提问到最终输出回答的完整链路，并说明每个环节的作用。',
              'answer': '完整链路为七步——① Query 用户查询；② 文档处理；③ Chunking 文本切分；④ Embedding 向量化；⑤ 检索；⑥ Rerank 重排序；⑦ 生成回答。关键得分点：七步顺序正确；能说明各环节作用（如切分影响检索粒度、Rerank 对候选重排提精度）；能点明“大模型负责理解与生成、RAG 负责提供事实素材”的分工。追问方向：切分大小/overlap 如何设定？Rerank 前后 Top-K 怎么变？'},
             {'problem': '设计 RAG 知识库系统时，文档更新如何保证向量库与搜索引擎的数据一致性？',
              'answer': '数据层通常采用向量库与 ES 搜索引擎双写存储，文档更新走异步任务处理。关键得分点：说出“双写存储”的架构；点明文档更新用异步任务；理解一致性问题来自向量库与 ES 两份存储。追问方向：异步任务失败如何补偿？更新期间用户查询读到旧数据怎么处理？'}
             ]

    config = {
        "configurable": {
            "thread_id": "test_9_18_8"
        }
    }

    with PostgresSaver.from_conn_string(db_config["DB_URL"]) as checkpointer:
        interviewGraph = builder.compile(checkpointer=checkpointer)

        interviewGraph.invoke({}, config=config)

        # 定义指令
        command = {
            "is_continuous": True,
            "task_list": []
        }

        num = len(list1)

        for i, e in enumerate(list1):

            # 拿取检查点信息
            snapshot = interviewGraph.get_state(config)

            # 判断是否要上传任务
            if snapshot.interrupts:  # 中断,上传任务指令

                res = interviewGraph.invoke(Command(resume=command), config=config)

                logger.info(res)

                command["task_list"] = []

            problem = e["problem"]
            answer = e["answer"]

            user_answer = input(problem)

            task = {
                "problem": problem,
                "answer": answer,
                "user_answer": user_answer
            }
            command["task_list"].append(task)

            # 判断是否最后一题
            is_last = (id == num - 1)
            command["is_continuous"] = not is_last


        while True:
            snapshot = interviewGraph.get_state(config)
            if snapshot.interrupts:
                print("提交最后一轮任务，开始生成面试总结...")
                res = interviewGraph.invoke(Command(resume=command), config=config)
                print(res)
                break
            time.sleep(0.5)"""
