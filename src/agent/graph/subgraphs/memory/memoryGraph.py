from langgraph.graph import StateGraph, START, END
from agent.graph.subgraphs.memory.memoryNode import *

builder = StateGraph(state_schema=MemaryOverAllState,output_schema=MemaryOutputState)

builder.add_node("interview_summary", interview_summary)
builder.add_node("create_md", create_md)
builder.add_node("output_node", output_node)

builder.add_edge(START, "interview_summary")
builder.add_edge(START, "create_md")
builder.add_edge("interview_summary", "output_node")
builder.add_edge("create_md", "output_node")
builder.add_edge("output_node", END)

memoryGraph = builder.compile()
