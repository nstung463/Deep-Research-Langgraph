import os
from typing import Union
from dotenv import dotenv_values, load_dotenv
from langchain_community.chat_models import ChatOpenAI

if os.path.exists(".env"):
    load_dotenv()
    config = dotenv_values(".env")
else:
    config = {}


class ChatGPT4Model:
    azure_endpoint: Union[str, None]
    api_key: Union[str, None]
    api_version: Union[str, None]
    azure_deployment: Union[str, None]
    timeout: Union[float, None]

    def __init__(self) -> None:
        self.azure_endpoint = config.get("OPENAI-GPT4O-ENDPOINT")
        self.api_key = config.get("OPENAI-GPT4O-API-KEY")
        self.api_version = config.get(
            "OPENAI-GPT4O-API-VERSION", "2024-08-01-preview"
        )
        self.azure_deployment = config.get(
            "OPENAI-GPT4O-DEPLOYMENT-NAME"
        )
        self.timeout = float(config.get("TIMEOUT", 60 * 5))


class ChatGPT4oMiniModel:
    azure_endpoint: Union[str, None]
    api_key: Union[str, None]
    api_version: Union[str, None]
    azure_deployment: Union[str, None]
    timeout: Union[float, None]

    def __init__(self) -> None:
        self.azure_endpoint = config.get(
            "OPENAI-GPT4O-MINI-ENDPOINT"
        )
        self.api_key = config.get("OPENAI-GPT4O-MINI-API-KEY")
        self.api_version = config.get(
            "OPENAI-GPT4O-MINI-API-VERSION",
            "2024-08-01-preview",
        )
        self.azure_deployment = config.get(
            "OPENAI-GPT4O-MINI-DEPLOYMENT-NAME"
        )
        self.timeout = float(config.get("TIMEOUT", 60 * 5))




class ChatOpenRouter(ChatOpenAI):
    openai_api_base: str
    openai_api_key: str
    model_name: str
    
    def __init__(self,
                model_name: str = None,
                openai_api_key: str = None,
                openai_api_base: str = None,
                 **kwargs):
        model_name = model_name or config.get('OPENROUTER_API_NAME')
        openai_api_key = openai_api_key or config.get('OPENROUTER_API_KEY')
        openai_api_base = openai_api_base or config.get('OPENROUTER_API_BASE')
        super().__init__(openai_api_base=openai_api_base,
                        openai_api_key=openai_api_key,
                        model_name=model_name, **kwargs)

class DeepSeekModel:
    api_key: Union[str, None]
    api_base: Union[str, None]
    model_name: str

    def __init__(self) -> None:
        self.api_key = config.get("DEEPSEEK_API_KEY")
        self.api_base = config.get("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")
        self.model_name = config.get("DEEPSEEK_MODEL_NAME", "deepseek-chat")  # Default model


class AzureOpenAI:
    chat_gpt4_32k_model: ChatGPT4Model
    chat_gpt4_mini_model: ChatGPT4oMiniModel

    def __init__(self) -> None:
        self.chat_gpt4_32k_model = ChatGPT4Model()
        self.chat_gpt4_mini_model = ChatGPT4oMiniModel()


