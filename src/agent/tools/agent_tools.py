from rag.vectorService import search_vector
from langchain_core.tools import tool



@tool(parse_docstring=True)
def search_rag(problem: str) -> list:
    """
    传入要检索的内容,返回知识库查阅到的内容

    Args:
        problem: 需要去知识库查询的问题
    """
    return search_vector(problem)
