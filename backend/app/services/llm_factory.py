from langchain_aws import ChatBedrock
from langchain_community.chat_models import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel
from app.core.config import settings
import os

class LLMFactory:
    @staticmethod
    def create_llm(model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0") -> BaseChatModel:
        """
        Creates an LLM instance based on configuration.
        Defaults to AWS Bedrock, falls back to Mock/OpenAI if credentials missing.
        """
        
        # Check for AWS Creds
        aws_key = os.getenv("AWS_ACCESS_KEY_ID") or settings.AWS_ACCESS_KEY_ID
        if aws_key and "mock" not in aws_key:
            return ChatBedrock(
                model_id=model_id,
                client=None, # let langchain create client
                region_name=settings.AWS_REGION
            )
        
        # Fallback to Mock / OpenAI (if key exists) or a custom FakeLLM (for demo)
        if settings.OPENAI_API_KEY and "mock" not in settings.OPENAI_API_KEY:
             return ChatOpenAI(model="gpt-4o", temperature=0)
        
        # If completely offline/mock
        print("WARNING: Using Mock LLM (FakeListChatModel) as no valid credentials found.")
        from langchain_community.chat_models import FakeListChatModel
        return FakeListChatModel(responses=[
            "Mock response: I have analyzed the sales data.",
            "Mock response: Sales in Q1 were $1M.",
            "Mock response: Creating a bar chart for you."
        ])

llm_factory = LLMFactory()
