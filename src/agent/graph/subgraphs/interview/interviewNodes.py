"""
对用户进行中断提问

传入:面试题列表
对用户中断
传出:面试题审查结果列表

"""

from agent.graph.state import OverAllState
from agent.graph.structure import ProblemReview
from factory.modelFactory import chat_model,think_mode
from langchain.messages import SystemMessage, HumanMessage
from prompt.prompt import review_prompt
from utils.loggerUtil import logger


def review_node(state: OverAllState) -> OverAllState:
    task = state.get("task")

    logger.debug(f"[review_node]准备开始处理任务,任务:{task}")

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

    logger.debug(f"[review_node]任务处理完成:{problem_review_dict}")

    return {
        "problem_review_list": [problem_review_dict]
    }
