import re
from backend.src.adapters.outbound.llms import GoogleGenAI
from langchain_core.messages import AIMessage,HumanMessage,SystemMessage
from backend.src.adapters.outbound.agents.market_mind.tools import *
import asyncio
import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from backend.src.adapters.outbound.logging.std_logger import StdLogger

current_dir = os.path.dirname(os.path.abspath(__file__))

async def load_prompt(template_name, **kwargs):
    env = Environment(loader=FileSystemLoader(os.path.join(current_dir,'..','prompts', 'templates')))
    template = env.get_template(template_name)
    return template.render(**kwargs)


class Nodes():
    def __init__(self):
        self.llm_obj=GoogleGenAI()
        self.tools=[run_cypher_query]
        self.tool_names=[func.__name__ for func in self.tools]
        self.llm_obj.llm_with_tools=self.llm_obj.llm.bind_tools(self.tools)
        self.logger=StdLogger()
    async def initial_state(self,state):
        self.logger.info('entering initial_state node')
        # graph_schema=await get_graph_schema()
        now = datetime.now()
        system_prompt = await load_prompt("market_mind_agent_prompt.jinja",
                                          date=now
                                          )
        messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"{state['query']}")
        ]
        return {"agent_messages":messages}
    
    async def agent(self,state):
        self.logger.info('entering agent node')
        
        response= await self.llm_obj.llm_with_tools.ainvoke(state["agent_messages"])
        await asyncio.sleep(5)
        return {"agent_messages":[response]}
    
    def final_state(self,state):
        # USED to clean cache if ANY
        return {"final_response":state["agent_messages"][-1].content}