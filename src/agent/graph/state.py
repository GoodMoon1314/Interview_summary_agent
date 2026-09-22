from typing import TypedDict, Annotated
from langgraph.graph import MessagesState
from operator import add
from typing import Annotated


# 主图的状态
class InputState(TypedDict):
    user_input: str  # 用户初始输入
    is_history: bool  # 是否查询历史(true:是/false否")
    user_id: str  # 用户id
    thread_id: str  # 线程id


class OverAllState(MessagesState):
    is_rule: bool  # 是否符合要求
    problem_demand: str  # 面试需求
    is_history: bool  # 是否需要查询历史
    problem_list: list  # 面试题列表

    task: dict  # 任务
    task_list: list  # 任务列表
    is_continuous: bool  # 是否继续
    is_summary:bool #是否进入总结
    problem_review_list: Annotated[list[dict], add]  # 面试题审查结果列表

    user_id: str  # 用户id
    thread_id: str  # 线程id
    user_data: dict  # 用户信息
    interview_summary: dict  # 用户面试总结

    agent_output_messages: str | list | dict


class OutputState(TypedDict):
    agent_output_messages: str | list | dict


# 子图的状态

# demand状态
class DemandOverALLState(MessagesState):
    problem_demand: str  # 面试需求
    is_history: bool  # 是否查询历史
    user_data: dict  # 用户信息


class DemandOutputState(TypedDict):
    problem_list: list  # 面试题列表


# memary状态
class MemaryOverAllState(TypedDict):
    problem_review_list: list
    user_data: dict
    thread_id: str
    user_id: str
    agent_output_messages: str


class MemaryOutputState(TypedDict):
    agent_output_messages: str
