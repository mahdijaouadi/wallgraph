import sys
from backend.src.adapters.outbound.agents.market_mind.workflow.nodes import Nodes
from backend.src.adapters.outbound.agents.market_mind.workflow.state import State
from langgraph.graph import START,END,StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
import os
from langfuse.langchain import CallbackHandler

current_dir = os.path.dirname(os.path.abspath(__file__))



async def agent_tool_node(state):
    last_message = state['agent_messages'][-1]
    
    if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
        return {}
    
    tool_messages = []
    for tool_call in last_message.tool_calls:
        tool_name = tool_call['name']
        tool_args = tool_call['args']
        
        tool_func = None
        for tool in Nodes().tools:
            if tool.__name__ == tool_name:
                tool_func = tool
                break
        
        if tool_func:
            try:
                filtered_args = {k: v for k, v in tool_args.items() if k != 'state'}
                result = await tool_func(**filtered_args, state=state)
                tool_message = ToolMessage(
                    content=str(result),
                    tool_call_id=tool_call['id']
                )
                tool_messages.append(tool_message)
            except Exception as e:
                error_message = ToolMessage(
                    content=f"Error executing {tool_name}: {str(e)}",
                    tool_call_id=tool_call['id']
                )
                tool_messages.append(error_message)
    
    return {"agent_messages": tool_messages}

async def tools_condition_executor(state):
    messages = state.get("agent_messages", [])
    if not messages:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")
    
    last_message = messages[-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "agent_tool_node"
    return "final_state"

class WorkFlow():
    def __init__(self,request):
        nodes=Nodes()
        self.workflow=StateGraph(State)
        #NODES
        self.workflow.add_node('initial_state',nodes.initial_state)
        self.workflow.add_node('agent',nodes.agent)
        self.workflow.add_node('agent_tool_node',agent_tool_node)
        self.workflow.add_node('final_state',nodes.final_state)

        #EDGES
        self.workflow.add_edge(START,'initial_state')
        self.workflow.add_edge("initial_state",'agent')
        self.workflow.add_conditional_edges('agent',tools_condition_executor,{'agent_tool_node':'agent_tool_node','final_state':"final_state"})
        self.workflow.add_edge("agent_tool_node",'agent')

        memory=MemorySaver()
        self.workflow = self.workflow.compile(checkpointer=memory)
        self.langfuse_handler = CallbackHandler()
        self.config={'configurable':{'thread_id':1},"recursion_limit": 100,"callbacks": [self.langfuse_handler]}
        # self.config={'configurable':{'thread_id':1},"recursion_limit": 10}
    async def __call__(self,request):
        response=await self.workflow.ainvoke({"query":request.query},self.config)
        return response