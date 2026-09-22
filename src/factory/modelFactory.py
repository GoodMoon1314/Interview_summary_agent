from dashscope.acli.cli import streaming
from langchain.chat_models import init_chat_model
from langchain_community.embeddings import DashScopeEmbeddings

from config.config import model_config


def get_model(model: str, thinking: bool = False, stream: bool = False):
    if stream:
        return init_chat_model(model=model, streaming=True)

    if thinking:
        return init_chat_model(model=model)
    else:
        return init_chat_model(
            model=model,
            extra_body={
                "thinking": {"type": "disabled"}
            },
        )


chat_model = get_model(model_config["deepseek_mode"])
think_mode = get_model(model_config["deepseek_mode"], True)
embedding_model = DashScopeEmbeddings(model=model_config["embedding_model"])
stream_model = get_model(model_config["deepseek_mode"], stream=True)

if __name__ == '__main__':
    think_mode.invoke("你好").pretty_print()
