from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from agent.graph.subgraphs.demand.demandNodes import *
from agent.tools.agent_tools import search_rag
from agent.tools.middleware import wrap_tool_call, UserContext

tools = [search_rag,web_sercher]

builder = StateGraph(state_schema=DemandOverALLState, output_schema=DemandOutputState)

builder.add_node("get_rag_node", get_rag_node)
builder.add_node("tool_node", ToolNode(tools=tools, wrap_tool_call=wrap_tool_call))
builder.add_node("demand_output_node", demand_output_node)

builder.add_edge(START, "get_rag_node")
builder.add_conditional_edges("get_rag_node", demand_router, ["tool_node", "demand_output_node"])
builder.add_edge("tool_node", "get_rag_node")
builder.add_edge("demand_output_node", END)

demandGraph = builder.compile()

if __name__ == '__main__':
    result = demandGraph.invoke({
        "is_history": False,
        "problem_demand": "rag面试题"
    }, context=UserContext(max_attempts=5))

    print(result)
