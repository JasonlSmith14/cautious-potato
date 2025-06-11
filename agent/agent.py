from typing import List, Optional, Type, TypeVar, Generic

from langchain_core.messages import HumanMessage
from langchain.chat_models import init_chat_model
from langchain_core.tools import BaseTool
from langgraph.prebuilt import create_react_agent
from sqlmodel import SQLModel

T = TypeVar("T", bound=SQLModel)


class Agent(Generic[T]):
    def __init__(
        self,
        name: str,
        model_name: str,
        model_provider: str,
        prompt: str,
        response_format: Type[T],
        tools: Optional[List[BaseTool]] = None,
    ):
        self.name = name
        self.model = init_chat_model(model=model_name, model_provider=model_provider)
        self.tools = tools or []
        self.prompt = prompt
        self.response_format = response_format

    def create_agent(self):
        return create_react_agent(
            self.model,
            tools=self.tools,
            response_format=self.response_format,
            prompt=self.prompt,
            name=self.name,
        )

    def invoke_agent(self, content: str) -> T:
        input = {"messages": [HumanMessage(content=content)]}
        response = self.create_agent().invoke(input, config={"recursion_limit": 100})
        return response["structured_response"]
