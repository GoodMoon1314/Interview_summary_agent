"""
用户初始输出  ->  llm结构化判断用户想要被面试的面试题类型 -> 浏览器搜索该类型的面试题->llm结构化整体/rag检索对应的面试题范围->

rag检索对应的面试题,凑齐十道题-> 进行查重校验,不满足重新上一轮调用 -> llm结构化整体十道面试题(问题/答案) -> 中断节点对用户进行提问 -> 用户回答恢复中断->

继续遍历题库,对用户提问/llm对上一题的用户回答以及答案进行思考判断正确率,结构化输出(正确率/批判内容)  -> .....10道题询问结束 ->

llm对上方所整理好的(题目/答案/正确率/批判内容)总结整体为md文件保存
"""
from langgraph.graph import StateGraph, START, END
from agent.graph.nodes import *
from agent.graph.state import OverAllState, InputState, OutputState

builder = StateGraph(state_schema=OverAllState, input_schema=InputState, output_schema=OutputState)

# 父节点
builder.add_node("user_input_node", user_input_node)
builder.add_node("agent_output_node", agent_output_node)
builder.add_node("get_task", get_task)
builder.add_node("get_problem_node", get_problem_node)
builder.add_node("get_user_data_node", get_user_data_node)
builder.add_node("review_node", review_node)


# 子图节点
builder.add_node("demand_graph_node", demand_graph_node)
builder.add_node("memory_node", memory_node)

# 构建边
builder.add_edge(START, "user_input_node")
builder.add_conditional_edges("user_input_node", demand_router, ["agent_output_node","get_user_data_node"])
builder.add_edge("get_user_data_node", "demand_graph_node")
builder.add_edge("demand_graph_node", "get_problem_node")
builder.add_edge("get_problem_node", "get_task")
builder.add_conditional_edges("get_task", search_node,["review_node","memory_node","get_task"])
builder.add_edge("review_node", "get_task")
builder.add_edge("memory_node", "agent_output_node")
builder.add_edge("agent_output_node", END)
