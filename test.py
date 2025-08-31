import os
from dotenv import load_dotenv
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities.sql_database import SQLDatabase
from sqlalchemy import create_engine, inspect
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel

from agent.agent import Agent

load_dotenv()

USERNAME = os.getenv("DATABASE_USERNAME")
PASSWORD = os.getenv("DATABASE_PASSWORD")
PORT = os.getenv("PORT")
DATABASE_NAME = os.getenv("DATABASE_NAME")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
)

engine = create_engine(
    f"postgresql://{USERNAME}:{PASSWORD}@localhost:{PORT}/{DATABASE_NAME}"
)

inspector = inspect(engine)
all_tables = inspector.get_table_names()

allowed_tables = [t for t in all_tables if t.startswith("gold_")]

db = SQLDatabase.from_uri(
    f"postgresql://{USERNAME}:{PASSWORD}@localhost:{PORT}/{DATABASE_NAME}",
    include_tables=allowed_tables,
)

toolkit = SQLDatabaseToolkit(db=db, llm=llm)

print(toolkit.get_context())


class Response(BaseModel):
    response: str

agent = Agent(
    "sql-agent",
    model_name="gemini-2.5-flash",
    model_provider="google_genai",
    prompt="Get the information related to the question",
    response_format=Response,
    tools=toolkit.get_tools(),
)

print(agent.invoke_agent("Is my spending across each category consistent over the months? If not, find which transactions caused this. Do not mention actual figures"))
