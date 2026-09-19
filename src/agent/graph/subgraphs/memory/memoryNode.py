from agent.graph.state import OverAllState
from factory.modelFactory import chat_model
from agent.graph.structure import LangMemory


def get_messages_node(state:OverAllState)->OverAllState:
    #获取本次面试总结
    problem_review_list = state["problem_review_list"]
    #获取agent
    agent = chat_model.with_structured_output(LangMemory)

    
