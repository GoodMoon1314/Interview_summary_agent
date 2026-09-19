import os

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

from factory.modelFactory import embedding_model
from utils.fileUtil import get_files, to_md5, check_file_md5, get_documents, save_md5_to_file
from utils.pathUtil import get_path
from utils.loggerUtil import logger
from config.config import path_config, vector_config

# 预设文档
predefined_docs = [
    Document(
        page_content="知识库",
        metadata={"source": "manual", "id": 1}
    )
]


class VectorStoreService:
    def __init__(self):
        self.embedding = embedding_model
        self.persist_directory = get_path(path_config["vector_db"])  # 向量存储文件夹

        if os.path.exists(self.persist_directory) and os.listdir(self.persist_directory):
            self.vector_store = FAISS.load_local(
                self.persist_directory,
                embeddings=self.embedding,  # 嵌入式模型
                allow_dangerous_deserialization=True
            )
        else:
            self.vector_store = FAISS.from_documents(predefined_docs, embedding=embedding_model)

        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["## ", "### ", "\n\n", "\n", ".", "!", "?", "。", "！", "？"],
            length_function=len,
        )

    def retriever(self):
        return self.vector_store.as_retriever(search_kwargs={"k": vector_config["k"]})

    def load_vector(self):
        """
        从数据文件夹内读取数据文件，转为向量存入向量库
        要计算文件的MD5做去重
        :return: None
        """
        allowed_files_path: list[str] = get_files(
            get_path(path_config["knowledge"])
        )

        for path in allowed_files_path:
            # 获取文件的MD5
            md5_hex = to_md5(path)

            if check_file_md5(md5_hex):
                logger.info(f"[加载知识库]{path}内容已经存在知识库内，跳过")
                continue

            try:
                documents: list[Document] = get_documents(path)

                if not documents:
                    logger.warning(f"[加载知识库]{path}内没有有效文本内容，跳过")
                    continue

                split_document: list[Document] = self.spliter.split_documents(documents)

                if not split_document:
                    logger.warning(f"[加载知识库]{path}分片后没有有效文本内容，跳过")
                    continue

                # 将内容存入向量库
                self.vector_store.add_documents(split_document)

                # 记录这个已经处理好的文件的md5，避免下次重复加载
                save_md5_to_file(md5_hex)

                logger.info(f"[加载知识库]{path} 内容加载成功")
            except Exception as e:
                # exc_info为True会记录详细的报错堆栈，如果为False仅记录报错信息本身
                logger.error(f"[加载知识库]{path}加载失败：{str(e)}", exc_info=True)
                continue

        self.vector_store.save_local(self.persist_directory)
        logger.info(f"FAISS向量库持久化完成，路径：{self.persist_directory}")


if __name__ == '__main__':
    vs = VectorStoreService()

    vs.load_vector()

    print(vs.persist_directory)

    retriever = vs.retriever()

    res = retriever.invoke("RAG")
    for r in res:
        print(r.page_content)
        print("-" * 20)
