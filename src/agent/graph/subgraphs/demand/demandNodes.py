from langchain_core.messages import HumanMessage, SystemMessage
from typing import Literal
from agent.graph.structure import ProblemList
from agent.graph.state import DemandOverALLState, DemandOutputState
from agent.tools.agent_tools import search_rag
from factory.modelFactory import chat_model
from prompt.prompt import problem_prompt, demand_structure_prompt
from utils.loggerUtil import logger

"""
输入:
    is_history:是否查询历史
    problem_demand:面试需求
输出:
    problem_list:面试题库
"""

tools = [search_rag]


# 去切换查询历史节点/直接查询rag节点
def history_router(state: DemandOverALLState) -> Literal["get_rag_node"]:
    is_history = state["is_history"]

    if is_history:
        pass

    else:
        return "get_rag_node"


def get_rag_node(state: DemandOverALLState) -> DemandOverALLState:
    problem_demand = state["problem_demand"]
    messages = state["messages"]

    demand_agent = chat_model.bind_tools(tools=tools)

    messages.append(HumanMessage(content=problem_demand))

    problem = demand_agent.invoke(
        [SystemMessage(content=problem_prompt)] + messages
    )

    messages.append(problem)

    return {
        "messages": messages
    }


def demand_router(state: DemandOverALLState) -> Literal["tool_node", "demand_output_node"]:
    messages = state.get("messages")

    user_input = messages[-1]

    if user_input.tool_calls:
        return "tool_node"

    return "demand_output_node"


def demand_output_node(state: DemandOverALLState) -> DemandOutputState:
    problem_agent = chat_model.with_structured_output(ProblemList)

    problem = state["messages"][-1]

    result = problem_agent.invoke(
        [SystemMessage(content=demand_structure_prompt)] + [problem]
    )

    result_message = []

    for e in result.problem_list:
        p = e.problem
        a = e.answer
        result_message.append({"problem": p, "answer": a})

    return {
        "problem_list": result_message
    }
