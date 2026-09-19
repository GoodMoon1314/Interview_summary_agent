import os

import yaml
from utils.loggerUtil import logger

from utils.pathUtil import get_path

# 获取config文件存储路径
CONFIGS_PATH = get_path("config/configs")


# 获取配置文件
def get_config(name: str, encoding: str = "utf_8"):
    configs_path = CONFIGS_PATH
    config_path = CONFIGS_PATH + "/" + name + ".yml"

    # 判断文件夹是否存在
    os.makedirs(configs_path,exist_ok=True)

    # 返回yml文件
    try:
        with open(config_path, "r", encoding=encoding) as f:
            return yaml.load(f, Loader=yaml.FullLoader)
    except Exception as e:
        logger.error("未查询到该字段")
        raise e


model_config = get_config("model")
path_config = get_config("path")
vector_config = get_config("vector")
rules_config = get_config("rules")
db_config = get_config("db")

if __name__ == '__main__':
    print(model_config["chat_model"])
