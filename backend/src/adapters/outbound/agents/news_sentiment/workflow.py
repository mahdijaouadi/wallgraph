from jinja2 import Environment, FileSystemLoader
import os
from langchain_core.messages import AIMessage,HumanMessage,SystemMessage,ToolMessage,RemoveMessage
from backend.src.adapters.outbound.llms import GoogleGenAI
import json
from backend.src.domain.models import NewsSentiment, News
from typing import List
import asyncio

current_dir = os.path.dirname(os.path.abspath(__file__))



class Workflow:
    def __init__(self) -> None:
        self.llm_obj = GoogleGenAI()
        self.llm= self.llm_obj.llm
        self.llm_sleep= self.llm_obj.llm_sleep
        pass
    async def parse(self, text: str) -> List[NewsSentiment]:
        try:
            data = json.loads(text)
            return [NewsSentiment(
                ticker=d["ticker"],
                sentiment=d["sentiment"],
                justification=d["justification"]
            ) for d in data]
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Failed to parse LLM output: {e}")
    async def load_prompt(self,template_name, **kwargs):
        env = Environment(loader=FileSystemLoader(os.path.join(current_dir,'prompts', 'templates')))
        template = env.get_template(template_name)
        return template.render(**kwargs)
    
    async def news_to_ticker_sentiment(self,news: News) -> List[NewsSentiment]:
        system_prompt = await self.load_prompt("news_sentiment_extractor_prompt.jinja")
        messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"{news.feed}")
            ]

        response= await self.llm.ainvoke(messages)
        if response.content[0]=="`":
            response.content=response.content[7:-4]
        response= await self.parse(response.content)
        await asyncio.sleep(self.llm_sleep)
        return response
