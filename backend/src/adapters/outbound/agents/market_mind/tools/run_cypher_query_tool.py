import os
from typing_extensions import Annotated
from langgraph.prebuilt import InjectedState
from backend.src.adapters.outbound.neo4j.driver import get_readonly_session

current_dir = os.path.dirname(os.path.abspath(__file__))


async def run_cypher_query(query: str, state: Annotated[dict, InjectedState]) -> str:
    """
    Execute a cypher query.

    Args:
        query (str): the cypher query to execute
        state: Automatically injected by the system - do not include this parameter in tool calls.
        
    Returns:
        The result of the query execution.
    """
    try:
        if query[0]=="`":
            query=query[9:-4]
        async with await get_readonly_session() as session:
            async with await session.begin_transaction() as tx:
                result = await tx.run(query)
                records = await result.data()
                await tx.commit()
                return records
    except Exception as e:
        return f"Error running cypher query: {e}"