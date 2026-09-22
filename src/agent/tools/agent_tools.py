from rag.vectorService import search_vector
from langchain_core.tools import tool
from langchain_tavily import TavilySearch

from utils.loggerUtil import logger


@tool(parse_docstring=True)
def search_rag(problem: str) -> list:
    """
    传入要检索的内容,返回知识库查阅到的内容

    Args:
        problem: 需要去知识库查询的问题
    """
    logger.info("正在查询知识库......")
    return search_vector(problem)


@tool(parse_docstring=True)
def web_sercher(topic: str) -> str:
    """
    传入要查询的主题,返回查询内容

    Args:
        topic:要查询的主题
    """
    logger.info("正在联网搜索......")
    web_search = TavilySearch(
        max_results=5,
        topic="general"
    )

    return web_search.invoke(topic).get("results")
