import time

from langchain.messages import HumanMessage, SystemMessage
from agent.tools.middleware import UserContext
from prompt.prompt import demand_prompt
from agent.graph.state import InputState, OverAllState, OutputState
from factory.modelFactory import chat_model
from agent.graph.structure import UserDemand
from typing import Literal
from agent.graph.subgraphs.demand.demandGraph import demandGraph
from agent.graph.subgraphs.interview.interviewGraph import interviewGraph
from utils.loggerUtil import logger
from langgraph.types import Command
from typing import Literal, Sequence
from langgraph.types import Send
from agent.graph.state import OverAllState
from langgraph.types import interrupt, Command

from agent.graph.structure import ProblemReview
from factory.modelFactory import chat_model
from langchain.messages import SystemMessage, HumanMessage

from prompt.prompt import review_prompt
from utils.loggerUtil import logger


# 用户输入端
def user_input_node(state: InputState) -> OverAllState:
    user_input: str = state["user_input"]
    is_history: bool = state["is_history"]

    # 查询用户输入是否合规,合规则优化
    agent = chat_model.with_structured_output(UserDemand)
    HumanMessage(content=user_input)

    result: UserDemand = agent.invoke(
        [SystemMessage(content=demand_prompt), HumanMessage(content=user_input)]
    )

    return {
        "is_rule": result["is_rule"],
        "problem_demand": result.get("demand", ""),
        "is_history": is_history,
        "agent_output_messages": "请输入面试需求!"
    }


# agent输出端
def agent_output_node(state: OverAllState) -> OutputState:
    problem_review_list = state.get("problem_review_list")

    return {
        "agent_output_messages": problem_review_list
    }


# 用户需求路由
def demand_router(state: OverAllState) -> Literal["demand_graph_node", "agent_output_node"]:
    is_rule: bool = state["is_rule"]

    if is_rule:
        return "demand_graph_node"
    else:
        return "agent_output_node"


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

    #中断,传出面试题
    interrupt(problem_list)

    return {
        "problem_list":problem_list
    }

# 进行面试
def get_task(state: OverAllState) -> OverAllState:
    # 中断,等待任务,
    command = interrupt("正在等待任务")

    task_list = command["task_list"]
    is_continuous = command["is_continuous"]

    logger.debug(f"[get_task]得到用户回复:{command}")

    return {
        "task_list": task_list,
        "is_continuous": is_continuous
    }

def output_node(state: OverAllState) -> OverAllState:
    problem_review_list = state["problem_review_list"]

    logger.debug(f"[output_node]面试结束,返回值:{problem_review_list}")

    return {
        "problem_review_list": problem_review_list
    }


def search_node(state: OverAllState) -> Sequence[Send]:
    # 拿取任务列表
    task_list = state.get("task_list", [])
    is_continuous = state.get("is_continuous")

    if not is_continuous:
        problem_review_list = state["problem_review_list"]
        return [Send("output_node", {
            "problem_review_list":problem_review_list
        })]

    # 遍历任务列表,没有任务则去中断等待
    if not task_list:
        return [Send("get_task", {})]

    logger.debug(f"[search_node]当前任务列表:{task_list}")
    logger.debug(f"[search_node]当前任务状态:{is_continuous}")

    # 去分配任务
    send_list = []
    for task in task_list:
        send = Send(
            "interviewGraph",
            {
                "task": task
            }
        )
        send_list.append(send)

    return send_list



