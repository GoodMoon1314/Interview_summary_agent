import os
import json
from datetime import datetime
from langchain.messages import SystemMessage, HumanMessage
from config.config import db_config
from agent.graph.state import MemaryOverAllState, MemaryOutputState
from factory.modelFactory import chat_model
from agent.graph.structure import LangMemory
import psycopg
from psycopg.rows import dict_row
from config.config import path_config
from prompt.prompt import interview_summary_prompt, create_md_prompt
from utils.loggerUtil import logger
from utils.pathUtil import get_path


# 调用大模型对用户面试总结
def interview_summary(state: MemaryOverAllState) -> MemaryOverAllState:
    logger.info("开始生成面试总结")

    user_data = state.get("user_data")
    problem_review_list = state.get("problem_review_list")
    thread_id = state.get("thread_id")
    user_id = state.get("user_id")

    user_name = user_data.get("user_name")
    summary_text = user_data.get("summary_text")

    agent = chat_model.with_structured_output(LangMemory)

    human_prompt = f"用户名称:{user_name},用户此次面试结果:{problem_review_list},用户历史总结:{summary_text}"

    system = SystemMessage(content=interview_summary_prompt)
    human = HumanMessage(content=human_prompt)

    result = agent.invoke([system,human])

    conn_str = db_config["DB_URL"]
    with psycopg.connect(conn_str, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            result_str = json.dumps(result, ensure_ascii=False)
            sql = "UPDATE interview_summary SET summary_text = %s, created_time = NOW() WHERE type = 'interview_summary' AND thread_id = %s AND user_id = %s;"
            cur.execute(sql, (result_str, thread_id, user_id))

    return {
        "interview_summary": result
    }


def create_md(state: MemaryOverAllState) -> MemaryOverAllState:
    logger.info("开始生成文件")

    problem_review_list = state.get("problem_review_list")
    user_data = state.get("user_data")
    user_name = user_data.get("user_name")
    thread_id = state.get("thread_id")

    human_prompt = f"用户名:{user_name},用户面试结果:{problem_review_list}"

    system = SystemMessage(content=create_md_prompt)
    human = HumanMessage(content=human_prompt)

    result = chat_model.invoke([system,human]).content

    # 生成文件:
    path = get_path(path_config["interview_summary"])
    os.makedirs(path, exist_ok=True)

    md_path = path + f"/{user_name}_{thread_id}_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S.%f")}.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(result)

    return {
        "agent_output_messages": result
    }


def output_node(state: MemaryOverAllState) -> MemaryOutputState:
    logger.info("生成结束")

    agent_output_messages = state.get("agent_output_messages")

    return {
        "agent_output_messages": agent_output_messages
    }
