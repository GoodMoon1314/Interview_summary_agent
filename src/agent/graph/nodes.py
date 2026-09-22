import time

from agent.graph.subgraphs.memory.memoryGraph import memoryGraph
from agent.tools.middleware import UserContext
from config.config import db_config
from prompt.prompt import demand_prompt, review_prompt
from agent.graph.state import InputState, OutputState
from agent.graph.structure import UserDemand, ProblemReview
from agent.graph.subgraphs.demand.demandGraph import demandGraph
from typing import Literal, Sequence
from langgraph.types import Send
from agent.graph.state import OverAllState
from langgraph.types import interrupt, Overwrite
from factory.modelFactory import chat_model
from langchain.messages import SystemMessage, HumanMessage
import psycopg
from psycopg.rows import dict_row
from utils.loggerUtil import logger


# 用户输入端
def user_input_node(state: InputState) -> OverAllState:
    user_input: str = state["user_input"]
    is_history: bool = state["is_history"]
    user_id: str = state["user_id"]
    thread_id: str = state["thread_id"]

    # 查询用户输入是否合规,合规则优化
    agent = chat_model.with_structured_output(UserDemand)
    HumanMessage(content=user_input)

    result: UserDemand = agent.invoke(
        [SystemMessage(content=demand_prompt), HumanMessage(content=user_input)]
    )

    return {
        "is_rule": result.get("is_rule"),
        "problem_demand": result.get("demand", ""),
        "is_history": is_history,
        "problem_list": [],
        "task": {},
        "task_list": [],
        "is_continuous": True,
        "is_summary": True,
        "problem_review_list": Overwrite([]),
        "user_id": user_id,
        "thread_id": thread_id,
        "user_data": {},
        "interview_summary": {},
        "agent_output_messages": "请输入面试需求!",
        "messages": [],
    }


# 用户需求路由
def demand_router(state: OverAllState) -> Literal["agent_output_node", "get_user_data_node"]:
    is_rule: bool = state["is_rule"]

    if is_rule:
        return "get_user_data_node"
    else:
        return "agent_output_node"


# 获取用户历史信息节点
def get_user_data_node(state: OverAllState) -> OverAllState:
    # 获取用户信息
    user_id = state["user_id"]
    thread_id = state["thread_id"]
    user_data = {}

    # 独立psycopg连接，和PostgresStore完全分开
    conn_str = db_config["DB_URL"]
    with psycopg.connect(conn_str, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            sql = "SELECT user_id, user_name, type, summary_text, created_time FROM interview_summary WHERE type = 'interview_summary' AND thread_id = %s AND user_id = %s;"
            cur.execute(sql, (thread_id, user_id))
            row = cur.fetchone()

            if row:
                user_data = row

    return {
        "user_data": user_data
    }


# 子图
# 获取面试题
def demand_graph_node(state: OverAllState) -> OverAllState:
    is_history = state["is_history"]
    problem_demand = state["problem_demand"]

    result = demandGraph.invoke({
        "is_history": is_history,
        "problem_demand": problem_demand
    }, context=UserContext(max_attempts=5))

    return {
        "problem_list": result["problem_list"]
    }


# 面试题传出
def get_problem_node(state: OverAllState) -> OverAllState:
    problem_list = state["problem_list"]

    interrupt(problem_list)

    return {
        "problem_list": problem_list,
        "is_continuous":True
    }


# 进行面试
def get_task(state: OverAllState) -> OverAllState:
    is_continuous = state["is_continuous"]

    if not is_continuous:
        return {
            "task_list": [],
            "is_summary": False
        }

    # 中断,等待任务,
    command = interrupt("正在等待任务")
    task_list = command["task_list"]
    is_continuous = command["is_continuous"]

    return {
        "task_list": task_list,
        "is_summary": True,
        "is_continuous": is_continuous
    }


def search_node(state: OverAllState) -> Sequence[Send]:
    # 拿取任务列表
    task_list = state.get("task_list", [])
    is_summary = state.get("is_summary")

    if not is_summary:
        problem_review_list = state.get("problem_review_list")
        user_data = state.get("user_data")
        thread_id = state.get("thread_id")
        user_id = state.get("user_id")
        return [Send("memory_node", {
            "problem_review_list": problem_review_list,
            "user_data": user_data,
            "thread_id": thread_id,
            "user_id": user_id,
        })]

    # 去分配任务
    send_list = []
    for task in task_list:
        send = Send(
            "review_node",
            {
                "task": task
            }
        )
        send_list.append(send)

    return send_list


def review_node(state: OverAllState) -> OverAllState:
    task = state.get("task")

    system = SystemMessage(content=review_prompt)

    problem = task["problem"]
    answer = task["answer"]
    user_answer = task["user_answer"]

    human = HumanMessage(content=f"问题:{problem}\n参考答案:{answer}\n用户回答:{user_answer}")

    agent = chat_model.with_structured_output(ProblemReview)

    result = agent.invoke(
        [system, human]
    )

    problem_review_dict = {}
    problem_review_dict["problem"] = problem
    problem_review_dict["answer"] = answer
    problem_review_dict["user_answer"] = user_answer
    problem_review_dict["review"] = result

    return {
        "problem_review_list": [problem_review_dict]
    }


# memory节点
def memory_node(state: OverAllState) -> OverAllState:
    problem_review_list = state.get("problem_review_list")
    user_data = state.get("user_data")
    thread_id = state.get("thread_id")
    user_id = state.get("user_id")

    result = memoryGraph.invoke({
        "problem_review_list": problem_review_list,
        "user_data": user_data,
        "thread_id": thread_id,
        "user_id": user_id,
    })

    return {
        "agent_output_messages": result["agent_output_messages"]
    }


# agent输出端
def agent_output_node(state: OverAllState) -> OutputState:
    agent_output_messages = state.get("agent_output_messages")

    return {
        "agent_output_messages": agent_output_messages
    }
