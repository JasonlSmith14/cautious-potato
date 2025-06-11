from langchain.chat_models import init_chat_model
from sqlmodel import SQLModel
from typing import List, Type, TypeVar
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import BaseTool
from llms.base_llm import BaseLLM


T = TypeVar("T", bound=SQLModel)


class Gemini(BaseLLM):

    def __init__(
        self,
        tools: List[BaseTool] = [],
        model_name: str = "gemini-2.0-flash",
        model_provider: str = "google_genai",
    ):

        self.model = init_chat_model(model_name, model_provider=model_provider)
        self.model = self.model.bind_tools(
            tools, tool_choice=("any" if tools else None)
        )
        self.tools = {t.name: t for t in tools}

    def generate_response(self, input: str, response_format: Type[T]) -> T:
        messages = [HumanMessage(content=input)]
        model_with_structure = self.model.with_structured_output(schema=response_format)

        ai_msg: AIMessage = self.model.invoke(messages)

        if getattr(ai_msg, "tool_calls", None):
            messages.append(ai_msg)

            for tool_call in ai_msg.tool_calls:
                selected_tool = self.tools[tool_call["name"]]
                tool_msg = selected_tool.invoke(tool_call)
                messages.append(tool_msg)

        ai_msg = model_with_structure.invoke(messages)

        return ai_msg


