from typing_extensions import TypedDict
from typing import Annotated, List
from langgraph.graph.message import add_messages
from pydantic import BaseModel



class State(TypedDict):
    query: str
    graph_schema: str
    cypher_query: str
    cypher_query_response: str
    final_response: str
    agent_messages: Annotated[list,add_messages]