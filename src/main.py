import threading
import queue
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.types import Command
from agent.graph.graph import builder
from config.config import db_config
from utils.loggerUtil import logger

q_to_sub = queue.Queue()
q_to_main = queue.Queue()
answer_buffer = queue.Queue()
stop_flag = threading.Event()
user_finished = threading.Event()


def _drain(q: queue.Queue) -> list:
    items = []
    while True:
        try:
            items.append(q.get_nowait())
        except queue.Empty:
            break
    return items


def graph_worker(thread_id: str):
    try:
        with PostgresSaver.from_conn_string(db_config["DB_URL"]) as checkpointer:
            main_graph = builder.compile(checkpointer=checkpointer)
            config = {"configurable": {"thread_id": thread_id}}

            user_input = input("您要面试的岗位以及面试需要?\n")
            is_history = True if input("是否需要根据您的历史面试情况进行筛选面试题?(y:是/n:否)") == 'y' else False

            # ---------- 启动图，触发第一次中断 ----------
            result = main_graph.invoke(
                {
                    "user_input": user_input,
                    "is_history": is_history,
                    "user_id": "1001",
                    "thread_id": "thread_001",
                },
                config=config,
            )

            while not stop_flag.is_set():
                interrupts = result.get("__interrupt__") if isinstance(result, dict) else None

                # ---------- 图跑完 ----------
                if not interrupts:
                    q_to_main.put({"type": "done", "result": result})
                    break

                iv = interrupts[0].value

                # ---------- 第一次中断：全部题目 ----------
                if not (isinstance(iv, str) and iv == "正在等待任务"):
                    q_to_main.put({"type": "question", "data": iv})
                    result = main_graph.invoke(
                        Command(resume={"task_list": [], "is_continuous": True}),
                        config=config,
                    )
                    continue

                # ---------- 后续中断：get_task 等答案 ----------
                # 阻塞等第一条答案（或用户答完信号）
                first = None
                got = False
                while not stop_flag.is_set():
                    try:
                        first = answer_buffer.get(timeout=0.5)
                        got = True
                        break
                    except queue.Empty:
                        if user_finished.is_set():
                            # 用户答完 + 缓冲区空 → 收尾
                            result = main_graph.invoke(
                                Command(resume={"task_list": [], "is_continuous": False}),
                                config=config,
                            )
                            break
                        continue

                if stop_flag.is_set():
                    break

                # 如果是"缓冲区空 + 用户答完"触发的收尾，first 没拿到
                if not got:
                    # result 已经是收尾后的结果，回到外层 while 检查是否还有中断
                    # 如果没有中断，外层会发 done 并 break
                    continue

                # ---------- 拿到 first，drain 剩余 ----------
                batch = [first]
                while True:
                    try:
                        item = answer_buffer.get_nowait()
                    except queue.Empty:
                        break
                    if item is not None:
                        batch.append(item)

                # 判断是不是最后一批：用户已答完 且 缓冲区已空
                is_last_batch = user_finished.is_set() and answer_buffer.empty()
                is_continuous = not is_last_batch

                q_to_main.put({
                    "type": "info",
                    "msg": f"图消费了 {len(batch)} 条答案，is_continuous={is_continuous}",
                })

                result = main_graph.invoke(
                    Command(resume={
                        "task_list": batch,
                        "is_continuous": is_continuous,
                    }),
                    config=config,
                )

                # 如果是最后一批，resume 后图应该跑完（无中断），
                # 下一次外层 while 会发 done。这里不需要特殊处理。
                # 但如果图因为其他原因又中断了（比如 get_task 又被调用），
                # 外层 while 会继续处理。

    except Exception as e:
        logger.exception("[graph_worker] 异常")
        q_to_main.put({"type": "error", "error": str(e)})
    finally:
        q_to_main.put({"type": "exit"})


if __name__ == "__main__":
    thread_id = "test_9_20_10"
    stop_flag.clear()
    user_finished.clear()

    worker_thread = threading.Thread(target=graph_worker, args=(thread_id,), daemon=True)
    worker_thread.start()

    all_problems = []
    final_result = None

    try:
        while True:
            msg = q_to_main.get()
            mtype = msg["type"]

            if mtype == "done":
                final_result = msg.get("result")
                print("\n========== 面试总结 ==========")
                if isinstance(final_result, dict):
                    print(final_result.get("agent_output_messages"))
                else:
                    print(final_result)
                print("==============================\n")
                break

            if mtype == "question":
                all_problems = msg["data"]
                total = len(all_problems)
                print(f"共 {total} 道题，请连续作答")

                for idx, p in enumerate(all_problems):
                    ans = input(f"[第{idx + 1}/{total}题] {p['problem']}\n> ")

                    # 最后一题：先 set 标记，再塞答案
                    if idx + 1 == total:
                        user_finished.set()

                    answer_buffer.put({
                        "problem": p["problem"],
                        "answer": p.get("answer", ""),
                        "user_answer": ans,
                    })
                continue

    except KeyboardInterrupt:
        print("用户中断")
    finally:
        stop_flag.set()
        user_finished.set()
        worker_thread.join(timeout=5)
