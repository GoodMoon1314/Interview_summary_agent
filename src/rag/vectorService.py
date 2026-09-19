from rag.vectorStore import VectorStoreService


def search_vector(problem: str):
    vs = VectorStoreService()

    retriever = vs.retriever()

    res = retriever.invoke("RAG 的完整链路是怎样的？")

    return res