import json
from dataclasses import dataclass
from utils.loggerUtil import logger
from langchain_core.messages import ToolMessage

cache_list = {}

@dataclass
class UserContext:
    max_attempts: int

def wrap_tool_call(request, execute):
    max_attempts = request.runtime.context.max_attempts
    tool_call_id = request.runtime.tool_call_id
    tool_name = request.tool_call["name"]
    tool_args = json.dumps(request.tool_call["args"])

    cache = (tool_name, tool_args)
    message = cache_list.get(cache)

    if not max_attempts:
        max_attempts = 3

    msg = None

    if message:
        logger.info("利用缓存")
        return ToolMessage(
            tool_call_id=tool_call_id,
            content=message
        )

    else:
        for i in range(max_attempts):
            try:
                logger.debug(f"开始调用工具:{tool_name}")

                msg = execute(request)

                logger.debug("工具调用成功")

                cache_list[cache] = msg.content

                break
            except ConnectionError as e:
                logger.info(f"工具调用失败,调用{i}次,还剩{max_attempts - i}次")
                logger.error(e)

            if not msg:
                msg = ToolMessage(
                    tool_call_id=tool_call_id,
                    content="工具调用失败,调用次数已经达到上限"
                )

    return msg
