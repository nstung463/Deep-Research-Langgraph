from langchain_deepseek import ChatDeepSeek
from langchain_openai.chat_models import AzureChatOpenAI
from ..settings import AzureOpenAI, ChatOpenRouter, DeepSeekModel
from src.config.agents import LLMType
open_router = ChatOpenRouter()

deepseek_chat = ChatDeepSeek(
    **DeepSeekModel().__dict__,
    temperature=0.0,
)

azure_chat_openai_4 = AzureChatOpenAI(
    **AzureOpenAI().chat_gpt4_32k_model.__dict__,
    temperature=0,
    max_tokens=6000,
    model="gpt-4o",
    top_p=1.0,
    n=1,
    presence_penalty=0.0,
    frequency_penalty=0.0,
)

azure_chat_openai_41 = AzureChatOpenAI(
    **AzureOpenAI().chat_gpt4_1_model.__dict__,
    temperature=0,
    max_tokens=6000,
    model="gpt-4o",
    top_p=1.0,
    n=1,
    presence_penalty=0.0,
    frequency_penalty=0.0,
)

azure_chat_openai_4_mini = AzureChatOpenAI(
    **AzureOpenAI().chat_gpt4_mini_model.__dict__,
    temperature=0,
    max_tokens=4000,
    model="gpt-4o-mini",
    top_p=1.0,
    n=1,
    presence_penalty=0.0,
    frequency_penalty=0.0,
)


def get_llm_by_type(llm_type: LLMType):
    if llm_type == "basic":
        return azure_chat_openai_4
    elif llm_type == "reasoning":
        return deepseek_chat
    elif llm_type == "simple_tasks":
        return azure_chat_openai_4_mini
    elif llm_type == "gpt41":
        return azure_chat_openai_41
    elif llm_type == "gemini":
        return open_router