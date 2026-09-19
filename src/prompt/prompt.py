import os

from utils.loggerUtil import logger
from config.config import path_config
from utils.pathUtil import get_path

# 获取config文件存储路径
PROMPT_PATH = get_path(path_config["prompt"])


# 获取提示词
def get_config(name: str, encoding: str = "utf_8"):
    prompts_path = PROMPT_PATH
    prompt_path = PROMPT_PATH + "/" + name + ".txt"

    # 判断文件夹是否存在
    os.makedirs(prompts_path, exist_ok=True)

    # 返回提示词内容文件
    try:
        return open(prompt_path, "r", encoding=encoding).read()
    except Exception as e:
        logger.error("未找到提示词文件")
        raise e


demand_prompt = get_config("demand_prompt")
problem_prompt = get_config("problem_prompt")
demand_structure_prompt = get_config("demand_structure_prompt")
review_prompt = get_config("review_prompt")

if __name__ == '__main__':
    print(demand_prompt)
