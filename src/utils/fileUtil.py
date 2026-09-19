import os
import hashlib
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from utils.loggerUtil import logger
from config.config import path_config, rules_config
from utils.pathUtil import get_path

MD5_FILE_PATH = get_path(path_config["md5_file"])  # 默认MD5文件存储路径
ALLOW_FILES_TYPES = tuple(rules_config["allow_files_types"])  # 运行查询的文件类型
ENCODING = "utf-8"


def to_md5(path: str) -> str | None:
    """
    传入文件路径,转md5值
    :param path: str
    :return: md5
    """
    # 查询文件是否存在
    if not os.path.exists(path):
        return None

    # 读取文件内容
    md5_obj = hashlib.md5()
    chunk_size = 4096  # 每次读取的文件数量
    try:
        with open(path, "rb") as f:
            while chunk := f.read(chunk_size):
                md5_obj.update(chunk)
            md5_messages = md5_obj.hexdigest()
            return md5_messages
    except Exception as e:
        logger.error("md5转换失败")
        raise e


def check_file_md5(md5: str, path: str = MD5_FILE_PATH) -> bool:
    """
    传入md5值和文件路径,查询是否存在
    :param md5: str
    :param path: md5存储文件路径
    :return: bool是否存在
    """
    # 查询文件是否存在
    if not os.path.exists(path):
        return False

    # 读取文件内容
    with open(path, "r", encoding=ENCODING) as f:
        for line in f.readlines():
            if line.strip() == md5:
                return True

    return False


def save_md5_to_file(md5: str, path: str = MD5_FILE_PATH) -> bool:
    """
    传入md5值和文件路径,将md5值存入文件
    :param md5: str
    :param path: md5存储文件路径
    :return: bool是否成功
    """
    # 查询文件是否存在
    if not os.path.exists(path):
        # 创建文件
        open(path, "w", encoding=ENCODING).close()

    # 写入文件
    try:
        with open(path, "a", encoding=ENCODING) as f:
            f.write(md5 + "\n")
            return True
    except Exception as e:
        logger.error("写入失败")
        raise e


def get_documents(path: str, passwd=None):
    """
    传入文件路径,返回documents
    :param path: 文件路径
    :param passwd: pdf密码
    :return: 文件documents
    """
    if path.endswith("txt") or path.endswith("md"):
        return TextLoader(path, encoding=ENCODING).load()

    if path.endswith("pdf"):
        return PyPDFLoader(path, passwd).load()

    return []


def get_files(path: str) -> list:
    # 判断path是否为空
    if not path:
        raise Exception("路径不可以为空")

    # 判断文件夹是否存在
    if not os.path.isdir(path):
        raise Exception("路径位置不是文件夹")

    files = []

    for f in os.listdir(path):
        if f.endswith(ALLOW_FILES_TYPES):
            files.append(os.path.join(path, f))

    return files


if __name__ == '__main__':
    path = get_path("data/knowledge")
    # md5 = to_md5(path)
    # save_md5_to_file(md5)
    print(get_files(path))
