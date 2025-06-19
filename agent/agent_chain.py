import json
from typing import List, Optional
from langgraph.graph import StateGraph, END
from pydantic import BaseModel

from agent.agent import Agent
from models.information import TransactionInformation
from models.inputs import CategoryInformationInputs, ParsedInformationInputs
from models.tables import ParsedStatement


class TransactionState(BaseModel):
    parsed_statements: List[ParsedStatement] = []
    parsing_information: Optional[ParsedInformationInputs] = None
    categorising_information: Optional[CategoryInformationInputs] = None
    transactions: Optional[List[TransactionInformation]] = None


class AgentChain:
    def __init__(
        self,
        parsing_agent: Agent,
        categorising_agent: Agent,
    ):
        self.parsing_agent = parsing_agent
        self.categorsing_agent = categorising_agent

        self.graph = self.build_graph()

    def _parsing_node(self, state: TransactionState) -> TransactionState:
        parsed_statements = state.parsed_statements

        content = ""
        for parsed_statement in parsed_statements:
            content += f"{parsed_statement.strategy_name}:\n\n{parsed_statement.strategy_result}\n\n\n"

        parsing_information = self.parsing_agent.invoke_agent(content=content)
        state.parsing_information = parsing_information
        return state

    def _categorising_node(self, state: TransactionState) -> TransactionState:
        parsed = state.parsing_information.parsed_information_inputs

        content = [
            {p.id: {"description": p.data.description, "amount": p.data.amount}}
            for p in parsed
        ]

        content = json.dumps(content)

        categorising_information = self.categorsing_agent.invoke_agent(content=content)
        state.categorising_information = categorising_information
        return state

    def _consolidating_node(self, state: TransactionState):
        parsed = state.parsing_information.parsed_information_inputs
        categorised = state.categorising_information.category_information_inputs

        parsed_mapping = {p.id: p.data for p in parsed}
        categorised_mapping = {c.id: c.data for c in categorised}

        transaction_information_inputs = []
        for c in categorised:
            parsed = parsed_mapping[c.id]
            category = categorised_mapping[c.id]

            transaction_information_inputs.append(
                TransactionInformation(
                    transaction_date=parsed.transaction_date,
                    amount=parsed.amount,
                    balance=parsed.balance,
                    description=parsed.description,
                    cleaned_description=category.cleaned_description,
                    category=category.category,
                    reasoning=category.reasoning,
                )
            )

        state.transactions = transaction_information_inputs
        return state

    def build_graph(self):
        builder = StateGraph(TransactionState)

        builder.add_node("parsing", self._parsing_node)
        builder.add_node("categorising", self._categorising_node)
        builder.add_node("consolidating", self._consolidating_node)

        builder.set_entry_point("parsing")
        builder.add_edge("parsing", "categorising")
        builder.add_edge("categorising", "consolidating")
        builder.add_edge("consolidating", END)

        return builder.compile()

    def process_transactions(
        self, parsed_statements: ParsedStatement
    ) -> List[TransactionInformation]:
        result = self.graph.invoke(
            TransactionState(parsed_statements=parsed_statements)
        )

        return result.get("transactions")
