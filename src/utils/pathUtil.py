"""
路径获取工具
"""
import os


def get_project_path() -> str:
    """
    获取项目所在的根目录
    :return: 字符串根目录
    """
    # 当前文件的绝对路径
    current_file:str = os.path.abspath(__file__)
    # 获取项目的根目录,先获取文件所在的文件夹绝对路径
    current_dir:str = os.path.dirname(current_file)
    # 返回项目根目录
    return os.path.dirname(current_dir)


def get_path(relative_path: str) -> str:
    """
    传入相对路径str,返回绝对路径str
    :param relative_path: 相对路径str
    :return: 绝对路径str
    """
    project_root = get_project_path()
    return os.path.join(project_root,relative_path)
